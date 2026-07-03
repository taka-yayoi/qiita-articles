---
title: Databricksノートブックのユニットテストをやってみる
tags:
  - unittest
  - Databricks
private: false
updated_at: '2023-01-04T08:28:20+09:00'
id: ac88fbd9fdb4a5eb9ad6
organization_url_name: databricks
slide: false
ignorePublish: false
posting_campaign_uuid: null
agreed_posting_campaign_term: false
---
こちらの[ノートブックのテスト](https://qiita.com/taka_yayoi/items/ef3b05c29104b12a16a6)で説明されている内容を実際に試してみました。

テスト対象の関数を宣言します。入力された文字列の順序を逆にする関数です。

```py:Python
def reverse(s):
    return s[::-1]
```

[unittest](https://docs.python.org/3/library/unittest.html)を用いたテスト用コードを作成します。

```py:Python
import unittest

class TestHelpers(unittest.TestCase):
    def test_reverse(self):
        self.assertEqual(reverse('abc'), 'cba')
```

ユニットテストを実行します。

```py:Python
r = unittest.main(argv=[''], verbosity=2, exit=False)
assert r.result.wasSuccessful(), 'Test failed; see logs above'
```

期待した通りに動作するのでテストにパスします。
![Screen Shot 2022-05-19 at 13.54.31.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/fa6f5d14-6c7e-25c4-c8aa-41600e097d2a.png)

テストに失敗するように故意に関数を変更します。

```py:Python
def reverse(s):
    #return s[::-1]
    return "test"
```

期待している出力ではないためテストに失敗します。
![Screen Shot 2022-05-19 at 13.56.26.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/8bb097fa-74aa-d427-9e9f-4e3c31ad43d4.png)

# ウィジェットの活用

[ウィジェット](https://qiita.com/taka_yayoi/items/4df1fd723bdab9a99b08)を追加することで、テスト時の動作と通常時の動作を切り替えることができます。

```py:Python
dbutils.widgets.dropdown("Mode", "Test", ["Test", "Normal"])
```

```py:Python
import unittest

class TestHelpers(unittest.TestCase):
    def test_reverse(self):
        self.assertEqual(reverse('abc'), 'cba')

if dbutils.widgets.get("Mode") == "Test":
  r = unittest.main(argv=[''], verbosity=2, exit=False)
  assert r.result.wasSuccessful(), 'Test failed; see logs above'
else:
  print(reverse("desrever"))
```
![Screen Shot 2022-05-19 at 14.00.00.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/b53b98c8-6fa7-b575-9d97-1307854720fb.png)

PyTestとの連携に関しては、こちらの記事を参照ください。

https://qiita.com/maroon-db/items/ccafbaaeecab4d532355

### Databricks 無料トライアル

[Databricks 無料トライアル](https://databricks.com/jp/try-databricks)
