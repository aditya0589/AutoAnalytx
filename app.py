import streamlit as st
import pandas as pd
import os
from dotenv import load_dotenv

from agent.graph import get_agent_graph
from utils.data_loader import load_data
from utils.db import save_analysis
from langchain_core.messages import HumanMessage, AIMessage

# Load environment variables
load_dotenv()

st.set_page_config(page_title="AutoAnalytx", layout="wide")

# Custom CSS for better UI
st.markdown("""
<style>
    .stChatMessage {
        padding: 1rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
    }
    .stChatMessage.user {
        background-color: #f0f2f6;
    }
    .stChatMessage.assistant {
        background-color: #e8f0fe;
    }
</style>
""", unsafe_allow_html=True)

def main():
    st.title("🤖 AutoAnalytx")
    st.caption("Your Intelligent Data Analytics Agent")

    # Sidebar Configuration
    with st.sidebar:
        st.header("Configuration")
        
        # api_key = st.text_input("Gemini API Key", type="password", value=os.getenv("GOOGLE_API_KEY", ""))
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            st.error("GROQ_API_KEY not found in environment variables.")
        
        st.divider()
        st.subheader("Data Source")
        data_source = st.radio("Select Source", ["Upload File", "Database Connection", "Manual Input"])
        
        if data_source == "Upload File":
            uploaded_file = st.file_uploader("Upload CSV or Excel", type=["csv", "xlsx", "xls"])
            if uploaded_file:
                try:
                    df = load_data(uploaded_file, uploaded_file.name.split(".")[-1])
                    st.session_state["dataframes"] = {"df": df}
                    st.success(f"Loaded {uploaded_file.name} with {len(df)} rows.")
                    st.dataframe(df.head())
                except Exception as e:
                    st.error(f"Error loading file: {e}")
        
        elif data_source == "Database Connection":
            db_type = st.selectbox("Database Type", ["MySQL", "PostgreSQL", "TiDB"])
            host = st.text_input("Host", value="127.0.0.1")
            port = st.text_input("Port", value="4000" if db_type in ["TiDB", "MySQL"] else "5432")
            user = st.text_input("User", value="root")
            password = st.text_input("Password", type="password")
            database = st.text_input("Database Name", value="test")
            
            if st.button("Connect"):
                try:
                    from utils.db import create_db_engine, test_connection, get_tables
                    engine = create_db_engine(db_type, host, port, user, password, database)
                    success, msg = test_connection(engine)
                    if success:
                        st.success(msg)
                        st.session_state["db_engine"] = engine
                    else:
                        st.error(f"Connection failed: {msg}")
                except Exception as e:
                    st.error(f"Error: {e}")

            if "db_engine" in st.session_state:
                try:
                    from utils.db import get_tables, load_table
                    tables = get_tables(st.session_state["db_engine"])
                    selected_table = st.selectbox("Select Table", tables)
                    
                    if st.button("Load Table"):
                        df = load_table(st.session_state["db_engine"], selected_table, limit=5000)
                        st.session_state["dataframes"] = {"df": df}
                        st.success(f"Loaded table '{selected_table}' with {len(df)} rows.")
                        st.dataframe(df.head())
                except Exception as e:
                    st.error(f"Error loading table: {e}")

        elif data_source == "Manual Input":
            st.info("Manually input data is not yet implemented.")
            
        st.divider()
        with st.expander("ℹ️ Instructions & About"):
            st.markdown("""
            **AutoAnalytx** is an intelligent data analytics agent powered by **Google Gemini** and **LangGraph**.
            
            **How to use:**
            1. Choose a data source (Upload File or Database).
            2. Chat with your data! Ask for summaries, plots, or specific analysis.
            
            **Tech Stack:**
            - **Framework**: Streamlit & LangChain
            - **Agent**: LangGraph
            - **LLM**: Llama 3.2 (Groq) 
            - **Database**: TiDB / MySQL / PostgreSQL
            - **Tools**: Pandas, Plotly, Scikit-learn
            
            **Limitations:**
            - **Data Size**: Large files (>200MB) may encounter issues.
            - **LLM Accuracy**: The agent writes code to answer queries; complex logic may require refinement.
            - **Security**: Database credentials are not stored persistently but ensure you trust the environment.
            """)

    # Initialize Chat History
    if "messages" not in st.session_state:
        st.session_state["messages"] = []

    # Display Chat Messages
    for msg in st.session_state["messages"]:
        if isinstance(msg, HumanMessage):
            with st.chat_message("user"):
                st.write(msg.content)
        elif isinstance(msg, AIMessage):
            # Only display if there is content (skip purely tool-calling messages in main chat)
            if msg.content:
                with st.chat_message("assistant"):
                    st.write(msg.content)
                    # Check if there was a plot associated with this message
                    if "plot" in msg.additional_kwargs:
                        st.plotly_chart(msg.additional_kwargs["plot"])

    # Chat Input
    if prompt := st.chat_input("Ask a question about your data..."):
        if not api_key:
            st.error("Groq API Key is missing. Please check your .env file.")
            return

        # Add user message to state
        st.session_state["messages"].append(HumanMessage(content=prompt))
        with st.chat_message("user"):
            st.write(prompt)

        # Run Agent
        with st.chat_message("assistant"):
            st_callback = st.container() # For streaming thinking steps
            
            try:
                # Prepare shared state for plots
                shared_state = {}
                
                # Get dataframes from session state
                dataframes = st.session_state.get("dataframes", {})

                graph = get_agent_graph(api_key, dataframes, shared_state)
                # Prepare inputs
                inputs = {"messages": st.session_state["messages"]}
                
                # Stream output
                generated_messages = []
                final_response = None
                generated_plots = []
                
                with st.status("Thinking...", expanded=True) as status:
                    for event in graph.stream(inputs):
                        for key, value in event.items():
                            if "messages" in value:
                                new_msgs = value["messages"]
                                generated_messages.extend(new_msgs)
                            
                            if key == "agent":
                                msg = value["messages"][0]
                                if not msg.tool_calls:
                                    final_response = msg.content
                            
                            elif key == "tools":
                                # Display tool output
                                for msg in value["messages"]:
                                    status.write(f"**Tool Output ({msg.name})**:")
                                    status.code(msg.content)

                            # Check shared_state for plots after any step (agent or tool)
                            if "last_fig" in shared_state:
                                fig = shared_state["last_fig"]
                                generated_plots.append(fig)
                                status.write("**Plot Generated**")
                                del shared_state["last_fig"]

                    status.update(label="Analysis Complete", state="complete", expanded=False)
                
                # Append all generated messages to session state
                st.session_state["messages"].extend(generated_messages)

                if final_response:
                    st.write(final_response)
                    
                    # Display generated plots
                    for fig in generated_plots:
                        st.plotly_chart(fig)
                    
                    # Save to history with plots (associate with last message)
                    if generated_plots and isinstance(st.session_state["messages"][-1], AIMessage):
                        st.session_state["messages"][-1].additional_kwargs["plot"] = generated_plots[0]
                    
                    # Options to save/download
                    col1, col2 = st.columns(2)
                    with col1:
                        if st.button("💾 Save Analysis to TiDB"):
                            # For demo, we use user_id=1. In real app, get from login.
                            try:
                                from utils.db import save_analysis
                                import json
                                
                                # Serialize plot if available
                                viz_json = None
                                # We need to track if a plot was made in this turn. 
                                # Simplified: We don't have the plot object here easily unless we stored it in a specific way for saving.
                                # For now, we just save the text.
                                
                                save_analysis(1, prompt, final_response, viz_json)
                                st.success("Analysis saved to database!")
                            except Exception as e:
                                st.error(f"Failed to save: {e}")
                    
                    with col2:
                        st.download_button(
                            label="📥 Download Result",
                            data=final_response,
                            file_name="analysis_result.txt",
                            mime="text/plain"
                        )
                
            except Exception as e:
                st.error(f"An error occurred: {e}")

if __name__ == "__main__":
    main()
