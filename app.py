import os
import sys
import argparse
import glob
import difflib
from typing import List, Tuple

# Import the local linter and LLM agent
from lint_engine import lint_sql
from llm_agent import refactor_sql_query

# Conditionally load streamlit
try:
    import streamlit as st
    HAS_STREAMLIT = True
except ImportError:
    HAS_STREAMLIT = False

def is_streamlit_running() -> bool:
    """
    Checks if the script is running inside a Streamlit instance.
    """
    if not HAS_STREAMLIT:
        return False
    try:
        from streamlit.runtime import exists
        return exists()
    except ImportError:
        return False

def process_directory(directory_path: str, api_key: str = None) -> List[dict]:
    """
    Scans the specified directory for .sql files (excluding _fixed.sql),
    applies local linter (Phase 1) and LLM refactoring (Phase 2),
    and saves the output to a transformed '_fixed.sql' file.
    """
    if api_key:
        os.environ["GEMINI_API_KEY"] = api_key
        
    if not os.path.exists(directory_path):
        raise FileNotFoundError(f"Directory not found: {directory_path}")
        
    search_path = os.path.join(directory_path, "*.sql")
    sql_files = glob.glob(search_path)
    
    results = []
    
    for file_path in sql_files:
        # Enforce idempotency: Skip already fixed files
        if file_path.endswith("_fixed.sql"):
            continue
            
        file_name = os.path.basename(file_path)
        fixed_file_name = file_name.replace(".sql", "_fixed.sql")
        fixed_file_path = os.path.join(directory_path, fixed_file_name)
        
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                raw_sql = f.read()
                
            # Step 1: Run Phase 1 Linter
            linted_sql, warnings = lint_sql(raw_sql)
            
            # Step 2: Run Phase 2 LLM Optimizer if API key is present
            if os.environ.get("GEMINI_API_KEY"):
                refactored_sql = refactor_sql_query(linted_sql)
            else:
                refactored_sql = linted_sql
                warnings.append("Skipped Phase 2 optimization: No Gemini API Key configured.")
                
            # Save transformed SQL
            with open(fixed_file_path, "w", encoding="utf-8") as f:
                f.write(refactored_sql)
                
            adjusted = raw_sql.strip() != linted_sql.strip()
            results.append({
                "file_name": file_name,
                "status": "Success",
                "warnings": warnings,
                "adjusted": adjusted,
                "error": None,
                "output_path": fixed_file_path
            })
            
        except Exception as e:
            results.append({
                "file_name": file_name,
                "status": "Failed",
                "warnings": [],
                "error": str(e),
                "output_path": None
            })
            
    return results

def run_streamlit_ui():
    """
    Renders the Streamlit Web Application interface.
    """
    st.set_page_config(
        page_title="SQL Query Linter & Style Fixer",
        page_icon="🔍",
        layout="wide"
    )
    
    # Inject premium styling with micro-animations & custom typography
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Outfit:wght@400;600;800&display=swap');
    
    .stApp {
        font-family: 'Inter', sans-serif;
        background-color: #0f172a;
        color: #f8fafc;
    }
    
    h1, h2, h3, h4, h5, h6 {
        font-family: 'Outfit', sans-serif;
        color: #f1f5f9 !important;
        font-weight: 600;
    }
    
    /* Header layout */
    .header-container {
        background: linear-gradient(135deg, #6366f1 0%, #06b6d4 50%, #4338ca 100%);
        padding: 2.5rem;
        border-radius: 16px;
        color: white;
        margin-bottom: 2rem;
        box-shadow: 0 10px 25px -5px rgba(99, 102, 241, 0.4);
    }
    
    .header-container h1 {
        color: white !important;
        margin: 0 0 0.5rem 0;
        font-size: 3rem;
        font-weight: 800;
        letter-spacing: -0.03em;
    }
    
    .header-container p {
        margin: 0;
        opacity: 0.95;
        font-size: 1.25rem;
        font-weight: 300;
    }
    
    /* Sleek card frames for columns */
    .section-card {
        background-color: #1e293b;
        padding: 2rem;
        border-radius: 14px;
        border: 1px solid #334155;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
        margin-bottom: 1.5rem;
        transition: transform 0.25s ease, box-shadow 0.25s ease;
    }
    
    .section-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 12px 20px -8px rgba(0, 0, 0, 0.5), 0 0 0 1px #4f46e5;
    }
    
    /* Warnings and custom badges */
    .warning-card {
        background: rgba(245, 158, 11, 0.1);
        border-left: 4px solid #f59e0b;
        padding: 0.75rem 1.25rem;
        border-radius: 6px;
        margin-bottom: 0.75rem;
        color: #fef3c7;
        font-size: 0.95rem;
    }
    
    .stButton>button {
        background: linear-gradient(90deg, #4f46e5 0%, #06b6d4 100%);
        color: white;
        border: none;
        padding: 0.6rem 1.5rem;
        border-radius: 8px;
        font-weight: 600;
        transition: all 0.2s ease-in-out;
    }
    
    .stButton>button:hover {
        background: linear-gradient(90deg, #6366f1 0%, #0891b2 100%);
        transform: scale(1.02);
        box-shadow: 0 5px 15px rgba(99, 102, 241, 0.4);
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Render Application Header
    st.markdown("""
    <div class="header-container">
        <h1>SQL Query Linter & Style Fixer</h1>
        <p>A high-performance hybrid optimization pipeline combining local parsing regex rules with LLM-based refactoring.</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Sidebar Setup for Config
    st.sidebar.title("🛠️ Configuration")
    
    # Always require the user to input their key in the UI
    api_key = st.sidebar.text_input(
        "Enter Google Gemini API Key:",
        type="password",
        key="api_key_sidebar",
        help="Required to optimize query architecture and run the Phase 2 LLM Agent."
    )
    if not api_key:
        st.sidebar.warning("⚠️ Phase 2 LLM Refactor requires an API Key.")
            
    st.sidebar.markdown("""
    ### 🚀 The Multi-Agent Pipeline
    - **Phase 1: Deterministic Linter**
      - Local regex execution.
      - Enforces uppercase SQL keywords.
      - Standardizes camelCase and PascalCase to snake_case.
      - Logs explicit `SELECT *` anti-patterns.
    - **Phase 2: LLM Refactor**
      - Leverages `gemini-2.5-flash`.
      - Extracts deep nested subqueries into clean CTEs.
      - Converts outdated implicit comma-joins into explicit `JOIN ... ON` statements.
    """)
    
    # Layout Split
    left_col, right_col = st.columns(2)
    
    # LEFT COLUMN: Directory scan pipeline
    with left_col:
        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        st.subheader("📂 Local Directory Scan Pipeline")
        st.write("Process multiple `.sql` queries inside a folder automatically. Results are saved as `*_fixed.sql`.")
        
        dir_path = st.text_input(
            "Target Directory Folder Path:",
            placeholder="e.g., C:/Users/avina/queries",
            key="scan_dir_path",
            help="Specify the absolute folder directory where raw .sql files reside."
        )
        
        scan_button = st.button("Scan & Optimize Folder", key="scan_dir_btn", use_container_width=True)
        
        if scan_button:
            if not dir_path.strip():
                st.error("Please provide a valid directory path.")
            elif not os.path.exists(dir_path):
                st.error("The specified path does not exist on your filesystem.")
            elif not api_key:
                st.error("A Gemini API Key is required for the optimization pipeline. Please set it in the sidebar.")
            else:
                with st.spinner("Executing hybrid processing pipeline on folder..."):
                    try:
                        results = process_directory(dir_path, api_key)
                        
                        if not results:
                            st.info("No candidate SQL files found in the directory (or all matching queries are already fixed).")
                        else:
                            st.success(f"Processing complete! Batch summary below:")
                            
                            for res in results:
                                status_color = "🟢" if res["status"] == "Success" else "🔴"
                                with st.expander(f"{status_color} {res['file_name']} — {res['status']}", expanded=True):
                                    if res["status"] == "Success":
                                        st.write(f"💾 **Output location:** `{res['output_path']}`")
                                        if res["warnings"]:
                                            for w in res["warnings"]:
                                                st.markdown(f'<div class="warning-card">⚠️ {w}</div>', unsafe_allow_html=True)
                                        
                                        if res["adjusted"]:
                                            st.info("🎨 Style adjustments applied! Standardized casing and keywords.")
                                        elif not res["warnings"]:
                                            st.success("✅ Clean baseline code: No style violations or select star anti-patterns found.")
                                    else:
                                        st.error(f"Failed to process file: {res['error']}")
                                        error_msg = str(res["error"])
                                        if "API_KEY" in error_msg or "API key" in error_msg or "APIError" in error_msg or "400" in error_msg or "403" in error_msg or "Invalid" in error_msg:
                                            st.markdown(
                                                '<div class="warning-card">⚠️ **API Key Error:** The Gemini API key you entered appears to be invalid, expired, or restricted.<br><br>'
                                                '**How to fix:** Generate a free API key from your own '
                                                '<a href="https://aistudio.google.com/" target="_blank">Google AI Studio dashboard</a> '
                                                'and paste it into the <b>Enter Google Gemini API Key</b> '
                                                'input field in the left sidebar configuration.</div>',
                                                unsafe_allow_html=True
                                            )
                    except Exception as e:
                        st.error(f"An error occurred during scanning: {e}")
        st.markdown('</div>', unsafe_allow_html=True)
        
    # RIGHT COLUMN: Sandbox playground
    with right_col:
        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        st.subheader("🧪 Interactive Sandbox Playground")
        st.write("Paste a custom query to view real-time style transformation and SQL refactoring outputs.")
        
        example_sql = """select userId, employeeShiftStart, (select count(1) from roles r where r.userId = e.userId) as roleCount
from employeeTable e, shiftDetails s
where e.empId = s.employeeId and e.status = 'ACTIVE';"""
        
        raw_sql_input = st.text_area(
            "Raw SQL Input:",
            value=example_sql,
            height=180,
            key="raw_sql_input_area"
        )
        
        refactor_button = st.button("Optimize & Refactor Query", key="refactor_query_btn", use_container_width=True)
        
        if refactor_button:
            if not raw_sql_input.strip():
                st.error("Please enter some SQL code to process.")
            else:
                # Run Phase 1
                with st.spinner("Phase 1: Deterministic Linter formatting..."):
                    linted_sql, warnings = lint_sql(raw_sql_input)
                
                # Run Phase 2
                refactored_sql = ""
                has_error = False
                
                if api_key:
                    with st.spinner("Phase 2: LLM Refactor agent optimizing..."):
                        try:
                            os.environ["GEMINI_API_KEY"] = api_key
                            refactored_sql = refactor_sql_query(linted_sql)
                        except Exception as e:
                            error_msg = str(e)
                            refactored_sql = f"-- Error executing Phase 2 LLM Agent:\n-- {error_msg}"
                            has_error = True
                            
                            # Check if the error is likely due to an invalid/expired key
                            if "API_KEY" in error_msg or "API key" in error_msg or "APIError" in error_msg or "400" in error_msg or "403" in error_msg or "Invalid" in error_msg:
                                st.session_state["api_key_error_banner"] = (
                                    "⚠️ **API Key Error:** The Gemini API key you entered appears to be invalid, expired, or restricted.\n\n"
                                    "**How to fix:**\n"
                                    "1. Generate a free API key from your own [Google AI Studio dashboard](https://aistudio.google.com/).\n"
                                    "2. Copy the key and paste it into the **Enter Google Gemini API Key** input field in the left sidebar configuration."
                                )
                else:
                    refactored_sql = "-- SKIPPED Phase 2 Optimization. (Gemini API Key was not provided in sidebar)"
                    has_error = True
                
                # Render validation banner if error is present
                if has_error and "api_key_error_banner" in st.session_state:
                    st.markdown(f'<div class="warning-card">{st.session_state["api_key_error_banner"]}</div>', unsafe_allow_html=True)
                    # Clean up session state
                    del st.session_state["api_key_error_banner"]
                    
                # Render results tabs
                tab1, tab2, tab3 = st.tabs(["✨ Optimized Query", "🔍 Phase 1 Linter Report", "📊 Diff Comparison"])
                
                with tab1:
                    st.write("### Final Refactored SQL Output")
                    st.code(refactored_sql, language="sql")
                    if has_error:
                        st.warning("Only Phase 1 formatting could be completed successfully.")
                        
                with tab2:
                    st.write("### Phase 1: Local Deterministic Linter")
                    if warnings:
                        for w in warnings:
                            st.markdown(f'<div class="warning-card">⚠️ {w}</div>', unsafe_allow_html=True)
                    
                    if raw_sql_input.strip() == linted_sql.strip():
                        if not warnings:
                            st.success("✅ Clean baseline code: No style violations or select star anti-patterns found.")
                    else:
                        st.info("🎨 Style adjustments applied! Standardized casing and keywords.")
                        
                    st.write("#### Baseline Capitalized & snake_cased SQL:")
                    st.code(linted_sql, language="sql")
                    
                with tab3:
                    st.write("### Structure Diff Comparison")
                    diff_target = linted_sql if has_error else refactored_sql
                    diff_lines = list(difflib.unified_diff(
                        raw_sql_input.splitlines(),
                        diff_target.splitlines(),
                        fromfile="Raw SQL Input",
                        tofile="Optimized Output",
                        lineterm=""
                    ))
                    if diff_lines:
                        st.code("\n".join(diff_lines), language="diff")
                    else:
                        st.info("No modifications detected.")
        st.markdown('</div>', unsafe_allow_html=True)

def run_cli():
    """
    Renders and executes the Command Line Interface (CLI) command pipeline.
    """
    parser = argparse.ArgumentParser(description="SQL Query Linter & Style Fixer CLI")
    parser.add_argument(
        "--dir", "-d",
        type=str,
        required=True,
        help="Absolute path to local folder containing your .sql query files."
    )
    args = parser.parse_args()
    
    directory = args.dir
    if not os.path.exists(directory):
        print(f"Error: Directory '{directory}' does not exist on this machine.", file=sys.stderr)
        sys.exit(1)
        
    print("\n" + "="*70)
    print(" SQL QUERY LINTER & STYLE FIXER - HYBRID PIPELINE ")
    print("="*70)
    print(f"Scanning Target Directory: {os.path.abspath(directory)}")
    
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        print("Warning: GEMINI_API_KEY variable is not set. Execution will fall back to Phase 1 only.", file=sys.stderr)
        
    search_path = os.path.join(directory, "*.sql")
    sql_files = glob.glob(search_path)
    
    processed = 0
    skipped = 0
    failed = 0
    
    for file_path in sql_files:
        if file_path.endswith("_fixed.sql"):
            skipped += 1
            continue
            
        file_name = os.path.basename(file_path)
        print(f"\n[+] File: {file_name}")
        
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                raw_sql = f.read()
                
            # Phase 1: Local Deterministic Linter
            linted_sql, warnings = lint_sql(raw_sql)
            if warnings:
                for w in warnings:
                    print(f"    [Warning] {w}")
            else:
                print("    [Success] Phase 1: Local formatting applied successfully.")
                
            # Phase 2: LLM Optimization Refactor
            if api_key:
                print("    [Refactoring] Phase 2: Refactoring with gemini-2.5-flash...")
                refactored_sql = refactor_sql_query(linted_sql)
            else:
                print("    [Skipped] Phase 2: Skipped (no API key configured). Saving Phase 1 changes only.")
                refactored_sql = linted_sql
                
            # Save transformed SQL
            fixed_file_name = file_name.replace(".sql", "_fixed.sql")
            fixed_file_path = os.path.join(directory, fixed_file_name)
            with open(fixed_file_path, "w", encoding="utf-8") as f:
                f.write(refactored_sql)
                
            print(f"    [Saved] {fixed_file_name}")
            processed += 1
            
        except Exception as e:
            print(f"    [Failed] {e}", file=sys.stderr)
            failed += 1
            
    print("\n" + "="*70)
    print(" BATCH EXECUTION RUN SUMMARY ")
    print("="*70)
    print(f"Processed: {processed} file(s) successfully.")
    print(f"Failed:    {failed} file(s).")
    print(f"Skipped:   {skipped} file(s) (idempotent matching).")
    print("="*70 + "\n")

if __name__ == "__main__":
    if is_streamlit_running():
        run_streamlit_ui()
    else:
        # CLI Entry-Point Mode
        if len(sys.argv) > 1:
            run_cli()
        else:
            print("\n" + "="*65)
            print("         SQL Query Linter & Style Fixer Orchestrator")
            print("="*65)
            print("This script supports two running modes:")
            print("\n1. Web Interface (Streamlit Dashboard)")
            print("   Execute the following in your shell:")
            print("   streamlit run app.py")
            print("\n2. Command Line Interface (CLI Batch Scan)")
            print("   Execute the following in your shell:")
            print("   python app.py --dir <directory_path>")
            print("="*65 + "\n")
