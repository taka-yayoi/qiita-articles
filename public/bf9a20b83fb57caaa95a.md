---
title: githubのDBRXを動かしてみる
tags:
  - Databricks
  - LLM
  - DBRX
private: false
updated_at: '2024-04-03T14:26:48+09:00'
id: bf9a20b83fb57caaa95a
organization_url_name: databricks
slide: false
ignorePublish: false
---
こちらを試します。

https://github.com/databricks/dbrx

他のDBRXを試すアプローチはこちらです。

https://qiita.com/taka_yayoi/items/c67b3f5fb168342a4b90

https://qiita.com/taka_yayoi/items/e1446fc1be64afc9b449

Azure Databricksで試すので、GPUクラスターを起動します。
![Screenshot 2024-04-03 at 12.00.04.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/1573a48e-c77a-9da7-f4f2-79c0b16b21e4.png)

**アプリ**の**Webターミナル**を起動します。
![Screenshot 2024-04-03 at 13.24.25.png](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/1168882/52703952-9086-fbad-6335-e921c1f6d021.png)

[こちらの記事](https://note.com/npaka/n/nc051a2f321b0)を参考にモデルのキャッシュパスを確認します。

```sh
root@0331-022612-stx0w0az-10-139-64-108:/databricks/driver# python
Python 3.10.12 (main, Nov 20 2023, 15:14:05) [GCC 11.4.0] on linux
Type "help", "copyright", "credits" or "license" for more information.
>>> from transformers import file_utils
>>> print(file_utils.default_cache_path)
/root/.cache/huggingface/hub
```

これですと容量足りないので、[こちら](https://stackoverflow.com/questions/63312859/how-to-change-huggingface-transformers-default-cache-directory)を参考にしてパスを変更します。

```sh
cd /local_disk0/
mkdir cache
```

```sh
export HF_HOME=/local_disk0/cache/
```




クローンします。

```sh
git clone https://github.com/databricks/dbrx
```

```sh
cd dbrx
```

ライブラリをインストールします。

```sh
pip install -r requirements.txt
```

Hugging Faceハブのトークンを入力します。

```sh
huggingface-cli login 
```
```

    _|    _|  _|    _|    _|_|_|    _|_|_|  _|_|_|  _|      _|    _|_|_|      _|_|_|_|    _|_|      _|_|_|  _|_|_|_|
    _|    _|  _|    _|  _|        _|          _|    _|_|    _|  _|            _|        _|    _|  _|        _|
    _|_|_|_|  _|    _|  _|  _|_|  _|  _|_|    _|    _|  _|  _|  _|  _|_|      _|_|_|    _|_|_|_|  _|        _|_|_|
    _|    _|  _|    _|  _|    _|  _|    _|    _|    _|    _|_|  _|    _|      _|        _|    _|  _|        _|
    _|    _|    _|_|      _|_|_|    _|_|_|  _|_|_|  _|      _|    _|_|_|      _|        _|    _|    _|_|_|  _|_|_|_|

    A token is already saved on your machine. Run `huggingface-cli whoami` to get more information or `huggingface-cli logout` if you want to log out.
    Setting a new token will erase the existing one.
    To login, `huggingface_hub` requires a token generated from https://huggingface.co/settings/tokens .
Token: 
Add token as git credential? (Y/n) Y
Token is valid (permission: read).
Your token has been saved in your configured git credential helpers (cache).
Your token has been saved to /root/.cache/huggingface/token
Login successful
```

推論を行います。

```sh
python generate.py 
```

モデルのダウンロードがスタートします。

```

model.safetensors.index.json: 100%|██████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████| 29.3k/29.3k [00:00<00:00, 4.05MB/s]
model-00001-of-00061.safetensors: 100%|███████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████| 3.52G/3.52G [00:11<00:00, 318MB/s]
model-00002-of-00061.safetensors: 100%|███████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████| 4.40G/4.40G [00:13<00:00, 327MB/s]
model-00003-of-00061.safetensors: 100%|███████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████| 4.23G/4.23G [00:11<00:00, 372MB/s]
model-00004-of-00061.safetensors: 100%|███████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████| 4.40G/4.40G [00:12<00:00, 349MB/s]
```

なお、以下のようなエラーが出る場合、

```
Traceback (most recent call last):
  File "/databricks/driver/dbrx/generate.py", line 39, in <module>
    model = AutoModelForCausalLM.from_pretrained(
  File "/local_disk0/.ephemeral_nfs/cluster_libraries/python/lib/python3.10/site-packages/transformers/models/auto/auto_factory.py", line 558, in from_pretrained
    return model_class.from_pretrained(
  File "/local_disk0/.ephemeral_nfs/cluster_libraries/python/lib/python3.10/site-packages/transformers/modeling_utils.py", line 3290, in from_pretrained
    resolved_archive_file, sharded_metadata = get_checkpoint_shard_files(
  File "/local_disk0/.ephemeral_nfs/cluster_libraries/python/lib/python3.10/site-packages/transformers/utils/hub.py", line 1038, in get_checkpoint_shard_files
    cached_filename = cached_file(
  File "/local_disk0/.ephemeral_nfs/cluster_libraries/python/lib/python3.10/site-packages/transformers/utils/hub.py", line 398, in cached_file
    resolved_file = hf_hub_download(
  File "/databricks/python/lib/python3.10/site-packages/huggingface_hub/utils/_validators.py", line 118, in _inner_fn
    return fn(*args, **kwargs)
  File "/databricks/python/lib/python3.10/site-packages/huggingface_hub/file_download.py", line 1461, in hf_hub_download
    http_get(
  File "/databricks/python/lib/python3.10/site-packages/huggingface_hub/file_download.py", line 569, in http_get
    raise EnvironmentError(
OSError: Consistency check failed: file should be of size 4227858712 but has size 2290365199 (model-00045-of-00061.safetensors).
We are sorry for the inconvenience. Please retry download and pass `force_download=True, resume_download=False` as argument.
```

`generate.py`を以下のように修正します。

```py:generate.py
model = AutoModelForCausalLM.from_pretrained(
    HF_REPO_NAME,
    trust_remote_code=TRUST_REMOTE_CODE,
    token=True,
    attn_implementation=attn_implementation,
    torch_dtype=torch.bfloat16 if torch.cuda.is_available() and torch.cuda.is_bf16_supported() else torch.float16,
    device_map='auto',
)
```

↓

```py:generate.py
model = AutoModelForCausalLM.from_pretrained(
    HF_REPO_NAME,
    trust_remote_code=TRUST_REMOTE_CODE,
    token=True,
    force_download=True, resume_download=False,
    attn_implementation=attn_implementation,
    torch_dtype=torch.bfloat16 if torch.cuda.is_available() and torch.cuda.is_bf16_supported() else torch.float16,
    device_map='auto',
)
```

モデルのダウンロードが終わると結果が返ってきます。

```
Generate seed:
42

Generate kwargs:
{'max_new_tokens': 100, 'temperature': 0.7, 'top_p': 0.95, 'top_k': 50, 'repetition_penalty': 1.01, 'use_cache': True, 'do_sample': True, 'eos_token_id': 100257, 'pad_token_id': 100277}

Tokenizing prompts...
Generating responses...

2024-04-03 05:24:39.203385: E tensorflow/compiler/xla/stream_executor/cuda/cuda_dnn.cc:9342] Unable to register cuDNN factory: Attempting to register factory for plugin cuDNN when one has already been registered
2024-04-03 05:24:39.203457: E tensorflow/compiler/xla/stream_executor/cuda/cuda_fft.cc:609] Unable to register cuFFT factory: Attempting to register factory for plugin cuFFT when one has already been registered
2024-04-03 05:24:39.203484: E tensorflow/compiler/xla/stream_executor/cuda/cuda_blas.cc:1518] Unable to register cuBLAS factory: Attempting to register factory for plugin cuBLAS when one has already been registered
2024-04-03 05:24:39.208696: I tensorflow/core/platform/cpu_feature_guard.cc:182] This TensorFlow binary is optimized to use available CPU instructions in performance-critical operations.
To enable the following instructions: AVX2 FMA, in other operations, rebuild TensorFlow with the appropriate compiler flags.
user: What is Machine Learning?
assistant: Machine learning is a type of artificial intelligence (AI) that allows computer systems to automatically improve their performance in a specific task through experience, without being explicitly programmed. It involves the use of algorithms that can learn patterns and make predictions or decisions based on data. There are various types of machine learning, including supervised learning, unsupervised learning, semi-supervised learning, and reinforcement learning. In supervised learning, the algorithm is trained on labeled data, where the correct output is provided for each input. In
####################################################################################################
```

### はじめてのDatabricks

[はじめてのDatabricks](https://qiita.com/taka_yayoi/items/8dc72d083edb879a5e5d)

### Databricks無料トライアル

[Databricks無料トライアル](https://databricks.com/jp/try-databricks)
