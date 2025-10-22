# my-gpt-wrapper

FastAPI wrapper around a pluggable GPT client (Echo default, OpenAI), with simple API key auth and optional SSE streaming.

## Quickstart

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# Edit .env (set API_KEYS; optionally set OPENAI_API_KEY and GPT_PROVIDER=openai)

bash scripts/run_server.sh
# -> http://localhost:8080
