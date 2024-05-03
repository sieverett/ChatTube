from IPython import get_ipython
import pandas as pd
from io import StringIO
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from langchain_openai import AzureChatOpenAI
from langchain_core.output_parsers import StrOutputParser
from dotenv import load_dotenv
import os
res = load_dotenv('.env', override=True)
print("loaded env:", res)
print(os.getenv("AZURE_OPENAI_ENDPOINT"))


def make_cell_print_results(res):
    ipython = get_ipython()
    # ipython.set_next_input(res) > sets the next cell to be executed to res
    # ipython.run_cell(code)
    ipython.run_cell_magic("markdown", "", res)


def chatit(line, cell):
    template = """You are an AI expert and experienced international development consultant. 
    You try to resolve the user's problem. Start by providing an overview of the answer.
    Use concrete examples where possible.
    When you do not know the answer, you ask for more information.
    Return text in Markdown format: 
    <<markdown>>
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
    # _, after = res.split("```python")
    with open('chat', 'w', encoding='utf-8') as f:
        f.write(res)
    if '@@' in cell:
        make_cell_print_results('**Prompt:** ```\n' +
                                cell.replace('@@', '')+'\n```')
    make_cell_print_results(res)


def load_ipython_extension(ipython):
    """This function is called when the extension is
    loaded. It accepts an IPython InteractiveShell
    instance. We can register the magic with the
    `register_magic_function` method of the shell
    instance."""
    ipython.register_magic_function(chatit, 'cell')
