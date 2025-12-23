# AutoAnalytx 🤖

AutoAnalytx is an intelligent data analytics agent that helps you analyze your data, create visualizations, and answer questions using natural language. It leverages Llama 3.2 (via LangChain/LangGraph) and supports multiple data sources.

The deployed app here:  https://autoanalytx.streamlit.app/
## Features

- **Interactive Chat Interface**: Ask questions about your data in plain English.
- **Multi-Source Support**:
    - Upload CSV/Excel files.
    - Connect to MySQL, PostgreSQL, or TiDB databases.
- **Smarter Analysis**:
    - "Thinking" mode shows the agent's logic and code execution.
    - Uses Python for accurate data processing and Plotly for interactive visualizations.
- **Persistence**: Save your analysis to a database and persist conversation history.

## Setup

1.  **Clone the repository**:
    ```bash
    git clone <repository-url>
    cd AutoAnalytx
    ```

2.  **Create a virtual environment**:
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate
    ```

3.  **Install dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

4.  **Environment Configuration**:
    Create a `.env` file in the root directory with the following keys:
    ```env
    GROQ_API_KEY=your_api_key_here
    # Optional: Internal Storage DB (TiDB)
    TIDB_HOST=127.0.0.1
    TIDB_PORT=4000
    TIDB_USER=root
    TIDB_PASSWORD=
    TIDB_DATABASE=autoanalytx
    ```

5.  **Database Setup (Optional)**:
    If you want to use the "Save Analysis" feature, run the `tidb_setup.sql` script on your TiDB/MySQL instance.

## Usage

Run the Streamlit application:
```bash
streamlit run app.py
```
Access the app at `http://localhost:8501`.

## Tech Stack

- **Frontend**: Streamlit
- **Agent Framework**: LangGraph, LangChain
- **LLM**: Llama 3.2 (Groq)
- **Data Tools**: Pandas, Plotly, Scikit-learn
- **Database**: SQLAlchemy, TiDB/MySQL

