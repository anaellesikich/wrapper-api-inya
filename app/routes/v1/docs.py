from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from fastapi.responses import JSONResponse
from ...deps import require_api_key
from ...config import settings
from ...services.gpt_service import OpenAIClient
import logging

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post("/docs/upload")
async def upload_doc(
    file: UploadFile = File(...),
    api_key: str = Depends(require_api_key)
):
    """
    Upload a document to the assistant's vector store (OpenAI only).
    Accepts .txt, .md, .pdf files. Requires GPT_PROVIDER=openai.
    Enforces a max file size of 5MB.
    """
    MAX_SIZE = 5 * 1024 * 1024  # 5MB
    contents = await file.read()
    if len(contents) > MAX_SIZE:
        raise HTTPException(status_code=413, detail="File too large (max 5MB)")

    if settings.GPT_PROVIDER != "openai":
        raise HTTPException(status_code=400, detail="Upload supported only with GPT_PROVIDER=openai")

    if not settings.OPENAI_VECTOR_STORE_ID:
        raise HTTPException(status_code=400, detail="OPENAI_VECTOR_STORE_ID is not set")

    try:
        client = OpenAIClient(settings.OPENAI_API_KEY, settings.OPENAI_MODEL)
        # Upload file to OpenAI (purpose=assistants)
        uploaded = client.client.files.create(
            file=(file.filename, contents),
            purpose="assistants"
        )
        # Attach to vector store
        client.client.beta.vector_stores.files.create(
            vector_store_id=settings.OPENAI_VECTOR_STORE_ID,
            file_id=uploaded.id
        )
        return JSONResponse({"ok": True, "file_id": uploaded.id, "filename": file.filename})
    except Exception as e:
        logger.exception("upload_failed")
        raise HTTPException(status_code=502, detail=f"Upload failed: {e}")
