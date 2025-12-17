import base64
from io import BytesIO

import pandas as pd
import streamlit as st

import re

from graph import run_demo_workflow


def extract_entities_from_query(query: str, default_molecule: str, default_region: str) -> tuple[str, str]:
    """
    Extract molecule and region from user query if mentioned.
    Returns (molecule, region) tuple.
    """
    query_lower = query.lower()
    
    # Common molecule names (add more as needed)
    common_molecules = [
        "aspirin", "tiotropium", "metformin", "atorvastatin", "lisinopril",
        "amlodipine", "metoprolol", "omeprazole", "simvastatin", "losartan",
        "albuterol", "levothyroxine", "azithromycin", "amoxicillin", "gabapentin"
    ]
    
    # Common regions
    regions = ["india", "us", "usa", "united states", "china", "brazil", "eu", "europe", "global", "uk"]
    
    # Extract molecule
    molecule = default_molecule
    for mol in common_molecules:
        if mol in query_lower:
            molecule = mol.capitalize()
            break
    
    # Extract region
    region = default_region
    for reg in regions:
        if reg in query_lower:
            # Map variations to standard names
            if reg in ["us", "usa", "united states"]:
                region = "US"
            elif reg in ["eu", "europe"]:
                region = "EU"
            elif reg == "uk":
                region = "Global"  # or handle UK separately
            else:
                region = reg.capitalize()
            break
    
    return molecule, region


def main():
    st.set_page_config(page_title="EY Pharma Agentic AI", layout="wide")
    st.title("EY Techathon 6.0 – Pharma Agentic AI Demo")

    st.markdown(
        """
        **Agentic AI for Pharma Portfolio Innovation**  
        This system orchestrates multiple specialized agents to identify innovation opportunities 
        by analyzing market data, clinical trials, patents, trade flows, and scientific literature.
        """
    )

    # Simple session state for chat history
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "last_report_path" not in st.session_state:
        st.session_state.last_report_path = None
    if "last_agent_results" not in st.session_state:
        st.session_state.last_agent_results = {}
    if "last_agent_full_results" not in st.session_state:
        st.session_state.last_agent_full_results = {}

    # Sidebar for configuration / molecule selection
    with st.sidebar:
        st.header("Query Configuration")
        molecule = st.text_input("Molecule", value="Tiotropium")
        region = st.selectbox("Region", ["Global", "US", "India", "EU"], index=2)
        time_horizon = st.selectbox(
            "Time Horizon", ["3 years", "5 years", "10 years"], index=1
        )

        st.markdown("### File Upload")
        uploaded_file = st.file_uploader(
            "Upload Internal Document (PDF)", 
            type=["pdf"],
            help="Upload strategy decks, MINS, or field reports for analysis"
        )
        if uploaded_file:
            st.success(f"Uploaded: {uploaded_file.name}")
            # Store in session state for internal agent to use
            st.session_state.uploaded_doc = uploaded_file.read()
        
        st.markdown("### Demo Info")
        st.write("Team: EY Techathon 6.0 – Pharma Domain")

    # Main chat area
    chat_col, agent_col = st.columns([2, 1])

    with chat_col:
        st.subheader("Chat")

        for msg in st.session_state.messages:
            role = msg["role"]
            content = msg["content"]
            if role == "user":
                st.chat_message("user").markdown(content)
            else:
                st.chat_message("assistant").markdown(content)

        prompt = st.chat_input("Ask a strategic question about your molecule...")
        if prompt:
            st.session_state.messages.append({"role": "user", "content": prompt})

            # Extract molecule and region from query if mentioned, otherwise use sidebar defaults
            extracted_molecule, extracted_region = extract_entities_from_query(
                prompt, molecule, region
            )
            
            # Update sidebar values if extracted (for next query)
            if extracted_molecule != molecule:
                st.info(f"🔍 Detected molecule: **{extracted_molecule}** (from query)")
            if extracted_region != region:
                st.info(f"🌍 Detected region: **{extracted_region}** (from query)")

            # Call the (temporary) demo workflow instead of a real LangGraph graph
            uploaded_doc = st.session_state.get("uploaded_doc", None)
            state = run_demo_workflow(
                user_query=prompt,
                molecule=extracted_molecule,
                region=extracted_region,
                time_horizon=time_horizon,
                uploaded_doc=uploaded_doc,
            )

            response = state.final_summary or "No summary generated."
            st.session_state.last_report_path = state.report_path
            st.session_state.last_agent_results = {
                k: v.summary for k, v in state.agent_results.items()
            }
            st.session_state.last_agent_full_results = {
                k: v for k, v in state.agent_results.items()
            }
            st.session_state.messages.append(
                {"role": "assistant", "content": response}
            )
            # Rerun to immediately show the new messages and updated report button
            st.rerun()

    with agent_col:
        st.subheader("Agent Activity")
        
        # Show count of agents that ran
        if st.session_state.last_agent_full_results:
            agent_count = len(st.session_state.last_agent_full_results)
            st.caption(f"**{agent_count} agent(s) executed**")
            st.divider()
            
            for key, result in st.session_state.last_agent_full_results.items():
                agent_name = result.agent_name if hasattr(result, 'agent_name') else key.replace("_", " ").title()
                with st.expander(f"✅ {agent_name}", expanded=False):
                    st.markdown(f"**Summary:** {result.summary}")
                    
                    # Display charts
                    if hasattr(result, 'charts') and result.charts:
                        for chart in result.charts:
                            st.markdown(f"**{chart.get('title', 'Chart')}**")
                            chart_data = base64.b64decode(chart.get('data', ''))
                            st.image(BytesIO(chart_data), use_container_width=True)
                    
                    # Display tables
                    if hasattr(result, 'tables') and result.tables:
                        for table in result.tables:
                            if table.get('rows'):
                                df = pd.DataFrame(table['rows'])
                                st.markdown(f"**{table.get('name', 'Data')}**")
                                st.dataframe(df, use_container_width=True, hide_index=True)
        else:
            st.markdown(
                "- **No agents run yet**: ask a question in the chat to trigger the workflow."
            )
            st.info("💡 **Tip**: Use queries like 'Find innovation opportunities' to run all agents")

        if st.session_state.last_report_path:
            try:
                with open(st.session_state.last_report_path, "rb") as f:
                    st.download_button(
                        label="Download latest PDF report",
                        data=f,
                        file_name=st.session_state.last_report_path.split("\\")[-1],
                        mime="application/pdf",
                    )
            except OSError:
                st.write("Report file not found. Run a query to regenerate it.")


if __name__ == "__main__":
    main()


