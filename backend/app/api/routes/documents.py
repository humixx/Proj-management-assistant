"""Document API routes."""
from pathlib import Path
from uuid import UUID, uuid4

import aiofiles
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db, get_current_project_id, verify_project_ownership
from app.auth.deps import get_current_user
from app.config import settings
from app.db.models.user import User
from app.db.repositories import DocumentRepository
from app.services.document_processor import DocumentProcessor
from app.services.embedding_service import embedding_service
from app.services.vector_store import VectorStore
from app.schemas import (
    DocumentResponse,
    DocumentListResponse,
    SearchResponse,
    SearchResult,
)

router = APIRouter()


@router.post("/upload", response_model=DocumentResponse, status_code=status.HTTP_201_CREATED)
async def upload_document(
    file: UploadFile = File(...),
    project_id: UUID = Depends(get_current_project_id),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Upload and process a document.

    The document will be processed synchronously:
    1. Save file to disk
    2. Extract text and create chunks
    3. Generate embeddings
    4. Store in database
    """
    await verify_project_ownership(project_id, current_user.id, db)

    # Validate file type
    try:
        file_type = DocumentProcessor.get_file_type(file.filename)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    # Create upload directory
    upload_dir = Path(settings.UPLOAD_DIR) / str(project_id)
    upload_dir.mkdir(parents=True, exist_ok=True)

    # Save file
    file_id = uuid4()
    file_path = upload_dir / f"{file_id}_{file.filename}"

    async with aiofiles.open(file_path, "wb") as f:
        content = await file.read()
        await f.write(content)

    file_size = len(content)

    # Create document record
    repo = DocumentRepository(db)
    document = await repo.create(
        project_id=project_id,
        filename=file.filename,
        file_type=file_type,
        storage_path=str(file_path),
        file_size=file_size,
    )

    # Process document
    try:
        processor = DocumentProcessor(
            chunk_size=settings.CHUNK_SIZE,
            chunk_overlap=settings.CHUNK_OVERLAP,
        )
        chunks = await processor.process(str(file_path), file_type)

        if chunks:
            # Generate embeddings
            texts = [c["chunk_text"] for c in chunks]
            embeddings = await embedding_service.embed_batch(texts)

            # Add embeddings to chunks
            for chunk, embedding in zip(chunks, embeddings):
                chunk["embedding"] = embedding

            # Store chunks
            chunk_count = await repo.add_chunks(document.id, chunks)
            document = await repo.update_processed(document.id, chunk_count)
        else:
            document = await repo.update_processed(document.id, 0)

    except Exception as e:
        # Log error but don't fail - document is saved
        print(f"Error processing document {document.id}: {e}")

    return document


@router.get("", response_model=DocumentListResponse)
async def list_documents(
    project_id: UUID = Depends(get_current_project_id),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """List all documents for a project."""
    await verify_project_ownership(project_id, current_user.id, db)
    repo = DocumentRepository(db)
    documents = await repo.list_by_project(project_id)
    return DocumentListResponse(documents=documents, total=len(documents))


@router.get("/{document_id}", response_model=DocumentResponse)
async def get_document(
    document_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get a document by ID."""
    repo = DocumentRepository(db)
    document = await repo.get_by_id(document_id)
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    await verify_project_ownership(document.project_id, current_user.id, db)
    return document


@router.delete("/{document_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_document(
    document_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Delete a document and its chunks."""
    repo = DocumentRepository(db)

    # Get document to find file path
    document = await repo.get_by_id(document_id)
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    await verify_project_ownership(document.project_id, current_user.id, db)

    # Delete chunks
    vector_store = VectorStore(db)
    await vector_store.delete_by_document(document_id)

    # Delete document record
    await repo.delete(document_id)

    # Delete file (best effort)
    try:
        Path(document.storage_path).unlink(missing_ok=True)
    except Exception:
        pass


@router.post("/search", response_model=SearchResponse)
async def search_documents(
    query: str = Query(..., description="Search query"),
    project_id: UUID = Depends(get_current_project_id),
    top_k: int = Query(5, description="Number of results"),
    threshold: float = Query(0.3, description="Similarity threshold (0-1)"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Search documents using semantic similarity."""
    await verify_project_ownership(project_id, current_user.id, db)

    # Generate query embedding
    query_embedding = await embedding_service.embed_text(query)

    # Search
    vector_store = VectorStore(db)
    results = await vector_store.search_similar(
        project_id=project_id,
        query_embedding=query_embedding,
        top_k=top_k,
        threshold=threshold,
    )

    search_results = [
        SearchResult(
            chunk_text=r["chunk_text"],
            document_id=r["document_id"],
            document_name=r["document_name"],
            page_number=r["page_number"],
            score=r["score"],
        )
        for r in results
    ]

    return SearchResponse(results=search_results, query=query, total=len(search_results))
