import os
import re
from google import genai
from google.genai import types
from google.genai.errors import APIError

# Try to import sqlglot for local syntax validation and AST refactoring
try:
    import sqlglot
    HAS_SQLGLOT = True
except ImportError:
    HAS_SQLGLOT = False

def clean_segment(text: str) -> str:
    """
    Cleans up aggressive spacing around dots and commas in code segments.
    e.g., 'u . user_id' -> 'u.user_id', 'a , b' -> 'a, b'
    """
    # Replace spaces around dot: e.g., "u . user_id" -> "u.user_id"
    text = re.sub(r'(\b[a-zA-Z0-9_]+)[ \t]*\.[ \t]*([a-zA-Z0-9_]+\b)', r'\1.\2', text)
    # Replace spaces around comma: e.g., "user_id , email" -> "user_id, email"
    text = re.sub(r'[ \t]*,[ \t]*', ', ', text)
    # Clean up trailing spaces from lines that have a comma at the end
    text = re.sub(r'[ \t]+(\r?\n)', r'\1', text)
    return text

def clean_llm_spaces(sql: str) -> str:
    """
    Tokenizes SQL to isolate comments and strings, then cleans spacing
    around dots and commas in the raw code segments.
    """
    pattern = re.compile(
        r'(?P<comment>--.*$|/\*[\s\S]*?\*/)'
        r'|(?P<string>\'(?:\'\'|[^\'])*\'|"(?:""|[^"])*")',
        re.MULTILINE
    )
    
    last_idx = 0
    parts = []
    
    for match in pattern.finditer(sql):
        start, end = match.span()
        # Segment before the match is code, clean it
        code_segment = sql[last_idx:start]
        parts.append(clean_segment(code_segment))
        
        # Keep comment or string as is
        parts.append(match.group(0))
        last_idx = end
        
    # Final segment of code
    code_segment = sql[last_idx:]
    parts.append(clean_segment(code_segment))
    
    return "".join(parts)

def local_refactor_sql(sql: str) -> str:
    """
    Performs a local, rule-based structural refactor using sqlglot's AST engine.
    Pretty-prints the query, standardizes keyword casing, and validates structure.
    """
    if not HAS_SQLGLOT:
        return f"-- Local AST Refactoring skipped (sqlglot package not available).\n\n{sql}"
        
    try:
        # Parse the query using sqlglot
        parsed = sqlglot.parse_one(sql)
        # Generate pretty-printed SQL
        return parsed.sql(pretty=True)
    except Exception as e:
        # Return fallback with parsing error commented out
        return f"-- Local AST Parsing Notice: {e}\n\n{sql}"

def refactor_sql_query(sql: str) -> str:
    """
    Phase 2: LLM Refactor Agent (with Self-Correction Agent Loop)
    Sends the pre-formatted SQL query to gemini-2.5-flash to:
    - Refactor nested subqueries into clean Common Table Expressions (CTEs).
    - Convert implicit joins (comma in FROM clause) to explicit modern SQL JOINs.
    - Optimize overall structure and performance while preserving business logic.
    - Output raw executable SQL code only (no conversational text or markdown blocks).
    
    If sqlglot is installed, it runs a self-correction loop up to 3 times:
    - Validates generated SQL syntax locally.
    - If syntactically invalid, feeds back the parsing error to the LLM to fix.
    """
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise ValueError(
            "GEMINI_API_KEY environment variable is missing. "
            "Please set your GEMINI_API_KEY in the environment or input it in the UI sidebar before running Phase 2."
        )
        
    try:
        # Initialize Google GenAI client (picks up GEMINI_API_KEY from environment)
        client = genai.Client()
    except Exception as e:
        raise RuntimeError(f"Failed to initialize Google GenAI Client: {e}")
        
    system_instruction = (
        "You are an expert Principal Database Administrator and SQL Solutions Architect.\n"
        "Your goal is to refactor and optimize the provided SQL query. You must strictly follow these rules:\n"
        "1. Refactor deep, nested subqueries into clean, named Common Table Expressions (CTEs) to improve readability.\n"
        "2. Convert all implicit joins (e.g., 'FROM table_a, table_b WHERE table_a.id = table_b.id') into explicit modern SQL joins "
        "(e.g., 'FROM table_a INNER JOIN table_b ON table_a.id = table_b.id') based on query intent.\n"
        "3. Ensure all table columns referenced in joins and selections have clear aliases where appropriate.\n"
        "4. Ensure all table aliases and alias references are strictly lowercased consistently throughout the query "
        "(e.g., use 'e.user_id' and 'urc.role_count' instead of uppercase aliases like 'E.user_id' or 'URC.role_count').\n"
        "5. Return the refactored SQL with standard, compact left-aligned formatting (no aggressive tab spaces or double indentations at the start of lines).\n"
        "6. Preserve the exact business logic and result set structure of the original query.\n"
        "7. Maintain consistent uppercase formatting for standard SQL keywords.\n"
        "8. Do NOT insert spaces around dots (.) or commas (,). Always write table/column aliases compactly (e.g., 'u.user_id' instead of 'u . user_id').\n"
        "9. Output ONLY valid, raw, executable SQL. Do NOT wrap the query in markdown formatting like ```sql or ```. Do NOT include any explanations, greetings, warnings, or notes in the output. The response must contain nothing but the query itself."
    )
    
    config = types.GenerateContentConfig(
        temperature=0.1,
        system_instruction=system_instruction,
    )
    
    max_iterations = 3
    current_prompt = sql
    last_error = None
    refined_sql = ""
    
    for i in range(max_iterations):
        try:
            # Call gemini-2.5-flash
            response = client.models.generate_content(
                model='gemini-2.5-flash',
                contents=current_prompt,
                config=config,
            )
            
            if not response.text:
                raise RuntimeError("Received empty response from Gemini model.")
                
            refined_sql = response.text.strip()
            
            # Post-process response to guarantee no markdown fences are returned
            if refined_sql.startswith("```"):
                refined_sql = re.sub(r"^```[a-zA-Z]*\n?", "", refined_sql)
                refined_sql = re.sub(r"\n?```$", "", refined_sql)
                refined_sql = refined_sql.strip()
                
            # Clean any spaces around dots and commas that may have slipped through
            refined_sql = clean_llm_spaces(refined_sql)
            
            # Syntax validation using sqlglot (if available)
            if HAS_SQLGLOT:
                try:
                    sqlglot.parse_one(refined_sql)
                    # If parsing succeeded, the SQL is valid! Return immediately.
                    return refined_sql
                except Exception as parse_err:
                    last_error = parse_err
                    # Syntax error detected, feed it back into the loop context
                    current_prompt = (
                        f"Your previous refactored SQL attempt had a syntax validation error: {parse_err}.\n"
                        f"Please fix the syntax error and output the correct SQL query.\n"
                        f"Original input SQL:\n{sql}\n\n"
                        f"Incorrect SQL attempt:\n{refined_sql}"
                    )
            else:
                # If sqlglot is not installed, return the raw query without validation
                return refined_sql
                
        except APIError as e:
            raise RuntimeError(f"Google GenAI API Error: {e}")
        except Exception as e:
            # If we hit an unexpected error, raise it on the final attempt
            if i == max_iterations - 1:
                raise RuntimeError(f"Unexpected error during SQL Refactoring: {e}")
                
    # If the loop finished without returning, the agent failed to generate valid SQL
    raise RuntimeError(
        f"SQL Refactor Agent failed to generate syntactically valid SQL after {max_iterations} attempts.\n"
        f"Last validation error: {last_error}\n\nLast generated query:\n{refined_sql}"
    )
