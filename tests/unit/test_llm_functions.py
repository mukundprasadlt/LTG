import os
os.environ['ENVIRONMENT'] = "test"
import pytest
from unittest.mock import patch, MagicMock
import sys, os
path1 = "__file__".split("tests")[0]
sys.path.append(path1)
from app.modules.policy.llm_functions import init_azure_llm, get_openai_embedding
from app.configs.settings import settings


# Test init_azure_llm
@patch("app.modules.policy.llm_functions.AzureChatOpenAI")
def test_init_azure_llm(mock_azure_chat_openai):
    mock_llm_instance = MagicMock()
    mock_azure_chat_openai.return_value = mock_llm_instance
    llm = init_azure_llm()
    mock_azure_chat_openai.assert_called_once_with(
        openai_api_version=settings.common_secrets.azure_openai_api_version,
        azure_deployment=settings.common_secrets.azure_openai_deployment_id,
        api_key=settings.common_secrets.azure_openai_api_key,
        azure_endpoint=settings.common_secrets.azure_openai_endpoint,
        temperature=0,
        max_tokens=4096,
        timeout=None,
        max_retries=2
    )
    assert llm == mock_llm_instance


# Test get_openai_embedding
@patch("app.modules.policy.llm_functions.AzureOpenAIEmbeddings")
def test_get_openai_embedding(mock_azure_embeddings):
    mock_embeddings_instance = MagicMock()
    mock_embeddings_instance.embed_documents.return_value = [[0.1, 0.2, 0.3], [0.4, 0.5, 0.6]]
    mock_azure_embeddings.return_value = mock_embeddings_instance
    sample_data = ["Text 1", "Text 2"]
    embedding = get_openai_embedding(sample_data)
    mock_azure_embeddings.assert_called_once_with(
        azure_deployment="text-embedding-3-large",
        api_key=settings.common_secrets.azure_openai_api_key,
        azure_endpoint=settings.common_secrets.azure_openai_endpoint,
    )
    mock_embeddings_instance.embed_documents.assert_called_once_with(sample_data)
    assert embedding == [[0.1, 0.2, 0.3], [0.4, 0.5, 0.6]]  