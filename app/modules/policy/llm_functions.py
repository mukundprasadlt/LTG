from langchain_openai import AzureOpenAIEmbeddings, AzureChatOpenAI
from app.configs.settings import settings


def init_azure_llm():
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

def get_openai_embedding(array):
    embeddings = AzureOpenAIEmbeddings(
        azure_deployment="text-embedding-3-large",
        api_key = settings.common_secrets.azure_openai_api_key,
        azure_endpoint = settings.common_secrets.azure_openai_endpoint,
    )

    # Generate embeddings for each document
    # embedding = embeddings.embed_query(text)
    embedding = embeddings.embed_documents(array)
    return embedding