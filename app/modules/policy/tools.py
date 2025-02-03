##
## FUNCTIONS ##
##

# Function: create markdown of controls
def apply_markdown(f_obj,index):
    f_obj['DomainId'] = f'{index}:{f_obj["DomainId"]}'
    markdown_output = []
    for control in f_obj['Controls']:
        control['controlId'] = f_obj['DomainId']+':'+control['controlId']
        markdown_output.append(f"**{control['controlId']} - {control['name']}**: {control['description']}")
        control['markdown'] = f"**{control['controlId']} - {control['name']}**: {control['description']}"
    return markdown_output

# Function: create markdown of controls GAP
def apply_markdown_gap(f_obj,index):
    f_obj['domain_number'] = f'{index}:{f_obj["domain_number"]}'
    markdown_output = []
    for control in f_obj['controls']:
        control['control_number'] = f_obj['domain_number']+':'+control['control_number']
        markdown_output.append(f"**{control['control_number']} - {control['control_name']}**: {control['control_description']}")
        control['markdown'] = f"**{control['control_number']} - {control['control_name']}**: {control['control_description']}"
    return markdown_output

# Function: merge sets
def merge_sets(setA, setB):
    merged_set = setA.copy()
    result = []

    for subset in setB:
        if merged_set & subset:
            merged_set |= subset
        else:
            result.append(subset)

    result.insert(0, merged_set)
    return result

# Function to create markdown for policy
def create_policy_markdown(f_obj):
    markdown_output = f"""
    ### Domain: {f_obj['domain']}
    #### Controls:
    """
    for control in f_obj['Controls']:
        markdown_output += f"""
    - **Control ID**: {control['id']}
      - **Name**: {control['name']}
      - **Description**: {control['description']}
    """
    return markdown_output