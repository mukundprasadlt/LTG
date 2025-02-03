import numpy as np
from sklearn.metrics.pairwise import cosine_distances
import json
from app.configs.settings import settings
import os
os.environ['AZURE_OPENAI_API_KEY'] = settings.common_secrets.azure_openai_api_key
os.environ['AZURE_OPENAI_ENDPOINT'] = settings.common_secrets.azure_openai_endpoint
os.environ['AZURE_OPENAI_DEPLOYMENT_ID'] = settings.common_secrets.azure_openai_deployment_id
os.environ['AZURE_OPENAI_API_VERSION'] = settings.common_secrets.azure_openai_api_version
os.environ['OPENAI_ORG'] = settings.common_secrets.openai_org
os.environ['OPENAI_API_KEY'] = settings.common_secrets.openai_api_key
# from langchain_openai import AzureChatOpenAI
# from langchain.prompts import PromptTemplate
# from langchain_openai import AzureOpenAIEmbeddings
import concurrent.futures

from app.modules.policy.prompts import policy_prompt_template, controls_prompt_template, policy_gap_prompt_template, policy_gap_output
from app.modules.policy.llm_functions import get_openai_embedding, init_azure_llm
from app.modules.policy.tools import apply_markdown, apply_markdown_gap, merge_sets, create_policy_markdown

##
## FUNCTIONS ##
##


# Function to extract headings using LangChain
def extract_headings_using_langchain(llm,Domain,domain_name):
    prompt = policy_prompt_template.format(current_input=Domain, domain_name=domain_name)
    json_llm = llm.bind(response_format={"type": "json_object"})
    response = json_llm.invoke(prompt)
    return response

    return markdown_output

##
## PROCESSOR ##
##
def combine_similar_controls(standards, threshold=0.7): 
    # Apply markdown to all standards
    # standards = load_standards()
    for idx, standard in enumerate(standards):
        for domain in standard['Controls']:
            domain['Markdown'] = apply_markdown(domain, idx)
    arrays = [standard['Controls'] for standard in standards]
    unique_items = []
    array_indices = []

    for array_index, sublist in enumerate(arrays):
        unique_items.extend(sublist)
        array_indices.extend([array_index] * len(sublist))
    ids = [item['DomainId'] for item in unique_items]  # Define 'ids' here
    # ids = [f"{array_indices[index]}:{item['DomainId']}" for index, item in enumerate(unique_items)]  # Define 'ids' here


    # Extract all controls and their associated domain IDs
    all_controls = []
    control_domain_ids = [] 
    for item in unique_items:
        for control in item['Controls']:
            all_controls.append(control['markdown'])
            control_domain_ids.append(control['controlId'])
    # print(all_controls)
    # Get embeddings for each control
    embeddings = np.array(get_openai_embedding(all_controls))

    # Compute cosine distances
    cosine_dist = cosine_distances(embeddings)

    # print("cosine_dist=",cosine_dist)
    # Create a mapping from control index to its domain ID
    cosine_dist2 = cosine_dist

    ### Applying triangular indices to reduce cost
    cosine_dist2 = np.triu(cosine_dist,)
    # Get the lower triangular indices (excluding the diagonal)
    lower_triangular_indices = np.tril_indices_from(cosine_dist2, k=-1)

    # Replace elements at these indices with '1'
    cosine_dist2[lower_triangular_indices] = '1'

    #make diagonal 1 of cosine_dist2 matrix
    np.fill_diagonal(cosine_dist2, 1)
    cosine_dist = cosine_dist2

    control_to_domain = {i: control_domain_ids[i] for i in range(len(all_controls))}
    
    # Identify pairs of controls with cosine similarity above the threshold
    similar_pairs = []

    # for i, j in product(range(len(cosine_dist)), range(len(cosine_dist))):
    already_matched1 = []
    already_matched2 = []
    for i in range(len(cosine_dist)):
        icnt = 0
        for j in range(len(cosine_dist)):
            if i != j and cosine_dist[i][j] <= 1 - threshold and j not in already_matched2: #and i not in already_matched1: 
                domain1 = control_to_domain[i]
                domain2 = control_to_domain[j]
                i_d_c1 =  domain1.split(":")
                i_d_c2 =  domain2.split(":")
                
                if i_d_c1[0] != i_d_c2[0]:
                    if icnt >=int(i_d_c2[0]): 
                        continue
                    similar_pairs.append((domain1, domain2))
                    already_matched1.append(i)
                    already_matched2.append(j)
                    icnt = int(i_d_c2[0])

    # print("similar_pairs=",similar_pairs)
    # Create a graph where nodes are domain IDs and edges represent similarity
    graph = {domain_id: set() for domain_id in ids}
    for domain1, domain2 in similar_pairs:
        d1 = domain1.split(":")
        d1 = d1[0] + ':' + d1[1]
        d2 = domain2.split(":")
        d2 = d2[0] + ':' + d2[1]
        graph[d1].add(d2)
        graph[d2].add(d1)
    # Find connected components in the graph
    visited = set()
    clusters = []
    for domain_id in ids:
        if domain_id not in visited:
            cluster = set()
            stack = [domain_id]
            while stack:
                current_domain = stack.pop()
                if current_domain not in visited:
                    visited.add(current_domain)
                    cluster.add(current_domain)
                    stack.extend(graph[current_domain])
            clusters.append(cluster)
    # print("clusters=",clusters)

    # Merge domains and controls within each cluster
    merged_list = []
    merged_set = []
    for cluster in clusters:

        merged_item = {
            'id': '-'.join(map(str, cluster)),
            'domain': '-'.join(item['Domain'] for item in unique_items if item['DomainId'] in cluster),
            'Controls': []
        }

        # Gather and merge controls, considering cosine similarity
        seen_control_names = []
        merged_controls = [] # To track merged control IDs
        for d1, d2 in similar_pairs:
            domain1 =  d1[:d1.rfind(":")]
            domain2 =  d2[:d2.rfind(":")]
            if domain1 in cluster and domain2 in cluster:
                control1=next((c for item in unique_items if item['DomainId'] == domain1 for c in item['Controls'] if c['controlId'] == d1), {})
                control2=next((c for item in unique_items if item['DomainId'] == domain2 for c in item['Controls'] if c['controlId'] == d2), {})
                if control1 and control2:
                    control_names_set = set({control1['controlId'], control2['controlId']})
                    control_markdown_set = set({control1['markdown'], control2['markdown']})
                    if control_names_set not in seen_control_names:
                        merged_item['Controls'].append({
                            'id': f"{control1['controlId']}-{control2['controlId']}",
                            # 'name': '-'.join(sorted(control_markdown_set)),
                            'name': control1['name'] +'-'+control2['name'],
                            'desc': [control1['markdown'], control2['markdown']]
                        })

                        if(len(seen_control_names)>0):
                            # seen_control_names=merge_sets(control_names_set,seen_control_names)
                            seen_control_names.append(control_names_set)
                        else:
                            seen_control_names.append(control_names_set)
                        merged_controls.append(control1['controlId'])
                        merged_controls.append(control2['controlId'])
        merged_set.append(seen_control_names)
        # Add unmerged controls
        for domain_id in cluster:
            for control in next((item for item in unique_items if item['DomainId'] == domain_id), {})['Controls']:
                if control['controlId'] not in merged_controls: # Check if control was already merged
                    merged_item['Controls'].append({
                        'id': control['controlId'],
                        'name': control['name'],
                        'description': control['description']
                    })
        merged_list.append(merged_item)    
    return merged_list

# Function to extract Controls GAP
def extract_controls_gap(input_standards):
    input_standards = input_standards[0]
    standards = [
        {
            "StandardName": input_standards['source_standard_name'],
            "controls": input_standards['source_standard_info']
        },
        {
            "StandardName": input_standards['target_standard_name'],
            "controls": input_standards['target_standard_info']
        }
    ]
     # Apply markdown to all standards
    # standards = load_standards()
    
    for idx, standard in enumerate(standards):
        for domain in standard["controls"]:
            domain['Markdown'] = apply_markdown_gap(domain, idx)
    arrays = [standard['controls'] for standard in standards]

    # def merge_arrays(arrays, threshold=0.5): 
    unique_items = []
    array_indices = []

    for array_index, sublist in enumerate(arrays):
        unique_items.extend(sublist)
        array_indices.extend([array_index] * len(sublist))

    # Extract all controls and their associated domain IDs
    all_controls = []
    all_controls_details = {}
    control_domain_ids = [] 
    for item in unique_items:
        for control in item['controls']:
            all_controls.append(control['markdown'])
            all_controls_details[control['control_number']]={'domain': f"{item['domain_number'].split(':')[1]} - {item['domain_name']}", 'control': f"{control['control_number'].split(':')[2]} - {control['control_name']}"}
            control_domain_ids.append(control['control_number'])
    # Get embeddings for each control
    embeddings = np.array(get_openai_embedding(all_controls))

    # Compute cosine distances
    cosine_dist = cosine_distances(embeddings)

    # Create a mapping from control index to its domain ID
    cosine_dist2 = cosine_dist

    cosine_dist2 = np.triu(cosine_dist,)
    # Get the lower triangular indices (excluding the diagonal)
    lower_triangular_indices = np.tril_indices_from(cosine_dist2, k=-1)

    # Replace elements at these indices with '1'
    cosine_dist2[lower_triangular_indices] = '1'

    #make diagonal 1 of cosine_dist2 matrix
    np.fill_diagonal(cosine_dist2, 1)

    cosine_dist = cosine_dist2

    threshold = 0.5
    control_to_domain = {i: control_domain_ids[i] for i in range(len(all_controls))}
    similar_pairs = []
    already_matched1 = []
    already_matched2 = []
    matched_controls = set()
    for i in range(len(cosine_dist)):
        icnt = 0
        for j in range(len(cosine_dist)):
            if i != j and cosine_dist[i][j] <= 1 - threshold and j not in already_matched2 and i not in already_matched1: 

                domain1 = control_to_domain[i]
                domain2 = control_to_domain[j]
                i_d_c1 =  domain1.split(":")
                i_d_c2 =  domain2.split(":")
                if i_d_c1[0] != i_d_c2[0]:
                    if icnt >=int(i_d_c2[0]): 
                        continue
                    similar_pairs.append((domain1, domain2, 1 - cosine_dist[i][j]))
                    matched_controls.add(domain1)
                    matched_controls.add(domain2)
                    already_matched1.append(i)
                    already_matched2.append(j)
                    icnt = int(i_d_c2[0])

    matched_controls_high = [pair for pair in similar_pairs if pair[2] >= 0.7]
    matched_controls_gap = [pair for pair in similar_pairs if pair[2] < 0.7]

    # print("Matched Controls with Cosine Value >= 0.7:", matched_controls_high)
    # print("Matched Controls in GAP State:", matched_controls_high)

    unmatched_controls = [control for control in control_domain_ids if control not in matched_controls]
    # print("Not Matched Controls State:", unmatched_controls)

    comparison_result = {
        "status": "success",
        "source_standard_name": standards[0]['StandardName'],
        "target_standard_name": standards[1]['StandardName'],
        "comparison_matrix": {
            "controls": []
        }
    }

    for source_control, target_control, similarity in matched_controls_high:
        source_control = all_controls_details[source_control]
        target_control = all_controls_details[target_control]
        comparison_result["comparison_matrix"]["controls"].append({
            "source_control": source_control['control'],
            "target_control": target_control['control'],
            "source_domain": source_control['domain'],
            "target_domain": target_control['domain'],
            "status": "match"
        })

    for source_control, target_control, similarity in matched_controls_gap:
        source_control = all_controls_details[source_control]
        target_control = all_controls_details[target_control]
        comparison_result["comparison_matrix"]["controls"].append({
            "source_control": source_control['control'],
            "target_control": target_control['control'],
            "source_domain": source_control['domain'],
            "target_domain": target_control['domain'],
            "status": "gap"
        })

    for control in unmatched_controls:
        s_control = all_controls_details[control]
        control = control.split(":")
        source_control = []
        target_control = []
        if control[0] == "0":
            source_control = control
        else:
            target_control = control
        comparison_result["comparison_matrix"]["controls"].append({
            "source_control": s_control['control'] if len(source_control) > 2 else "",
            "target_control": s_control['control'] if len(target_control) > 2 else "",
            "source_domain": s_control['domain'] if len(source_control) > 1 else "",
            "target_domain": s_control['domain'] if len(target_control) > 1 else "",
            "missing_source": control[0] == "1",
            "status": "missing"
        })
    return comparison_result

# Function to extract headings using LangChain
def merge_controls_using_LLM(llm, text):
    prompt = controls_prompt_template.format(current_input=text)
    response = llm.invoke(prompt)
    return response.content

def merge_controls(llm, merged_list):
    # for each merged_list
    # find the controls that have '-' in their id and merge them
    for merged_item in merged_list:
        for control in merged_item['Controls']:
            if '-' in control['id']:
                control['description'] = merge_controls_using_LLM(llm, control['desc'])
                del control['desc']
    return merged_list

def standard_processor(standards):
    print('control api process started')
    llm = init_azure_llm()
    merged_list = combine_similar_controls(standards)
    merged_controls = merge_controls(llm, merged_list)
    print('control api process completed')
    return merged_controls

def policy_standard_processor(input_standards):
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
        response = extract_headings_using_langchain(llm, m_Domain_Controls, policy['domain'])
        response_json = json.loads(response.content)
        return response_json

    with concurrent.futures.ThreadPoolExecutor() as executor:
        response_json_list = list(executor.map(process_policy, updated_policies))
    print('policy api process completed')
    return response_json_list  #list

def controls_gap_processor(input_standards):
    print('control gap api process started')
    comparison_result = extract_controls_gap(input_standards)
    print('control gap api process completed')
    return comparison_result


##
## POLICY GAP PROCESSOR ##
##

def generate_policy_gap(llm,domain,policy,standard_name):
    ONE_DOMAIN = domain
    ONE_DOMAIN['standard_name']=standard_name
    ONE_DOMAIN = f"""
        ```json 
        {str(ONE_DOMAIN)}
        ```"""
    input_policy_str = f"""
        ```json
        {str(policy)}
        ```"""
    
    prompt = policy_gap_prompt_template.format(input_policy=input_policy_str,input_standard=ONE_DOMAIN,output_str=policy_gap_output)
    response = llm.bind(response_format={"type": "json_object"}).invoke(prompt)
    return response

def policy_gap_summary(llm, policy_gap_resp):
    # Combine gap_analysis descriptions
    combined_description = " ".join([json.loads(resp.content)['gap_analysis']['description'] for resp in policy_gap_resp])

    # Summarize the combined description using llm
    summary_response = llm.invoke(f"Summarize the following text: {combined_description}")
    summary_description = summary_response.content.strip()

    # Combine missing_controls and matching_controls
    combined_missing_controls = []
    combined_matching_controls = []

    for resp in policy_gap_resp:
        content = json.loads(resp.content)
        combined_missing_controls.extend(content['controls_comparison']['missing_controls'])
        combined_matching_controls.extend(content['controls_comparison']['matching_controls'])

    # Create the combined output
    combined_output = {
        "status": "success",
        "gap_analysis": {
            "description": summary_description
        },
        "controls_comparison": {
            "missing_controls": combined_missing_controls,
            "matching_controls": combined_matching_controls
        }
    }
    return combined_output

def policy_gap_processor(input_data):
    policy_gap_resp = []
    print('control api process started')
    llm = init_azure_llm()
    [input_policy, input_standard] = input_data
    standard_name = input_standard['standard_name']
    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = [executor.submit(generate_policy_gap, llm,domain,input_policy,standard_name) for domain in input_standard['domains']]
        for future in concurrent.futures.as_completed(futures):
            policy_gap_resp.append(future.result())

    combined_output = policy_gap_summary(llm, policy_gap_resp)

    return combined_output