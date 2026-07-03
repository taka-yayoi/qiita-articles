---
title: Databricks共有クラスターにおけるinitスクリプトの活用
tags:
  - Databricks
private: false
updated_at: '2023-08-25T14:07:04+09:00'
id: dff4ba249bcfdf3f7eb3
organization_url_name: databricks
slide: false
ignorePublish: false
posting_campaign_uuid: null
agreed_posting_campaign_term: false
---
Databricksのクラスターにはいくつかの種類があります。Unity Catalogを活用する際には共有クラスターがお勧めなのですが、initスクリプトが使えないなどの制限がありました。

https://qiita.com/taka_yayoi/items/a1b4977a80ace39c7e81#%E5%85%B1%E6%9C%89%E3%82%A2%E3%82%AF%E3%82%BB%E3%82%B9%E3%83%A2%E3%83%BC%E3%83%89%E3%81%AE%E6%A9%9F%E8%83%BD%E5%88%B6%E9%99%90

しかし、こちらの記事にありますように、共有クラスターでもinitスクリプトが使えるようになりました！

https://qiita.com/taka_yayoi/items/6e06c457f020896b1418

早速やってみます。

# initスクリプトの作成

こちらで使っているinitスクリプトを使います。

https://qiita.com/taka_yayoi/items/6ac6b521698da47a3c25

```sh:taka_librosa_init.sh
#!/bin/bash
apt-get --yes install libsndfile1
```

ローカルマシンにこちらのシェルスクリプトファイルを保存します。

# ボリュームへのアップロード

Databricksのデータエクスプローラにアクセスして、シェルスクリプトファイルをVol.にアップロードします。シェルスクリプトのファイルのパスをコピーします。
![Screenshot 2023-08-25 at 13.05.25.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/7b58bec9-715d-e185-9c9e-cfbeaaff27b1.png)

# 許可リストにinitスクリプトを追加

データエクスプローラのタイトルの右にあるギアマークをクリックします。
![Screenshot 2023-08-25 at 13.03.02.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/d8eda89c-6cd6-f40d-a660-a124d45dfdcd.png)

**Allowed JAR/Init Scripts**タブを開きます。
![Screenshot 2023-08-25 at 13.03.22.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/5690431d-127e-1942-d74e-a7063a26f136.png)

**追加**をクリックして、タイプは`Init Script`、ソースタイプ`Volume`、ソースに先ほどコピーしたinitスクリプトのパスを指定して許可リストに追加します。
![Screenshot 2023-08-25 at 13.05.47.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/079381b5-7719-8403-641e-83058934fe7a.png)
![Screenshot 2023-08-25 at 13.06.00.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/4d3af399-0f29-9352-0ea2-1fa544ed37cd.png)

# クラスターにおけるinitスクリプトの設定

共有クラスターを作成し、ランタイムには13.3以降を選択します。そうしないとinitスクリプトは設定できません。
![Screenshot 2023-08-25 at 13.59.20.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/4473d2b7-59fb-0666-630a-e0dfcbbcc0ae.png)

**高度なオプション > initスクリプト**で、上で指定したinitスクリプトを指定して追加します。
![Screenshot 2023-08-25 at 13.07.16.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/c43078fa-f189-3177-9b37-0f21be33c518.png)

# クラスターの起動

クラスターを起動するとinitスクリプトが実行されます。
![Screenshot 2023-08-25 at 14.03.19.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/275503b0-b526-4840-78f9-18e1f1267bdc.png)

```py
%pip install librosa
```
```py
# Beat tracking example
import librosa

# 1. Get the file path to an included audio example
filename = librosa.example('nutcracker')

# 2. Load the audio as a waveform `y`
#    Store the sampling rate as `sr`
y, sr = librosa.load(filename)

# 3. Run the default beat tracker
tempo, beat_frames = librosa.beat.beat_track(y=y, sr=sr)

print('Estimated tempo: {:.2f} beats per minute'.format(tempo))

# 4. Convert the frame indices of beat events into timestamps
beat_times = librosa.frames_to_time(beat_frames, sr=sr)
```

```
Estimated tempo: 107.67 beats per minute
```

動きました！

### Databricksクイックスタートガイド

[Databricksクイックスタートガイド](https://www.amazon.co.jp/dp/B09V1YXFVQ/)


### Databricks無料トライアル

[Databricks無料トライアル](https://databricks.com/jp/try-databricks)
