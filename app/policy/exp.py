import streamlit as st
import zipfile
import os
import json
import pandas as pd
from datetime import datetime
from PIL import Image
import requests
from typing import List, Dict, Any

# --- Constants ---
OLLAMA_API_URL = "http://localhost:11434/api/generate"  # Changed to local Llama
MODEL_NAME = "llama3.2:3b"  # Changed to your local model
ZIP_FILE_PATH = "standards.zip"
EXTRACT_TO = "temp_data"

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

def standard_processor(standards: List[Dict]) -> List[Dict]:
    """Process standards and generate controls using local Llama"""
    processed_standards = []
    
    for standard in standards:
        processed_controls = []
        for domain in standard["Controls"]:
            for control in domain["Controls"]:
                prompt = f"""
                Analyze and enhance this security control:
                ID: {control['controlId']}
                Name: {control['name']}
                Description: {control['description']}
                
                Provide an enhanced description with specific requirements and implementation guidance.
                """
                
                enhanced_description = make_llm_request(prompt)
                processed_controls.append({
                    "controlId": control['controlId'],
                    "name": control['name'],
                    "description": enhanced_description if enhanced_description else control['description']
                })
                
        processed_standards.append({
            "StandardName": standard["StandardName"],
            "Controls": processed_controls
        })
    
    return processed_standards

def policy_standard_processor(standards: List[Dict], region: str, industry: str) -> List[str]:
    """Generate policies based on standards using local Llama"""
    policies = []
    
    for standard in standards:
        prompt = f"""
        Generate a security policy document for:
        Standard: {standard['StandardName']}
        Region: {region}
        Industry: {industry}
        
        Consider the following controls:
        {json.dumps(standard['Controls'], indent=2)}
        
        Create a comprehensive policy that addresses these controls while considering:
        1. {region} regional requirements
        2. {industry} industry-specific needs
        3. Best practices for implementation
        """
        
        policy = make_llm_request(prompt)
        if policy:
            policies.append(f"# {standard['StandardName']} Policy\n\n{policy}")
    
    return policies

def extract_json_from_zip(zip_path: str, extract_to: str) -> List[Dict]:
    """Extracts JSON files from a ZIP and loads them as a list."""
    json_data = []
    try:
        with zipfile.ZipFile(zip_path, "r") as zip_ref:
            zip_ref.extractall(extract_to)
            for filename in zip_ref.namelist():
                if filename.endswith(".json") and not filename.startswith('__MACOSX'):
                    file_path = os.path.join(extract_to, filename)
                    try:
                        with open(file_path, "r", encoding="utf-8") as file:
                            json_data.append(json.load(file))
                    except UnicodeDecodeError:
                        with open(file_path, "r", encoding="ISO-8859-1") as file:
                            json_data.append(json.load(file))
    except Exception as e:
        st.error(f"Error processing ZIP file: {str(e)}")
    return json_data

# --- Main Streamlit App ---
def main():
    # Initialize session state
    if "page" not in st.session_state:
        st.session_state.page = "Home"
        
    # Try to load logo
    try:
        logo = Image.open("./app/logo.png")
        st.image(logo, width=200)
    except Exception as e:
        st.warning("Logo not found")

    # Extract and load standards JSON files
    if os.path.exists(ZIP_FILE_PATH):
        json_data = extract_json_from_zip(ZIP_FILE_PATH, EXTRACT_TO)
        st.session_state["json_files"] = json_data
    else:
        st.error(f"ZIP file not found at {ZIP_FILE_PATH}")
        return

    # --- Page Navigation ---
    pages = ["Home", "Domains & Region/Industry", "Results"]
    current_page = st.session_state.get("page", "Home")

    # --- Page 1: Home Page ---
    if current_page == "Home":
        st.title("Lock Threat Genius")

        standard_options = [std["StandardName"] for std in json_data]
        selected_standards = st.multiselect("Choose the Standards:", standard_options)

        if selected_standards:
            filtered_standards = [std for std in json_data if std["StandardName"] in selected_standards]
            st.session_state["selected_standards"] = filtered_standards
            
            if st.button("Next"):
                st.session_state["page"] = "Domains & Region/Industry"
                st.rerun()
        elif not selected_standards and json_data:
            st.warning("Please select standards to continue.")

    # --- Page 2: Domains & Region/Industry Selection ---
    elif current_page == "Domains & Region/Industry":
        st.title("Select Domains, Region & Industry")

        selected_standards = st.session_state.get("selected_standards", [])
        if not selected_standards:
            st.warning("Please select standards first.")
            return

        # Domain selection
        domain_options = []
        for std in selected_standards:
            domain_options.extend([f"{std['StandardName']} - {domain['Domain']}" 
                                 for domain in std["Controls"]])
        
        selected_domains = st.multiselect("Choose Domains:", domain_options)
        
        # Region and Industry selection
        regions = ["North America", "Europe", "Asia", "South America", "Africa", "Australia"]
        industries = ["Finance", "Healthcare", "Technology", "Retail", "Manufacturing", "Education"]

        selected_region = st.selectbox("Select a Region:", regions)
        selected_industry = st.selectbox("Select an Industry:", industries)

        # Store selections
        st.session_state.update({
            "selected_domains": selected_domains,
            "selected_region": selected_region,
            "selected_industry": selected_industry
        })

        # Generate buttons
        col1, col2 = st.columns(2)
        if col1.button("Generate Controls"):
            st.session_state["mode"] = "controls"
            st.session_state["page"] = "Results"
            st.rerun()

        if col2.button("Generate Policies"):
            st.session_state["mode"] = "policies"
            st.session_state["page"] = "Results"
            st.rerun()

    # --- Page 3: Results Page ---
    elif current_page == "Results":
        st.title("Generated Results")
        
        selected_standards = st.session_state.get("selected_standards", [])
        if not selected_standards:
            st.warning("No standards selected.")
            return

        with st.spinner("Processing with local Llama model..."):
            if st.session_state["mode"] == "controls":
                st.subheader("Generated Controls")
                try:
                    generated_controls = standard_processor(selected_standards)
                    df = pd.DataFrame([{
                        "Control ID": ctrl["controlId"],
                        "Name": ctrl["name"],
                        "Description": ctrl["description"]
                    } for std in generated_controls for ctrl in std["Controls"]])
                    
                    st.dataframe(df)
                    st.download_button(
                        "Download Controls JSON",
                        json.dumps(generated_controls, indent=4),
                        "controls.json",
                        "application/json"
                    )
                except Exception as e:
                    st.error(f"Error generating controls: {str(e)}")

            elif st.session_state["mode"] == "policies":
                st.subheader("Generated Policies")
                try:
                    generated_policies = policy_standard_processor(
                        selected_standards,
                        st.session_state["selected_region"],
                        st.session_state["selected_industry"]
                    )
                    
                    for policy in generated_policies:
                        st.divider()
                        st.markdown(policy)

                    filename = f"policy_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
                    st.download_button(
                        "Download Policy JSON",
                        json.dumps(generated_policies, indent=4),
                        filename,
                        "application/json"
                    )
                except Exception as e:
                    st.error(f"Error generating policies: {str(e)}")

        # Go back button
        if st.button("Go Back"):
            st.session_state.clear()
            st.rerun()

if __name__ == "__main__":
    main()