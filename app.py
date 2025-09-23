from dotenv import load_dotenv
import streamlit as st
import os
import re
import sqlite3
import google.generativeai as genai

# Load environment variables
load_dotenv()

# Configure GenAI Key
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# --- Core Functions ---

def get_gemini_response(question, prompt):
    """Loads Google Gemini Model and provides response to the query."""
    model = genai.GenerativeModel('gemini-2.0-flash')
    response = model.generate_content([prompt, question])
    return response.text

def read_sql_query(sql, db):
    """Executes a SQL query and returns the results."""
    conn = sqlite3.connect(db)
    cur = conn.cursor()
    try:
        cur.execute(sql)
        rows = cur.fetchall()
    except sqlite3.Error as err:
        print(f"Database error: {err}")
        return None
    finally:
        conn.close()
    return rows

def get_db_schema_description(db_path):
    """Inspects the database and returns a string description of the schema."""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Get list of tables
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%';")
    tables = cursor.fetchall()
    
    if not tables:
        conn.close()
        return "No tables found in the database."

    schema_description = "The database has the following schema:\n"
    for table_name_tuple in tables:
        table_name = table_name_tuple[0]
        schema_description += f"\nTable '{table_name}':\n"
        
        # Get column info for each table
        cursor.execute(f'PRAGMA table_info("{table_name}");')
        columns = cursor.fetchall()
        
        for column in columns:
            col_name = column[1]
            col_type = column[2]
            schema_description += f"  - Column '{col_name}' with data type '{col_type}'\n"
            
    conn.close()
    return schema_description

def get_db_tables_and_columns(db_path):
    """Returns a dict of table -> list of columns for validation and prompting."""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%';")
    tables = [t[0] for t in cursor.fetchall()]
    schema: dict[str, list[str]] = {}
    for table_name in tables:
        cursor.execute(f'PRAGMA table_info("{table_name}");')
        columns = [row[1] for row in cursor.fetchall()]
        schema[table_name] = columns
    conn.close()
    return schema

def clean_sql_output(text):
    """Extracts a plausible SQL statement from model output, removing code fences/explanations."""
    if not text:
        return ""
    cleaned = text.strip()
    # Remove markdown fences if present
    cleaned = re.sub(r"^```(?:sql)?\s*", "", cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r"\s*```\s*$", "", cleaned)
    # If the model prefixed with labels, remove them
    cleaned = re.sub(r"^(SQL\s*Query\s*:\s*)", "", cleaned, flags=re.IGNORECASE)
    # Try to extract the first SELECT...; statement
    match = re.search(r"(SELECT[\s\S]*?;)", cleaned, flags=re.IGNORECASE)
    if match:
        return match.group(1).strip()
    return cleaned

def validate_sql_tables(sql, allowed_tables):
    """Basic validation to ensure referenced tables exist in the database."""
    # Find FROM and JOIN table tokens (very naive but sufficient for single-table EMPLOYEE)
    table_like = re.findall(r"\bFROM\s+([A-Za-z_][A-Za-z0-9_]*)|\bJOIN\s+([A-Za-z_][A-Za-z0-9_]*)", sql, flags=re.IGNORECASE)
    referenced = set([t for pair in table_like for t in pair if t])
    # If no tables found, allow (the model might use subqueries). Otherwise enforce
    return not referenced or all(t in allowed_tables for t in referenced)

# --- Streamlit App ---

st.set_page_config(page_title="AI-Driven Movie Insights", page_icon=":clapper:", layout="wide")

# --- UI Styling ---
st.markdown("""
    <style>
        .main { background-color: #F3F2F1; }
        h1 { color: #E71D73; }
        .stButton button { background-color: #1E91D6; color: white; }
        .stTextInput > div > div > input { background-color: #FFE9F3; color: #1E91D6; }
    </style>
    """, unsafe_allow_html=True)

st.title("AI-Driven Movie Insights")
st.markdown("### Query Your Movies Database with Natural Language")

# --- Dynamic Prompt Generation ---
db_path = "employee_kpi.db"

if os.path.exists(db_path):
    schema_description = get_db_schema_description(db_path)
    schema_dict = get_db_tables_and_columns(db_path)
    allowed_tables = list(schema_dict.keys())
    # Build a concise, machine-friendly schema hint
    schema_hint_lines = []
    for table_name, columns in schema_dict.items():
        cols = ", ".join(columns)
        schema_hint_lines.append(f"- {table_name}({cols})")
    schema_hint = "\n".join(schema_hint_lines)
    
    prompt_template = f"""
    You convert English questions into valid SQLite SQL.
    Use ONLY existing tables and columns from this schema:
    {schema_hint}

    Rules:
    - Output ONLY the final SQL statement; no explanations or labels.
    - Use exact table/column names and SQLite syntax.
    - Prefer a single statement ending with a semicolon.
    - If aggregation is implied, use GROUP BY appropriately.
    - Do NOT invent tables or columns.

    Example:
    Q: How many movies are in the Action genre?
    A: SELECT COUNT(*) AS count FROM MOVIES WHERE GENRE = 'Action';
    """

    # --- User Input ---
    question = st.text_input("Ask your question:", key="input", placeholder="e.g., Top 5 movies by BOX_OFFICE_DOMESTIC; or Average RATING by GENRE")
    submit = st.button("Get Insights")

    if submit and question:
        with st.spinner("Generating SQL query and fetching data..."):
            raw = get_gemini_response(question, prompt_template)
            sql_query = clean_sql_output(raw)

            # Validate and, if needed, try one stricter regeneration
            if not validate_sql_tables(sql_query, set(allowed_tables)):
                strict_prompt = (
                    prompt_template
                    + "\nAdditional constraint: The ONLY valid tables are: "
                    + ", ".join(allowed_tables)
                    + ". Do not reference any other tables."
                )
                raw2 = get_gemini_response(question, strict_prompt)
                sql_query = clean_sql_output(raw2)

            st.subheader("Generated SQL Query")
            st.code(sql_query, language='sql')

            data = read_sql_query(sql_query, db_path)

            if data:
                st.subheader("Query Results")
                st.dataframe(data)
            elif data is None:
                st.error("There was an error executing the SQL query. Please check the generated query and your database.")
            else:
                st.warning("The query returned no data.")
else:
    st.error(f"Database file '{db_path}' not found. Please make sure the database file is in the same directory as the application.")

# --- Sidebar & Footer ---
st.sidebar.header("About")
st.sidebar.info("""
This app uses AI to dynamically generate SQL queries based on your movie database schema. 
It inspects the tables and columns (e.g., MOVIES, ACTORS, MOVIE_ACTORS, REVENUES) to provide accurate, natural language querying.
""")
st.markdown("---")
st.markdown("**Note:** This is a POC. Ensure data privacy and security when handling real data.")
