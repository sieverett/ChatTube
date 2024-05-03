from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import AzureChatOpenAI
from langchain_core.output_parsers import StrOutputParser
from dotenv import load_dotenv
import os
res = load_dotenv('.env', override=True)
r = os.getenv("DEPLOYMENT_NAME")
print("loaded env:", res, r)


def codeit(line, cell):
    template = """Write some python code to solve the user's problem. 
    Return only python code in Markdown format, e.g.:
    ```python
    ....
    ```
    Do not include any other text, example or code.
    """
    prompt = ChatPromptTemplate.from_messages(
        [("system", template), ("human", "{input}")])
    model = AzureChatOpenAI(
        deployment_name=os.getenv("DEPLOYMENT_NAME"),
        model_name="gpt-4",
        openai_api_key=os.getenv("AZURE_OPENAI_API_KEY"),
        azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
        openai_api_version="2024-02-15-preview"
    )

    chain = prompt | model | StrOutputParser()
    # sio = StringIO(cell)
    # df=pd.read_csv(sio)*10
    res = chain.invoke({"input": cell})
    print(res)
    _, after = res.split("```python")
    with open('code', 'w') as f:
        f.write(after.split("```")[0])


def load_ipython_extension(ipython):
    """This function is called when the extension is
    loaded. It accepts an IPython InteractiveShell
    instance. We can register the magic with the
    `register_magic_function` method of the shell
    instance."""
    ipython.register_magic_function(codeit, 'cell')
