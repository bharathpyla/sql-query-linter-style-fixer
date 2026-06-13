import re
from typing import List, Tuple

# Core keywords to capitalize
KEYWORDS = {
    "SELECT", "FROM", "WHERE", "JOIN", "ON", "AND", "OR", "WITH", "AS", 
    "GROUP", "BY", "ORDER", "LIMIT", "HAVING", "LEFT", "RIGHT", "INNER", 
    "OUTER", "CROSS", "USING", "UNION", "ALL", "INSERT", "UPDATE", "DELETE", 
    "CREATE", "TABLE", "INTO", "VALUES", "CASE", "WHEN", "THEN", "ELSE", 
    "END", "NOT", "IN", "IS", "NULL", "LIKE", "EXISTS", "BETWEEN", "ASC", "DESC"
}

def camel_to_snake(name: str) -> str:
    """
    Converts camelCase or PascalCase identifiers into lowercase snake_case.
    e.g., userId -> user_id, EmployeeShiftStart -> employee_shift_start
    """
    s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
    return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()

def clean_sql_spacing(sql: str) -> str:
    """
    Ensures correct spacing around dots and commas in code segments.
    Leaves text inside comments and string literals completely untouched.
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
        code_segment = sql[last_idx:start]
        
        # Clean segment using horizontal space matches [ \t] to avoid stripping newlines
        cleaned = re.sub(r'(\b[a-zA-Z0-9_]+)[ \t]*\.[ \t]*([a-zA-Z0-9_]+\b)', r'\1.\2', code_segment)
        cleaned = re.sub(r'[ \t]*,[ \t]*', ', ', cleaned)
        cleaned = re.sub(r'[ \t]+(\r?\n)', r'\1', cleaned)
        parts.append(cleaned)
        
        parts.append(match.group(0))
        last_idx = end
        
    code_segment = sql[last_idx:]
    cleaned = re.sub(r'(\b[a-zA-Z0-9_]+)[ \t]*\.[ \t]*([a-zA-Z0-9_]+\b)', r'\1.\2', code_segment)
    cleaned = re.sub(r'[ \t]*,[ \t]*', ', ', cleaned)
    cleaned = re.sub(r'[ \t]+(\r?\n)', r'\1', cleaned)
    parts.append(cleaned)
    
    return "".join(parts).rstrip()

def lint_sql(sql: str) -> Tuple[str, List[str]]:
    """
    Phase 1: Deterministic Linter Agent
    - Capitalizes core SQL keywords.
    - Converts camelCase / PascalCase identifiers to lowercase snake_case.
    - Identifies and logs explicit 'SELECT *' anti-patterns.
    
    Returns:
        - The formatted SQL query.
        - A list of warning messages (if any).
    """
    pattern = re.compile(
        r'(?P<comment>--.*$|/\*[\s\S]*?\*/)'
        r'|(?P<string>\'(?:\'\'|[^\'])*\'|"(?:""|[^"])*")'
        r'|(?P<word>[a-zA-Z_][a-zA-Z0-9_]*)'
        r'|(?P<other>[\s\S])',
        re.MULTILINE
    )
    
    warnings = []
    
    # Check for SELECT * (after stripping comments to avoid false positives)
    comment_stripped_parts = []
    for match in pattern.finditer(sql):
        if not match.group('comment'):
            comment_stripped_parts.append(match.group(0))
    comment_stripped_sql = "".join(comment_stripped_parts)
    
    if re.search(r'\bSELECT\s+\*', comment_stripped_sql, re.IGNORECASE):
        warnings.append("Anti-pattern warning: Explicit 'SELECT *' detected. Retrieve only necessary columns to minimize cloud data processing costs and improve efficiency.")
        
    output_parts = []
    
    for match in pattern.finditer(sql):
        comment = match.group('comment')
        string_lit = match.group('string')
        word = match.group('word')
        other = match.group('other')
        
        if comment:
            output_parts.append(comment)
        elif string_lit:
            output_parts.append(string_lit)
        elif word:
            word_upper = word.upper()
            if word_upper in KEYWORDS:
                output_parts.append(word_upper)
            else:
                # Identify if it's camelCase or PascalCase (mix of lower and upper)
                has_lower = any(c.islower() for c in word)
                has_upper = any(c.isupper() for c in word)
                if has_lower and has_upper:
                    output_parts.append(camel_to_snake(word))
                else:
                    output_parts.append(word)
        elif other:
            output_parts.append(other)
            
    raw_linted = "".join(output_parts)
    cleaned_linted = clean_sql_spacing(raw_linted)
    
    return cleaned_linted, warnings
