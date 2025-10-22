# app/services/gpt_service.py
from __future__ import annotations

import asyncio
import logging
import time
from typing import Dict, List, Optional, Tuple

from openai import OpenAI

log = logging.getLogger("app.gpt_service")


# ---------- Interface ----------

class GPTClient:
    async def generate(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.6,
        max_tokens: int = 600,
        stream: bool = False,
        session_id: Optional[str] = None,
        context_text: Optional[str] = None,
    ) -> Tuple[str, Dict, Optional[str]]:
        raise NotImplementedError


# ---------- Dev stub ----------

class EchoClient(GPTClient):
    async def generate(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.0,
        max_tokens: int = 100,
        stream: bool = False,
        session_id: Optional[str] = None,
        context_text: Optional[str] = None,
    ) -> Tuple[str, Dict, Optional[str]]:
        last = next((m["content"] for m in reversed(messages) if m.get("role") == "user"), "")
        content = f"[echo] {last}"
        return content, {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0}, "echo"


# ---------- OpenAI client (Assistant first, chat fallback) ----------

class OpenAIClient(GPTClient):
    """
    If `assistant_id` is provided -> use Assistants v2 (beta.threads / runs) so replies
    come from your configured Assistant (Inya).
    Otherwise -> use Chat Completions as a fallback.
    """

    def __init__(self, api_key: str, model: str, assistant_id: Optional[str] = None):
        self.client = OpenAI(api_key=api_key)
        self.model = model
        self.assistant_id = assistant_id
        self._threads: Dict[str, str] = {}  # session_id -> thread_id

        mode = "assistant" if assistant_id else "chat"
        tail = (assistant_id or "")[:10]
        log.info("OpenAIClient init mode=%s model=%s assistant_id=%s", mode, model, tail)

    # ------------- Public -------------

    async def generate(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.6,
        max_tokens: int = 600,
        stream: bool = False,
        session_id: Optional[str] = None,
        context_text: Optional[str] = None,
    ) -> Tuple[str, Dict, Optional[str]]:
        if self.assistant_id:
            # Assistant path via beta.threads/runs – wrap blocking SDK calls in a thread
            return await asyncio.to_thread(
                self._assistant_reply_sync,
                messages,
                temperature,
                max_tokens,
                stream,
                session_id,
                context_text,
            )

        # Fallback: Chat Completions (blocking SDK call → thread)
        return await asyncio.to_thread(
            self._chat_reply_sync,
            messages,
            temperature,
            max_tokens,
            stream,
        )

    # ------------- Internals: Assistants V2 (sync) -------------

    def _ensure_thread(self, session_id: Optional[str]) -> str:
        sid = session_id or "default"
        tid = self._threads.get(sid)
        if tid:
            return tid
        t = self.client.beta.threads.create()
        self._threads[sid] = t.id
        return t.id

    def _assistant_reply_sync(
        self,
        messages: List[Dict[str, str]],
        temperature: float,
        max_tokens: int,
        stream: bool,
        session_id: Optional[str],
        context_text: Optional[str],
    ) -> Tuple[str, Dict, Optional[str]]:
        """
        - Ensures a thread per session_id.
        - Appends the latest user turn (optionally with ephemeral context) to the thread.
        - Creates a run addressed to your assistant and polls until completion.
        - Returns the assistant text.
        """
        # Take the latest user message; Assistants keep the history in the thread.
        user_text = ""
        for m in reversed(messages):
            if m.get("role") == "user":
                user_text = m.get("content", "")
                break

        if context_text:
            user_text = (
                "Temporary document context for THIS reply only (do not store):\n\n"
                f"{context_text[:15000]}\n\n"
                f"User request:\n{user_text}"
            )

        thread_id = self._ensure_thread(session_id)

        # 1) Add message to the thread
        self.client.beta.threads.messages.create(
            thread_id=thread_id,
            role="user",
            content=user_text,
        )

        # 2) Create a run addressed to your assistant
        run = self.client.beta.threads.runs.create(
            thread_id=thread_id,
            assistant_id=self.assistant_id,
            # Some SDKs allow overrides; if available in your version, you can pass:
            # temperature=temperature,
            # max_output_tokens=max_tokens,
        )

        # 3) Poll until the run completes (simple polling loop)
        while True:
            r = self.client.beta.threads.runs.retrieve(thread_id=thread_id, run_id=run.id)
            if r.status in {"completed", "failed", "cancelled", "expired"}:
                break
            time.sleep(0.4)

        if r.status != "completed":
            log.warning("Assistant run ended with status=%s", r.status)
            return f"Assistant error: {r.status}", {"status": r.status}, self.model

        # 4) Fetch the latest assistant message text
        msgs = self.client.beta.threads.messages.list(thread_id=thread_id, order="desc", limit=1)
        text_out = ""
        try:
            latest = msgs.data[0]
            parts = latest.content or []
            for p in parts:
                if getattr(p, "type", None) == "text":
                    # Newer SDKs: p.text.value
                    v = getattr(p, "text", None)
                    if v and getattr(v, "value", None):
                        text_out += v.value
        except Exception:
            pass

        if not text_out:
            text_out = "Sorry—I couldn’t produce a response."

        # Usage isn't consistently exposed for assistants v2 yet
        usage = {"status": "ok", "source": "assistants_v2"}
        return text_out, usage, self.model

    # ------------- Internals: Chat Completions (sync) -------------

    def _chat_reply_sync(
        self,
        messages: List[Dict[str, str]],
        temperature: float,
        max_tokens: int,
        stream: bool,
    ) -> Tuple[str, Dict, Optional[str]]:
        resp = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
        )
        content = resp.choices[0].message.content
        usage = {
            "prompt_tokens": getattr(resp, "usage", {}).get("prompt_tokens", None) if hasattr(resp, "usage") else None,
            "completion_tokens": getattr(resp, "usage", {}).get("completion_tokens", None) if hasattr(resp, "usage") else None,
            "total_tokens": getattr(resp, "usage", {}).get("total_tokens", None) if hasattr(resp, "usage") else None,
        }
        return content, usage, self.model
