from typing import List, Dict, Any
import streamlit as st
import zipfile
import os
import json
import pandas as pd
import requests
from datetime import datetime
from PIL import Image

# Constants for Local Llama
OLLAMA_API_URL = "http://localhost:11434/api/generate"
MODEL_NAME = "llama3.2:3b"

def make_llm_request(prompt: str) -> str:
    """Make a request to local Llama model"""
    try:
        response = requests.post(
            OLLAMA_API_URL,
            json={
                "model": MODEL_NAME,
                "prompt": prompt,
                "stream": False
            }
        )
        if response.status_code == 200:
            return response.json().get('response', '')
        else:
            st.error(f"Error calling Llama: {response.status_code}")
            return ""
    except Exception as e:
        st.error(f"Error connecting to Ollama: {str(e)}")
        return ""

def standard_processor(json_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Process standards and generate controls"""
    processed_data = []
    
    for item in json_data:
        domain = item.get('domain', '')
        controls = item.get('Controls', [])
        
        processed_controls = []
        for control in controls:
            # Create prompt for Llama
            prompt = f"""Given this control:
            ID: {control.get('id', '')}
            Name: {control.get('name', '')}
            Description: {control.get('description', '')}
            
            Generate an enhanced security control with detailed requirements and implementation guidance."""
            
            # Get response from Llama
            enhanced_description = make_llm_request(prompt)
            
            processed_controls.append({
                'id': control.get('id', ''),
                'name': control.get('name', ''),
                'description': enhanced_description or control.get('description', '')
            })
        
        processed_data.append({
            'domain': domain,
            'Controls': processed_controls
        })
    
    return processed_data

def policy_standard_processor(json_data: List[Dict[str, Any]], region: str, industry: str) -> List[str]:
    """Process standards and generate policies based on region and industry"""
    policies = []
    
    for item in json_data:
        domain = item.get('domain', '')
        controls = item.get('Controls', [])
        
        # Create context-aware prompt for Llama
        prompt = f"""Generate a security policy for:
        Region: {region}
        Industry: {industry}
        Domain: {domain}
        
        Consider these controls:
        {json.dumps(controls, indent=2)}
        
        Create a comprehensive security policy that addresses these controls while considering regional and industry requirements."""
        
        policy = make_llm_request(prompt)
        if policy:
            policies.append(f"# {domain} Policy\n\n{policy}")
    
    return policies

def extract_json_from_zip(zip_path, extract_to="temp_data"):
    """Extracts JSON files from a ZIP and loads them as a dictionary."""
    json_data = []
    
    with zipfile.ZipFile(zip_path, "r") as zip_ref:
        zip_ref.extractall(extract_to)
        for filename in zip_ref.namelist():
            if filename.endswith(".json") and not filename.startswith('__MACOSX'):
                st.info(filename)
                file_path = os.path.join(extract_to, filename)
                try:
                    with open(file_path, "r", encoding="utf-8") as file:
                        json_data.append(json.load(file))
                except UnicodeDecodeError:
                    with open(file_path, "r", encoding="ISO-8859-1") as file:
                        json_data.append(json.load(file))
    return json_data

def json_to_table(json_data: List[Dict[str, Any]]) -> pd.DataFrame:
    """Convert JSON to tabular format with controls & domains."""
    table_data = []
    
    for standard in json_data:
        domain = standard.get("domain", "N/A")
        controls = standard.get("Controls", [])
        
        for control in controls:
            table_data.append({
                "Control ID": control.get("id", "N/A"),
                "Control Name": control.get("name", "N/A"),
                "Domain": domain,
                "Description": control.get("description", "N/A"),
            })
    
    return pd.DataFrame(table_data)

# --- STREAMLIT UI ---
def main():
    # Load and display logo
    try:
        logo = Image.open("./app/logo.png")
        st.image(logo, width=200)
    except:
        st.warning("Logo file not found")

    st.title("Lock Threat Genius")

    # Region and Industry Selection
    regions = ["North America", "Europe", "Asia", "South America", "Africa", "Australia"]
    industries = ["Finance", "Healthcare", "Technology", "Retail", "Manufacturing", "Education"]

    selected_region = st.selectbox("Select a Region:", regions)
    selected_industry = st.selectbox("Select an Industry:", industries)

    # File Upload
    uploaded_file = st.file_uploader("Upload a ZIP file containing JSON files", type="zip")

    if uploaded_file:
        json_data = extract_json_from_zip(uploaded_file)
        st.session_state["json_files"] = json_data

    # Generate Controls and Policies Buttons
    col1, col2 = st.columns(2)
    if col1.button("Generate Controls"):
        st.session_state["mode"] = "controls"

    if col2.button("Generate Policies"):
        st.session_state["mode"] = "policies"

    # Main Processing Logic
    if "mode" in st.session_state and "json_files" in st.session_state:
        json_data = st.session_state["json_files"]

        if st.session_state["mode"] == "controls":
            st.subheader("Generated Controls")
            with st.spinner("Generating controls using local Llama model..."):
                generated_controls = standard_processor(json_data)
                df = json_to_table(generated_controls)
                
                st.subheader("Converted Table")
                st.dataframe(df)
                
                # Download button for controls
                st.download_button(
                    "Download Controls JSON",
                    json.dumps(generated_controls, indent=4),
                    "controls.json",
                    "application/json"
                )

        elif st.session_state["mode"] == "policies":
            st.subheader("Generated Policies")
            with st.spinner("Generating policies using local Llama model..."):
                generated_policies = policy_standard_processor(json_data, selected_region, selected_industry)
                for policy in generated_policies:
                    st.divider()
                    st.markdown(policy)
                
                # Download button for policies
                filename = f"policy_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
                st.download_button(
                    "Download Policy JSON",
                    json.dumps(generated_policies, indent=4),
                    filename,
                    "application/json"
                )

    # Go Back Button
    if st.button("Go Back"):
        st.session_state.clear()
        st.experimental_rerun()

if __name__ == "__main__":
    main()