# import google.generativeai as genai
# from dotenv import load_dotenv
# import os

# load_dotenv()
# api_key = os.getenv("GEMINI_API_KEY")

# genai.configure(api_key=api_key)
# model = genai.GenerativeModel(model_name="models/gemini-1.5-flash")

# def ask_llm_gemini(question: str) -> dict:
#     prompt = f"""
# You are an assistant that generates SQL queries for SQLite based on user questions.
# Assume the following tables exist:

# - total_sales(date TEXT, item_id INTEGER, total_sales REAL, total_units_ordered INTEGER)
# - ad_sales(date TEXT, item_id INTEGER, ad_sales REAL, impressions INTEGER, ad_spend REAL, clicks INTEGER, units_sold INTEGER)
# - eligibility(eligibility_datetime_utc TEXT, item_id INTEGER, eligibility TEXT, message TEXT)

# Step 1: Convert the user's question into a valid SQLite SQL query.
# Step 2: Respond with both:
# - The SQL query
# - A short explanation of what the query does.

# Format:
# SQL: <the SQL>
# Explanation: <the explanation>

# Question: {question}
# """

#     try:
#         response = model.generate_content(prompt)
#         raw_output = response.text.strip()

#         # Optional logging (debugging)
#         # print("RAW OUTPUT FROM GEMINI:\n", raw_output)

#         # Initialize defaults
#         sql = ""
#         explanation = ""

#         # Safely extract SQL and explanation
#         if "SQL:" in raw_output and "Explanation:" in raw_output:
#             parts = raw_output.split("Explanation:", 1)
#             sql = parts[0].replace("SQL:", "").strip()
#             explanation = parts[1].strip()
#         else:
#             sql = raw_output.strip()

#         # Cleanup if wrapped in markdown
#         if sql.startswith("```sql") and "```" in sql:
#             sql = sql.replace("```sql", "").replace("```", "").strip()

#         return {
#             "sql": sql or "-- No SQL generated",
#             "explanation": explanation or "No explanation provided."
#         }

#     except Exception as e:
#         return {
#             "sql": "-- Error: Failed to generate query",
#             "explanation": f"Gemini API error: {str(e)}"
#         }
# query_llm.py
import subprocess
from typing import Dict, Any, List

def ask_llm_ollama(question: str, history: List[str]) -> Dict[str, Any]:
    """
    Generate SQL, explanation, and chart suggestion using current question and past history.

    Returns:
        dict: {
            "sql": str,
            "explanation": str,
            "chart_type": Optional[str],
            "chart_label": Optional[str],
            "chart_suggestion": Optional[str]
        }
    """
    history_text = "\n".join([f"- {q}" for q in history[-5:]])  # Include last 5 user questions

    prompt = f"""
You are a smart AI AGENT that helps users by generating correct SQL queries from natural language questions
and suggesting appropriate visualizations when needed.

🎯 GOAL:
1. Generate accurate SQL queries
2. Suggest visualizations for data exploration
3. Provide clear explanations

---

📋 Available Tables:
- total_sales(date TEXT, item_id INTEGER, total_sales REAL, total_units_ordered INTEGER)
- ad_sales(date TEXT, item_id INTEGER, ad_sales REAL, impressions INTEGER, ad_spend REAL, clicks INTEGER, units_sold INTEGER)
- eligibility(eligibility_datetime_utc TEXT, item_id INTEGER, eligibility TEXT, message TEXT)

---

⚠️ SQL RULES:
- Use SQLite-compatible syntax only
- Always use table aliases:
  - total_sales → ts
  - ad_sales → ads
  - eligibility → el
- Always qualify column names with aliases
- For chart-friendly results, return exactly 2 columns (x-axis, y-axis)

---
Chat History:
{history_text}

---

📊 CHART GUIDELINES:
1. Time series data → Suggest 'line' chart
2. Comparisons between categories → Suggest 'bar' chart
3. Proportions/percentages → Suggest 'pie' or 'doughnut' chart
4. Relationships → Suggest 'scatter' chart
5. Distributions → Suggest 'histogram'

---

🧾 RESPONSE FORMAT:
```sql
<valid SQL query>

Explanation: <1-3 line reasoning of what the query does>

---
type: bar
label: Total Sales
suggestion: Compare monthly total sales
---

Question: {question}
"""

    try:
        result = subprocess.run(
            ["ollama", "run", "gemma3:4b"],
            input=prompt.encode("utf-8"),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=120
        )

        if result.returncode != 0:
            return {
                "sql": "-- Error: Ollama query failed",
                "explanation": result.stderr.decode("utf-8"),
                "chart_type": None,
                "chart_label": None,
                "chart_suggestion": None
            }

        output = result.stdout.decode("utf-8").strip()

        response = {
            "sql": "",
            "explanation": "",
            "chart_type": None,
            "chart_label": None,
            "chart_suggestion": None
        }

        # --- SQL extraction ---
        sql_start = output.find("```sql")
        sql_end = output.find("```", sql_start + 6)
        if sql_start != -1 and sql_end != -1:
            response["sql"] = output[sql_start + 6:sql_end].strip()
        elif "SQL:" in output:
            sql_line = output.split("SQL:")[1].split("Explanation:")[0].strip()
            response["sql"] = sql_line
        else:
            sql_lines = []
            in_sql = False
            for line in output.splitlines():
                if line.strip().lower().startswith("select") or in_sql:
                    sql_lines.append(line)
                    in_sql = True
                    if line.strip().endswith(";"):
                        break
            if sql_lines:
                response["sql"] = "\n".join(sql_lines).strip()

        # --- Explanation extraction ---
        if "Explanation:" in output:
            explanation = output.split("Explanation:")[1].strip()
            explanation = explanation.split("```")[0].strip()  # Stop at next block
            response["explanation"] = explanation
        else:
            response["explanation"] = "Generated SQL query for the question"

        # --- Chart metadata extraction ---
        chart_start = output.find("```chart")
        chart_end = output.find("```", chart_start + 7)
        if chart_start != -1 and chart_end != -1:
            chart_block = output[chart_start + 7:chart_end].strip()
            for line in chart_block.splitlines():
                if line.startswith("type:"):
                    response["chart_type"] = line.split("type:")[1].strip()
                elif line.startswith("label:"):
                    response["chart_label"] = line.split("label:")[1].strip()
                elif line.startswith("suggestion:"):
                    response["chart_suggestion"] = line.split("suggestion:")[1].strip()

        return response

    except Exception as e:
        return {
            "sql": f"-- Error: {str(e)}",
            "explanation": "Failed to generate query",
            "chart_type": None,
            "chart_label": None,
            "chart_suggestion": None
        }
