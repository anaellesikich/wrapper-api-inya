# app/routes/v1/docs.py
"""
Endpoints for user document uploads.

- /v1/docs/upload → upload a file to temporary memory
- /v1/docs/clear  → clear all uploads for a user session
"""

from fastapi import APIRouter, UploadFile, File, Header, HTTPException, Depends
from ...utils.auth import api_key_auth  # reuse your existing API key validation
from ...services import doc_store

router = APIRouter()

@router.post("/upload")
async def upload_doc(
    file: UploadFile = File(...),
    x_session_id: str | None = Header(default=None, alias="X-Session-Id"),
    api_key: str = Depends(api_key_auth),
):
    """Accept a file upload and store it temporarily for this session."""
    if not x_session_id:
        raise HTTPException(status_code=400, detail="Missing X-Session-Id header.")
    
    result = doc_store.add(x_session_id, file)
    if not result.get("ok"):
        raise HTTPException(status_code=400, detail=result.get("error", "Upload failed"))
    
    return result


@router.post("/clear")
async def clear_docs(
    x_session_id: str | None = Header(default=None, alias="X-Session-Id"),
    api_key: str = Depends(api_key_auth),
):
    """Remove all uploaded files for this session."""
    if not x_session_id:
        raise HTTPException(status_code=400, detail="Missing X-Session-Id header.")
    
    doc_store.clear(x_session_id)
    return {"ok": True, "message": "Uploads cleared successfully."}
