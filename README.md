# HR Insights — Natural-Language to SQL for HR Data 🏢📊

[Live Demo on Streamlit](https://hr-sql-genai.streamlit.app/)  
Ask HR questions in plain English, get valid SQLite queries, and see results instantly.

---

## Overview
HR Insights is a Streamlit app that turns natural-language questions into real SQL queries against a local SQLite database. It dynamically inspects your database schema, guides the LLM to only use valid tables/columns, and executes the generated SQL to display results.

The app ships with a synthetic `employee_kpi.db` containing 100 sample employees so you can explore immediately. Replace it with your own SQLite DB when you’re ready.

## Key Features
- Schema-aware SQL generation (SQLite)
- Built-in validation of table references
- Clean extraction of SQL from model output (no code fences or explanations)
- One-click data exploration via Streamlit UI
- Sample database generator for quick demos

## How It Works
1. The app inspects your SQLite DB and builds a concise schema hint (tables and columns).  
2. A prompt constrains the model to generate SQLite-only SQL using only existing fields.  
3. The output is sanitized to extract a single `SELECT ...;` statement.  
4. A basic validator checks referenced tables; if invalid, the app regenerates once with stricter constraints.  
5. The SQL is executed and the results are displayed in the UI.

## Live Demo
- App: https://hr-sql-genai.streamlit.app/

## Screenshots
Coming soon.

## Quickstart (Local)

### Prerequisites
- Python 3.10+
- A Google Generative AI API key (`GOOGLE_API_KEY`)

### 1) Clone and install
```bash
pip install -r requirements.txt
```

### 2) Set your environment variable
Create a `.env` file in the project root:
```bash
GOOGLE_API_KEY=your_api_key_here
```

### 3) Generate the sample database (optional)
```bash
python generate_db.py
```
This creates `employee_kpi.db` with 100 synthetic rows.

### 4) Run the app
```bash
streamlit run app.py
```

Open the provided local URL and start asking HR-related questions.

## Example Prompts
- "Top 5 highest paid employees in Engineering"
- "Average PERFORMANCE_SCORE by DEPARTMENT"
- "Employees in London with more than 5 years of experience"
- "Count of employees promoted since 2021 by DEPARTMENT"

## Default Database Schema
The included generator creates a single table `EMPLOYEE`:

- `ID` INTEGER PRIMARY KEY
- `NAME` TEXT
- `AGE` INTEGER
- `DEPARTMENT` TEXT
- `SALARY` REAL
- `PERFORMANCE_SCORE` REAL
- `YEARS_OF_EXPERIENCE` INTEGER
- `LAST_PROMOTION_YEAR` INTEGER (nullable)
- `LOCATION` TEXT

You can point the app to any SQLite database file by replacing `employee_kpi.db` in `app.py`.

## Tech Stack
- Streamlit (UI)
- SQLite (storage)
- Google Generative AI (SQL generation)
- Python: `dotenv`, `faker` (for sample data), `sqlite3`

## Project Structure
```
HR-Insights/
├─ app.py               # Streamlit app, prompt, validation, execution
├─ generate_db.py       # Sample SQLite DB generator
├─ employee_kpi.db      # Generated demo database
├─ requirements.txt     # Python dependencies
├─ pyproject.toml       # Optional project metadata
└─ README.md            # This file
```

## Configuration
- `GOOGLE_API_KEY` must be available in the environment (or `.env`).
- The app currently targets SQLite and expects queries to be `SELECT` statements.

## Tips for Better Results
- Ask clear, specific questions: include filters (department, location), metrics (count, average), and grouping if needed.
- Use actual column names when possible (e.g., `DEPARTMENT`, `LOCATION`).
- Start simple; if a query returns no rows, try relaxing constraints.

## Troubleshooting
- "The query returned no data": Try a broader question or a different department/location.
- "There was an error executing the SQL query": Check that the generated SQL references only existing tables/columns and ends with a semicolon. Regenerate or refine your question.
- No database found: Ensure `employee_kpi.db` exists (run `python generate_db.py`) or update the path in `app.py`.
- API errors: Confirm `GOOGLE_API_KEY` is set and valid.

## Security & Privacy
- Do not upload sensitive HR data without appropriate safeguards.
- Consider PII handling, access control, and auditing in production deployments.

## Roadmap
- Few-shot prompt examples specialized for HR analytics
- Result visualizations (charts)
- Multi-table joins and schema introspection across schemas
- Caching and query history

## Contributing
Issues and PRs are welcome. Please open an issue to discuss significant changes.

## License
Add your preferred license (e.g., MIT) to the repository.

