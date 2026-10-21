# Amazon-Style Shopping Backend + Simple Agentic RAG

A FastAPI shopping backend with JWT authentication, product management, cart, orders, mock payments, Docker Compose, and an Nginx reverse proxy. This version also includes a **small agentic RAG assistant** that routes questions to retrieval tools and answers using the current product catalog and a local backend knowledge base.

## What the Agentic RAG Does

- **Agent/planner:** selects one or both retrieval tools based on the user's question.
- **Tool 1 — Product catalog:** retrieves matching products from the live SQLAlchemy database, including name, price, stock, category, and description.
- **Tool 2 — Backend knowledge:** retrieves relevant local knowledge about authentication, API routes, cart, orders, mock payments, Docker, and Nginx.
- **Grounded answer:** combines the retrieved information and returns the tools used and source excerpts.
- **No external API key required:** the starter agent runs locally and uses Python's standard library plus the project's existing dependencies.

This first version deliberately uses simple lexical keyword matching, **not embeddings or semantic search**. Semantic/vector search can be added as a separate next step. The planner is rule-based rather than an LLM-based autonomous planner, keeping this initial implementation easy to run and debug.

## Architecture

```text
Client / Swagger UI
       |
       v
Nginx Reverse Proxy :80
       |
       v
FastAPI :8000
  |       |       |
  |       |       +--> Existing shopping APIs
  |       |
  |       +--> Agent planner
  |               |--> Product catalog retrieval (SQLAlchemy)
  |               +--> Local knowledge-base retrieval (JSON)
  |
  +--> Existing SQL database
```

## Agentic RAG API

### `POST /api/agent/ask`

Request:

```json
{
  "question": "How does the Nginx reverse proxy work?"
}
```

Example questions:

- `How does login and JWT authentication work?`
- `Explain the Nginx reverse proxy setup.`
- `Find headphones in the product catalog.`
- `What does the mock payment endpoint do?`
- `How can I check Docker logs?`

The response contains:

- `question`: submitted question
- `answer`: generated with Ollama when available, otherwise assembled from retrieved context
- `tools_used`: retrieval tools and optional generation tool used
- `answer_mode`: `ollama_generation` or `retrieval_fallback`
- `sources`: knowledge-base excerpts or product catalog records used

The product tool can only retrieve products that already exist in the database. If the database has no matching products, add products through the existing admin-protected product API first.

### `GET /api/agent/health`

Checks that the local knowledge base can be loaded and reports the number of knowledge documents.

## Run Locally on Windows

Use Python 3.11 or another version supported by the existing project dependencies.

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
Copy-Item .env.example .env
```

Edit `.env` and set a private `SECRET_KEY`. Ollama generation is optional. To enable generated answers, install Ollama and download the default model with `ollama pull llama3.2`; if Ollama or the model is unavailable, the API falls back to the retrieved context. Then run:

```powershell
uvicorn app.main:app --reload
```

Open Swagger UI at http://127.0.0.1:8000/docs.

## Run with Docker Compose and Nginx

1. Ensure Docker Desktop is running.
2. Create `.env` from `.env.example` and set a private secret key.
3. From the folder containing `docker-compose.yml`, run:

```powershell
docker compose config
docker compose up --build -d
docker compose ps
docker compose logs --tail=100
```

Open:

- Application: http://localhost/
- Swagger UI (through Nginx): http://localhost/docs
- Agentic RAG health: http://localhost/api/agent/health

Try the assistant from Swagger UI by expanding `POST /api/agent/ask`, clicking **Try it out**, and sending a question in the request body.

Stop the services with:

```powershell
docker compose down
```

## Existing Shopping API

| Method | Endpoint | Purpose |
|---|---|---|
| POST | `/api/auth/register` | Register a user |
| POST | `/api/auth/login` | Log in and obtain a token |
| GET | `/api/products/` | List/search products |
| GET | `/api/products/{product_id}` | Retrieve one product |
| POST/PUT/DELETE | `/api/products/` and `/api/products/{product_id}` | Admin product management, as implemented by the router |
| GET/POST | `/api/cart/` | Read cart/add item |
| PUT/DELETE | `/api/cart/{product_id}` | Update/remove cart item |
| POST | `/api/orders/` | Place an order |
| GET | `/api/orders/` | Read order history |
| GET | `/api/orders/{order_id}` | Read one order |
| POST | `/api/payment/` | Mock payment operation |
| GET | `/api/payment/{order_id}` | Retrieve payment information |
| POST | `/api/agent/ask` | Ask the Agentic RAG assistant |
| GET | `/api/agent/health` | Check RAG knowledge-base loading |

Use `/docs` for exact request schemas and authentication requirements.

## Project Structure (new files)

```text
app/
└── agentic_rag/
    ├── __init__.py
    ├── knowledge_base.json
    ├── router.py
    ├── schemas.py
    └── service.py
```

The RAG code is isolated in `app/agentic_rag/` and is registered by `app/main.py`. It does not change the existing product, cart, order, payment, or authentication routes.

## Current Scope and Next Step

This is a deliberately small first milestone: transparent rule-based tool routing, lexical retrieval, source excerpts, and grounded answers. Ollama can optionally provide local LLM generation. It does not yet use vector embeddings, a vector database, or reranking. Semantic search can be added as the next stage after this baseline is running reliably.

## Security Notes

- Do not commit `.env`, database files, logs, virtual environments, or credentials.
- The payment endpoint is a mock and does not process real payments.
- Use HTTPS, restricted CORS origins, strong secrets, and appropriate access controls for a production deployment.

## Author

**Poornima H B**

- GitHub: https://github.com/POORNIMA205
- LinkedIn: https://www.linkedin.com/in/poornima-h-b-36bb3a2aa/
