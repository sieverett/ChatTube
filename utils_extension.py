import pandas as pd
from elevenlabs.client import ElevenLabs
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import AzureChatOpenAI
from langchain_core.output_parsers import StrOutputParser
import os
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import AzureChatOpenAI
import pandas as pd
from langchain_community.document_loaders import DataFrameLoader
from langchain_community.vectorstores import FAISS
import tiktoken
from langchain.vectorstores import FAISS
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import TextLoader
from elevenlabs import Voice, VoiceSettings, save
from elevenlabs.client import ElevenLabs
from langchain_community.embeddings import AzureOpenAIEmbeddings
from langchain.chains.combine_documents.stuff import StuffDocumentsChain
from langchain.chains.llm import LLMChain
from langchain_core.prompts import PromptTemplate
import uuid
from dotenv import load_dotenv
load_dotenv('.env')


def get_docs(presenter, source="transcripts", loader_type='text'):
    if loader_type == 'text':
        loader = TextLoader(
            f'RI/personas/{presenter}/transcripts/transcript.txt')
        docs = loader.load()
    if loader_type == 'df':
        with open(f'RI/personas/{presenter}/transcripts/transcript.txt') as f:
            s = f.read()
        df = pd.DataFrame([s], columns=['transcripts'])
        loader = DataFrameLoader(df, page_content_column=source)
        docs = loader.load()
    return docs


def chunk_docs(docs):
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000, chunk_overlap=200)
    splits = text_splitter.split_documents(docs)
    return splits


def add_meta_data(presenter, docs):
    for doc in docs:
        id = uuid.uuid4()
        doc.metadata = {"id": id.hex, "source": "youtube",
                        "document_name": "transcript", "owner": presenter}
    return docs


def make_vectors(docs):
    embeddings = AzureOpenAIEmbeddings(
        azure_deployment="blue",
        show_progress_bar=True
    )
    vectors = FAISS.from_documents(docs, embeddings)
    return vectors


def save_vectors(presenter, vectors):
    vector_save_path = f'RI/personas/{presenter}/vector_store/'
    os.makedirs(vector_save_path, exist_ok=True)
    vectors.save_local(vector_save_path)


def load_vectors(presenter):
    embeddings = AzureOpenAIEmbeddings(
        azure_deployment="blue",
        chunk_size=10,
    )
    vectors = FAISS.load_local(f'RI/personas/{presenter}/vector_store/',
                               embeddings=embeddings, allow_dangerous_deserialization=True)
    return vectors


def build_vector_store(presenter):
    docs = get_docs(presenter)
    chunks = chunk_docs(docs)
    chunks = add_meta_data(presenter, chunks)
    vectors = make_vectors(chunks)
    save_vectors(presenter, vectors)


def count_tokens(docs):
    encoding = tiktoken.encoding_for_model("gpt-4")
    token_counts = [len(encoding.encode(d.page_content)) for d in docs]
    print('total tokens:', sum(token_counts))
    print('counts:', token_counts)


def get_llm():
    llm = AzureChatOpenAI(
        deployment_name=os.getenv("DEPLOYMENT_NAME"),
        model_name="gpt-4",
        openai_api_key=os.getenv("AZURE_OPENAI_API_KEY"),
        azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
        openai_api_version="2024-02-15-preview"
    )
    return llm


def build_rag_chain(presenter):

    def format_docs(docs):
        return "\n\n".join(doc.page_content for doc in docs)

    template = """Given a question directed to the speaker, 
    give an answer in two sentences at most as if you were that speaker based only on the following context:
    {context}

    Question: {question}

    """
    prompt = ChatPromptTemplate.from_template(template)

    vectors = load_vectors(presenter)
    retriever = vectors.as_retriever()
    llm = get_llm()

    rag_chain = (
        {"context": retriever | format_docs, "question": RunnablePassthrough()}
        | prompt
        | llm
        | StrOutputParser()
    )
    return rag_chain


def ask_rag(question, rag_chain):
    chunk_ = []
    for chunk in rag_chain.stream(question):
        yield chunk
    # return "".join(chunk_)


def get_summary_chain():
    # Define prompt
    prompt_template = """Write a concise summary for each of the following:
    "{text}"
    CONCISE SUMMARY:"""
    prompt = PromptTemplate.from_template(prompt_template)
    llm = get_llm()
    # Define LLM chain
    llm_chain = LLMChain(llm=llm, prompt=prompt)
    # Define StuffDocumentsChain
    stuff_chain = StuffDocumentsChain(
        llm_chain=llm_chain, document_variable_name="text")
    return stuff_chain


def get_summary_text(presenter):
    docs = get_docs(presenter)
    chunks = chunk_docs(docs)
    chunks = add_meta_data(presenter, chunks)
    stuff_chain = get_summary_chain()
    response = stuff_chain.invoke(chunks)
    summary = [i for i in response['output_text'].split("\n\n")]
    summary_text = "\n".join(summary)
    with open(f'RI/personas/{presenter}/transcripts/summary.txt', 'w') as f:
        f.write(summary_text)


# def list_cloned_voices():
#     # set_api_key(os.getenv("ELEVEN_API_KEY"))
#     client = ElevenLabs(api_key=os.getenv("ELEVEN_API_KEY"))
#     result = client.voices.get_all()
#     voice_dict = {i.name: i.voice_id for i in [
#         v for v in result.voices] if i.category == 'cloned'}
#     return voice_dict


# def speak(presenter, text):
#     client = ElevenLabs()
#     voice_dict = list_cloned_voices()
#     voice_id = voice_dict[presenter]
#     audio = client.generate(
#         text=text,
#         voice=Voice(
#             voice_id=voice_id,
#             settings=VoiceSettings(
#                 stability=0.71, similarity_boost=0.5, style=0.0, use_speaker_boost=True)
#         )
#     )
#     cloned_audio_save_path = f'RI/personas/{presenter}/cloned/audio_cloned_{uuid.uuid4().hex}.wav'
#     save(audio, cloned_audio_save_path)
#     return cloned_audio_save_path
