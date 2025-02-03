from langchain.prompts import PromptTemplate

##
## PROMPTS ##
##
# Define a prompt template for extracting headings and subheadings
controls_prompt_template = PromptTemplate(
        input_variables=["current_input"],
        template="""
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
        {current_input}

        """
    )
# Define a prompt template for extracting headings and subheadings
policy_prompt_template = PromptTemplate(
    input_variables=["current_input","domain_name"],
    template="""
    Role:
    Expert Policy Analyst of Lockthreat

    Task:
        Create a detailed policy document for the domain titled '{domain_name}'. The policy should be structured into a three-column table with the following fields: Policy Information: Include 'Policy Name', 'Policy Number', 'Effective Date', 'Review Date', 'Version', 'Policy Owner', and 'Approved By'. Introduction: Provide the 'Purpose of the Policy' and 'Scope and Applicability'. Policy Objectives: Outline key objectives such as statutory compliance, applicability, and precise definitions. Controls Overview: List each control within the domain, including control identifiers and descriptions. Generate the control overview which is an overview of the control descriptions and generate implementation guidance for that control. Roles and Responsibilities: Specify the roles of internal teams (e.g., Compliance Officer, IT Security Team) and external auditors. Risk Management: Describe how risks will be identified, analyzed, and mitigated. Compliance and Monitoring: Provide details on internal and external monitoring of compliance. Communication and Training: Outline how the policy will be communicated and training will be provided to relevant staff. Document Control and Review: Include information about version control and the review process. References: Provide a list of relevant standards and regulations associated with the domain. Ensure that the final output is a three-column table format with the following columns: Section, Item, and Description. 
        
        Here's how you will structure the comprehensive policy document, taking into account the previously mentioned requirements and the specific focus on the controls within the document: 

        Comprehensive Policy Document Structure 
        1. Introduction 
            Purpose of the Policy: 
                Introduce the policy, explaining its purpose as it relates to the specific subpart and its importance in the context of the provided standard’s compliance. The purpose here is to ensure that the organization meets all regulatory requirements under the specific subpart and to guide employees on adhering to these controls. 
            Scope and Applicability: 
                Define the scope of the policy, indicating that it applies to all employees, departments, and activities governed by the specified subpart. 
            Clarify that this policy is mandatory for internal teams (e.g., compliance, IT) and will also be used to demonstrate compliance to external auditors and regulators. 

        2. Policy Information 
            Policy Name: Named after the specific subpart. 
            Policy Number: A unique identifier for tracking. 
            Effective Date and Review Date: Dates indicating when the policy comes into effect and when it should be reviewed. 
            Version Number: Helps in tracking changes over time. 
            Policy Owner and Approved By: Names or titles of those responsible for the policy. 

        3. Policy Objectives 
            High-Level Objectives: 
            Provide an overview of what the policy intends to achieve. 
            Mention specific objectives for each control within the subpart, emphasizing compliance and ensuring the organization's practices align with the document’s standards. 

        4. Controls Overview 
            Detailed Descriptions: 
                Provide a high-level overview of each control under the subpart. 
                Include the exact wording of the controls, ensuring minimal paraphrasing to maintain alignment with the foundational regulations. 
                Focus on how each control impacts the organization, what it requires, and why it is important. 

        5. Roles and Responsibilities 
            Internal Roles: 
                Specify the roles responsible for implementing and overseeing each control (e.g., Compliance Officer, IT Security Team). 
                Include a description of their responsibilities in ensuring compliance with the policy. 
            External Engagement: 
                Outline how external auditors, regulators, or third parties will interact with the policy. 
                Include responsibilities for providing evidence of compliance, undergoing audits, and facilitating inspections. 

        6. Risk Management 
            Risk Identification and Analysis: 
                Identify potential risks associated with each control (e.g., non-compliance, operational inefficiencies). 
                Analyze the potential impact of these risks on the organization, both from a regulatory and operational perspective. 
            Mitigation Strategies: 
                Provide strategies to mitigate identified risks, such as regular audits, training, and automated monitoring systems. 

        7. Compliance and Monitoring 
            Compliance Assurance: 
                Describe how compliance with the policy will be monitored internally (e.g., periodic reviews, regular audits). 
                Include a high-level overview of tools or processes used to ensure ongoing compliance. 
            External Audits: 
                Detail how the organization will prepare for and engage in external audits or reviews. 
                Mention documentation practices and evidence-gathering procedures to demonstrate compliance to external parties. 

        8. Communication and Training 
            Internal Communication: 
                Specify how the policy will be communicated to internal teams. 
                Include the frequency of updates, training sessions, and how feedback will be gathered and incorporated. 
            Training Programs: 
                Outline the training programs that will be provided to ensure employees understand the policy and can comply with the controls. 
            External Communication: 
                Explain how the policy will be communicated to external parties, such as auditors or partners. 
                Include how compliance status and updates will be shared. 

        9. Document Control and Review 
            Version Control: 
                Describe how the policy will be updated and version-controlled. 
                Include procedures for documenting changes and ensuring all stakeholders have access to the latest version. 
            Review Process: 
                Outline the process for regularly reviewing and updating the policy. 
                Include timelines for reviews and the roles responsible for carrying out these reviews. 

        10. References 
            Regulatory References: 
                List the specific standards’ regulations and any other relevant laws or standards that the policy is based on. 
            Internal References: 
                Mention related internal policies, procedures, and guidelines that are aligned with this policy. 

        Execution Strategy 
            Step-by-Step Drafting: 
                    Ensuring that each control is comprehensively covered within the document. 
                    Include the exact wording of each control, adding context and explanation as needed. 
                    Ensure that roles, responsibilities, and processes are clearly defined without making assumptions beyond what is outlined in the document. 
            Review and Feedback: 
                After drafting each section, review it to ensure that it aligns with the organization's needs and the regulatory requirements. 
                Seek feedback from internal stakeholders, such as compliance officers and legal teams, to ensure accuracy and completeness. 
            Finalization: 
                Once all sections are complete, compile them into a cohesive policy document. 
                Perform a final review for consistency, clarity, and compliance before publishing and distributing the policy. 
        

        Next Steps 
        Make sure you fully understand the above instruction for the policy document.

        Now start Generting the Policy document for the domain with the list of controls below:
        
        Doamin(JSON format):
            {current_input}

        Note:  

        The content from this prompt only needs to directly matching to your document for the following 2 sections – policy information where the policy name needs to similar to the domain name. The controls overview ids should be matching to the controls under that domain.  

        Other than that chatgpt can infer from the domain and generate content for the rest of the sections. As long as the sections and items are matching for all your policies, you are valid in your generation method for these policies. We dont need to focus too much on the content for these policies, as long as we are generating in a consistent format. Just make sure that the content is not repetitive and is unique for each policy. Hopefully chatgpt will give you unique content since the controls will be different for each domain. If the domain is similar, then you can expect that it will give you similar content for that policy which is no problem. 

        "GENERATE OUTPUT INTO JSON FORMAT"

    """
)
##
## POLICY GAP ANALYSIS PROMPT
## FOR ALL DOMAIN INPUTS
policy_gap_all_domain_prompt_template = PromptTemplate(
    input_variables=["input_policy","input_standard","output_str"],
    template="""
    Role:
    Expert Policy Analyst

    System: 
    Combine multiple standard control statements into a single, cohesive policy statement, preserving all relevant information and following the original control structure.

    Task:
    You will be given a policy input and a standard(containing a set of domains with their respective controls). Your task is to match the content of the policy with the domain controls and provide an output indicating whether each control is similar, partially similar, or not similar to the policy content.
    
    Policy Input: 
    {input_policy}

    Domain Input: 
    {input_standard}
    
    Output: 
    {output_str}
    
    Requirements:
    - Only validate with domain input, if policy control don't have match then don't consider it under output.
    - Merge duplicate or similar information into a single, concise statement.
    - Preserve keywords and phrases from the original controls, ensuring their meaning and context are maintained.

    """
)
##
## POLICY GAP ANALYSIS PROMPT
## FOR ONE DOMAIN INPUTS
policy_gap_prompt_template = PromptTemplate(
    input_variables=["input_policy","input_standard","output_str"],
    template="""
    Role:
    Expert Policy Analyst

    System: 
    Combine multiple standard control statements into a single, cohesive policy statement, preserving all relevant information and following the original control structure.

    Task:
    You will be given a policy input and a standard(containing a domain with their respective controls). Your task is to match the content of the policy with the domain controls and provide an output indicating whether each control is similar, partially similar, or not similar to the policy content.
    
    Policy Input: 
    {input_policy}

    Domain Input: 
    {input_standard}
    
    Output: 
    {output_str}
    
    Requirements:
    - Only validate with domain input, if policy control don't have match then don't consider it under output.
    - Merge duplicate or similar information into a single, concise statement.
    - Preserve keywords and phrases from the original controls, ensuring their meaning and context are maintained.
    - When summarizing use the control number and name from the standard control reference.

    """
)
##
## POLICY GAP ANALYSIS PROMPT
## SAMPLE OUTPUT FOR PROMPT
##
policy_gap_output = """```json
{
    "status": "success",
    "gap_analysis": {
        "description": "The policy '<policy_name>' aligns with several controls in the target standard <standard_name>. However, there are gaps in coverage related to remote access control and cryptographic controls. The existing policy addresses user endpoint devices and privileged access rights, which align with <standard_name>, but does not cover the control '<control_name>' (<standard_name> Control <control_number>) or '<control_name>' (<standard_name> Control <control_number>)."
    },
    "controls_comparison": {
        "missing_controls": [
            {
                "control_number": "<control_number>",
                "control_name": "<control_name>",
                "control_description": "<control_description>"
            },
            {
                "control_number": "<control_number>",
                "control_name": "<control_name>",
                "control_description": "<control_description>"
            }
        ],
        "matching_controls": [{
            "policy_control": {
                "control_number": "<control_number>",
                "control_name": "<control_name>",
                "control_description": "<control_description>"
            },
            "standard_control": {
                "control_number": "<control_number>",
                "control_name": "<control_name>",
                "control_description": "<control_description>"
                }
            }
        }]
    }
}```"""



__all__ = [
    "controls_prompt_template", 
    "policy_prompt_template",
    "policy_gap_output",
    "policy_gap_prompt_template",
    ]