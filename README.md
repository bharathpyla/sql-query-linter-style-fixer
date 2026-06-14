# SQL Query Linter & Style Fixer

A high-performance hybrid SQL optimization pipeline combining local, zero-token regex-based rules (Phase 1) with GenAI-driven structural refactoring (Phase 2). 

This tool helps database administrators and developers transform legacy, unformatted SQL queries into modern, readable, and highly optimized SQL.

---

## 👥 Team Members & Resumes
* **Team Name**: **TEAM 20**
* **Team Members**:
  * **Member 1**: **Penta Satwika** (Reg. No: `23U41A4245`) - Role: Lead Full-Stack Developer & UI Architect
  * **Member 2**: **Bharath Pyla** (Reg. No: `23U41A0536`) - Role: Backend & Data Processing Engineer
  * **Member 3**: **Aythi Eswar** (Reg. No: `23U41A0406`) - Role: LLM Prompts & AI Integration Specialist
  * **Member 4**: **Dadi James** (Reg. No: `24U45A0212`) - Role: Quality Assurance & Documentation Engineer
* **Resumes**: Resumes for all team members are saved in PDF format in the [RESUMES](./RESUMES) folder.

---

## 🚀 Key Features

### 🔍 Phase 1: Local Deterministic Linter
* **Keyword Capitalization**: Automatically standardizes SQL keywords (e.g., `SELECT`, `FROM`, `WHERE`, `INNER JOIN`) to uppercase.
* **Casing Normalization**: Automatically converts camelCase and PascalCase identifiers (columns and table names) to lowercase `snake_case`.
* **Markdown Sanitization**: Strips decorative markdown formatting elements (like asterisks `*` or underscores `_` around words) from query inputs safely using negative lookbehinds/lookaheads without mangling snake_case names.
* **Anti-Pattern Diagnostics**: Detects and logs explicit `SELECT *` statements as warning diagnostics to encourage cost-efficient querying.

### 🧠 Phase 2: GenAI Refactoring Agent (with Self-Correction)
* **Implicit-to-Explicit Joins**: Rewrites legacy comma-joins (e.g., `FROM a, b WHERE a.id = b.id`) into modern, explicit `INNER JOIN` or outer join syntax with proper lowercased aliases.
* **CTE Extraction**: Extracts deeply nested subqueries (e.g., in SELECT projections) into clean, named Common Table Expressions (CTEs).
* **Self-Correction Agent Loop**: Automatically validates generated SQL syntax using local AST checking (`sqlglot`). If a syntax error is found, the error is fed back to `gemini-2.5-flash` in a 3-step loop to self-correct the query before outputting.
* **Local AST Fallback**: Runs a local AST-based pretty-printer (`sqlglot`) if no API key is provided, ensuring zero-cost formatting capability.

### 💻 Dual Interface Support
1. **Interactive Web Dashboard**: A Streamlit-based UI featuring:
   * **🧪 Sandbox Playground**: Paste individual raw queries to see syntax updates and diff reports in real-time.
   * **📤 File Uploader (Cloud Friendly)**: Upload multiple `.sql` files, optimize them in-memory, view colored diffs, and download fixed outputs instantly (perfect for Streamlit Community Cloud hosting).
   * **📂 Folder Directory Scanner**: Scan a local directory of queries, rewrite them, and output new `_fixed.sql` files.
2. **Command Line Interface (CLI)**: Automate scan operations locally with text logs suitable for cron jobs or CI/CD pipelines.

---

## 📂 Project Structure

```
sql_query_linter/
│
├── app.py                # Main entry point (Streamlit Web App & CLI)
├── lint_engine.py        # Phase 1: Regex Linter and Markdown Sanitizer
├── llm_agent.py          # Phase 2: GenAI Refactor, Agent Loop & Local AST Fallback
├── requirements.txt      # Dependency configurations
├── test_sql/             # Verification folder with sample queries
└── README.md             # Project documentation
```

---

## 🛠️ Installation & Setup

### 1. Clone & Navigate to Project
```bash
cd C:\Users\avina\.gemini\antigravity\scratch\sql_query_linter
```

### 2. Configure Virtual Environment (Optional but Recommended)
```bash
python -m venv venv
# On Windows (PowerShell):
.\venv\Scripts\Activate.ps1
# On Linux/macOS:
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Provide Google Gemini API Key
To execute the Phase 2 AI engine, you need a Google Gemini API Key. Generate one for free from your [Google AI Studio dashboard](https://aistudio.google.com/).

* **CLI/Terminal Mode**: Export it as an environment variable:
  ```bash
  # PowerShell:
  $env:GEMINI_API_KEY="your-api-key-here"
  # Command Prompt (cmd):
  set GEMINI_API_KEY=your-api-key-here
  ```
* **Web UI Mode**: You can paste your key directly into the **🛠️ Configuration** panel on the left sidebar of the Streamlit dashboard, or add it to Streamlit Secrets.

---

## 🖥️ Usage

### 1. Launch the Streamlit Web Application
Run the following command in your terminal:
```bash
python -m streamlit run app.py
```
This will open the interactive dashboard in your default browser (usually at `http://localhost:8501`).

### 2. Run CLI Batch Scan
Run app.py directly with the `--dir` or `-d` flag targeting a directory containing `.sql` files:
```bash
python app.py --dir .\test_sql
```
This will process all candidate files in the directory and save the optimized queries as `<original_name>_fixed.sql`.

---

## 🧪 Example Optimization

### Raw Query Input:
```sql
select userId, employeeShiftStart, (select count(1) from roles r where r.userId = e.userId) as roleCount
from employeeTable e, shiftDetails s
where e.empId = s.employeeId and e.status = 'ACTIVE';
```

### Processed Output (Phase 1 & 2 LLM):
```sql
WITH role_counts AS (
  SELECT
    user_id,
    COUNT(1) AS role_count
  FROM roles
  GROUP BY
    user_id
)
SELECT
  e.user_id,
  e.employee_shift_start,
  COALESCE(rc.role_count, 0) AS role_count
FROM employee_table AS e
INNER JOIN shift_details AS s
  ON e.emp_id = s.employee_id
LEFT JOIN role_counts AS rc
  ON e.user_id = rc.user_id
WHERE
  e.status = 'ACTIVE';
```

