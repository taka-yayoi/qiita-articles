---
title: 'Unity Gateway は Unity Catalog の上に乗っている: 2つの製品の役割分担を整理する'
tags:
  - Databricks
  - UnityCatalog
  - UnityGateway
  - MCP
  - LLM
private: false
updated_at: '2026-10-12T19:09:25+09:00'
id: afff1a2fbdf0a29aa847
organization_url_name: databricks
slide: false
ignorePublish: false
posting_campaign_uuid: null
agreed_posting_campaign_term: false
---
# はじめに

2026年10月時点のDatabricksのドキュメントでは、Unity Gatewayが独立した章として整理されています。モデル推論、MCP、スキルをまとめて扱う入口として、Unity Catalogと並ぶ「Unity」のもう一つの柱になりました。

- [Unity Gateway](https://docs.databricks.com/aws/ja/unity-gateway/)
- [Unity Gateway の概念](https://docs.databricks.com/aws/ja/unity-gateway/concepts)
- [AIガバナンスガイド](https://docs.databricks.com/aws/ja/ai-gateway/ai-governance)

ただ、2つの製品は対等に並んでいるわけではありません。Unity Gatewayが扱うモデルサービスやMCPは、すべてUnity Catalogのオブジェクトとして登録され、権限もUnity Catalogの仕組みで管理されます。Unity Gatewayは、Unity Catalogの上に乗っている製品です。

ドキュメントを読み、実際にワークスペースの画面を開いて、この関係を確かめました。画面で確かめた結果も含めて書いていきます。

# Unity Gateway とは

Unity Gatewayは、AIアプリケーションとコーディングエージェントが使うモデル推論、ツール、スキルを1か所で扱うコントロールプレーンです。主な用途は次の3つです。

- モデル推論へのアクセス: Databricksがホストするモデルに加えて、OpenAI、Anthropic、Amazon Bedrock、Azure Foundryなどの既存の契約も持ち込めます
- コストとパフォーマンスの最適化: リクエストを適したモデルに振り分け、使用量と支出を追跡し、予算と支出上限を設定できます
- AIへのアクセスの保護: モデル、エージェント、MCPサーバー、ツールへのアクセスを権限で管理し、PIIのマスキングや監査ログの記録を行います

# 役割は3つの統制で分かれている

AIガバナンスガイドでは、DatabricksのAIガバナンスを3つの側面に分けて説明しています。Unity GatewayとUnity Catalogの役割分担は、この3つで整理すると見通しが良くなります。

| 側面 | 担当 | 内容 |
| --- | --- | --- |
| 資産ガバナンス | Unity Catalog | モデル、MCPサーバー、関数、接続をセキュリティ保護可能なオブジェクトとして管理する。テーブルやボリュームと同じ権限とABAC付与ポリシーを使う |
| トラフィックガバナンス | Unity Gateway | モデルサービスとMCPサービスへのリクエストをルーティングし、レート制限、予算、使用状況の追跡を適用する |
| 振る舞いガバナンス | サービスポリシー | 呼び出し元と、リクエストやレスポンスの内容をもとに、個々のやり取りを許可、拒否、または承認待ちにする |

ドキュメントでは、Unity CatalogをAIガバナンスの「基盤」と位置づけています。Unity Gatewayは、Unity Catalogが管理する資産へのトラフィックを制御する役割です。

エージェントがツールやモデルを呼び出すときの処理は、次の順番で進みます。

1. Databricksがリクエストを認証する
2. Unity Catalogの権限に照らして、呼び出してよいかを確認する
3. Unity Gatewayを経由して、外部のシステムやモデルに届ける

図にすると次のようになります。土台にUnity Catalogがあり、その上でUnity Gatewayが呼び出しを受け、Unity Gatewayの中でサービスポリシーが中身を検査します。

![fig1-unity-gateway.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/9f35a438-f08e-4714-b960-5ab9fb3ae845.png)

AI用に別の権限の台帳を作るのではなく、データと同じ枠組みにそのまま乗る。テーブルの権限設計をすでに回している組織にとって、この点は導入のハードルを大きく下げます。

# モデルとモデルサービスは別物

Unity Gatewayでは、次の6つの概念を組み合わせてモデルとツールを管理します。

| 概念 | 役割 | ドキュメントの例 |
| --- | --- | --- |
| モデル | LLMまたは埋め込みモデル。登録しただけでは呼び出せず、呼び出すにはモデルサービスが必要 | `gpt-astra-6` |
| モデルサービス | 推論リクエストを1つ以上のモデルに振り分けるエンドポイント。トラフィック分割とフォールバックに対応する | `frontier-model` |
| モデルプロバイダー | 外部のモデルプロバイダーへの接続。認証情報を一元管理する | `anthropic-prod` |
| MCP | エージェントがModel Context Protocolでツールを見つけて呼び出すためのインターフェース | `support-tools` |
| スキル | エージェントが読み込む、再利用可能な指示とファイル | `customer-support` |
| サービスポリシー | AIサービスへのリクエストとレスポンスを検査するガードレール | `detect_sensitive_data` |

ここが最初のハマりどころです。モデルとモデルサービスは別の概念です。Unity Catalogでは、モデルはバージョン、メタデータ、成果物をまとめた静的な資産で、登録しただけでは呼び出せません。アプリケーションが呼び出すのはモデルサービスのほうです。

モデルサービスを挟むことで、アプリケーション側のコードを変えずに、呼び出し先のモデルやフォールバック先を入れ替えられます。ドキュメントの例では、`frontier-model` というモデルサービスがDatabricks上のGPT Astra 6を呼び出し、Claude Opus 5をフォールバック先にしています。

外部のモデルを使う場合は、モデルを登録するのではなく、モデルプロバイダーの接続を登録します。

# Unity Gateway のオブジェクトはすべて Unity Catalog に登録される

## 名前はテーブルと同じ3階層

モデル、モデルサービス、モデルプロバイダー、MCP、スキルは、どれもUnity Catalogのセキュリティ保護可能なオブジェクトです。名前もテーブルと同じ `catalog.schema.name` の形式に従います。

- 自分で作ったモデルサービスの例: `production.ai.frontier-model`
- Databricksが提供するモデルサービス: `system.ai` に登録されています

## 画面で確かめる

実際にワークスペースで確かめてみました。Unity Gatewayの画面を開くと、「モデル」タブにモデルサービスが一覧で並び、Location列にはそれぞれの登録先として `system.ai` が表示されます。

![Screenshot 2026-10-12 at 19.03.58.JPG](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/d12fb9fd-2824-4299-9a9d-bbe253d0003b.jpeg)

Unity Gatewayの画面の「モデル」タブに並んでいるのは、前の節でいうモデルサービスです。タブの名前とドキュメントの用語が一致しないので、読み替えが必要です。

同じ `system.ai` スキーマをカタログエクスプローラーで開くと、「モデル」と「サービス」が別のタブに分かれて並んでいます。左のツリーの「サービス」には、Unity Gatewayの画面と同じ名前のモデルサービスが並んでいます。

![Screenshot 2026-10-12 at 19.03.12.JPG](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/92e73497-2253-484e-9c4f-7ab63492ee17.jpeg)

Unity Gatewayの画面で見ていたものが、Unity Catalogではテーブルや関数と同じスキーマの中にある。2つの画面を並べると、Unity GatewayがUnity Catalogの上に乗っていることがよく分かります。

## 権限はテーブルと同じ考え方で付与する

モデルサービス、モデルプロバイダー、MCPには、次の権限を付与します。使う権限と管理する権限が分かれています。

| 権限 | できること |
| --- | --- |
| `EXECUTE` | モデルサービス、モデルプロバイダー、MCPを呼び出す |
| `CREATE SERVICE` | スキーマ内にサービスを作成し、モデルプロバイダーを登録する |
| `READ METADATA` | 構成を参照する |
| `MANAGE` | 構成を変更し、他のユーザーにアクセス権を付与する |

テーブルを読むときと同じく、呼び出す側には親のカタログとスキーマに対する `USE CATALOG` と `USE SCHEMA` も必要です。ここを忘れると、`EXECUTE` を付与しても呼び出せません。

## サービスポリシーはアクセス権を与えない

サービスポリシーは、サービスにアタッチして使います。サービスポリシー自体は、単独のセキュリティ保護可能なオブジェクトではありません。

また、サービスポリシーはアクセス権を付与しません。権限で許可された呼び出しを、内容に応じてさらに絞り込むためのものです。呼び出せるかどうかはUnity Catalogの権限で決まり、その中身が問題ないかをサービスポリシーで確認する、という順番になります。

# 呼び出し先も Unity Catalog の名前で指定する

Unity Gateway経由の呼び出しは、すべてワークスペースの `/ai-gateway/` 以下のパスに送ります。

認証にはDatabricks CLIのOAuthで取得した短期トークンを使います。個人アクセストークンを作る必要はありません。

```bash
databricks auth login --host https://<workspace-url>
export DATABRICKS_TOKEN=$(databricks auth token --host https://<workspace-url> | jq -r .access_token)
```

これで以降の例がそのまま実行できます。

モデルサービスを呼び出す場合は、OpenAI互換のChat Completions APIが使えます。`model` にUnity Catalogの名前を指定します。

```bash
curl "https://<workspace-url>/ai-gateway/mlflow/v1/chat/completions" \
  -H "Authorization: Bearer $DATABRICKS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "production.ai.frontier-model",
    "max_tokens": 256,
    "messages": [{"role": "user", "content": "Hello!"}]
  }'
```

モデルプロバイダーを使う場合は、プロバイダー本来のAPI (この例ではAnthropic Messages API) の形式で送ります。どの接続を使うかはヘッダーで指定します。

```bash
curl "https://<workspace-url>/ai-gateway/anthropic/v1/messages" \
  -H "Authorization: Bearer $DATABRICKS_TOKEN" \
  -H "Databricks-Model-Provider-Service: production.ai.anthropic-prod" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "claude-opus-5",
    "max_tokens": 256,
    "messages": [{"role": "user", "content": "Hello!"}]
  }'
```

プロバイダーの認証情報はUnity Gatewayが付けるので、呼び出す側はAnthropicのAPIキーを持つ必要がありません。APIキーを開発者に配らずに済むのは、運用する側からすると大きな利点です。

MCPを呼び出す場合も、パスにUnity Catalogの名前を入れます。

```bash
curl "https://<workspace-url>/ai-gateway/mcp-services/production.ai.support-tools" \
  -H "Authorization: Bearer $DATABRICKS_TOKEN" \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -d '{
    "jsonrpc": "2.0",
    "id": 1,
    "method": "tools/list",
    "params": {}
  }'
```

これでMCPサービスが提供するツールの一覧が返ってきます。3つの例のどれも、呼び出す対象をUnity Catalogの名前で指定しています。

# まとめ

Unity GatewayとUnity Catalogの関係を整理して分かったことをまとめます。

- Unity Gatewayは、モデル推論、MCP、スキルを呼び出すときの入口。ルーティング、レート制限、使用状況の記録を担う
- **Unity Gatewayが扱うモデルサービス、モデルプロバイダー、MCP、スキルは、すべてUnity Catalogのオブジェクトとして登録される**
- 権限は `EXECUTE` などをテーブルと同じ考え方で付与する。親のカタログとスキーマの `USE` 権限も必要
- **モデルとモデルサービスは別物。呼び出すのはモデルサービスのほう**
- Unity Gatewayの画面の「モデル」タブに並ぶのはモデルサービス
- サービスポリシーは中身を検査するもので、アクセス権は付与しない

一番の収穫は、Unity GatewayとUnity Catalogの画面を並べて見たことでした。Unity Gatewayだけを触っていると新しい製品に見えますが、登録先も権限も名前の付け方もUnity Catalogのものです。テーブルの権限管理に慣れていれば、モデルやMCPの権限管理も同じ考え方で扱えます。

# 参考リンク

- [Unity Gateway](https://docs.databricks.com/aws/ja/unity-gateway/)
- [Unity Gateway の概念](https://docs.databricks.com/aws/ja/unity-gateway/concepts)
- [Unity Gateway クイックスタート](https://docs.databricks.com/aws/ja/unity-gateway/quickstart)
- [AIガバナンスガイド](https://docs.databricks.com/aws/ja/ai-gateway/ai-governance)
- [Unity Catalog のセキュリティ保護可能なオブジェクト](https://docs.databricks.com/aws/ja/data-governance/unity-catalog/securable-objects)
- [AI セキュラブルのサービスポリシー](https://docs.databricks.com/aws/ja/data-governance/unity-catalog/service-policies)

### はじめてのDatabricks

[はじめてのDatabricks](https://qiita.com/taka_yayoi/items/8dc72d083edb879a5e5d)

### Databricks無料トライアル

[Databricks無料トライアル](https://databricks.com/jp/try-databricks)
