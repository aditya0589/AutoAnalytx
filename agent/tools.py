import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from langchain_core.tools import tool
import sys
from io import StringIO
import contextlib

@contextlib.contextmanager
def stdoutIO(stdout=None):
    old = sys.stdout
    if stdout is None:
        stdout = StringIO()
    sys.stdout = stdout
    yield stdout
    sys.stdout = old

def get_tools(dataframes: dict, shared_state: dict):
    """
    Creates tools with access to the provided dataframes and shared state.
    This avoids accessing st.session_state directly in threads.
    """
    
    @tool
    def execute_python(code: str):
        """Executes Python code. Use this to analyze data, create plots, etc.
        The code should be valid Python.
        You have access to `pd`, `px`, `go`, and any loaded dataframes (e.g., `df`).
        If you create a Plotly figure, assign it to a variable named `fig`.
        """
        try:
            # Prepare the local namespace
            local_vars = {
                "pd": pd,
                "px": px,
                "go": go,
            }
            
            # Inject dataframes
            local_vars.update(dataframes)

            # Execute the code and capture stdout
            with stdoutIO() as s:
                exec(code, {}, local_vars)
            
            output = s.getvalue()
            
            # Check for 'fig' variable
            if "fig" in local_vars:
                fig = local_vars["fig"]
                shared_state["last_fig"] = fig
                return f"Code executed successfully.\nOutput:\n{output}\n\nA plot was generated and saved to shared state."
            
            if not output:
                return "Code executed successfully, but produced no output. Did you forget to print()?"

            return f"Code executed successfully.\nOutput:\n{output}"
        except Exception as e:
            return f"Error executing code: {e}"

    return [execute_python]
