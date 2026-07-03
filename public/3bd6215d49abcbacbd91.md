---
title: Databricksにおけるinitスクリプトのデバッグ
tags:
  - Databricks
private: false
updated_at: '2024-02-07T18:12:34+09:00'
id: 3bd6215d49abcbacbd91
organization_url_name: databricks
slide: false
ignorePublish: false
posting_campaign_uuid: null
agreed_posting_campaign_term: false
---
ハマることがあるのでメモ。

https://docs.databricks.com/ja/init-scripts/index.html

initスクリプトを設定することで、クラスター起動時にシェルスクリプトを実行することができますので、ソフトウェアのインストールやネットワーク設定を行うことができます。便利ですが、デバッグする際には注意が必要です。

エラー発生時にクラスターのイベントログを見ても、initスクリプトが失敗したことしか確認できません。
![Screenshot 2024-02-07 at 17.54.13.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/633bcb87-c432-11eb-5634-386e6137739a.png)

以下の手順を踏む必要があります。

1. クラスターのログ配信を有効化します。
1. initスクリプトが有効化されている状態でクラスターを起動します。
1. initスクリプトのログが記録されます。
1. initスクリプトを無効化してクラスターを起動します。
1. initスクリプトのログを確認して問題を特定します。
1. initスクリプトを修正して有効化します。
1. クラスターが起動することを確認します。

# クラスターログ配信の有効化

原因を特定するには、[クラスターログ](https://learn.microsoft.com/ja-jp/azure/databricks/init-scripts/logs)のデリバリーを有効化する必要があります。

[クラスター ログの配信](https://learn.microsoft.com/ja-jp/azure/databricks/compute/configure#cluster-log-delivery)にあるように、クラスターの設定を行います。
![cluster log delivery.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/5111b0b7-1046-915e-fe6e-6e417bd61d07.png)

# initスクリプトが有効化されている状態でクラスターを起動

今回は[グローバルinitスクリプト](https://learn.microsoft.com/ja-jp/azure/databricks/init-scripts/global)を使います。以下のように意図的に間違ったスクリプトを記述します。
![Screenshot 2024-02-07 at 17.59.13.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/70fe6361-69c3-568a-6948-92eb1f750185.png)

これでクラスターを起動すると冒頭のエラーでクラスターの起動に失敗します。

# initスクリプトを無効化してクラスターを起動

クラスターが起動するように、initスクリプトを無効化します。
![disable global init script.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/1ed21b37-4529-4689-db10-07e64299b6f9.png)

# initスクリプトのログを確認して問題を特定

クラスターログのパスにはクラスターIDが使用されるので、クラスターIDを特定します。

```py
# クラスターIDを取得
current_cluster_id = spark.conf.get("spark.databricks.clusterUsageTags.clusterId")
print(current_cluster_id)
```

```
0206-052938-gctb3cax
```

パスに埋め込んでログファイルを一覧します。

```py
# 当該クラスターのinit scriptのログを一覧
dir_list = dbutils.fs.ls(f"/cluster-logs/{current_cluster_id}/init_scripts")
display(dbutils.fs.ls(dir_list[0].path))
```
![Screenshot 2024-02-07 at 18.03.29.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/c607fee0-2c2f-0033-3d44-3cb95724ab9b.png)

エラーは`...stderr.log`に記録されるので中身を確認します。こちらは自動化してないので上のセルをコピーして以下のセルに貼り付けてます。

```py
# 末尾が　.stderr.log　のファイルの内容を表示
dbutils.fs.head("dbfs:/cluster-logs/0206-052938-gctb3cax/init_scripts/0206-052938-gctb3cax_10_139_64_5/20240206_053551_00_8DFAB0EAC552ACE6-326561e75002166972179f312d06073bf2fd3d29ee7070be136c22cd6f4bda9f-GLOBAL-failure_script.stderr.log")
```
```
'bash: line 1: ech: command not found\n'
```

当たり前ですが`echo`ではなく`ech`にしているので、そのようなコマンドがないと怒られています。問題が特定できました。

# initスクリプトを修正して有効化

直します。そして、有効化します。

![Screenshot 2024-02-07 at 18.05.11.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/0689db80-f0d1-e163-7126-1f037a3b9482.png)

# クラスターが起動することを確認

起動しました！
![Screenshot 2024-02-07 at 18.11.19.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/7ff404ef-5319-2d72-d15e-5fb0f5b346f2.png)

デバッグが完了したら、[クラスターログ配信の有効化](#クラスターログ配信の有効化)で有効化したログ配信はオフにして問題ありません。
![Screenshot 2024-02-07 at 18.12.03.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/17018359-8f89-9d66-6cd5-5e9c39cae1b6.png)

### はじめてのDatabricks

[はじめてのDatabricks](https://qiita.com/taka_yayoi/items/8dc72d083edb879a5e5d)

### Databricks無料トライアル

[Databricks無料トライアル](https://databricks.com/jp/try-databricks)
