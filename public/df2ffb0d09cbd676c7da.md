---
title: ローカルのopencodeからDatabricks Model ServingのClaudeを使ってみた
tags:
  - opencode
  - Databricks
  - ClaudeSonnet
  - AIエージェント
  - LLM
private: false
updated_at: '2026-08-06T15:51:29+09:00'
id: df2ffb0d09cbd676c7da
organization_url_name: databricks
slide: false
ignorePublish: false
posting_campaign_uuid: null
agreed_posting_campaign_term: false
---
# はじめに

以前の記事で、Databricksがオープンソースで公開したOmnigentと「メタハーネス」という考え方を紹介しました。メタハーネスは、Claude CodeやCodexといった個々のエージェントハーネスの一段上に立って、合成・制御・協働を担う層でした。

- [メタハーネスとは何か ― Databricks発のOSS『Omnigent』が解決しようとしていること](https://qiita.com/taka_yayoi/items/2ff51f2df46cc1285ba3)

今回はその一段下、ハーネス層そのものに目を向けます。OSSのエージェントハーネスの代表格であるopencodeを手元のMacで動かし、モデルプロバイダーとしてDatabricks Model Serving (基盤モデルAPI) を指定する構成を試しました。つまり「メタハーネス → ハーネス → モデル」の三層のうち、ハーネスをOSSに、モデルをDatabricksに差し替えてみる、という検証です。

- [opencode公式ドキュメント](https://opencode.ai/docs/)
- [Databricks 基盤モデルAPI](https://docs.databricks.com/aws/ja/machine-learning/foundation-model-apis)

結論から言うと、設定ファイルを1つ書くだけで、opencodeのエージェントループがDatabricksエンドポイント経由のClaudeで普通に回ります。そのあたりも含めて書いていきます。

# エージェントハーネスとしてのopencode

ここで言う「ハーネス」は、モデルの周囲にある足場のことです。ファイルを読み、ツールを呼び、シェルコマンドを実行し、その結果をモデルに返して次のステップに進ませるループ。モデル自体は「次に何をすべきか」を出力するだけなので、エージェントとして仕事を完遂させるのはこのハーネス層の役割です。

opencodeは、このハーネス層のOSS実装として2026年時点で最も勢いのあるプロジェクトです。特徴を整理すると以下のとおりです。

- **プロバイダー非依存**: 特定のモデルベンダーに紐づかず、75以上のプロバイダーとローカルモデル (Ollama等) をサポート。OpenAI互換のカスタムエンドポイントも設定ファイルだけで追加できる
- **ターミナルファーストのTUI**: Claude CodeやCodexと同じ操作感のターミナルUI。plan/buildのモード切り替え、サブエージェント、LSP連携を標準装備
- **オープンソース**: GitHubスター数は16万を超え、OSSハーネスとしては最大規模。リポジトリは現在 anomalyco/opencode

一方で、注意しておきたい経緯もあります。2026年1月のAnthropicとの係争を受けて、opencodeはClaude Pro/Maxサブスクリプションでのログインを削除しました。現在Claudeを使うには生のAPIキーが必要です。「Claude Codeと同じ感覚でサブスクのClaudeを使う」という選択肢が塞がれたことで、「では、どこからClaudeを調達するか」が実務上の論点になりました。

# なぜモデルプロバイダーをDatabricksにするのか

この「Claudeの調達先」問題に対する一つの答えが、Databricks Model Servingです。

Databricksの基盤モデルAPIは、Claude、GPT、Geminiといった主要モデルをDatabricksホストのサービングエンドポイントとして提供しており、これらはすべてOpenAI互換のAPIを公開しています。

- [Databricksホストの基盤モデル](https://docs.databricks.com/aws/ja/machine-learning/foundation-model-apis/supported-models)

つまり、opencodeから見れば「ただのOpenAI互換エンドポイント」として扱えます。Anthropicと個別に契約してAPIキーを管理する代わりに、既存のDatabricksワークスペースの個人用アクセストークン (PAT) だけでClaudeが使えます。モデルの利用がワークスペースの認証・監査・課金の枠組みにそのまま乗る。この点が、開発者ごとにAPIキーを配る運用を避けたい組織ではじわじわ効いてきます。

# curlで疎通確認

opencodeに組み込む前に、素のcurlでエンドポイントの疎通を確認しておきます。ここを飛ばすと、後で問題が起きたときにopencode側の設定とDatabricks側のどちらが原因か切り分けられなくなります。

事前にワークスペースでPATを発行し (ユーザー設定 > Developer > Access tokens)、環境変数に入れておきます。

```bash
export DATABRICKS_TOKEN=dapi...
```

チャット補完のエンドポイントを直接叩きます。`model` にはワークスペースのServing画面で確認したエンドポイント名を指定します。今回は `databricks-claude-sonnet-4-5` を使いました。

```bash
curl -u token:$DATABRICKS_TOKEN \
  -X POST \
  -H "Content-Type: application/json" \
  -d '{"model": "databricks-claude-sonnet-4-5", "messages": [{"role": "user", "content": "hello"}], "max_tokens": 32}' \
  https://<workspace-host>/serving-endpoints/chat/completions
```

次のようなレスポンスが返ってくれば成功です。

```json
{"model":"global.anthropic.claude-sonnet-4-5-20250929-v1:0","choices":[{"message":{"role":"assistant","content":"Hello! How can I help you today?"},"index":0,"finish_reason":"stop"}],"usage":{"completion_tokens":12,"prompt_tokens":8,"total_tokens":20},"object":"chat.completion","id":"msg_bdrk_018ZD8urRW7PiewaCeAPv15M","created":1785998408}
```

`model` フィールドを見ると `global.anthropic.claude-sonnet-4-5...` となっており、裏側がBedrock経由のClaudeであることが分かります。レスポンス形式は標準的なOpenAI互換なので、クライアント側はこれを意識する必要はありません。

# opencodeのプロバイダー設定

opencodeをインストールします。

```bash
brew install opencode
```

opencodeはカスタムのOpenAI互換プロバイダーを `@ai-sdk/openai-compatible` アダプター経由で追加できます。

- [opencode: Providers](https://opencode.ai/docs/providers/)

グローバル設定の `~/.config/opencode/opencode.json` に以下を書きます (特定プロジェクトだけで使うなら、そのディレクトリ直下の `opencode.json` でも構いません)。

```json
{
  "$schema": "https://opencode.ai/config.json",
  "provider": {
    "databricks": {
      "npm": "@ai-sdk/openai-compatible",
      "name": "Databricks",
      "options": {
        "baseURL": "https://<workspace-host>/serving-endpoints",
        "apiKey": "{env:DATABRICKS_TOKEN}"
      },
      "models": {
        "databricks-claude-sonnet-4-5": {
          "name": "Claude Sonnet 4.5 (Databricks)",
          "limit": {
            "context": 200000,
            "output": 8192
          }
        }
      }
    }
  },
  "model": "databricks/databricks-claude-sonnet-4-5"
}
```

ポイントは3つあります。

- `baseURL` は `/serving-endpoints` で止める。`/chat/completions` まで書くとパスが二重になって失敗します
- `models` のキーはサービングエンドポイント名と完全一致させる。カスタムプロバイダーではこのIDがそのままAPIに渡されます
- 設定を編集したらopencodeの再起動が必要

APIキーは `{env:DATABRICKS_TOKEN}` で環境変数を参照させています。起動時のシェル環境を参照するので、`DATABRICKS_TOKEN` をexportしたシェルからopencodeを起動してください。別タブや再起動後のシェルでexportが抜けていると、不可解な認証エラーとして現れます。

# 動かしてみる

`opencode` で起動し、`/models` を開くとモデル一覧に「Claude Sonnet 4.5 (Databricks)」が表示されます。

![Screenshot 2026-08-06 at 15.41.49.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/abd1438f-ddd7-4b1e-8fbf-b898c1316a9e.png)

選択すると、画面下部のステータスにプロバイダー名として Databricks が表示されます。

![Screenshot 2026-08-06 at 15.43.14.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/9038c167-5bd4-496e-b42d-85f042a76aec.png)

適当なリポジトリのディレクトリで起動して、実際にエージェントとして仕事をさせてみます。今回はOmnigentのリポジトリで次の指示を投げました。

```
このリポジトリのファイル構成を調べて、何のプロジェクトか説明して
```

opencodeがファイル読み取りツールを呼び出してリポジトリを走査し、ディレクトリ構成、SDK、デプロイ先までまとめた説明が返ってきました。画面右下のコンテキスト使用量が13.6Kから32.7Kへ増えており、ツールコールで読み込んだファイルの内容がモデルに渡っていることが確認できます。単発のチャット応答ではなく、ツールコールを挟んだエージェントループがDatabricksエンドポイント経由で複数ターン回っている、ということです。

![Screenshot 2026-08-06 at 15.50.22.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/be386d20-846d-4f28-817f-a51164cddb0f.png)
![Screenshot 2026-08-06 at 15.45.00.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/675166ec-a20b-40e4-90ab-abfafd68de87.png)
![Screenshot 2026-08-06 at 15.45.09.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/cff8ed35-f73c-48f4-b557-f438b36ea8e9.png)

## コスト表示は参考値

一点注意があります。opencodeの画面に表示されるコスト (今回の例では $0.15) は、opencodeがモデルの一般的なAPI単価から推定した参考値です。実際の課金はDatabricks側の基盤モデルAPIの従量課金 (トークン単位) として発生します。実際の消費量はワークスペースのシステムテーブルや使用量画面で確認してください。

# 次のステップ: AI Gatewayを噛ませる

今回はopencodeからサービングエンドポイントを直接叩きましたが、この構成の真価は、間にMosaic AI Gatewayを挟んだときに出てくると考えています。

- [Mosaic AI Gatewayの紹介](https://docs.databricks.com/aws/ja/ai-gateway/)

AI Gatewayをエンドポイントに設定すると、レート制限、ペイロードのロギング、ガードレール、使用状況の追跡といったガバナンス機能が、opencode側には一切手を入れずに適用できます。コーディングエージェントは性質上、人間のチャットよりはるかに高頻度・大量にトークンを消費するので、「誰がどのエージェントでどれだけ使ったか」を可視化し、上限を設ける仕組みは、組織でエージェントを配る際の前提条件になっていくはずです。このあたりは別の記事で検証したいと思います。

# まとめ

ローカルのopencodeからDatabricks Model Servingのモデルを使ってみて分かったことをまとめます。

- opencodeはOSSのエージェントハーネスの代表格。プロバイダー非依存で、OpenAI互換のカスタムエンドポイントを設定ファイルだけで追加できる
- Databricksの基盤モデルAPIはOpenAI互換なので、`baseURL` をワークスペースの `/serving-endpoints` に向けるだけでopencodeのプロバイダーになる
- **`models` のキーはサービングエンドポイント名と完全一致させる。`baseURL` は `/serving-endpoints` で止める**
- 認証はDatabricksのPATのみ。Anthropicとの個別契約もAPIキー管理も不要
- ツールコールを挟んだエージェントループが問題なく複数ターン動作する
- **opencodeの画面に出るコスト表示は参考値。実課金はDatabricks側の従量課金**

一番の収穫は、ハーネスとモデルの分離が実際にきれいに機能することを確かめられたことでした。opencodeのようなプロバイダー非依存のハーネスにとって、モデルは差し替え可能な部品です。そしてその調達先をDatabricksにすると、認証・監査・課金が既存のワークスペースの枠組みに乗ります。エージェントハーネスを組織で使う際の「モデルの配り方」の選択肢として、覚えておいて損はない構成だと思います。

# 参考リンク

- [opencode公式ドキュメント](https://opencode.ai/docs/)
- [opencode: Providers](https://opencode.ai/docs/providers/)
- [Databricks 基盤モデルAPI](https://docs.databricks.com/aws/ja/machine-learning/foundation-model-apis)
- [Databricksホストの基盤モデル](https://docs.databricks.com/aws/ja/machine-learning/foundation-model-apis/supported-models)
- [Mosaic AI Gatewayの紹介](https://docs.databricks.com/aws/ja/ai-gateway/)
- [メタハーネスとは何か ― Databricks発のOSS『Omnigent』が解決しようとしていること](https://qiita.com/taka_yayoi/items/2ff51f2df46cc1285ba3)

### はじめてのDatabricks

[はじめてのDatabricks](https://qiita.com/taka_yayoi/items/8dc72d083edb879a5e5d)

### Databricks無料トライアル

[Databricks無料トライアル](https://databricks.com/jp/try-databricks)
