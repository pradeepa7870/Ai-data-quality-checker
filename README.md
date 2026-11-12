# DataGuard AI — Beginner Data Quality Checker

A learning project that checks CSV/Excel business data, retrieves relevant data-quality rules with RAG, and uses a local Ollama model to explain findings. It also includes a separate MCP server exposing data-quality tools.

## Features
- Upload CSV or Excel files.
- Detect missing values, duplicate rows, invalid email formats and non-positive salary values.
- Calculate a simple completeness-oriented quality score.
- Retrieve business rules using Sentence Transformers + ChromaDB.
- Ask a local Ollama model to explain scan findings.
- Expose sample analysis functions through an MCP server.

## Requirements
- Python 3.10–3.12 recommended.
- VS Code and Python extension.
- Internet connection for first-time package/model downloads.
- Ollama installed for AI explanations.

## Windows PowerShell setup

Open this project folder in VS Code. Open Terminal > New Terminal and run:

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
```

If PowerShell blocks activation, run this in the current terminal:
```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1
```

## Run the website

1. Install Ollama from https://ollama.com/download
2. In a terminal, download the model:
```powershell
ollama pull gemma3:1b
```
3. Start Ollama (the desktop app normally runs the local service).
4. In the VS Code project terminal:
```powershell
streamlit run app.py
```
5. Open the local address Streamlit prints, usually http://localhost:8501.
6. Select the sample dataset or upload your own CSV/XLSX and click **Analyze dataset**.
7. Ask a question in the AI assistant.

The first RAG run downloads the `all-MiniLM-L6-v2` embedding model. This can take a few minutes.

## Run the MCP server

Open a second VS Code terminal, activate the same virtual environment, then run:

```powershell
python -m mcp_server.server
```

This server uses STDIO transport and waits for an MCP client. It is not a website and normally produces no browser page.

To inspect it, install/use MCP Inspector as described in the official MCP Python SDK documentation:
https://github.com/modelcontextprotocol/python-sdk

For a local MCP Inspector workflow, use its documented command for launching a Python STDIO server and point it to:
`python -m mcp_server.server`

Available MCP tools:
- `analyze_sample_dataset`
- `check_salary`
- `count_missing_values`

## How the parts fit together

- Pandas: reads and checks records.
- Custom validation code: identifies actual issues deterministically.
- Sentence Transformers: converts business-rule text and questions into vectors.
- ChromaDB: stores and searches the rule vectors.
- Ollama + Gemma: explains scan results using retrieved rules.
- MCP Python SDK: exposes selected Python functions as tools to an MCP-compatible client.
- Streamlit: provides the browser-based UI.

Important: In this beginner version, the Streamlit app calls the Python validation and RAG functions directly. The MCP server is a separate tool interface for an MCP-compatible client. This keeps the first implementation understandable; a later integration can make the AI client call MCP tools during chat.

## Current validation limitations
- Duplicate detection checks fully identical rows.
- Email validation is a simple format check, not proof that an email exists.
- Salary validation runs only when a column name contains `salary`.
- Quality score is a simple illustrative completeness score, not a certified enterprise metric.
- No source data is modified automatically.

## Suggested next improvements
1. Add configurable rules for customer and sales datasets.
2. Add scan history in SQLite or SQL Server.
3. Add user login and role-based access.
4. Add tests with pytest.
5. Connect the Streamlit chat to MCP tools through an MCP client.
6. Add audit logs and approval before any data correction.
