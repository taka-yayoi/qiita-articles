---
title: Databricksのコレーション(照合順序)を試してみる
tags:
  - Databricks
  - collation
private: false
updated_at: '2025-01-19T15:41:13+09:00'
id: f4bdfdd98bdd29d5d6eb
organization_url_name: null
slide: false
ignorePublish: false
posting_campaign_uuid: fd9d012cdc6dcd0b2f5c
agreed_posting_campaign_term: true
---
こちらの機能を試してみます。

https://qiita.com/taka_yayoi/items/d9620f7ec31d849a1db4

ギリシャ語と英語を含むテーブルを作ります。

```sql
CREATE TABLE users.takaaki_yayoi.HeroNames (
    GreekName STRING COLLATE EL_AI,
    EnglishName STRING COLLATE UTF8_LCASE
);
INSERT INTO users.takaaki_yayoi.HeroNames (GreekName, EnglishName)
VALUES 
    ('Ἀχιλλεύς', 'Achilles'),
    ('Ἀγαμέμνων', 'Agamemnon'),
    ('Ὀδυσσεύς', 'Odysseus'),
    ('Διομήδης', 'Diomedes'),
    ('Αἴας ὁ Μέγας', 'Ajax the Greater'),
    ('Αἴας ὁ Λοκρός', 'Ajax the Lesser'),
    ('Μενέλαος', 'Menelaus'),
    ('Νέστωρ', 'Nestor'),
    ('Πάτροκλος', 'Patroclus'),
    ('Ἰδομενεύς', 'Idomeneus'),
    ('Ἕκτωρ', 'Hector'),
    ('Αἰνείας', 'Aeneas'),
    ('Πάρις', 'Paris'),
    ('Σαρπηδών', 'Sarpedon'),
    ('Γλαῦκος', 'Glaucus'),
    ('Πολυδάμας', 'Polydamas'),
    ('Πάνδαρος', 'Pandarus'),
    ('Δηίφοβος', 'Deiphobus'),
    ('Ἀντήνωρ', 'Antenor'),
    ('Αἰσύητης', 'Aesyetes');
```

カタログエクスプローラではタイプでコレーションを確認できます。サンプルデータを表示する際には、Databricksランタイム16.1以降のクラスターを使うようにしてください。SQLウェアハウスではまだコレーションがサポートされていないので、SQLウェアハウスでコレーションが指定されているテーブルを表示しようとすると、未サポートのエラーになります。

![Screenshot 2025-01-19 at 15.30.04.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/ddcba5b8-7257-695c-e979-03db06812576.png)
![Screenshot 2025-01-19 at 15.31.21.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/98bc1727-996e-7be0-c54a-440fdbd379d5.png)

サポートされているコレーションを確認します。

```sql
SELECT * FROM collations()
```

日本語もサポートされています。あとで試します。

![Screenshot 2025-01-19 at 15.31.57.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/97bf4089-ec9c-c746-6819-25e0f2dc8568.png)

統計情報を更新します。

```sql
ANALYZE TABLE users.takaaki_yayoi.HeroNames COMPUTE STATISTICS FOR COLUMNS GreekName, EnglishName;
```

大文字小文字を区別しない(`CASE_INSENSITIVE`)検索を行います。

```sql
SELECT * FROM users.takaaki_yayoi.HeroNames WHERE EnglishName = 'achilles';
```

大文字のAchillesがヒットしました。もう`lower`は不要なんですね。

![Screenshot 2025-01-19 at 15.33.12.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/ae457f89-a2b8-2c31-72cd-2020c0d79d4d.png)

ギリシャ語でソートします。

```sql
SELECT * FROM users.takaaki_yayoi.HeroNames ORDER BY GreekName;
```

英語のアルファベット順ではないことはわかります(ギリシャ語わかりません)。

![Screenshot 2025-01-19 at 15.34.08.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/f6621f3d-8977-0230-8fef-bf03426649ba.png)

アクセント文字の区別をしない`ACCENT_INSENSITIVE`な検索を行います。

```sql
SELECT * FROM users.takaaki_yayoi.HeroNames WHERE GreekName = 'Αγαμεμνων';
```

小さいですがアクセント文字がある`Ἀγαμέμνων`がヒットしていることがわかります。

![Screenshot 2025-01-19 at 15.35.09.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/1c3bc554-d307-b9a2-9260-85a04ec41924.png)

日本語でも挙動を見てみます。こちらを参考にさせていただきました。日本語における濁点、半濁点はアクセント文字とのことです。

https://qiita.com/subun33/items/9df8ca30e282c691dd54

文字列上、`は`と`ぱ`は違うので以下は`false`になります。

```sql
SELECT 'は' = 'ば' AS comparison_result;
```

![Screenshot 2025-01-19 at 15.36.51.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/a033b9df-935d-12d2-68e8-696454b7f64d.png)

アクセント文字を区別しないで照合します。

```sql
SELECT 'は' = 'ば' COLLATE ja_AI AS comparison_result;
```

同じと見なされました。

![Screenshot 2025-01-19 at 15.37.29.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/7f375e93-587d-935a-43c9-ad2db4afa8f8.png)

大文字小文字も見てみます。以下は`false`になります。

```sql
SELECT 'あ' = 'ぁ' AS comparison_result;
```

大文字小文字を区別せず(CASE_INSENSITIVE)に照合させます。

```sql
SELECT 'あ' = 'ぁ' COLLATE ja_CI AS comparison_result;
```

同じと見なされました。

![Screenshot 2025-01-19 at 15.39.51.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/4bbf43e0-cbbd-09df-5798-1f2be8d99f6b.png)

まもなく、SQLウェアハウスでもコレーションが使えるようになるとのことです。たげんごをしょりするじょうきょうにおいてm文字列操作の幅が広がる機能ですので是非ご活用ください！

### はじめてのDatabricks

[はじめてのDatabricks](https://qiita.com/taka_yayoi/items/8dc72d083edb879a5e5d)

### Databricks無料トライアル

[Databricks無料トライアル](https://databricks.com/jp/try-databricks)
