import streamlit as st
import zipfile
import os
import json
import pandas as pd
import requests
from datetime import datetime
from typing import List, Dict, Any
# from sentence_transformers import SentenceTransformer

# Constants
OLLAMA_API_URL = "http://135.232.123.7:11434/api/generate"
MODEL_NAME = "llama3.3:70b-instruct-q8_0"

# --- STREAMLIT UI ---
st.title("Lock Threat Genius")

# Step 1: Upload ZIP file containing CSVs
uploaded_file = st.file_uploader("Upload a ZIP file containing CSV files", type="zip")

if uploaded_file:
    with zipfile.ZipFile(uploaded_file, "r") as zip_ref:
        zip_ref.extractall("temp_data")

    # Convert CSVs to JSON
    json_data = {}
    for filename in os.listdir("temp_data"):
        if filename.endswith(".csv"):
            df = pd.read_csv(os.path.join("temp_data", filename))
            json_data[filename.replace(".csv", "")] = df.to_dict(orient="records")

    st.session_state["json_files"] = json_data

# Buttons for Generating Controls and Policies
col1, col2 = st.columns(2)
if col1.button("Generate Controls"):
    st.session_state["mode"] = "controls"

if col2.button("Generate Policies"):
    st.session_state["mode"] = "policies"

# --- CONTROL GENERATION ---
def init_llama_llm():
    """Initialize LLAMA LLM client"""
    class LlamaLLM:
        def __init__(self, host, port, model):
            self.base_url = f"http://{host}:{port}"
            self.model = model
        
        def invoke(self, prompt: str) -> Any:
            url = f"{self.base_url}/api/generate"
            payload = {
                "model": self.model,
                "prompt": prompt,
                "stream": False
            }
            try:
                response = requests.post(url, json=payload)
                response.raise_for_status()
                return response.json()["response"]
            except requests.exceptions.RequestException as e:
                raise Exception(f"Error calling LLAMA API: {str(e)}")

    return LlamaLLM("135.232.123.7", "11434", MODEL_NAME)

def merge_controls_using_LLM(llm: Any, text: List[str]) -> str:
    """Merge control descriptions using LLAMA"""
    prompt = f"""
    Role:
    Expert Policy Analyst of Lockthreat
    System: Combine multiple standard control statements into a single, cohesive policy statement, preserving all relevant information and following the original control structure.
    
    Input: A list of control statements from various standards (e.g., ISO-9001, IEE, ISO-27001)
    
    Output: A single string representing the combined policy statement, formatted with bullets, paragraphs, and statements as in the original controls.
    
    Requirements:
    - Merge duplicate or similar information into a single, concise statement.
    - Preserve keywords and phrases from the original controls, ensuring their meaning and context are maintained.
    - Ensure clarity and concision in the combined output, without adding or removing information.
    - Just return description without markdown
    
    Controls:
    {text}
    """
    response = llm.invoke(prompt)
    return response

def generate_controls(standards: Dict[str, List[Dict]]) -> Dict:
    """Process standards and merge similar controls"""
    st.write("Processing controls...")
    llm = init_llama_llm()

    control_texts = []
    for standard_name, controls in standards.items():
        for control in controls:
            control_texts.append(control.get("Description", ""))

    if control_texts:
        merged_controls = merge_controls_using_LLM(llm, control_texts)
        try:
            return json.loads(merged_controls)  # Ensure JSON format
        except json.JSONDecodeError:
            st.error("Error: Generated controls are not in valid JSON format.")
            return {"error": "Invalid JSON response from LLAMA"}
    else:
        return {"error": "No control descriptions found"}

# --- POLICY GENERATION ---
def create_policy_prompt():
    """Create the policy generation prompt"""
    return """
    Role:
    Expert Policy Analyst to generate policy documents based on domains of the standards
    Task:
    Generate a structured policy document with the following format:
    1. **Introduction**
       - Purpose of the Policy
       - Scope and Applicability
    2. **Policy Information**
       - Policy Name
       - Policy Number
       - Effective Date, Review Date
       - Version, Policy Owner, Approved By
    3. **Policy Objectives**
       - High-Level Objectives: Provide an overview of what the policy intends to achieve.
       - Compliance with relevant standards 
    4. **Controls Overview**
       - List each control with a control ID, description, and implementation guidance
        Include the exact wording of the controls, ensuring minimal paraphrasing to maintain alignment with the foundational regulations.
        Focus on how each control impacts the organization, what it requires, and why it is important.
    5. **Roles and Responsibilities**
       - Define roles such as Compliance Officer, IT Security, and Auditors
    6. **Risk Management**
       - How risks will be identified, analyzed, and mitigated
    7. **Compliance and Monitoring**
       - Internal & External compliance monitoring strategies
    8. **Communication and Training**
       - Internal and external training plans
    9. **Document Control and Review**
       - Version control and review procedures
    10. **References**
       - Applicable standards and internal policies
    Ensure that the output is in **JSON format**.
    """

def invoke_ollama_model(selected_standard):
    """Invoke LLAMA model to generate policies"""
    payload = {
        "model": MODEL_NAME,
        "prompt": create_policy_prompt() + f"\n\nGenerate policy based on this standard: {json.dumps(selected_standard)}",
        "stream": False
    }
    try:
        with st.spinner('Generating policy...'):
            response = requests.post(OLLAMA_API_URL, json=payload, timeout=200)
            response.raise_for_status()
            response_data = response.json()
            response_text = response_data.get("response", "")

            try:
                return json.loads(response_text)  # Ensure valid JSON
            except json.JSONDecodeError:
                st.error("Error: The generated policy is not in valid JSON format.")
                return {"error": "Invalid JSON response from LLAMA"}

    except requests.exceptions.RequestException as e:
        st.error(f"Error: {e}")
        return {"error": "API request failed"}

# --- MAIN LOGIC ---
if "mode" in st.session_state and "json_files" in st.session_state:
    json_data = st.session_state["json_files"]

    if st.session_state["mode"] == "controls":
        st.subheader("Generated Controls")
        generated_controls = generate_controls(json_data)
        st.json(generated_controls)

        # Download button
        st.download_button("Download Controls JSON", json.dumps(generated_controls, indent=4), "controls.json", "application/json")

    elif st.session_state["mode"] == "policies":
        st.subheader("Generated Policies")
        generated_policies = invoke_ollama_model(json_data)
        st.json(generated_policies)

        # Download button
        filename = f"policy_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        st.download_button("Download Policy JSON", json.dumps(generated_policies, indent=4), filename, "application/json")

# --- GO BACK BUTTON ---
if st.button("Go Back"):
    st.session_state.clear()
    st.experimental_rerun()
 