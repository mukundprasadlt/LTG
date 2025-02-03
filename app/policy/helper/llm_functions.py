"""Helper functions for LLM Models"""

# AUTOGENERATED! DO NOT EDIT! File to edit: ../../../nbs/Helper/llm_functions.ipynb.

# %% auto 0
__all__ = ['init_azure_openai_llm', 'init_ollama_llm', 'init_azure_llm', 'get_ollama_embedding', 'get_azure_openai_embedding',
           'get_openai_embedding']

# %% ../../../nbs/Helper/llm_functions.ipynb 2
from langchain_openai import AzureOpenAIEmbeddings, AzureChatOpenAI
from ...configs.settings import settings
from langchain_ollama import ChatOllama, OllamaEmbeddings

# %% ../../../nbs/Helper/llm_functions.ipynb 3
def init_azure_openai_llm():
    "Azure OpenAI gpt-4o model instance"
    llm = AzureChatOpenAI(
        openai_api_version = settings.common_secrets.azure_openai_api_version,
        azure_deployment = settings.common_secrets.azure_openai_deployment_id,
        api_key = settings.common_secrets.azure_openai_api_key,
        azure_endpoint = settings.common_secrets.azure_openai_endpoint,
        temperature=0,
        max_tokens=4096,
        timeout=None,
        max_retries=2,
    )
    return llm

# %% ../../../nbs/Helper/llm_functions.ipynb 5
def init_ollama_llm():
    "Ollama Llama3.2 model instance"
    # llm = ChatOllama(model="llama3.2")
    llm = ChatOllama(
        base_url="http://135.232.123.7:11434",
        model="llama3.3:70b-instruct-q8_0"
    )
    return llm  


# %% ../../../nbs/Helper/llm_functions.ipynb 7
# TODO: change the function name with init_llm(Ollama,Azure)
def init_azure_llm(type = 'Ollama'):
    "Azure OpenAI gpt-4o model instance"
    if type == 'Ollama':
        return init_ollama_llm()
    if type == 'Azure':
        return init_azure_openai_llm()
    return None

# %% ../../../nbs/Helper/llm_functions.ipynb 9
def get_ollama_embedding(array):
    # embeddings = OllamaEmbeddings(
    #     model="llama3.2"
    # )
    embeddings = OllamaEmbeddings(
        base_url="http://135.232.123.7:11434",
        model="llama3.3:70b-instruct-q8_0"
    )
    # Generate embeddings for each document
    embedding = embeddings.embed_documents(array)
    # embedding = embeddings.embed_documents(array)
    return embedding

# %% ../../../nbs/Helper/llm_functions.ipynb 11
def get_azure_openai_embedding(array):#list of string
    "Using Azure OpenAI text-embedding-3-large model for embeddings"
    embeddings = AzureOpenAIEmbeddings(
        azure_deployment="text-embedding-3-large",
        api_key = settings.common_secrets.azure_openai_api_key,
        azure_endpoint = settings.common_secrets.azure_openai_endpoint,
    )

    # Generate embeddings for each document
    # embedding = embeddings.embed_query(text)
    embedding = embeddings.embed_documents(array)
    return embedding

# %% ../../../nbs/Helper/llm_functions.ipynb 16
def get_openai_embedding(array,type = 'Ollama'):#Either 'Azure' or 'Ollama'
    """Retrieve the embedding from either Azure OpenAI or Ollama."""
    if type == 'Ollama':
        return get_ollama_embedding(array)
    if type == 'Azure':
        return get_azure_openai_embedding(array)
    return None
