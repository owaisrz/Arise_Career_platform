import os
import uuid
from pathlib import Path
from typing import List
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from backend.app.core.config import settings
from backend.app.core.database import get_db
from backend.app.models.user import User
from backend.app.models.document import Document, ExtractedClaim
from backend.app.api.deps import get_current_user
from backend.app.services.document_service import (
    calculate_sha256,
    validate_file_bytes,
    extract_text_from_pdf,
    extract_text_from_docx,
    extract_text_from_txt,
    parse_claims_from_text
)
from backend.app.services.audit_service import log_audit_event

router = APIRouter(prefix="/documents", tags=["Document Scanner"])

@router.post("/upload")
async def upload_document(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    contents = await file.read()
    if not contents:
        raise HTTPException(status_code=400, detail="Uploaded file is empty.")

    # Validate file format and size
    is_valid, err_msg, mime_type = validate_file_bytes(contents, file.filename, settings.MAX_UPLOAD_SIZE_MB)
    if not is_valid:
        raise HTTPException(status_code=400, detail=err_msg)

    # Compute SHA-256 for integrity and duplicate check
    file_hash = calculate_sha256(contents)
    
    # Check for duplicate
    dup_res = await db.execute(select(Document).where(Document.user_id == current_user.id, Document.file_hash == file_hash))
    existing_dup = dup_res.scalar_one_or_none()
    is_duplicate = existing_dup is not None

    # Generate secure random storage filename
    ext = os.path.splitext(file.filename)[1].lower()
    stored_filename = f"{uuid.uuid4().hex}{ext}"
    storage_path = os.path.join(settings.STORAGE_DIR, stored_filename)

    with open(storage_path, "wb") as f:
        f.write(contents)

    # Text extraction based on format
    if ext == ".pdf":
        pages_data = extract_text_from_pdf(storage_path)
    elif ext == ".docx":
        pages_data = extract_text_from_docx(storage_path)
    elif ext == ".txt":
        pages_data = extract_text_from_txt(storage_path)
    else:
        # Image file
        pages_data = [{"page_number": 1, "text": ""}]

    # Claim extraction
    parsed_results = parse_claims_from_text(pages_data)

    # Save Document record
    doc = Document(
        user_id=current_user.id,
        filename=file.filename,
        file_hash=file_hash,
        file_type=ext.lstrip("."),
        mime_type=mime_type,
        file_size=len(contents),
        storage_path=storage_path,
        page_count=parsed_results["page_count"],
        document_type=parsed_results["document_type"],
        extraction_quality=parsed_results["extraction_quality"],
        status="review_required"
    )
    db.add(doc)
    await db.flush()

    # Save extracted claims
    saved_claims = []
    for c in parsed_results["claims"]:
        claim_obj = ExtractedClaim(
            document_id=doc.id,
            claim_type=c["claim_type"],
            field_name=c["field_name"],
            raw_value=c["raw_value"],
            normalized_value=c.get("normalized_value", c["raw_value"]),
            confidence=c.get("confidence", 0.85),
            page_number=c.get("page_number", 1),
            section_heading=c.get("section_heading", ""),
            text_excerpt=c.get("text_excerpt", ""),
            status="pending_review"
        )
        db.add(claim_obj)
        saved_claims.append(claim_obj)

    await db.commit()
    await db.refresh(doc)

    await log_audit_event(db, current_user.id, "document_uploaded", {
        "document_id": doc.id,
        "filename": doc.filename,
        "claims_extracted": len(saved_claims)
    })

    return {
        "id": doc.id,
        "filename": doc.filename,
        "file_type": doc.file_type,
        "file_size": doc.file_size,
        "page_count": doc.page_count,
        "document_type": doc.document_type,
        "extraction_quality": doc.extraction_quality,
        "is_duplicate": is_duplicate,
        "warnings": parsed_results["warnings"],
        "claims": [
            {
                "id": c.id,
                "claim_type": c.claim_type,
                "field_name": c.field_name,
                "raw_value": c.raw_value,
                "normalized_value": c.normalized_value,
                "confidence": c.confidence,
                "page_number": c.page_number,
                "section_heading": c.section_heading,
                "text_excerpt": c.text_excerpt,
                "status": c.status
            } for c in saved_claims
        ]
    }

@router.get("/")
async def list_documents(current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    res = await db.execute(select(Document).where(Document.user_id == current_user.id).order_by(Document.created_at.desc()))
    docs = res.scalars().all()
    return [
        {
            "id": d.id,
            "filename": d.filename,
            "file_type": d.file_type,
            "file_size": d.file_size,
            "page_count": d.page_count,
            "document_type": d.document_type,
            "extraction_quality": d.extraction_quality,
            "status": d.status,
            "created_at": d.created_at.isoformat() if d.created_at else None
        } for d in docs
    ]

@router.get("/{document_id}")
async def get_document(document_id: str, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    doc_res = await db.execute(select(Document).where(Document.id == document_id, Document.user_id == current_user.id))
    doc = doc_res.scalar_one_or_none()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
        
    claims_res = await db.execute(select(ExtractedClaim).where(ExtractedClaim.document_id == doc.id))
    claims = claims_res.scalars().all()
    
    return {
        "id": doc.id,
        "filename": doc.filename,
        "file_type": doc.file_type,
        "file_size": doc.file_size,
        "page_count": doc.page_count,
        "document_type": doc.document_type,
        "extraction_quality": doc.extraction_quality,
        "status": doc.status,
        "created_at": doc.created_at.isoformat() if doc.created_at else None,
        "claims": [
            {
                "id": c.id,
                "claim_type": c.claim_type,
                "field_name": c.field_name,
                "raw_value": c.raw_value,
                "normalized_value": c.normalized_value,
                "confidence": c.confidence,
                "page_number": c.page_number,
                "section_heading": c.section_heading,
                "text_excerpt": c.text_excerpt,
                "status": c.status
            } for c in claims
        ]
    }

@router.delete("/{document_id}")
async def delete_document(document_id: str, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    doc_res = await db.execute(select(Document).where(Document.id == document_id, Document.user_id == current_user.id))
    doc = doc_res.scalar_one_or_none()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
        
    # Remove file from disk
    if os.path.exists(doc.storage_path):
        try:
            os.remove(doc.storage_path)
        except Exception:
            pass

    await db.execute(delete(ExtractedClaim).where(ExtractedClaim.document_id == doc.id))
    await db.execute(delete(Document).where(Document.id == doc.id))
    await db.commit()
    
    await log_audit_event(db, current_user.id, "document_deleted", {"document_id": document_id, "filename": doc.filename})
    return {"message": "Document and associated claims securely deleted."}
