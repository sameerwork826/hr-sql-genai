from dotenv import load_dotenv
import streamlit as st
import os
import sqlite3
import google.generativeai as genai

# Load environment variables
load_dotenv()

# Configure GenAI Key
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# --- Core Functions ---

def get_gemini_response(question, prompt):
    """Loads Google Gemini Model and provides response to the query."""
    model = genai.GenerativeModel('gemini-pro')
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

# --- Streamlit App ---

st.set_page_config(page_title="AI-Driven HR Insights", page_icon=":bar_chart:", layout="wide")

# --- UI Styling ---
st.markdown("""
    <style>
        .main { background-color: #F3F2F1; }
        h1 { color: #E71D73; }
        .stButton button { background-color: #1E91D6; color: white; }
        .stTextInput > div > div > input { background-color: #FFE9F3; color: #1E91D6; }
    </style>
    """, unsafe_allow_html=True)

st.title("AI-Driven HR Insights")
st.markdown("### Query Your HR Data with Natural Language")

# --- Dynamic Prompt Generation ---
db_path = "employee_kpi.db"

if os.path.exists(db_path):
    schema_description = get_db_schema_description(db_path)
    
    prompt_template = f"""
    You are an expert in converting English questions into SQL queries.
    Based on the database schema provided below, generate a SQL query that answers the user's question.
    
    **Database Schema:**
    {schema_description}
    
    **Instructions:**
    - Only output the SQL query.
    - Do not include ```sql at the beginning or ``` at the end.
    
    **Example:**
    User Question: "How many employees are in the IT department?"
    SQL Query: SELECT COUNT(*) FROM EMPLOYEE WHERE DEPARTMENT="IT";
    """

    # --- User Input ---
    question = st.text_input("Ask your question:", key="input", placeholder="e.g., What is the average salary in the Sales department?")
    submit = st.button("Get Insights")

    if submit and question:
        with st.spinner("Generating SQL query and fetching data..."):
            sql_query = get_gemini_response(question, prompt_template)
            
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
This app uses AI to dynamically generate SQL queries based on the structure of your database. 
It inspects the tables and columns to provide accurate, natural language querying of your HR data.
""")
st.markdown("---")
st.markdown("**Note:** This is a POC. Ensure data privacy and security when handling real employee data.")
