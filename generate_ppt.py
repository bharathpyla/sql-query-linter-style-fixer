import collections
import collections.abc
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN
from pptx.enum.shapes import MSO_SHAPE

# Premium Dark Cyber/Teal Corporate Theme Palette
COLOR_BG = RGBColor(11, 19, 36)          # Dark Obsidian/Slate (Sleek deep navy background)
COLOR_TITLE = RGBColor(248, 250, 252)    # Slate 50 (Crisp off-white for titles)
COLOR_BODY = RGBColor(203, 213, 225)     # Slate 300 (Light silver-gray for high readability)
COLOR_ACCENT = RGBColor(34, 211, 238)    # Cyan 400 (Vibrant electric cyan for secondary highlights/accents)
COLOR_MUTED = RGBColor(100, 116, 139)    # Slate 500 (Muted gray for footnotes and line decorations)
COLOR_CARD_BG = RGBColor(22, 32, 59)     # Slate 800 (Contrasting background card color)

def apply_background(slide):
    background = slide.background
    fill = background.fill
    fill.solid()
    fill.fore_color.rgb = COLOR_BG

def add_divider_line(slide, left, top, width, height, color):
    shape = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, left, top, width, height)
    shape.fill.solid()
    shape.fill.fore_color.rgb = color
    shape.line.fill.background()  # Remove shape border
    return shape

def add_footer(slide):
    footer_box = slide.shapes.add_textbox(Inches(0.75), Inches(6.9), Inches(11.83), Inches(0.3))
    tf = footer_box.text_frame
    tf.word_wrap = True
    tf.margin_left = tf.margin_top = tf.margin_right = tf.margin_bottom = 0
    p = tf.paragraphs[0]
    p.text = "SQL Query Linter & Style Fixer  |  Developed by Team 20"
    p.font.name = 'Segoe UI'
    p.font.size = Pt(10)
    p.font.color.rgb = COLOR_MUTED
    p.alignment = PP_ALIGN.LEFT

def add_title(slide, text):
    title_box = slide.shapes.add_textbox(Inches(0.75), Inches(0.5), Inches(11.83), Inches(0.8))
    tf = title_box.text_frame
    tf.word_wrap = True
    tf.margin_left = tf.margin_top = tf.margin_right = tf.margin_bottom = 0
    p = tf.paragraphs[0]
    p.text = text
    p.font.name = 'Segoe UI'
    p.font.size = Pt(32)
    p.font.bold = True
    p.font.color.rgb = COLOR_TITLE
    
    # Elegant thin neon accent divider line under title
    add_divider_line(slide, Inches(0.75), Inches(1.3), Inches(11.83), Inches(0.03), COLOR_ACCENT)
    
    # Add slide footer
    add_footer(slide)
    return title_box

def build_presentation():
    prs = Presentation()
    prs.slide_width = Inches(13.33)
    prs.slide_height = Inches(7.5)
    
    # Slide layouts: index 6 is blank
    blank_layout = prs.slide_layouts[6]
    
    # ----------------------------------------------------
    # SLIDE 1: Title Slide (Premium Dark landing style)
    # ----------------------------------------------------
    slide1 = prs.slides.add_slide(blank_layout)
    apply_background(slide1)
    
    # Elegant top accent bar
    add_divider_line(slide1, Inches(0), Inches(0), Inches(13.33), Inches(0.1), COLOR_ACCENT)
    
    # Large Title Box
    title_box = slide1.shapes.add_textbox(Inches(0.75), Inches(1.5), Inches(11.83), Inches(2.2))
    tf = title_box.text_frame
    tf.word_wrap = True
    tf.margin_left = tf.margin_top = tf.margin_right = tf.margin_bottom = 0
    p1 = tf.paragraphs[0]
    p1.text = "SQL Query Linter & Style Fixer"
    p1.font.name = 'Segoe UI'
    p1.font.size = Pt(50)
    p1.font.bold = True
    p1.font.color.rgb = COLOR_TITLE
    
    p2 = tf.add_paragraph()
    p2.text = "Hybrid Local-AI Database Optimization Pipeline"
    p2.font.name = 'Segoe UI'
    p2.font.size = Pt(22)
    p2.font.bold = True
    p2.font.color.rgb = COLOR_ACCENT
    p2.space_before = Pt(12)
    
    # Title divider line
    add_divider_line(slide1, Inches(0.75), Inches(4.0), Inches(11.83), Inches(0.02), COLOR_MUTED)
    
    # Team Info Box
    team_box = slide1.shapes.add_textbox(Inches(0.75), Inches(4.3), Inches(11.83), Inches(2.5))
    tf_team = team_box.text_frame
    tf_team.word_wrap = True
    tf_team.margin_left = tf_team.margin_top = tf_team.margin_right = tf_team.margin_bottom = 0
    
    p_team_hdr = tf_team.paragraphs[0]
    p_team_hdr.text = "DEVELOPED BY: TEAM 20"
    p_team_hdr.font.name = 'Segoe UI'
    p_team_hdr.font.size = Pt(13)
    p_team_hdr.font.bold = True
    p_team_hdr.font.color.rgb = COLOR_ACCENT
    p_team_hdr.space_after = Pt(8)
    
    members = [
        "Penta Satwika (23U41A4245) - Lead Streamlit UI & Dashboard Developer",
        "Bharath Pyla (23U41A0536) - Core SQL Parser & Spacing Engine Architect",
        "Aythi Eswar (23U41A0406) - Gemini LLM Prompt Engineer & AI Architect",
        "Dadi James (24U45A0212) - AST Validation Loop & QA Tester"
    ]
    
    for member in members:
        p_mem = tf_team.add_paragraph()
        p_mem.text = member
        p_mem.font.name = 'Segoe UI'
        p_mem.font.size = Pt(12.5)
        p_mem.font.color.rgb = COLOR_BODY
        p_mem.space_before = Pt(3)
        
    # ----------------------------------------------------
    # SLIDE 2: Objective
    # ----------------------------------------------------
    slide2 = prs.slides.add_slide(blank_layout)
    apply_background(slide2)
    add_title(slide2, "Objective")
    
    content_box2 = slide2.shapes.add_textbox(Inches(0.75), Inches(1.8), Inches(11.83), Inches(4.8))
    tf2 = content_box2.text_frame
    tf2.word_wrap = True
    tf2.margin_left = tf2.margin_top = tf2.margin_right = tf2.margin_bottom = 0
    
    p2_body = tf2.paragraphs[0]
    p2_body.text = "To build a robust database utility that automates layout formatting, syntax cleansing, and structural optimization for database development teams by merging client-side deterministic parsers with serverless Large Language Models."
    p2_body.font.name = 'Segoe UI'
    p2_body.font.size = Pt(19)
    p2_body.font.color.rgb = COLOR_BODY
    p2_body.space_after = Pt(20)
    
    objectives = [
        "Standardize mixed casings (camelCase/PascalCase) into uniform lowercase snake_case.",
        "Enforce SQL keywords capitalization rules locally at zero compute cost.",
        "Isolate and purge markdown formatting artifacts to safeguard downstream compiler integrity.",
        "Refactor implicit comma-joins and nested subqueries into explicit joins and Common Table Expressions (CTEs) via AI logic.",
        "Secure syntax correctness using an in-memory Abstract Syntax Tree validation loop."
    ]
    
    for obj in objectives:
        p_bullet = tf2.add_paragraph()
        p_bullet.text = f"\u2022  {obj}"
        p_bullet.font.name = 'Segoe UI'
        p_bullet.font.size = Pt(15)
        p_bullet.font.color.rgb = COLOR_BODY
        p_bullet.space_before = Pt(8)
        
    # ----------------------------------------------------
    # SLIDE 3: Problem Statement
    # ----------------------------------------------------
    slide3 = prs.slides.add_slide(blank_layout)
    apply_background(slide3)
    add_title(slide3, "Problem Statement")
    
    content_box3 = slide3.shapes.add_textbox(Inches(0.75), Inches(1.8), Inches(11.83), Inches(4.8))
    tf3 = content_box3.text_frame
    tf3.word_wrap = True
    tf3.margin_left = tf3.margin_top = tf3.margin_right = tf3.margin_bottom = 0
    
    problems = [
        "Inconsistent Casing: Mixed naming structures (camelCase, PascalCase, lowercase) create style violations and audit complications.",
        "Legacy Join Syntax: Extensive usage of implicit comma-joins (e.g., FROM TableA, TableB WHERE A.id = B.id) obscures join pathways and increases maintenance overhead.",
        "Complex Subquery Nesting: Deeply nested SELECT projections decrease readability and limit database optimizer index lookup performance.",
        "Cost Inflation: Unrestricted use of SELECT * drives up cloud data processing costs under pay-per-query models.",
        "Validation Vulnerability: Rule-based linters only clean basic whitespace, whereas raw LLM optimization agents can hallucinate and generate syntactically broken SQL queries."
    ]
    
    for i, prob in enumerate(problems):
        p_prob = tf3.add_paragraph() if i > 0 else tf3.paragraphs[0]
        p_prob.text = f"\u2022  {prob}"
        p_prob.font.name = 'Segoe UI'
        p_prob.font.size = Pt(15.5)
        p_prob.font.color.rgb = COLOR_BODY
        p_prob.space_after = Pt(12)
        
    # ----------------------------------------------------
    # SLIDE 4: Technologies Used (With high-contrast layout)
    # ----------------------------------------------------
    slide4 = prs.slides.add_slide(blank_layout)
    apply_background(slide4)
    add_title(slide4, "Technologies Used")
    
    content_box4 = slide4.shapes.add_textbox(Inches(0.75), Inches(1.8), Inches(11.83), Inches(4.8))
    tf4 = content_box4.text_frame
    tf4.word_wrap = True
    tf4.margin_left = tf4.margin_top = tf4.margin_right = tf4.margin_bottom = 0
    
    techs = [
        ("Python", "Core language for deterministic regex compilation, script execution, and API routing."),
        ("Streamlit Framework", "For designing the user interface dashboard workspace, the batch file uploader, and in-memory downloads."),
        ("Google Gemini API (gemini-2.5-flash)", "Serverless AI model utilized for semantic query refactoring (CTEs, Joins) configured with low temperature (0.1) and few-shot examples."),
        ("sqlglot Parser", "Local dialect-aware parser used to pretty-print statements and validate AST syntax inside the correction loop."),
        ("difflib", "Native engine used to compile unified diff reports between raw query inputs and optimized outputs.")
    ]
    
    for i, (tech, desc) in enumerate(techs):
        p_tech = tf4.add_paragraph() if i > 0 else tf4.paragraphs[0]
        p_tech.text = f"\u2022  {tech}: "
        p_tech.font.name = 'Segoe UI'
        p_tech.font.size = Pt(15.5)
        p_tech.font.bold = True
        p_tech.font.color.rgb = COLOR_ACCENT
        
        run = p_tech.add_run()
        run.text = desc
        run.font.name = 'Segoe UI'
        run.font.size = Pt(15.5)
        run.font.bold = False
        run.font.color.rgb = COLOR_BODY
        p_tech.space_after = Pt(10)
        
    # ----------------------------------------------------
    # SLIDE 5: System Architecture & Workflow
    # ----------------------------------------------------
    slide5 = prs.slides.add_slide(blank_layout)
    apply_background(slide5)
    add_title(slide5, "System Architecture & Workflow")
    
    content_box5 = slide5.shapes.add_textbox(Inches(0.75), Inches(1.8), Inches(11.83), Inches(4.8))
    tf5 = content_box5.text_frame
    tf5.word_wrap = True
    tf5.margin_left = tf5.margin_top = tf5.margin_right = tf5.margin_bottom = 0
    
    p5_hdr = tf5.paragraphs[0]
    p5_hdr.text = "Sequential Processing Pipeline Layout"
    p5_hdr.font.name = 'Segoe UI'
    p5_hdr.font.size = Pt(17)
    p5_hdr.font.bold = True
    p5_hdr.font.color.rgb = COLOR_ACCENT
    p5_hdr.space_after = Pt(16)
    
    flow_steps = [
        "1. Query Input -> Sandbox Area, File Uploader, or CLI batch scanner reads statement.",
        "2. Input Sanitization -> strip_markdown_artifacts() strips code blocks, bold asterisks, and italic underscores safely.",
        "3. Phase 1 Linter -> Deterministic capitalization of standard keywords, regex-based conversion of camelCase to snake_case, and SELECT * diagnostic checks.",
        "4. Phase 2 Refactor -> gemini-2.5-flash receives baseline formatting and optimizes syntax structures (implicit joins to explicit joins, subqueries to CTEs).",
        "5. Self-Correction Loop -> Output SQL is evaluated by local parser. If syntax errors occur, the traceback is fed back to the LLM to self-heal (up to 3 iterations).",
        "6. Finalization -> Renders refactored SQL inside copyable st.code frames and outputs colored diff blocks."
    ]
    
    for step in flow_steps:
        p_step = tf5.add_paragraph()
        p_step.text = step
        p_step.font.name = 'Segoe UI'
        p_step.font.size = Pt(14)
        p_step.font.color.rgb = COLOR_BODY
        p_step.space_after = Pt(8)
        
    # ----------------------------------------------------
    # SLIDE 6: Modules Overview
    # ----------------------------------------------------
    slide6 = prs.slides.add_slide(blank_layout)
    apply_background(slide6)
    add_title(slide6, "Modules Overview")
    
    content_box6 = slide6.shapes.add_textbox(Inches(0.75), Inches(1.8), Inches(11.83), Inches(4.8))
    tf6 = content_box6.text_frame
    tf6.word_wrap = True
    tf6.margin_left = tf6.margin_top = tf6.margin_right = tf6.margin_bottom = 0
    
    modules = [
        ("Sanitization & Cleaning Module", "Contains lookbehind/lookahead regular expressions that clean styling artifacts from incoming text without corrupting snake_case columns."),
        ("Phase 1: Local Linter Module", "Zero-cost deterministic casing cleaner and capitalization compiler. Enforces standard keywords and casing conventions locally before network calls."),
        ("Phase 2: AI Refactoring Module", "Leverages Gemini LLM with few-shot instructions to translate legacy comma-joins and extract subqueries into CTEs."),
        ("Validation & Critic Module", "Compares LLM outputs against local syntax rules using sqlglot, orchestrating the self-correcting logic loop if discrepancies are found."),
        ("Interface & Download Module", "Manages dual Streamlit and CLI interfaces, in-memory uploads, diff blocks rendering, and download actions.")
    ]
    
    for i, (mod, desc) in enumerate(modules):
        p_mod = tf6.add_paragraph() if i > 0 else tf6.paragraphs[0]
        p_mod.text = f"\u2022  {mod}: "
        p_mod.font.name = 'Segoe UI'
        p_mod.font.size = Pt(15)
        p_mod.font.bold = True
        p_mod.font.color.rgb = COLOR_ACCENT
        
        run = p_mod.add_run()
        run.text = desc
        run.font.name = 'Segoe UI'
        run.font.size = Pt(15)
        run.font.bold = False
        run.font.color.rgb = COLOR_BODY
        p_mod.space_after = Pt(10)
        
    # ----------------------------------------------------
    # SLIDE 7: Advantages
    # ----------------------------------------------------
    slide7 = prs.slides.add_slide(blank_layout)
    apply_background(slide7)
    add_title(slide7, "Project Advantages")
    
    content_box7 = slide7.shapes.add_textbox(Inches(0.75), Inches(1.8), Inches(11.83), Inches(4.8))
    tf7 = content_box7.text_frame
    tf7.word_wrap = True
    tf7.margin_left = tf7.margin_top = tf7.margin_right = tf7.margin_bottom = 0
    
    advs = [
        ("Cost-Efficiency", "Capitalization and casing rules run locally at zero token cost, conserving expensive LLM API bandwidth for semantic restructuring tasks."),
        ("Syntax Security", "The self-correcting validation loop acts as a compiler guard, preventing code hallucinations and ensuring the user only receives valid, executable SQL."),
        ("Cloud Deployability", "Supports in-memory batch file uploads, allowing the application to run smoothly on isolated cloud deployment servers like Streamlit Community Cloud."),
        ("Pipeline Integration", "Dual CLI and web dashboard structure allows the tool to fit seamlessly into single-query debugging sessions or automated Git pre-commit hooks.")
    ]
    
    for i, (adv, desc) in enumerate(advs):
        p_adv = tf7.add_paragraph() if i > 0 else tf7.paragraphs[0]
        p_adv.text = f"\u2022  {adv}: "
        p_adv.font.name = 'Segoe UI'
        p_adv.font.size = Pt(15.5)
        p_adv.font.bold = True
        p_adv.font.color.rgb = COLOR_ACCENT
        
        run = p_adv.add_run()
        run.text = desc
        run.font.name = 'Segoe UI'
        run.font.size = Pt(15.5)
        run.font.bold = False
        run.font.color.rgb = COLOR_BODY
        p_adv.space_after = Pt(12)
        
    # ----------------------------------------------------
    # SLIDE 8: Conclusion
    # ----------------------------------------------------
    slide8 = prs.slides.add_slide(blank_layout)
    apply_background(slide8)
    add_title(slide8, "Conclusion")
    
    content_box8 = slide8.shapes.add_textbox(Inches(0.75), Inches(1.8), Inches(11.83), Inches(4.8))
    tf8 = content_box8.text_frame
    tf8.word_wrap = True
    tf8.margin_left = tf8.margin_top = tf8.margin_right = tf8.margin_bottom = 0
    
    p8_body = tf8.paragraphs[0]
    p8_body.text = "The SQL Query Linter & Style Fixer successfully bridges the gap between rule-based style cleaners and AI-driven semantic query model refactoring."
    p8_body.font.name = 'Segoe UI'
    p8_body.font.size = Pt(19)
    p8_body.font.bold = True
    p8_body.font.color.rgb = COLOR_ACCENT
    p8_body.space_after = Pt(20)
    
    points = [
        "Optimizes developer workflow speed and audit readiness for legacy SQL codebases.",
        "Guarantees compilation integrity through an AST validation loop architecture.",
        "Reduces database runtime search complexity by converting nested subqueries to CTEs and implicit comma-joins to explicit joins.",
        "Provides a cloud-deployable dashboard and automated CLI script to accommodate any integration pipeline environment."
    ]
    
    for pt in points:
        p_pt = tf8.add_paragraph()
        p_pt.text = f"\u2022  {pt}"
        p_pt.font.name = 'Segoe UI'
        p_pt.font.size = Pt(15)
        p_pt.font.color.rgb = COLOR_BODY
        p_pt.space_before = Pt(8)
        
    prs.save("Presentation.pptx")
    print("Presentation saved successfully.")

if __name__ == '__main__':
    build_presentation()
