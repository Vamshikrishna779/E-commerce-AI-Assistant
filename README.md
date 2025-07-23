# E-commerce AI Assistant

A FastAPI-based web application that converts natural language queries into SQL for e-commerce data analytics. The generated SQL is executed on a SQLite database, and the results are visualized using charts.

## Features

- Natural language to SQL translation using local LLMs (via Ollama)
- Query explanation and result rendering
- Automatic chart generation (bar/pie) using Chart.js
- Chat interface with session history
- Export chat sessions to JSON
- Clear and delete individual sessions
- Optional streaming support

## Technologies Used

- FastAPI
- SQLite
- Jinja2
- HTML/CSS/JS
- Chart.js
- Ollama (Gemma or similar models)


## Installation

### Step 1: Clone the Repository

```bash
git clone https://github.com/your-username/ecommerce-sql-assistant.git
cd ecommerce-ai-assistant
````

### Step 2: Create a Virtual Environment

```bash
python -m venv venv
source venv/bin/activate  # For Windows: venv\Scripts\activate
```

### Step 3: Install Python Dependencies

```bash
pip install -r requirements.txt
```

### Step 4: Set Up Ollama

Install Ollama: [https://ollama.com](https://ollama.com)

Pull and run the model:

```bash
ollama pull gemma:4b
ollama run gemma:4b
```

Ensure it is running on `localhost:11434`.

### Step 5: Start the FastAPI App

```bash
uvicorn app.main:app --reload
```

Visit: [http://127.0.0.1:8000](http://127.0.0.1:8000)

## Endpoints

| Method | URL                         | Function                         |
| ------ | --------------------------- | -------------------------------- |
| GET    | `/`                         | Home with chat list              |
| GET    | `/chat/new`                 | Start a new chat                 |
| GET    | `/chat/{session_id}`        | View a specific chat             |
| POST   | `/chat/{session_id}/ask`    | Submit a question                |
| POST   | `/chat/{session_id}/clear`  | Clear messages in session        |
| POST   | `/chat/{session_id}/delete` | Delete session completely        |
| GET    | `/chat/{session_id}/export` | Download session as JSON         |
| POST   | `/ask_stream`               | (Optional) Streamed response API |

## JSON Export Format

```json
{
  "metadata": {
    "title": "Example Chat Title",
    "created_at": "2025-07-23 14:15"
  },
  "messages": [
    {
      "question": "What are total sales?",
      "sql": "SELECT SUM(total_sales) FROM total_sales;",
      "explanation": "This query calculates the total sales.",
      "result": [{ "SUM(total_sales)": 12345 }],
      "chart_data": {
        "labels": ["Electronics", "Books"],
        "values": [1000, 2000],
        "label": "sales"
      },
      "chart_type": "bar",
      "time": "14:16"
    }
  ]
}
```

## License

This project is licensed under the MIT License.

```

Let me know if you want this written into a `README.md` file and served by your FastAPI app.
```
