---
title: '[翻訳] LangChainにおけるプロンプトテンプレートのGetting Started'
tags:
  - LangChain
private: false
updated_at: '2023-05-30T14:25:47+09:00'
id: 3effed7c88dd3d2f4a85
organization_url_name: null
slide: false
ignorePublish: false
posting_campaign_uuid: null
agreed_posting_campaign_term: false
---
[Getting Started — 🦜🔗 LangChain 0\.0\.184](https://python.langchain.com/en/latest/modules/prompts/prompt_templates/getting_started.html)の翻訳です。

:::note warn
本書は抄訳であり内容の正確性を保証するものではありません。正確な内容に関しては原文を参照ください。
:::

このチュートリアルでは、以下を学びます:

- プロンプトテンプレートとは何か、なぜ必要なのか
- プロンプトテンプレートの作成方法
- プロンプトテンプレートに対するfew shotサンプルの渡し方
- プロンプトテンプレートに対するサンプルの選択方法

# プロンプトテンプレートとは？

プロンプトテンプレートは、プロンプトを作成する再現可能な方法を指します。これには、エンドユーザーから一連のパラメーターを受け取り、プロンプトを生成するテキスト文字列(テンプレート)が含まれます。

プロンプトテンプレートには以下が含まれます:

- 言語モデルに対する指示
- 言語モデルがより良いレスポンスを生成できるようにするためのfew shotサンプルのセット
- 言語モデルに対する質問

以下のコードスニペットには、プロンプトテンプレートのサンプルが含まれています:

```py
from langchain import PromptTemplate


template = """
I want you to act as a naming consultant for new companies.
What is a good name for a company that makes {product}?
"""

prompt = PromptTemplate(
    input_variables=["product"],
    template=template,
)
prompt.format(product="colorful socks")
# -> I want you to act as a naming consultant for new companies.
# -> What is a good name for a company that makes colorful socks?
```

# プロンプトテンプレートの作成

`PromptTemplate`クラスを用いて、シンプルなハードコードされたプロンプトを作成することができます。プロンプトテンプレートは、任意の数の入力変数を受け取り、プロンプトを生成するためにフォーマットすることができます。

```py
from langchain import PromptTemplate

# An example prompt with no input variables
no_input_prompt = PromptTemplate(input_variables=[], template="Tell me a joke.")
no_input_prompt.format()
# -> "Tell me a joke."

# An example prompt with one input variable
one_input_prompt = PromptTemplate(input_variables=["adjective"], template="Tell me a {adjective} joke.")
one_input_prompt.format(adjective="funny")
# -> "Tell me a funny joke."

# An example prompt with multiple input variables
multiple_input_prompt = PromptTemplate(
    input_variables=["adjective", "content"], 
    template="Tell me a {adjective} joke about {content}."
)
multiple_input_prompt.format(adjective="funny", content="chickens")
# -> "Tell me a funny joke about chickens."
```

手動で`input_variables`を指定したく無いのであれば、`from_template`クラスメソッドを用いて`PromptTemplate`を作成することもできます。`langchain`は指定された`template`に基づいて自動で`input_variables`を推定します。

```py
template = "Tell me a {adjective} joke about {content}."

prompt_template = PromptTemplate.from_template(template)
prompt_template.input_variables
# -> ['adjective', 'content']
prompt_template.format(adjective="funny", content="chickens")
# -> Tell me a funny joke about chickens.
```

好きな方法でプロンプトをフォーマットするカスタムプロンプトテンプレートを作成することができます。詳細は[Custom Prompt Templates](https://python.langchain.com/en/latest/modules/prompts/prompt_templates/examples/custom_prompt_template.html)をご覧ください。

# テンプレートのフォーマット

デフォルトでは、`PromptTemplate`はテンプレートをPythonのf-stringとして取り扱います。引数`template_format`を通じて、他のテンプレートフォーマットを指定することができます。

```py
# Make sure jinja2 is installed before running this

jinja2_template = "Tell me a {{ adjective }} joke about {{ content }}"
prompt_template = PromptTemplate.from_template(template=jinja2_template, template_format="jinja2")

prompt_template.format(adjective="funny", content="chickens")
# -> Tell me a funny joke about chickens.
```

現時点では、`PromptTemplate`は`jinja2`と`f-string`テンプレートフォーマットのみをサポートしています。使用したい他のテンプレートフォーマットがあるのであれば、[Github](https://github.com/hwchase17/langchain/issues)ページでイシューをオープンしてください。

# テンプレートの検証

デフォルトでは、`PromptTemplate`は`template`で定義されている変数が`input_variables`とマッチするかをチェックすることで`template`文字列を検証します。`validate_template`を`False`に設定することで、この挙動を無効にすることができます。

```py
template = "I am learning langchain because {reason}."

prompt_template = PromptTemplate(template=template, 
                                 input_variables=["reason", "foo"]) # ValueError due to extra variables
prompt_template = PromptTemplate(template=template, 
                                 input_variables=["reason", "foo"], 
                                 validate_template=False) # No error
```

# プロンプトテンプレートのシリアライズ

お使いのローカルファイルシステムのファイルに`PromptTemplate`を保存することができます。`langchain`は、ファイルの拡張子を通じてファイルフォーマットを自動で推定します。現時点では、`langchain`はYAMLかJSONファイルでのテンプレート保存をサポートしています。

```py
prompt_template.save("awesome_prompt.json") # Save to JSON file
```

```py
from langchain.prompts import load_prompt
loaded_prompt = load_prompt("awesome_prompt.json")

assert prompt_template == loaded_prompt
```

また、`langchain`はご自身のプロジェクトで使用できる有用なプロンプトのコレクションを格納するLangChainHubからのプロンプトテンプレートのロードをサポートしています。LangChainHubと利用できるプロンプトの詳細については、[こちら](https://github.com/hwchase17/langchain-hub)をご覧ください。

```py
from langchain.prompts import load_prompt

prompt = load_prompt("lc://prompts/conversation/prompt.json")
prompt.format(history="", input="What is 1 + 1?")
```

[How to serialize prompts](https://python.langchain.com/en/latest/modules/prompts/prompt_templates/examples/prompt_serialization.html)でプロンプトテンプレートのシリアライズに関して学ぶことができます。

# プロンプトテンプレートにfew shotサンプルを渡す

Few shotサンプルは、言語モデルがより良いレスポンスを生成する助けになる一連のサンプルです。

Few shotサンプルを用いてプロンプトを生成するには、`FewShotPromptTemplate`を使うことができます。このクラスは`PromptTemplate`とfew shotサンプルのリストを受け取ります。そして、few shotサンプルを用いてプロンプトテンプレートをフォーマットします。

この例では、反語を生成するためのプロンプトを作成します。

```py
from langchain import PromptTemplate, FewShotPromptTemplate

# First, create the list of few shot examples.
examples = [
    {"word": "happy", "antonym": "sad"},
    {"word": "tall", "antonym": "short"},
]

# Next, we specify the template to format the examples we have provided.
# We use the `PromptTemplate` class for this.
example_formatter_template = """Word: {word}
Antonym: {antonym}
"""

example_prompt = PromptTemplate(
    input_variables=["word", "antonym"],
    template=example_formatter_template,
)

# Finally, we create the `FewShotPromptTemplate` object.
few_shot_prompt = FewShotPromptTemplate(
    # These are the examples we want to insert into the prompt.
    examples=examples,
    # This is how we want to format the examples when we insert them into the prompt.
    example_prompt=example_prompt,
    # The prefix is some text that goes before the examples in the prompt.
    # Usually, this consists of intructions.
    prefix="Give the antonym of every input\n",
    # The suffix is some text that goes after the examples in the prompt.
    # Usually, this is where the user input will go
    suffix="Word: {input}\nAntonym: ",
    # The input variables are the variables that the overall prompt expects.
    input_variables=["input"],
    # The example_separator is the string we will use to join the prefix, examples, and suffix together with.
    example_separator="\n",
)

# We can now generate a prompt using the `format` method.
print(few_shot_prompt.format(input="big"))
# -> Give the antonym of every input
# -> 
# -> Word: happy
# -> Antonym: sad
# ->
# -> Word: tall
# -> Antonym: short
# ->
# -> Word: big
# -> Antonym: 
```

# プロンプトテンプレートに対するサンプルの選択

大量のサンプルがある場合、言語モデルにとって最も有意なサンプルのサブセットを選択するために、`ExampleSelector`を活用することができます。これは、良いレスポンスを生成するであろうプロンプトの生成に役立ちます。

以下では、入力の長さに基づいてサンプルを選択する`LengthBasedExampleSelector`を使用します。これは、コンテキストウィンドウの長さを上回るプロンプトを構築する際に心配な場合には有用です。長い入力に対しては、含めるサンプルの数を少なくし、短い入力を多く選択します。

以前のセクションのサンプルを使い続けますが、今回はサンプルの選択に`LengthBasedExampleSelector`を使います。

```py
from langchain.prompts.example_selector import LengthBasedExampleSelector


# These are a lot of examples of a pretend task of creating antonyms.
examples = [
    {"word": "happy", "antonym": "sad"},
    {"word": "tall", "antonym": "short"},
    {"word": "energetic", "antonym": "lethargic"},
    {"word": "sunny", "antonym": "gloomy"},
    {"word": "windy", "antonym": "calm"},
]

# We'll use the `LengthBasedExampleSelector` to select the examples.
example_selector = LengthBasedExampleSelector(
    # These are the examples is has available to choose from.
    examples=examples, 
    # This is the PromptTemplate being used to format the examples.
    example_prompt=example_prompt, 
    # This is the maximum length that the formatted examples should be.
    # Length is measured by the get_text_length function below.
    max_length=25
    # This is the function used to get the length of a string, which is used
    # to determine which examples to include. It is commented out because
    # it is provided as a default value if none is specified.
    # get_text_length: Callable[[str], int] = lambda x: len(re.split("\n| ", x))
)

# We can now use the `example_selector` to create a `FewShotPromptTemplate`.
dynamic_prompt = FewShotPromptTemplate(
    # We provide an ExampleSelector instead of examples.
    example_selector=example_selector,
    example_prompt=example_prompt,
    prefix="Give the antonym of every input",
    suffix="Word: {input}\nAntonym:",
    input_variables=["input"],
    example_separator="\n\n",
)

# We can now generate a prompt using the `format` method.
print(dynamic_prompt.format(input="big"))
# -> Give the antonym of every input
# ->
# -> Word: happy
# -> Antonym: sad
# ->
# -> Word: tall
# -> Antonym: short
# ->
# -> Word: energetic
# -> Antonym: lethargic
# ->
# -> Word: sunny
# -> Antonym: gloomy
# ->
# -> Word: windy
# -> Antonym: calm
# ->
# -> Word: big
# -> Antonym:
```

逆に、非常に長い入力を渡すと、`LengthBasedExampleSelector`はプロンプトに少ない量のサンプルを選択します。

```py
long_string = "big and huge and massive and large and gigantic and tall and much much much much much bigger than everything else"
print(dynamic_prompt.format(input=long_string))
# -> Give the antonym of every input

# -> Word: happy
# -> Antonym: sad
# ->
# -> Word: big and huge and massive and large and gigantic and tall and much much much much much bigger than everything else
# -> Antonym:
```

LangChainは使用できるいくつかのサンプルセレクターを提供します。これらの使い方の詳細については、[Example Selectors](https://python.langchain.com/en/latest/modules/prompts/example_selectors.html)をご覧ください。

任意の評価指標に基づいてサンプルを選択するカスタムのサンプルセレクターを作成することができます。方法の詳細については、[Creating a custom example selector](https://python.langchain.com/en/latest/modules/prompts/example_selectors/examples/custom_example_selector.html)をご覧ください。
