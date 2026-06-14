# AI Usage & Prompt Engineering Note

This document summarizes the role of AI (Google Gemini) in the development of the **SQL Query Linter & Style Fixer** application. It highlights the areas of assistance, early challenges/errors faced, and key prompts utilized to design the system.

---

## 💡 What AI Helped With

1. **Deterministic Phase 1 Parser**: Designing custom regex patterns to isolate comments and string literals, capitalising SQL keywords, and converting camelCase/PascalCase to `snake_case` safely.
2. **Phase 2 LLM Integration**: Incorporating the modern `google-genai` SDK and using `gemini-2.5-flash` with optimized instructions for AST-like database refactoring (nested queries to CTEs, implicit joins to explicit joins).
3. **Self-Correction Agent Loop**: Creating a lightweight local validation loop using `sqlglot`. The AI helped structure the loop context so that if local parsing fails, syntax errors are fed back to Gemini to recursively correct the code up to 3 times.
4. **Interactive Dashboard Styling**: Generating premium dark-themed styling (glassmorphism cards, HSL color palettes, custom Google Fonts typography) and implementing an in-memory batch uploader with download functionality to bypass cloud sandbox constraints.

---

## ⚠️ What AI Got Wrong & How it Was Fixed

During the iterative development process, the AI ran into several architectural and syntax design challenges that required correction:

1. **Markdown Formatting Stripping (Over-aggressive Regex)**:
   * *The Issue*: When stripping markdown asterisks (`*`) or underscores (`_`) from queries, the AI originally wrote a simple regex `re.sub(r'_([a-zA-Z0-9_]+)_', r'\1', sql)`. This inadvertently matched underscores inside valid snake_case column names (e.g. converting `employee_shift_start` into `employeeshiftstart`).
   * *The Fix*: The pattern was rewritten using negative lookbehinds and lookaheads:
     `r'(?<![a-zA-Z0-9_])_([a-zA-Z0-9_]+)_(?![a-zA-Z0-9_])'`
     This ensures only standalone word wrappers are stripped, preserving valid identifiers.

2. **Implicit Comma-Join Conversion**:
   * *The Issue*: The model initially struggled to reliably translate comma-joins (e.g., `FROM A, B WHERE A.id = B.id`) into explicit `INNER JOIN` statements, occasionally keeping the comma syntax while only changing casing.
   * *The Fix*: Few-shot learning examples were explicitly added to the system instruction prompt showing step-by-step transformations of implicit comma-joins and nested subqueries.

3. **Unicode Windows CLI Errors**:
   * *The Issue*: Emojis (e.g., `🟢`, `🔴`, `❌`, `✅`) printed to the console caused `UnicodeEncodeError` crashes on Windows command line environments.
   * *The Fix*: CLI print statements were refactored to use standard text tags (like `[Warning]` and `[Success]`), while retaining visual emojis exclusively for the Streamlit web browser UI.

---

## 🎯 Best Prompts Used

### 1. Implicit Join Refactoring (Few-shot engineering)
**Prompt:**
> *"Write a system prompt for gemini-2.5-flash that acts as a Database Administrator. Instruct it to convert legacy implicit joins in a query to modern explicit INNER JOIN ... ON syntax. Provide a clear few-shot example in the instruction showing `FROM employeeTable e, shiftDetails s WHERE e.empId = s.employeeId` refactoring into `FROM employee_table AS e INNER JOIN shift_details AS s ON e.emp_id = s.employee_id`. Enforce standard uppercase keywords and lowercase aliases."*

### 2. Standalone Markdown Format Stripping (Lookbehind/Lookahead regex)
**Prompt:**
> *"Write a Python regular expression function to strip formatting asterisks (`*` and `**`) and underscores (`_` and `__`) that wrap words in a query string (e.g. `*count*` to `count`). The regex must NOT match underscores that are inside snake_case words (like `employee_shift_start`), and it must NOT match mathematical multiplication symbols or SELECT * stars."*

### 3. Self-Correction Agent Loop Logic
**Prompt:**
> *"Design a Python loop using the google-genai SDK. It should send a query to gemini-2.5-flash, receive the SQL output, and attempt to parse it locally using `sqlglot.parse_one`. If parsing fails, catch the Exception, append the error message to the prompt, and ask the model to fix its syntax. Allow up to 3 correction iterations."*
