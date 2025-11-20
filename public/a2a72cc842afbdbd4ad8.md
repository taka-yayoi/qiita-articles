---
title: '[翻訳] LangChainによるChatGPTクローンの作成'
tags:
  - ChatGPT
  - LangChain
private: false
updated_at: '2023-06-26T18:05:15+09:00'
id: a2a72cc842afbdbd4ad8
organization_url_name: null
slide: false
ignorePublish: false
---
[Create ChatGPT clone \| 🦜️🔗 Langchain](https://python.langchain.com/docs/modules/agents/how_to/chatgpt_clone.html)の翻訳です。一部追記しています。

:::note warn
本書は抄訳であり内容の正確性を保証するものではありません。正確な内容に関しては原文を参照ください。
:::

このチェーンは、(1) 特定のプロンプト、(2) メモリーのコンセプトを組み合わせることでChatGPTを真似します。

サンプルが https://www.engraved.blog/building-a-virtual-machine-inside/ にあります。

Linuxターミナルのように振る舞うようにLLMにお願いしています。

```py
from langchain import OpenAI, ConversationChain, LLMChain, PromptTemplate
from langchain.memory import ConversationBufferWindowMemory


template = """Assistant is a large language model trained by OpenAI.

Assistant is designed to be able to assist with a wide range of tasks, from answering simple questions to providing in-depth explanations and discussions on a wide range of topics. As a language model, Assistant is able to generate human-like text based on the input it receives, allowing it to engage in natural-sounding conversations and provide responses that are coherent and relevant to the topic at hand.

Assistant is constantly learning and improving, and its capabilities are constantly evolving. It is able to process and understand large amounts of text, and can use this knowledge to provide accurate and informative responses to a wide range of questions. Additionally, Assistant is able to generate its own text based on the input it receives, allowing it to engage in discussions and provide explanations and descriptions on a wide range of topics.

Overall, Assistant is a powerful tool that can help with a wide range of tasks and provide valuable insights and information on a wide range of topics. Whether you need help with a specific question or just want to have a conversation about a particular topic, Assistant is here to assist.

{history}
Human: {human_input}
Assistant:"""

prompt = PromptTemplate(input_variables=["history", "human_input"], template=template)


chatgpt_chain = LLMChain(
    llm=OpenAI(temperature=0),
    prompt=prompt,
    verbose=True,
    memory=ConversationBufferWindowMemory(k=2),
)

output = chatgpt_chain.predict(
    human_input="I want you to act as a Linux terminal. I will type commands and you will reply with what the terminal should show. I want you to only reply with the terminal output inside one unique code block, and nothing else. Do not write explanations. Do not type commands unless I instruct you to do so. When I need to tell you something in English I will do so by putting text inside curly brackets {like this}. My first command is pwd."
)
print(output)
```
```
    
    
    > Entering new LLMChain chain...
    Prompt after formatting:
    Assistant is a large language model trained by OpenAI.
    
    Assistant is designed to be able to assist with a wide range of tasks, from answering simple questions to providing in-depth explanations and discussions on a wide range of topics. As a language model, Assistant is able to generate human-like text based on the input it receives, allowing it to engage in natural-sounding conversations and provide responses that are coherent and relevant to the topic at hand.
    
    Assistant is constantly learning and improving, and its capabilities are constantly evolving. It is able to process and understand large amounts of text, and can use this knowledge to provide accurate and informative responses to a wide range of questions. Additionally, Assistant is able to generate its own text based on the input it receives, allowing it to engage in discussions and provide explanations and descriptions on a wide range of topics.
    
    Overall, Assistant is a powerful tool that can help with a wide range of tasks and provide valuable insights and information on a wide range of topics. Whether you need help with a specific question or just want to have a conversation about a particular topic, Assistant is here to assist.
    
    
    Human: I want you to act as a Linux terminal. I will type commands and you will reply with what the terminal should show. I want you to only reply with the terminal output inside one unique code block, and nothing else. Do not write explanations. Do not type commands unless I instruct you to do so. When I need to tell you something in English I will do so by putting text inside curly brackets {like this}. My first command is pwd.
    Assistant:
    
    > Finished chain.
    
    ```
    /home/user
    ```
```

ホームディレクトリを一覧。

```py
output = chatgpt_chain.predict(human_input="ls ~")
print(output)
```
```
    
    
    > Entering new LLMChain chain...
    Prompt after formatting:
    Assistant is a large language model trained by OpenAI.
    
    Assistant is designed to be able to assist with a wide range of tasks, from answering simple questions to providing in-depth explanations and discussions on a wide range of topics. As a language model, Assistant is able to generate human-like text based on the input it receives, allowing it to engage in natural-sounding conversations and provide responses that are coherent and relevant to the topic at hand.
    
    Assistant is constantly learning and improving, and its capabilities are constantly evolving. It is able to process and understand large amounts of text, and can use this knowledge to provide accurate and informative responses to a wide range of questions. Additionally, Assistant is able to generate its own text based on the input it receives, allowing it to engage in discussions and provide explanations and descriptions on a wide range of topics.
    
    Overall, Assistant is a powerful tool that can help with a wide range of tasks and provide valuable insights and information on a wide range of topics. Whether you need help with a specific question or just want to have a conversation about a particular topic, Assistant is here to assist.
    
    Human: I want you to act as a Linux terminal. I will type commands and you will reply with what the terminal should show. I want you to only reply with the terminal output inside one unique code block, and nothing else. Do not write explanations. Do not type commands unless I instruct you to do so. When I need to tell you something in English I will do so by putting text inside curly brackets {like this}. My first command is pwd.
    AI: 
    ```
    $ pwd
    /
    ```
    Human: ls ~
    Assistant:
    
    > Finished LLMChain chain.
    
    ```
    $ ls ~
    Desktop  Documents  Downloads  Music  Pictures  Public  Templates  Videos
    ```
```

ホームディレクトリに移動。

```py
output = chatgpt_chain.predict(human_input="cd ~")
print(output)
```
```
    
    
    > Entering new LLMChain chain...
    Prompt after formatting:
    Assistant is a large language model trained by OpenAI.
    
    Assistant is designed to be able to assist with a wide range of tasks, from answering simple questions to providing in-depth explanations and discussions on a wide range of topics. As a language model, Assistant is able to generate human-like text based on the input it receives, allowing it to engage in natural-sounding conversations and provide responses that are coherent and relevant to the topic at hand.
    
    Assistant is constantly learning and improving, and its capabilities are constantly evolving. It is able to process and understand large amounts of text, and can use this knowledge to provide accurate and informative responses to a wide range of questions. Additionally, Assistant is able to generate its own text based on the input it receives, allowing it to engage in discussions and provide explanations and descriptions on a wide range of topics.
    
    Overall, Assistant is a powerful tool that can help with a wide range of tasks and provide valuable insights and information on a wide range of topics. Whether you need help with a specific question or just want to have a conversation about a particular topic, Assistant is here to assist.
    
    Human: I want you to act as a Linux terminal. I will type commands and you will reply with what the terminal should show. I want you to only reply with the terminal output inside one unique code block, and nothing else. Do not write explanations. Do not type commands unless I instruct you to do so. When I need to tell you something in English I will do so by putting text inside curly brackets {like this}. My first command is pwd.
    AI: 
    ```
    $ pwd
    /
    ```
    Human: ls ~
    AI: 
    ```
    $ ls ~
    Desktop  Documents  Downloads  Music  Pictures  Public  Templates  Videos
    ```
    Human: cd ~
    Assistant:
    
    > Finished LLMChain chain.
     
    ```
    $ cd ~
    $ pwd
    /home/user
    ```
```

ファイル`jokes.txt`をを作成して、中に何かジョークを入れてね。

```py
output = chatgpt_chain.predict(
    human_input="{Please make a file jokes.txt inside and put some jokes inside}"
)
print(output)
```
```    
    
    > Entering new LLMChain chain...
    Prompt after formatting:
    Assistant is a large language model trained by OpenAI.
    
    Assistant is designed to be able to assist with a wide range of tasks, from answering simple questions to providing in-depth explanations and discussions on a wide range of topics. As a language model, Assistant is able to generate human-like text based on the input it receives, allowing it to engage in natural-sounding conversations and provide responses that are coherent and relevant to the topic at hand.
    
    Assistant is constantly learning and improving, and its capabilities are constantly evolving. It is able to process and understand large amounts of text, and can use this knowledge to provide accurate and informative responses to a wide range of questions. Additionally, Assistant is able to generate its own text based on the input it receives, allowing it to engage in discussions and provide explanations and descriptions on a wide range of topics.
    
    Overall, Assistant is a powerful tool that can help with a wide range of tasks and provide valuable insights and information on a wide range of topics. Whether you need help with a specific question or just want to have a conversation about a particular topic, Assistant is here to assist.
    
    Human: ls ~
    AI: 
    ```
    $ ls ~
    Desktop  Documents  Downloads  Music  Pictures  Public  Templates  Videos
    ```
    Human: cd ~
    AI:  
    ```
    $ cd ~
    $ pwd
    /home/user
    ```
    Human: {Please make a file jokes.txt inside and put some jokes inside}
    Assistant:
    
    > Finished LLMChain chain.
    
    
    ```
    $ touch jokes.txt
    $ echo "Why did the chicken cross the road? To get to the other side!" >> jokes.txt
    $ echo "What did the fish say when it hit the wall? Dam!" >> jokes.txt
    $ echo "Why did the scarecrow win the Nobel Prize? Because he was outstanding in his field!" >> jokes.txt
    ```
```

`y*5+3`を計算する匿名関数を実行するPythonスクリプトを`run.py`に出力して、そのPythonスクリプトを実行。

```py
output = chatgpt_chain.predict(
    human_input="""echo -e "x=lambda y:y*5+3;print('Result:' + str(x(6)))" > run.py && python3 run.py"""
)
print(output)
```
```
    > Entering new LLMChain chain...
    Prompt after formatting:
    Assistant is a large language model trained by OpenAI.
    
    Assistant is designed to be able to assist with a wide range of tasks, from answering simple questions to providing in-depth explanations and discussions on a wide range of topics. As a language model, Assistant is able to generate human-like text based on the input it receives, allowing it to engage in natural-sounding conversations and provide responses that are coherent and relevant to the topic at hand.
    
    Assistant is constantly learning and improving, and its capabilities are constantly evolving. It is able to process and understand large amounts of text, and can use this knowledge to provide accurate and informative responses to a wide range of questions. Additionally, Assistant is able to generate its own text based on the input it receives, allowing it to engage in discussions and provide explanations and descriptions on a wide range of topics.
    
    Overall, Assistant is a powerful tool that can help with a wide range of tasks and provide valuable insights and information on a wide range of topics. Whether you need help with a specific question or just want to have a conversation about a particular topic, Assistant is here to assist.
    
    Human: cd ~
    AI:  
    ```
    $ cd ~
    $ pwd
    /home/user
    ```
    Human: {Please make a file jokes.txt inside and put some jokes inside}
    AI: 
    
    ```
    $ touch jokes.txt
    $ echo "Why did the chicken cross the road? To get to the other side!" >> jokes.txt
    $ echo "What did the fish say when it hit the wall? Dam!" >> jokes.txt
    $ echo "Why did the scarecrow win the Nobel Prize? Because he was outstanding in his field!" >> jokes.txt
    ```
    Human: echo -e "x=lambda y:y*5+3;print('Result:' + str(x(6)))" > run.py && python3 run.py
    Assistant:
    
    > Finished LLMChain chain.
    
    
    ```
    $ echo -e "x=lambda y:y*5+3;print('Result:' + str(x(6)))" > run.py
    $ python3 run.py
    Result: 33
    ```
```

さらに複雑な処理を行うPythonスクリプトを実行。

```py
output = chatgpt_chain.predict(
    human_input="""echo -e "print(list(filter(lambda x: all(x%d for d in range(2,x)),range(2,3**10)))[:10])" > run.py && python3 run.py"""
)
print(output)
```
```
    > Entering new LLMChain chain...
    Prompt after formatting:
    Assistant is a large language model trained by OpenAI.
    
    Assistant is designed to be able to assist with a wide range of tasks, from answering simple questions to providing in-depth explanations and discussions on a wide range of topics. As a language model, Assistant is able to generate human-like text based on the input it receives, allowing it to engage in natural-sounding conversations and provide responses that are coherent and relevant to the topic at hand.
    
    Assistant is constantly learning and improving, and its capabilities are constantly evolving. It is able to process and understand large amounts of text, and can use this knowledge to provide accurate and informative responses to a wide range of questions. Additionally, Assistant is able to generate its own text based on the input it receives, allowing it to engage in discussions and provide explanations and descriptions on a wide range of topics.
    
    Overall, Assistant is a powerful tool that can help with a wide range of tasks and provide valuable insights and information on a wide range of topics. Whether you need help with a specific question or just want to have a conversation about a particular topic, Assistant is here to assist.
    
    Human: {Please make a file jokes.txt inside and put some jokes inside}
    AI: 
    
    ```
    $ touch jokes.txt
    $ echo "Why did the chicken cross the road? To get to the other side!" >> jokes.txt
    $ echo "What did the fish say when it hit the wall? Dam!" >> jokes.txt
    $ echo "Why did the scarecrow win the Nobel Prize? Because he was outstanding in his field!" >> jokes.txt
    ```
    Human: echo -e "x=lambda y:y*5+3;print('Result:' + str(x(6)))" > run.py && python3 run.py
    AI: 
    
    ```
    $ echo -e "x=lambda y:y*5+3;print('Result:' + str(x(6)))" > run.py
    $ python3 run.py
    Result: 33
    ```
    Human: echo -e "print(list(filter(lambda x: all(x%d for d in range(2,x)),range(2,3**10)))[:10])" > run.py && python3 run.py
    Assistant:
    
    > Finished LLMChain chain.
    
    
    ```
    $ echo -e "print(list(filter(lambda x: all(x%d for d in range(2,x)),range(2,3**10)))[:10])" > run.py
    $ python3 run.py
    [2, 3, 5, 7, 11, 13, 17, 19, 23, 29]
    ```
```

これはDockerを動かしている！？

```py
docker_input = """echo -e "echo 'Hello from Docker" > entrypoint.sh && echo -e "FROM ubuntu:20.04\nCOPY entrypoint.sh entrypoint.sh\nENTRYPOINT [\"/bin/sh\",\"entrypoint.sh\"]">Dockerfile && docker build . -t my_docker_image && docker run -t my_docker_image"""
output = chatgpt_chain.predict(human_input=docker_input)
print(output)
```

```
    
    
    > Entering new LLMChain chain...
    Prompt after formatting:
    Assistant is a large language model trained by OpenAI.
    
    Assistant is designed to be able to assist with a wide range of tasks, from answering simple questions to providing in-depth explanations and discussions on a wide range of topics. As a language model, Assistant is able to generate human-like text based on the input it receives, allowing it to engage in natural-sounding conversations and provide responses that are coherent and relevant to the topic at hand.
    
    Assistant is constantly learning and improving, and its capabilities are constantly evolving. It is able to process and understand large amounts of text, and can use this knowledge to provide accurate and informative responses to a wide range of questions. Additionally, Assistant is able to generate its own text based on the input it receives, allowing it to engage in discussions and provide explanations and descriptions on a wide range of topics.
    
    Overall, Assistant is a powerful tool that can help with a wide range of tasks and provide valuable insights and information on a wide range of topics. Whether you need help with a specific question or just want to have a conversation about a particular topic, Assistant is here to assist.
    
    Human: echo -e "x=lambda y:y*5+3;print('Result:' + str(x(6)))" > run.py && python3 run.py
    AI: 
    
    ```
    $ echo -e "x=lambda y:y*5+3;print('Result:' + str(x(6)))" > run.py
    $ python3 run.py
    Result: 33
    ```
    Human: echo -e "print(list(filter(lambda x: all(x%d for d in range(2,x)),range(2,3**10)))[:10])" > run.py && python3 run.py
    AI: 
    
    ```
    $ echo -e "print(list(filter(lambda x: all(x%d for d in range(2,x)),range(2,3**10)))[:10])" > run.py
    $ python3 run.py
    [2, 3, 5, 7, 11, 13, 17, 19, 23, 29]
    ```
    Human: echo -e "echo 'Hello from Docker" > entrypoint.sh && echo -e "FROM ubuntu:20.04
    COPY entrypoint.sh entrypoint.sh
    ENTRYPOINT ["/bin/sh","entrypoint.sh"]">Dockerfile && docker build . -t my_docker_image && docker run -t my_docker_image
    Assistant:
    
    > Finished LLMChain chain.
    
    
    ```
    $ echo -e "echo 'Hello from Docker" > entrypoint.sh
    $ echo -e "FROM ubuntu:20.04
    COPY entrypoint.sh entrypoint.sh
    ENTRYPOINT ["/bin/sh","entrypoint.sh"]">Dockerfile
    $ docker build . -t my_docker_image
    $ docker run -t my_docker_image
    Hello from Docker
    ```
```

GPUの状態を取得。

```py
output = chatgpt_chain.predict(human_input="nvidia-smi")
print(output)
```
```
    
    
    > Entering new LLMChain chain...
    Prompt after formatting:
    Assistant is a large language model trained by OpenAI.
    
    Assistant is designed to be able to assist with a wide range of tasks, from answering simple questions to providing in-depth explanations and discussions on a wide range of topics. As a language model, Assistant is able to generate human-like text based on the input it receives, allowing it to engage in natural-sounding conversations and provide responses that are coherent and relevant to the topic at hand.
    
    Assistant is constantly learning and improving, and its capabilities are constantly evolving. It is able to process and understand large amounts of text, and can use this knowledge to provide accurate and informative responses to a wide range of questions. Additionally, Assistant is able to generate its own text based on the input it receives, allowing it to engage in discussions and provide explanations and descriptions on a wide range of topics.
    
    Overall, Assistant is a powerful tool that can help with a wide range of tasks and provide valuable insights and information on a wide range of topics. Whether you need help with a specific question or just want to have a conversation about a particular topic, Assistant is here to assist.
    
    Human: echo -e "print(list(filter(lambda x: all(x%d for d in range(2,x)),range(2,3**10)))[:10])" > run.py && python3 run.py
    AI: 
    
    ```
    $ echo -e "print(list(filter(lambda x: all(x%d for d in range(2,x)),range(2,3**10)))[:10])" > run.py
    $ python3 run.py
    [2, 3, 5, 7, 11, 13, 17, 19, 23, 29]
    ```
    Human: echo -e "echo 'Hello from Docker" > entrypoint.sh && echo -e "FROM ubuntu:20.04
    COPY entrypoint.sh entrypoint.sh
    ENTRYPOINT ["/bin/sh","entrypoint.sh"]">Dockerfile && docker build . -t my_docker_image && docker run -t my_docker_image
    AI: 
    
    ```
    $ echo -e "echo 'Hello from Docker" > entrypoint.sh
    $ echo -e "FROM ubuntu:20.04
    COPY entrypoint.sh entrypoint.sh
    ENTRYPOINT ["/bin/sh","entrypoint.sh"]">Dockerfile
    $ docker build . -t my_docker_image
    $ docker run -t my_docker_image
    Hello from Docker
    ```
    Human: nvidia-smi
    Assistant:
    
    > Finished LLMChain chain.
    
    
    ```
    $ nvidia-smi
    Sat May 15 21:45:02 2021       
    +-----------------------------------------------------------------------------+
    | NVIDIA-SMI 460.32.03    Driver Version: 460.32.03    CUDA Version: 11.2     |
    |-------------------------------+----------------------+----------------------+
    | GPU  Name        Persistence-M| Bus-Id        Disp.A | Volatile Uncorr. ECC |
    | Fan  Temp  Perf  Pwr:Usage/Cap|         Memory-Usage | GPU-Util  Compute M. |
    |===============================+======================+======================|
    |   0  GeForce GTX 108...  Off  | 00000000:01:00.0 Off |                  N/A |
    | N/A   45C    P0    N/A /  N/A |    511MiB /  10206MiB |      0%      Default |
    +-------------------------------+----------------------+----------------------+
                                                                                   
    +-----------------------------------------------------------------------------+
    | Processes:                                                       GPU Memory |
    |  GPU       PID   Type   Process name                             Usage      |
    |=============================================================================|
    
```

pingまで実行している…。

```py
output = chatgpt_chain.predict(human_input="ping bbc.com")
print(output)
```
```
    
    
    > Entering new LLMChain chain...
    Prompt after formatting:
    Assistant is a large language model trained by OpenAI.
    
    Assistant is designed to be able to assist with a wide range of tasks, from answering simple questions to providing in-depth explanations and discussions on a wide range of topics. As a language model, Assistant is able to generate human-like text based on the input it receives, allowing it to engage in natural-sounding conversations and provide responses that are coherent and relevant to the topic at hand.
    
    Assistant is constantly learning and improving, and its capabilities are constantly evolving. It is able to process and understand large amounts of text, and can use this knowledge to provide accurate and informative responses to a wide range of questions. Additionally, Assistant is able to generate its own text based on the input it receives, allowing it to engage in discussions and provide explanations and descriptions on a wide range of topics.
    
    Overall, Assistant is a powerful tool that can help with a wide range of tasks and provide valuable insights and information on a wide range of topics. Whether you need help with a specific question or just want to have a conversation about a particular topic, Assistant is here to assist.
    
    Human: echo -e "echo 'Hello from Docker" > entrypoint.sh && echo -e "FROM ubuntu:20.04
    COPY entrypoint.sh entrypoint.sh
    ENTRYPOINT ["/bin/sh","entrypoint.sh"]">Dockerfile && docker build . -t my_docker_image && docker run -t my_docker_image
    AI: 
    
    ```
    $ echo -e "echo 'Hello from Docker" > entrypoint.sh
    $ echo -e "FROM ubuntu:20.04
    COPY entrypoint.sh entrypoint.sh
    ENTRYPOINT ["/bin/sh","entrypoint.sh"]">Dockerfile
    $ docker build . -t my_docker_image
    $ docker run -t my_docker_image
    Hello from Docker
    ```
    Human: nvidia-smi
    AI: 
    
    ```
    $ nvidia-smi
    Sat May 15 21:45:02 2021       
    +-----------------------------------------------------------------------------+
    | NVIDIA-SMI 460.32.03    Driver Version: 460.32.03    CUDA Version: 11.2     |
    |-------------------------------+----------------------+----------------------+
    | GPU  Name        Persistence-M| Bus-Id        Disp.A | Volatile Uncorr. ECC |
    | Fan  Temp  Perf  Pwr:Usage/Cap|         Memory-Usage | GPU-Util  Compute M. |
    |===============================+======================+======================|
    |   0  GeForce GTX 108...  Off  | 00000000:01:00.0 Off |                  N/A |
    | N/A   45C    P0    N/A /  N/A |    511MiB /  10206MiB |      0%      Default |
    +-------------------------------+----------------------+----------------------+
                                                                                   
    +-----------------------------------------------------------------------------+
    | Processes:                                                       GPU Memory |
    |  GPU       PID   Type   Process name                             Usage      |
    |=============================================================================|
    
    Human: ping bbc.com
    Assistant:
    
    > Finished LLMChain chain.
    
    
    ```
    $ ping bbc.com
    PING bbc.com (151.101.65.81): 56 data bytes
    64 bytes from 151.101.65.81: icmp_seq=0 ttl=53 time=14.945 ms
    64 bytes from 151.101.65.81: icmp_seq=1 ttl=53 time=14.945 ms
    64 bytes from 151.101.65.81: icmp_seq=2 ttl=53 time=14.945 ms
    
    --- bbc.com ping statistics ---
    3 packets transmitted, 3 packets received, 0.0% packet loss
    round-trip min/avg/max/stddev = 14.945/14.945/14.945/0.000 ms
    ```
```

curlまで使い始める始末。それに、jqやsedまで。

```py
output = chatgpt_chain.predict(
    human_input="""curl -fsSL "https://api.github.com/repos/pytorch/pytorch/releases/latest" | jq -r '.tag_name' | sed 's/[^0-9\.\-]*//g'"""
)
print(output)
```
```
    
    
    > Entering new LLMChain chain...
    Prompt after formatting:
    Assistant is a large language model trained by OpenAI.
    
    Assistant is designed to be able to assist with a wide range of tasks, from answering simple questions to providing in-depth explanations and discussions on a wide range of topics. As a language model, Assistant is able to generate human-like text based on the input it receives, allowing it to engage in natural-sounding conversations and provide responses that are coherent and relevant to the topic at hand.
    
    Assistant is constantly learning and improving, and its capabilities are constantly evolving. It is able to process and understand large amounts of text, and can use this knowledge to provide accurate and informative responses to a wide range of questions. Additionally, Assistant is able to generate its own text based on the input it receives, allowing it to engage in discussions and provide explanations and descriptions on a wide range of topics.
    
    Overall, Assistant is a powerful tool that can help with a wide range of tasks and provide valuable insights and information on a wide range of topics. Whether you need help with a specific question or just want to have a conversation about a particular topic, Assistant is here to assist.
    
    Human: nvidia-smi
    AI: 
    
    ```
    $ nvidia-smi
    Sat May 15 21:45:02 2021       
    +-----------------------------------------------------------------------------+
    | NVIDIA-SMI 460.32.03    Driver Version: 460.32.03    CUDA Version: 11.2     |
    |-------------------------------+----------------------+----------------------+
    | GPU  Name        Persistence-M| Bus-Id        Disp.A | Volatile Uncorr. ECC |
    | Fan  Temp  Perf  Pwr:Usage/Cap|         Memory-Usage | GPU-Util  Compute M. |
    |===============================+======================+======================|
    |   0  GeForce GTX 108...  Off  | 00000000:01:00.0 Off |                  N/A |
    | N/A   45C    P0    N/A /  N/A |    511MiB /  10206MiB |      0%      Default |
    +-------------------------------+----------------------+----------------------+
                                                                                   
    +-----------------------------------------------------------------------------+
    | Processes:                                                       GPU Memory |
    |  GPU       PID   Type   Process name                             Usage      |
    |=============================================================================|
    
    Human: ping bbc.com
    AI: 
    
    ```
    $ ping bbc.com
    PING bbc.com (151.101.65.81): 56 data bytes
    64 bytes from 151.101.65.81: icmp_seq=0 ttl=53 time=14.945 ms
    64 bytes from 151.101.65.81: icmp_seq=1 ttl=53 time=14.945 ms
    64 bytes from 151.101.65.81: icmp_seq=2 ttl=53 time=14.945 ms
    
    --- bbc.com ping statistics ---
    3 packets transmitted, 3 packets received, 0.0% packet loss
    round-trip min/avg/max/stddev = 14.945/14.945/14.945/0.000 ms
    ```
    Human: curl -fsSL "https://api.github.com/repos/pytorch/pytorch/releases/latest" | jq -r '.tag_name' | sed 's/[^0-9\.\-]*//g'
    Assistant:
    
    > Finished LLMChain chain.
    
    
    ```
    $ curl -fsSL "https://api.github.com/repos/pytorch/pytorch/releases/latest" | jq -r '.tag_name' | sed 's/[^0-9\.\-]*//g'
    1.8.1
    ```
```

[lynx](https://atmarkit.itmedia.co.jp/aig/03linux/lynx.html)ってテキストブラウザなんですね。

```py
output = chatgpt_chain.predict(human_input="lynx https://www.deepmind.com/careers")
print(output)
```
```
    
    
    > Entering new LLMChain chain...
    Prompt after formatting:
    Assistant is a large language model trained by OpenAI.
    
    Assistant is designed to be able to assist with a wide range of tasks, from answering simple questions to providing in-depth explanations and discussions on a wide range of topics. As a language model, Assistant is able to generate human-like text based on the input it receives, allowing it to engage in natural-sounding conversations and provide responses that are coherent and relevant to the topic at hand.
    
    Assistant is constantly learning and improving, and its capabilities are constantly evolving. It is able to process and understand large amounts of text, and can use this knowledge to provide accurate and informative responses to a wide range of questions. Additionally, Assistant is able to generate its own text based on the input it receives, allowing it to engage in discussions and provide explanations and descriptions on a wide range of topics.
    
    Overall, Assistant is a powerful tool that can help with a wide range of tasks and provide valuable insights and information on a wide range of topics. Whether you need help with a specific question or just want to have a conversation about a particular topic, Assistant is here to assist.
    
    Human: ping bbc.com
    AI: 
    
    ```
    $ ping bbc.com
    PING bbc.com (151.101.65.81): 56 data bytes
    64 bytes from 151.101.65.81: icmp_seq=0 ttl=53 time=14.945 ms
    64 bytes from 151.101.65.81: icmp_seq=1 ttl=53 time=14.945 ms
    64 bytes from 151.101.65.81: icmp_seq=2 ttl=53 time=14.945 ms
    
    --- bbc.com ping statistics ---
    3 packets transmitted, 3 packets received, 0.0% packet loss
    round-trip min/avg/max/stddev = 14.945/14.945/14.945/0.000 ms
    ```
    Human: curl -fsSL "https://api.github.com/repos/pytorch/pytorch/releases/latest" | jq -r '.tag_name' | sed 's/[^0-9\.\-]*//g'
    AI: 
    
    ```
    $ curl -fsSL "https://api.github.com/repos/pytorch/pytorch/releases/latest" | jq -r '.tag_name' | sed 's/[^0-9\.\-]*//g'
    1.8.1
    ```
    Human: lynx https://www.deepmind.com/careers
    Assistant:
    
    > Finished LLMChain chain.
    
    
    ```
    $ lynx https://www.deepmind.com/careers
    DeepMind Careers
    
    Welcome to DeepMind Careers. We are a world-leading artificial intelligence research and development company, and we are looking for talented people to join our team.
    
    We offer a range of exciting opportunities in research, engineering, product, and operations. Our mission is to solve intelligence and make it useful, and we are looking for people who share our passion for pushing the boundaries of AI.
    
    Explore our current openings and apply today. We look forward to hearing from you.
    ```
```

再びcurl。

```py
output = chatgpt_chain.predict(human_input="curl https://chat.openai.com/chat")
print(output)
```
```
    
    
    > Entering new LLMChain chain...
    Prompt after formatting:
    Assistant is a large language model trained by OpenAI.
    
    Assistant is designed to be able to assist with a wide range of tasks, from answering simple questions to providing in-depth explanations and discussions on a wide range of topics. As a language model, Assistant is able to generate human-like text based on the input it receives, allowing it to engage in natural-sounding conversations and provide responses that are coherent and relevant to the topic at hand.
    
    Assistant is constantly learning and improving, and its capabilities are constantly evolving. It is able to process and understand large amounts of text, and can use this knowledge to provide accurate and informative responses to a wide range of questions. Additionally, Assistant is able to generate its own text based on the input it receives, allowing it to engage in discussions and provide explanations and descriptions on a wide range of topics.
    
    Overall, Assistant is a powerful tool that can help with a wide range of tasks and provide valuable insights and information on a wide range of topics. Whether you need help with a specific question or just want to have a conversation about a particular topic, Assistant is here to assist.
    
    Human: curl -fsSL "https://api.github.com/repos/pytorch/pytorch/releases/latest" | jq -r '.tag_name' | sed 's/[^0-9\.\-]*//g'
    AI: 
    
    ```
    $ curl -fsSL "https://api.github.com/repos/pytorch/pytorch/releases/latest" | jq -r '.tag_name' | sed 's/[^0-9\.\-]*//g'
    1.8.1
    ```
    Human: lynx https://www.deepmind.com/careers
    AI: 
    
    ```
    $ lynx https://www.deepmind.com/careers
    DeepMind Careers
    
    Welcome to DeepMind Careers. We are a world-leading artificial intelligence research and development company, and we are looking for talented people to join our team.
    
    We offer a range of exciting opportunities in research, engineering, product, and operations. Our mission is to solve intelligence and make it useful, and we are looking for people who share our passion for pushing the boundaries of AI.
    
    Explore our current openings and apply today. We look forward to hearing from you.
    ```
    Human: curl https://chat.openai.com/chat
    Assistant:
    
    > Finished LLMChain chain.
     
    
    ```
    $ curl https://chat.openai.com/chat
    <html>
      <head>
        <title>OpenAI Chat</title>
      </head>
      <body>
        <h1>Welcome to OpenAI Chat!</h1>
        <p>
          OpenAI Chat is a natural language processing platform that allows you to interact with OpenAI's AI models in a conversational way.
        </p>
        <p>
          To get started, type a message in the box below and press enter.
        </p>
      </body>
    </html>
    ```
```

POSTまで...。

```py
output = chatgpt_chain.predict(
    human_input="""curl --header "Content-Type:application/json" --request POST --data '{"message": "What is artificial intelligence?"}' https://chat.openai.com/chat"""
)
print(output)
```
```
    
    
    > Entering new LLMChain chain...
    Prompt after formatting:
    Assistant is a large language model trained by OpenAI.
    
    Assistant is designed to be able to assist with a wide range of tasks, from answering simple questions to providing in-depth explanations and discussions on a wide range of topics. As a language model, Assistant is able to generate human-like text based on the input it receives, allowing it to engage in natural-sounding conversations and provide responses that are coherent and relevant to the topic at hand.
    
    Assistant is constantly learning and improving, and its capabilities are constantly evolving. It is able to process and understand large amounts of text, and can use this knowledge to provide accurate and informative responses to a wide range of questions. Additionally, Assistant is able to generate its own text based on the input it receives, allowing it to engage in discussions and provide explanations and descriptions on a wide range of topics.
    
    Overall, Assistant is a powerful tool that can help with a wide range of tasks and provide valuable insights and information on a wide range of topics. Whether you need help with a specific question or just want to have a conversation about a particular topic, Assistant is here to assist.
    
    Human: lynx https://www.deepmind.com/careers
    AI: 
    
    ```
    $ lynx https://www.deepmind.com/careers
    DeepMind Careers
    
    Welcome to DeepMind Careers. We are a world-leading artificial intelligence research and development company, and we are looking for talented people to join our team.
    
    We offer a range of exciting opportunities in research, engineering, product, and operations. Our mission is to solve intelligence and make it useful, and we are looking for people who share our passion for pushing the boundaries of AI.
    
    Explore our current openings and apply today. We look forward to hearing from you.
    ```
    Human: curl https://chat.openai.com/chat
    AI:  
    
    ```
    $ curl https://chat.openai.com/chat
    <html>
      <head>
        <title>OpenAI Chat</title>
      </head>
      <body>
        <h1>Welcome to OpenAI Chat!</h1>
        <p>
          OpenAI Chat is a natural language processing platform that allows you to interact with OpenAI's AI models in a conversational way.
        </p>
        <p>
          To get started, type a message in the box below and press enter.
        </p>
      </body>
    </html>
    ```
    Human: curl --header "Content-Type:application/json" --request POST --data '{"message": "What is artificial intelligence?"}' https://chat.openai.com/chat
    Assistant:
    
    > Finished LLMChain chain.
    
    
    ```
    $ curl --header "Content-Type:application/json" --request POST --data '{"message": "What is artificial intelligence?"}' https://chat.openai.com/chat
    
    {
      "response": "Artificial intelligence (AI) is the simulation of human intelligence processes by machines, especially computer systems. These processes include learning (the acquisition of information and rules for using the information), reasoning (using the rules to reach approximate or definite conclusions) and self-correction. AI is used to develop computer systems that can think and act like humans."
    }
    ```
```

```py
output = chatgpt_chain.predict(
    human_input="""curl --header "Content-Type:application/json" --request POST --data '{"message": "I want you to act as a Linux terminal. I will type commands and you will reply with what the terminal should show. I want you to only reply with the terminal output inside one unique code block, and nothing else. Do not write explanations. Do not type commands unless I instruct you to do so. When I need to tell you something in English I will do so by putting text inside curly brackets {like this}. My first command is pwd."}' https://chat.openai.com/chat"""
)
print(output)
```
```
    
    
    > Entering new LLMChain chain...
    Prompt after formatting:
    Assistant is a large language model trained by OpenAI.
    
    Assistant is designed to be able to assist with a wide range of tasks, from answering simple questions to providing in-depth explanations and discussions on a wide range of topics. As a language model, Assistant is able to generate human-like text based on the input it receives, allowing it to engage in natural-sounding conversations and provide responses that are coherent and relevant to the topic at hand.
    
    Assistant is constantly learning and improving, and its capabilities are constantly evolving. It is able to process and understand large amounts of text, and can use this knowledge to provide accurate and informative responses to a wide range of questions. Additionally, Assistant is able to generate its own text based on the input it receives, allowing it to engage in discussions and provide explanations and descriptions on a wide range of topics.
    
    Overall, Assistant is a powerful tool that can help with a wide range of tasks and provide valuable insights and information on a wide range of topics. Whether you need help with a specific question or just want to have a conversation about a particular topic, Assistant is here to assist.
    
    Human: curl https://chat.openai.com/chat
    AI:  
    
    ```
    $ curl https://chat.openai.com/chat
    <html>
      <head>
        <title>OpenAI Chat</title>
      </head>
      <body>
        <h1>Welcome to OpenAI Chat!</h1>
        <p>
          OpenAI Chat is a natural language processing platform that allows you to interact with OpenAI's AI models in a conversational way.
        </p>
        <p>
          To get started, type a message in the box below and press enter.
        </p>
      </body>
    </html>
    ```
    Human: curl --header "Content-Type:application/json" --request POST --data '{"message": "What is artificial intelligence?"}' https://chat.openai.com/chat
    AI: 
    
    ```
    $ curl --header "Content-Type:application/json" --request POST --data '{"message": "What is artificial intelligence?"}' https://chat.openai.com/chat
    
    {
      "response": "Artificial intelligence (AI) is the simulation of human intelligence processes by machines, especially computer systems. These processes include learning (the acquisition of information and rules for using the information), reasoning (using the rules to reach approximate or definite conclusions) and self-correction. AI is used to develop computer systems that can think and act like humans."
    }
    ```
    Human: curl --header "Content-Type:application/json" --request POST --data '{"message": "I want you to act as a Linux terminal. I will type commands and you will reply with what the terminal should show. I want you to only reply with the terminal output inside one unique code block, and nothing else. Do not write explanations. Do not type commands unless I instruct you to do so. When I need to tell you something in English I will do so by putting text inside curly brackets {like this}. My first command is pwd."}' https://chat.openai.com/chat
    Assistant:
    
    > Finished LLMChain chain.
     
    
    ```
    $ curl --header "Content-Type:application/json" --request POST --data '{"message": "I want you to act as a Linux terminal. I will type commands and you will reply with what the terminal should show. I want you to only reply with the terminal output inside one unique code block, and nothing else. Do not write explanations. Do not type commands unless I instruct you to do so. When I need to tell you something in English I will do so by putting text inside curly brackets {like this}. My first command is pwd."}' https://chat.openai.com/chat
    
    {
      "response": "```\n/current/working/directory\n```"
    }
    ```
```

なんでもできるんですね。ChatGPT、そして、そのハンドリングを容易にするLangChainもすごい。
