import os
os.environ['ENVIRONMENT'] = "test"
import numpy as np
import json
import os, sys
import pytest
from unittest.mock import patch, MagicMock
path1 = "__file__".split("tests")[0]
sys.path.append(path1)
from app.modules.standard_processor import (
    apply_markdown,
    apply_markdown_gap,
    get_openai_embedding,
    merge_sets,
    extract_headings_using_langchain,
    create_policy_markdown,
    combine_similar_controls,
    extract_controls_gap,
    merge_controls_using_LLM,
    merge_controls,
    standard_processor,
    policy_standard_processor,
    controls_gap_processor
)

sample_control = {
    "DomainId": "1",
    "Controls": [{"controlId": "101", "name": "Test Control", "description": "A test description"}]
}

sample_gap_control = {
    "domain_number": "1",
    "controls": [{"control_number": "101", "control_name": "Gap Control", "control_description": "Gap description"}]
}

# 1. Test apply_markdown
def test_apply_markdown():
    result = apply_markdown(sample_control, 1)
    assert result[0] == "**1:1:101 - Test Control**: A test description"
    assert sample_control["Controls"][0]["markdown"] == result[0]

# 2. Test apply_markdown_gap
def test_apply_markdown_gap():
    result = apply_markdown_gap(sample_gap_control, 1)
    assert result[0] == "**1:1:101 - Gap Control**: Gap description"
    assert sample_gap_control["controls"][0]["markdown"] == result[0]

# # 3. Test get_openai_embedding
# @patch("app.modules.standard_processor.AzureOpenAIEmbeddings")
# def test_get_openai_embedding(mock_embeddings):
#     mock_embeddings_instance = mock_embeddings.return_value
#     mock_embeddings_instance.embed_documents.return_value = np.array([[0.1, 0.2], [0.3, 0.4]])
#     result = get_openai_embedding(["test text 1", "test text 2"])
#     assert result.shape == (2, 2)
#     mock_embeddings_instance.embed_documents.assert_called_once()

# 4. Test merge_sets
def test_merge_sets():
    setA = {1, 2, 3}
    setB = [{2, 4}, {5}]
    result = merge_sets(setA, setB)
    assert result[0] == {1, 2, 3, 4}

# # 5. Test extract_headings_using_langchain
# @patch("app.modules.standard_processor.AzureChatOpenAI")
# def test_extract_headings_using_langchain(mock_llm):
#     mock_llm_instance = mock_llm.return_value
#     mock_response = MagicMock()
#     mock_response.content = json.dumps({"heading": "Test Heading"})
#     mock_llm_instance.bind.return_value.invoke.return_value = mock_response
#     result = extract_headings_using_langchain(mock_llm_instance, "Domain", "Test Domain")
#     assert json.loads(result.content) == {"heading": "Test Heading"}

# 6. Test create_policy_markdown
def test_create_policy_markdown():
    test_obj = {"domain": "Test Domain", "Controls": [{"id": "1", "name": "Control Name", "description": "Description"}]}
    result = create_policy_markdown(test_obj)
    assert "Test Domain" in result
    assert "Control Name" in result

# 7. Test combine_similar_controls
@patch("app.modules.standard_processor.get_openai_embedding")
def test_combine_similar_controls(mock_embedding):
    mock_embedding.return_value = np.array([[0.1, 0.9], [0.9, 0.1]])
    standards = [
        {
            "Controls": [
                {
                    "DomainId": "1",
                    "Domain": "Sample Domain",
                    "Controls": [
                        {
                            "controlId": "1",
                            "markdown": "control text",
                            "name": "Sample Control Name",
                            "description": "Sample Control Description"
                        }
                    ]
                }
            ]
        }
    ]
    result = combine_similar_controls(standards, 0.8)
    assert isinstance(result, list)

# 8. Test extract_controls_gap
@patch("app.modules.standard_processor.get_openai_embedding")
def test_extract_controls_gap(mock_embedding):
    mock_embedding.return_value = np.array([[0.1, 0.2], [0.3, 0.4]])
    input_standards = [{
        "source_standard_name": "Source Standard",
        "target_standard_name": "Target Standard",
        "source_standard_info": [
            {
                "domain_number": "1",
                "domain_name": "Source Domain",
                "controls": [
                    {
                        "control_number": "1",
                        "control_name": "Source Control",
                        "control_description": "Source description"
                    }
                ]
            }
        ],
        "target_standard_info": [
            {
                "domain_number": "2",
                "domain_name": "Target Domain",
                "controls": [
                    {
                        "control_number": "2",
                        "control_name": "Target Control",
                        "control_description": "Target description"
                    }
                ]
            }
        ]
    }]
    
    result = extract_controls_gap(input_standards)
    assert result["status"] == "success"
    assert "comparison_matrix" in result

# # 9. Test merge_controls_using_LLM
# @patch("app.modules.standard_processor.AzureChatOpenAI")
# def test_merge_controls_using_LLM(mock_llm):
#     mock_llm_instance = mock_llm.return_value
#     mock_llm_instance.invoke.return_value = MagicMock(content="Merged description")
#     result = merge_controls_using_LLM(mock_llm_instance, "Sample text")
#     assert result == "Merged description"

# 10. Test merge_controls
@patch("app.modules.standard_processor.merge_controls_using_LLM")
def test_merge_controls(mock_merge):
    mock_merge.return_value = "Merged description"
    llm = MagicMock()
    merged_list = [{"Controls": [{"id": "1-2", "desc": ["Desc1", "Desc2"]}, {"id": "3", "name": "Control 3"}]}]
    result = merge_controls(llm, merged_list)
    assert result[0]["Controls"][0]["description"] == "Merged description"
    assert "desc" not in result[0]["Controls"][0]

# # 11. Test standard_processor
# @patch("app.modules.standard_processor.combine_similar_controls")
# @patch("app.modules.standard_processor.merge_controls")
# # @patch("app.modules.standard_processor.init_llm")
# def test_standard_processor(mock_init_llm, mock_merge_controls, mock_combine_controls):
#     mock_init_llm.return_value = MagicMock()
#     mock_combine_controls.return_value = [{"Controls": [{"id": "1", "desc": ["Desc1"]}]}]
#     mock_merge_controls.return_value = [{"Controls": [{"id": "1", "description": "Desc1"}]}]
#     result = standard_processor([{"Controls": []}])
#     assert isinstance(result, list)
#     assert result[0]["Controls"][0]["description"] == "Desc1"

# # 12. Test policy_standard_processor
# @patch("app.modules.standard_processor.standard_processor")
# @patch("app.modules.standard_processor.extract_headings_using_langchain")
# # @patch("app.modules.standard_processor.init_llm")
# def test_policy_standard_processor(mock_init_llm, mock_extract, mock_standard_proc):
#     mock_init_llm.return_value = MagicMock()
#     mock_standard_proc.return_value = [
#         {
#             "domain": "Test Domain",
#             "Controls": [
#                 {
#                     "id": "1-2",
#                     "name": "Sample Control Name",
#                     "description": "Sample Control Description"
#                 }
#             ]
#         }
#     ]
#     mock_response = MagicMock()
#     mock_response.content = json.dumps({"heading": "Extracted Heading"})
#     mock_extract.return_value = mock_response
#     result = policy_standard_processor([{"Controls": []}])
#     assert isinstance(result, list)
#     assert result[0] == {"heading": "Extracted Heading"}

# 13. Test controls_gap_processor
@patch("app.modules.standard_processor.extract_controls_gap")
def test_controls_gap_processor(mock_extract_gap):
    mock_extract_gap.return_value = {"status": "success"}
    result = controls_gap_processor([{"source_standard_name": "Test", "target_standard_name": "Test"}])
    assert result["status"] == "success"