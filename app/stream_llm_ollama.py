import subprocess
from typing import Dict, AsyncGenerator
import asyncio

async def stream_llm_ollama(question: str) -> AsyncGenerator[Dict[str, str], None]:
    """
    Query the Ollama LLM to generate SQL from natural language questions
    
    Args:
        question: Natural language question about e-commerce data
        
    Yields:
        Dictionary with 'sql' and 'explanation' keys
    """
    prompt = f"""
You are an AI AGENT that generates SQL queries for SQLite based on user questions.

⚠️ IMPORTANT SQL RULES:
- Always use **table aliases**:
  - total_sales → ts
  - ad_sales → ads
  - eligibility → el
- Always qualify columns with aliases: e.g., ts.date, ads.item_id
- When joining tables, use aliases and qualify all columns.
- Only output SQLite-compatible SQL.

Tables available:

- total_sales(date TEXT, item_id INTEGER, total_sales REAL, total_units_ordered INTEGER)
- ad_sales(date TEXT, item_id INTEGER, ad_sales REAL, impressions INTEGER, ad_spend REAL, clicks INTEGER, units_sold INTEGER)
- eligibility(eligibility_datetime_utc TEXT, item_id INTEGER, eligibility TEXT, message TEXT)

Respond in this format:

SQL: <SQL QUERY>
Explanation: <1-3 line explanation>

Question: {question}
    """

    try:
        process = await asyncio.create_subprocess_exec(
            "ollama", "run", "gemma3:4b",
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )

        stdout, stderr = await process.communicate(input=prompt.encode("utf-8"))

        if process.returncode != 0:
            yield {
                "sql": "-- Error: Ollama query failed",
                "explanation": stderr.decode("utf-8")[:500]
            }
            return

        output = stdout.decode("utf-8").strip()

        # Extract SQL and explanation
        sql = ""
        explanation = ""

        if "SQL:" in output and "Explanation:" in output:
            parts = output.split("Explanation:", 1)
            sql = parts[0].replace("SQL:", "").strip()
            explanation = parts[1].strip()
        else:
            sql = output.strip()

        # Clean up SQL if it's in a code block
        if sql.startswith("```sql"):
            sql = sql.replace("```sql", "").replace("```", "").strip()

        yield {
            "sql": sql or "-- No SQL generated",
            "explanation": explanation or "No explanation provided"
        }

    except subprocess.TimeoutExpired:
        yield {
            "sql": "-- Error: Ollama query timed out",
            "explanation": "The query took too long to process"
        }
    except Exception as e:
        yield {
            "sql": "-- Error: Failed to process query",
            "explanation": str(e)[:500]
        }