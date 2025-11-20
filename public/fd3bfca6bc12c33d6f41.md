---
title: Databricksアシスタントの新たなUIを試してみる
tags:
  - Databricks
private: false
updated_at: '2023-12-10T18:20:29+09:00'
id: fd3bfca6bc12c33d6f41
organization_url_name: databricks
slide: false
ignorePublish: false
---
こちらのアップデートで、Databricksアシスタントがデフォルトで有効化されました。なお、管理者画面からオプトアウト(無効化)することが可能です。

https://docs.databricks.com/ja/release-notes/product/2023/november.html#ai-assistive-features-are-enabled-by-default

そして、最近になってノートブックセルの変化に気づきました。右上がキラキラしてる。
![Screenshot 2023-12-10 at 17.50.07.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/59ca707d-8ec7-45e6-053f-810a5c5b732d.png)

**アシスタントを切り替え**とな。オンにしてみます。
![Screenshot 2023-12-10 at 17.50.29.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/718b67f4-d5d1-0965-a87c-a1175500c6fd.png)

何か出ました。アシスタントに尋ねるかコマンドのために`/`を入力だそうで。
![Screenshot 2023-12-10 at 17.51.31.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/15c59e76-c4e4-6845-eb0e-f48f3e59de7d.png)

`/`を入力します。`/doc`はコードにコメントを追加、`/explain`はチャットウィンドウでコードを説明、`/fix`はコードのエラーを修正。
![Screenshot 2023-12-10 at 17.53.13.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/8e514327-6c6e-d3a8-63cb-9f96e3df9ba1.png)
![Screenshot 2023-12-10 at 17.53.26.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/25e76708-40cb-d802-7a36-9e45ddf1d049.png)
![Screenshot 2023-12-10 at 17.53.31.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/724d133c-2664-107a-f2c5-955109842b06.png)

説明と修正はこれまでも使えていましたが、`/doc`はどうなるのだろうって、なんか出た。コードにコメントを挿入してくれるんですね。嬉しいですが英語対応してほしい…。
![Screenshot 2023-12-10 at 17.55.00.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/39c39b19-0fe7-4f45-61c8-2d8c8e870240.png)

承認するとコメントが挿入されます。
![Screenshot 2023-12-10 at 17.55.59.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/8953421e-826b-3bee-9deb-ea64f96a01be.png)

説明は上で言われていた通りコードの説明が表示されます。
![Screenshot 2023-12-10 at 17.56.28.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/993c7d25-56d4-e1a9-800f-ec4f2089f3bc.png)

エラーが起きた際には`/fix`を入力することで、修正案を提示してくれます。
![Screenshot 2023-12-10 at 18.03.37.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/5b44a9ab-9e64-1448-963d-085fb692eb17.png)


そして、普通にアシスタントに問い合わせをするとコードを生成してくれます。SDKでのクラスターの作り方を聞いてみました。
![Screenshot 2023-12-10 at 17.58.26.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/37fbe361-4da3-84f2-8391-437e195c8c5c.png)

ますますコーディングが捗ってしまいます。

と、これを書いてからすでに検証されている方がいることに気づきました。不覚(ありがとうございます)

https://qiita.com/isanakamishiro2/items/c7a9530205e503d4985e#_reference-e7e39f74f8cf06fb19e7

### Databricksクイックスタートガイド

[Databricksクイックスタートガイド](https://www.amazon.co.jp/dp/B09V1YXFVQ/)


### Databricks無料トライアル

[Databricks無料トライアル](https://databricks.com/jp/try-databricks)
