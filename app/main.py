import streamlit as st

from graph import run_demo_workflow


def main():
    st.set_page_config(page_title="EY Pharma Agentic AI", layout="wide")
    st.title("EY Techathon 6.0 – Pharma Agentic AI Demo")

    st.markdown(
        """
        This is a skeleton UI wired for a future LangGraph-based multi-agent backend.
        For now, it simulates the conversation flow and agent activity.
        """
    )

    # Simple session state for chat history
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "last_report_path" not in st.session_state:
        st.session_state.last_report_path = None
    if "last_agent_results" not in st.session_state:
        st.session_state.last_agent_results = {}

    # Sidebar for configuration / molecule selection
    with st.sidebar:
        st.header("Query Configuration")
        molecule = st.text_input("Molecule", value="Tiotropium")
        region = st.selectbox("Region", ["Global", "US", "India", "EU"], index=2)
        time_horizon = st.selectbox(
            "Time Horizon", ["3 years", "5 years", "10 years"], index=1
        )

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

            # Call the (temporary) demo workflow instead of a real LangGraph graph
            state = run_demo_workflow(
                user_query=prompt,
                molecule=molecule,
                region=region,
                time_horizon=time_horizon,
            )

            response = state.final_summary or "No summary generated."
            st.session_state.last_report_path = state.report_path
            st.session_state.last_agent_results = {
                k: v.summary for k, v in state.agent_results.items()
            }
            st.session_state.messages.append(
                {"role": "assistant", "content": response}
            )
            # Rerun to immediately show the new messages and updated report button
            st.rerun()

    with agent_col:
        st.subheader("Agent Activity")

        if st.session_state.last_agent_results:
            for key, summary in st.session_state.last_agent_results.items():
                with st.expander(f"{key} agent", expanded=False):
                    st.markdown(summary)
        else:
            st.markdown(
                "- **No agents run yet**: ask a question in the chat to trigger the workflow."
            )

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


