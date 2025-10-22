# Inya — Inclusive Language Assistant

**Inya** is an inclusive-language educator and consultant powered by the **OpenAI Assistants API**.  
It reviews user-provided text for non-inclusive, biased, or exclusionary language and suggests  
more inclusive alternatives based on Microsoft’s and King’s Inclusive Language Guidelines.

---

## Features

- **FastAPI backend** with `/v1/generate` endpoint using your custom OpenAI Assistant.
- **Ephemeral uploads**: users can upload PDFs or text files for temporary review (not stored permanently).
- **Modern chat interface** (index.html) inspired by ChatGPT.
- **Configurable `.env`** for API keys and model selection.
- **Redis-ready architecture** for caching and scaling.

---

## How It Works

1. The backend loads your OpenAI Assistant details from `.env`.
2. When users send text or upload files:
   - Text from uploads is extracted temporarily (PDF/TXT/MD supported).
   - That text is sent as **context** to your Assistant for this specific request.
   - Nothing from user uploads is added to the Assistant’s long-term vector store.
3. The Assistant (Inya) replies following her defined system instructions in the OpenAI dashboard.

---

## Project Structure

```
web_api/
├── app/
│   ├── main.py                 # FastAPI entrypoint
│   ├── config.py               # Environment and settings
│   ├── deps.py                 # Dependency injection
│   ├── routes/
│   │   └── v1/
│   │       ├── generate.py     # /v1/generate endpoint
│   │       ├── docs.py         # /v1/docs/upload and /v1/docs/clear
│   │       └── health.py       # /v1/health
│   ├── services/
│   │   ├── gpt_service.py      # OpenAI client (Assistants + fallback)
│   │   ├── doc_store.py        # Temporary in-memory upload store
│   │   └── cache.py            # Optional Redis integration
│   └── utils/
│       ├── auth.py             # API key validation
│       └── logging.py          # Structured JSON logger
├── scripts/
│   └── run_server.sh           # Server startup script
├── index.html                  # Chat UI
├── requirements.txt            # Dependencies
├── Dockerfile                  # Optional deployment config
└── .gitignore                  # Prevents secrets from being tracked
```

---

## Running Locally

### 1. Clone and enter the project

```bash
git clone https://github.com/<your-username>/<repo-name>.git
cd web_api
```

### 2. Create and activate a virtual environment

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Create your `.env`

```bash
APP_ENV=dev
LOG_LEVEL=INFO
ALLOW_ORIGINS=["*"]
API_KEYS=["dev-secret-key"]

GPT_PROVIDER=openai
OPENAI_API_KEY=sk-...
OPENAI_ASSISTANT_ID=asst_...
OPENAI_MODEL=gpt-4o-mini
REQUEST_TIMEOUT_S=30
```

**Never commit your `.env`** — it contains your OpenAI API key.

---

## Start the Backend

```bash
cd ~/Documents/web_api
source .venv/bin/activate
bash scripts/run_server.sh
```

Once running, open:

- **API Docs:** [http://localhost:8080/docs](http://localhost:8080/docs)
- **Health check:** [http://localhost:8080/v1/health](http://localhost:8080/v1/health)

You should see:
```json
{"provider":"openai","assistant":true,"status":"ok"}
```

---

## Start the Frontend

Run a quick static server for the chat UI:

```bash
python -m http.server 5173
```

Then open:
[http://localhost:5173/index.html](http://localhost:5173/index.html)

---

## Example Endpoints

### `GET /v1/health`
Health check confirming the service and assistant connection.

### `POST /v1/docs/upload`
Upload a `.pdf` or `.txt` for Inya to review temporarily.

### `POST /v1/generate`
Send a chat message or analysis request:
```json
{
  "messages": [{"role": "user", "content": "Please review this text for inclusivity."}],
  "session_id": "abc123"
}
```

---

## Restarting After Reboot

After restarting your computer:

```bash
cd ~/Documents/web_api
source .venv/bin/activate
bash scripts/run_server.sh
```

You do *not* need to reconfigure anything — it automatically reloads `.env`.

---

## Security

- `.env` is ignored in `.gitignore` to protect secrets.
- Uploaded files are processed in memory and deleted after use.
- Each request requires a valid `X-API-Key`.

---

## Developer Notes

- You can open two terminals:
  - **Terminal 1:** `bash scripts/run_server.sh` (backend)
  - **Terminal 2:** `python -m http.server 5173` (frontend)
- Update the Assistant behavior anytime via the OpenAI dashboard (Inya’s configuration).

---

## License

MIT License — feel free to adapt this project for your own internal tools or inclusive-language initiatives.

---

## Credits

- **FastAPI** for the backend framework  
- **OpenAI Assistants API** for the intelligent responses  
- **PyPDF**, **Pydantic**, **Uvicorn** for document parsing, data handling, and serving  
- Microsoft & King inclusive language guidelines as sole input for the assistant
