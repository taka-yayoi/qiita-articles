---
title: Databricks Container Serviceを用いたクラスターへのSSH接続
tags:
  - SSH
  - Docker
  - Databricks
private: false
updated_at: '2024-08-26T10:03:03+09:00'
id: dbb68eaad39dcaf3a1b0
organization_url_name: databricks
slide: false
ignorePublish: false
posting_campaign_uuid: null
agreed_posting_campaign_term: false
---
こちらの続編です。

https://qiita.com/taka_yayoi/items/1cc43ffdd41935491519

そして、こちらの知見も活用しています。

https://qiita.com/taka_yayoi/items/639700b77459ff5c491c

こちらでDatabricksクラスターのランタイムとして使用できるDockerイメージが公開されていますが、`standard`などとなっているものは、デフォルトではsshdが動いていません。

https://hub.docker.com/r/databricksruntime/standard

SSH対応版のDockerファイルが公開されていますが、若干修正が必要でした。

https://github.com/databricks/containers/blob/master/ubuntu/ssh/Dockerfile

以下のDockerfileでDockerイメージを作成します。[こちら](https://stackoverflow.com/questions/22886470/start-sshd-automatically-with-docker-container)を参考に`ENTRYPOINT`を使ってsshdを起動しています。

```dockerfile
FROM databricksruntime/standard:13.3-LTS
RUN apt-get update \
  && apt-get install --yes openssh-server \
  && apt-get clean \
  && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

ENTRYPOINT service ssh restart && bash
```

```sh
docker build -t  takaregistry.azurecr.io/ssh_custome_image:13.3 .
```
```sh
docker push takaregistry.azurecr.io/ssh_custome_image:13.3
```

クラスター作成時にレジストリのイメージを指定します。
![Screenshot 2024-08-26 at 9.11.56.JPG](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/91993cf3-a5a0-9bf4-42b9-f07f408ebb49.jpeg)

SSHの設定をします。
![Screenshot 2024-08-26 at 9.11.01.JPG](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/771b8180-db24-7ce4-4676-04e92e170670.jpeg)

クラスターが起動したら、クラスターにノートブックをアタッチしてsshdの動作を確認します。

```sh
%sh
ps aux | grep ssh
```
```
root           1  0.0  0.0   2892   988 pts/0    Ss   00:03   0:00 /bin/sh -c service ssh restart && bash /bin/bash
root          26  0.0  0.0  15432  1824 ?        Ss   00:03   0:00 sshd: /usr/sbin/sshd [listener] 0 of 10-100 startups
root         930  0.0  0.0   3852  1968 ?        S    00:04   0:00 grep ssh
```

sshdが動いてます。

ローカルマシンのターミナルからSSHで接続します。

```sh
ssh ubuntu@48.218.5.173 -p 2200 -i /Users/yayoi/.ssh/id_rsa
```
繋がりました！
![Screenshot 2024-08-26 at 9.13.55.JPG](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/c673cf5d-a8f3-c672-80bd-ed279cc72dda.jpeg)

### はじめてのDatabricks

[はじめてのDatabricks](https://qiita.com/taka_yayoi/items/8dc72d083edb879a5e5d)

### Databricks無料トライアル

[Databricks無料トライアル](https://databricks.com/jp/try-databricks)
