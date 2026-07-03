---
title: Databricksでsuperintendentを用いてアノテーションを行う
tags:
  - Databricks
  - superintendent
private: false
updated_at: '2023-09-19T15:11:35+09:00'
id: f7ea4c3c5a4dfacad639
organization_url_name: databricks
slide: false
ignorePublish: false
posting_campaign_uuid: null
agreed_posting_campaign_term: false
---
このようなライブラリがあるとは。

https://superintendent.readthedocs.io/en/latest/labelling-data.html

なお、関連ライブラリとして[ipyannotations](https://ipyannotations.readthedocs.io/en/latest/)がありますが、現時点ではこちらはDatabricksでは動作しません。

superintendentはテキストや画像のアノテーションをサポートしています。

```py
%pip install superintendent ipyannotations html5lib
dbutils.library.restartPython()
```

サンプルのテキストをニュースサイトから取り込みます。

```py
import requests
from bs4 import BeautifulSoup
import datetime

headlines = []
labels = []

r = requests.get('https://www.theguardian.com/uk').text #get html
soup = BeautifulSoup(r, 'html5lib') #run html through beautiful soup
headlines += [headline.text for headline in
              soup.find_all('span', class_='js-headline-text')][:10]
labels += ['guardian'] * (len(headlines) - len(labels))

soup = BeautifulSoup(requests.get('http://www.dailymail.co.uk/home/index.html').text, 'html5lib')
headlines += [headline.text.replace('\n', '').replace('\xa0', '').strip()
              for headline in soup.find_all(class_="linkro-darkred")][:10]
labels += ['daily mail'] * (len(headlines) - len(labels))
```

```py
headlines
```

```
Out[2]: ["Ex-model tells how Russell Brand 'stalked her through London streets demanding sex after they met in a bar forcing her to RUN to flee his advances': Woman to report incident to police - as C4 insiders say Big Brother bosses 'all knew he was a predator'",
 "Inside Russell Brand's rocky relationship with wife's family: How golf legend father-in-law Bernard Gallacher 'begged' daughter Laura to split with the star - as comic's sister-in-law Kirsty deletes Instagram post supporting him in wake of sex scandal",
 "It WAS Russell Brand who Katherine Ryan was talking about: Female comic repeatedly accused him of being a 'sexual predator' during filming for Comedy Central's Roast Battle before he was dropped from what was his last major TV job in the UK",
 'PETER HITCHENS: Trying to have a serious argument with Russell Brand is like playing chess with a squirrel. Why was he given a place in the national debate?',
 "NADINE DORRIES: How can Russell Brand's wife stand by a man accused of sending a car to pick up a girl of 16 from school?",
 "Keir Starmer is accused of 'Brexit betrayal' as he vows to re-write a deal with the EU ahead of a meeting with Emmanuel Macron",
 "Self-styled anti-slavery activist portrayed by Jim Caviezel in 'Sound of Freedom' steps down from Operation Underground Railroad after being accused of sexual misconduct by seven women",
 'Folk singer Roger Whittaker best known for hits Durham Town and New World in the Morning dies aged 87',
 "JAMES MACMANUS: I've dedicated my new book to a beautiful French lover I knew for months in 1974. My wife's not happy - but Marie-Aude's heartbroken fury as she hurled wine at me and fled from my life has haunted me for 50 years",
 'Are YOU one of the 12million Brits missing out on a Covid booster because of NHS penny-pinching?']
```

最初迷ったのは、**アノテーション結果がどこに保持されるか**ということでした。答えは、引数`database_url`にデータベースの格納パスを指定するということでした。引数が無い場合にはインメモリのsqliteが使用されます。パスの先頭にはスキーマ`sqlite:///`を指定します。

```py
from superintendent import Superintendent
from ipyannotations.text import ClassLabeller

# アノテーション結果を格納するデータベース
db_string = "sqlite:////databricks/driver/text_annotation.db"

input_widget = ClassLabeller(options=['professional', 'not professional'])
input_data = headlines
data_labeller = Superintendent(
    database_url=db_string,
    features=input_data,
    labelling_widget=input_widget,
)

data_labeller
```

以下のようにアノテーションのウィジェットが表示されます。
![Screenshot 2023-09-19 at 15.03.51.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/f4dfba21-a9d9-68b4-84cd-a15e23fa5837.png)

この場合、ニュースのヘッドラインを読んでプロらしいか(professional)そうで無いか(not professional)を選択する形となります。

:::note
**注意**
ウィジェットが表示されない場合には、ブラウザをリロードしてください。
:::

選択するとプログレスバーが進捗します。
![Screenshot 2023-09-19 at 15.05.00.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/ab5450fe-0630-e283-432f-a5fdba71da3f.png)

アノテーションが完了しました。
![Screenshot 2023-09-19 at 15.05.28.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/ab3b5866-645c-aea9-578c-1c97b554bb7a.png)

上で指定したパスでデータベースを確認できます。
![Screenshot 2023-09-19 at 15.05.53.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/06c28a0f-4945-9fb0-7d39-53ac5c574eec.png)

こちらではデータベースのパスでスキーマを指定しないことに注意してください。

```py
import sqlite3
connection = sqlite3.connect("/databricks/driver/text_annotation.db")

cursor = connection.cursor()

sql_query = """SELECT name FROM sqlite_master  
  WHERE type='table';"""
cursor.execute(sql_query)
print(cursor.fetchall())
```

`superintendentdata`というテーブルに格納されています。

```
[('superintendentdata',)]
```

テーブルの中を表示します。

```py
df = spark.read.format('jdbc') \
          .options(driver='org.sqlite.JDBC', dbtable='superintendentdata',
                   url='jdbc:sqlite:/databricks/driver/text_annotation.db').load()
display(df)
```
![Screenshot 2023-09-19 at 15.08.06.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/591a4326-1982-6e82-8e39-359da64d10ed.png)

ライブラリさえインストールすれば手軽に、アノテーションができて便利ですね。

なお、画像のアノテーションは以下のようになります。

```py
from superintendent import Superintendent
from ipyannotations.images import ClassLabeller
from sklearn.datasets import load_digits

input_data = load_digits().data.reshape(-1, 8, 8)
input_widget = ClassLabeller(
    options=list(range(1, 10)) + [0], image_size=(100, 100))
data_labeller = Superintendent(
    database_url=db_string,
    features=input_data,
    labelling_widget=input_widget,
)
data_labeller
```
![Screenshot 2023-09-19 at 15.09.37.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/44c4bec0-6fc6-ce24-bc49-9829b24ce814.png)

### Databricksクイックスタートガイド

[Databricksクイックスタートガイド](https://www.amazon.co.jp/dp/B09V1YXFVQ/)


### Databricks無料トライアル

[Databricks無料トライアル](https://databricks.com/jp/try-databricks)
