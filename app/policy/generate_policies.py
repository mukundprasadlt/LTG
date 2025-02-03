"""The Policy takes a zipped file containing Standard's JSON (2-5) as input. The API splits the controls from the standard and applies an embedding process. It then performs Cosine Similarity on the controls' vector and merges the controls' content, ultimately generating a new set of policies as output."""

# AUTOGENERATED! DO NOT EDIT! File to edit: ../../nbs/APIs/01_generate_policy.ipynb.

# %% auto 0
__all__ = ['extract_headings_using_langchain', 'policy_standard_processor']

# %% ../../nbs/APIs/01_generate_policy.ipynb 2
from .helper.llm_functions import get_openai_embedding, init_azure_llm
from .helper.tools import apply_markdown, apply_markdown_gap, merge_sets, create_policy_markdown
from .helper.prompts import policy_prompt_template, controls_prompt_template, policy_gap_prompt_template, policy_gap_output
from .generate_controls import standard_processor
import json
import concurrent.futures


# %% ../../nbs/APIs/01_generate_policy.ipynb 3
# Function to extract headings using LangChain
def extract_headings_using_langchain(
    llm, # LLM Object
    Domain, # `Domain` Object
    domain_name, #  Domain name
    region,industry
):
    prompt = policy_prompt_template.format(current_input=Domain, domain_name=domain_name, region=region,industry=industry)
    # json_llm = llm.bind(response_format={"type": "json_object"})
    response = llm.invoke(prompt)
    return response

# %% ../../nbs/APIs/01_generate_policy.ipynb 4
def policy_standard_processor(
    input_standards:list, # List of standards
    region:str,
    industry:str
)->list: # list of policies of similar domains
    "Generate policies for the similar domains"
    print('policy api process started')
    llm = init_azure_llm()
    standards = standard_processor(input_standards)
    updated_policies = []
    for standard in standards:
        for control in standard['Controls']:
            # print("len(control['id'].split('-'))",len(control['id'].split('-')))
            if len(control['id'].split('-'))>1:
                updated_policies.append(standard)
                break
    # print("updated_policies_count=",len(updated_policies))
    def process_policy(policy):
        m_Domain_Controls = create_policy_markdown(policy)
        response = extract_headings_using_langchain(llm, m_Domain_Controls, policy['domain'],region,industry)
        response_json = (response.content)
        return response_json

    with concurrent.futures.ThreadPoolExecutor() as executor:
        response_json_list = list(executor.map(process_policy, updated_policies))
    print('policy api process completed')
    return response_json_list  #list
