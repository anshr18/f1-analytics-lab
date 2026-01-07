"""
Document Ingestor

Convert F1 data into documents and generate embeddings for RAG.
"""

from typing import List, Dict, Any, Optional
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import text
from f1hub.db.models.llm import Document, Embedding
from f1hub.services.llm.embedding_service import EmbeddingService


class DocumentIngestor:
    """Service for ingesting F1 data as searchable documents."""

    def __init__(self, db: Session):
        """
        Initialize document ingestor.

        Args:
            db: Database session
        """
        self.db = db
        self.embedding_service = EmbeddingService()

    def chunk_text(self, text: str, chunk_size: int = 500, overlap: int = 50) -> List[str]:
        """
        Split text into overlapping chunks.

        Args:
            text: Text to chunk
            chunk_size: Maximum characters per chunk
            overlap: Overlap between chunks in characters

        Returns:
            List of text chunks
        """
        if len(text) <= chunk_size:
            return [text]

        chunks = []
        start = 0

        while start < len(text):
            end = start + chunk_size
            chunk = text[start:end]

            # Try to break at sentence boundary
            if end < len(text):
                last_period = chunk.rfind(".")
                last_newline = chunk.rfind("\n")
                break_point = max(last_period, last_newline)

                if break_point > chunk_size * 0.5:  # At least halfway through
                    chunk = chunk[: break_point + 1]
                    end = start + break_point + 1

            chunks.append(chunk.strip())
            start = end - overlap

        return chunks

    def ingest_session_summary(self, session_id: str) -> Document:
        """
        Create a document summarizing a race session.

        Args:
            session_id: Session UUID

        Returns:
            Created Document with embeddings
        """
        # Query session data with lap statistics
        query = text("""
            SELECT
                s.session_type,
                s.session_date,
                e.event_name,
                e.location,
                COUNT(DISTINCT l.driver_id) as num_drivers,
                COUNT(l.id) as total_laps,
                MIN(l.lap_time) as fastest_lap,
                AVG(l.lap_time) as avg_lap_time
            FROM sessions s
            JOIN events e ON s.event_id = e.id
            LEFT JOIN laps l ON l.session_id = s.id
            WHERE s.id = :session_id
            GROUP BY s.id, s.session_type, s.session_date, e.event_name, e.location
        """)

        result = self.db.execute(query, {"session_id": session_id}).fetchone()

        if not result:
            raise ValueError(f"Session {session_id} not found")

        # Generate document content
        content = f"""Session Summary: {result.session_type} at {result.event_name}

Location: {result.location}
Date: {result.session_date}
Drivers: {result.num_drivers}
Total Laps: {result.total_laps}
Fastest Lap: {result.fastest_lap:.3f}s
Average Lap Time: {result.avg_lap_time:.3f}s

This session featured {result.num_drivers} drivers competing at {result.location}.
The fastest lap time recorded was {result.fastest_lap:.3f} seconds, with an average
lap time of {result.avg_lap_time:.3f} seconds across all {result.total_laps} laps completed."""

        # Create document
        doc = Document(
            doc_type="session_summary",
            title=f"{result.event_name} - {result.session_type}",
            content=content,
            metadata={
                "session_id": session_id,
                "event_name": result.event_name,
                "location": result.location,
                "session_type": result.session_type,
                "session_date": str(result.session_date),
            },
        )
        self.db.add(doc)
        self.db.flush()  # Get doc.id

        # Chunk and embed
        chunks = self.chunk_text(content)
        embeddings_batch = self.embedding_service.generate_embeddings_batch(chunks)

        for i, (chunk, embedding) in enumerate(zip(chunks, embeddings_batch)):
            emb = Embedding(
                document_id=doc.id,
                chunk_text=chunk,
                chunk_index=i,
                embedding=embedding,
                chunk_metadata={"chunk_size": len(chunk)},
            )
            self.db.add(emb)

        self.db.commit()
        self.db.refresh(doc)
        return doc

    def ingest_driver_performance(
        self, session_id: str, driver_id: str
    ) -> Document:
        """
        Create a document about driver performance in a session.

        Args:
            session_id: Session UUID
            driver_id: Driver identifier

        Returns:
            Created Document with embeddings
        """
        # Query driver performance data
        query = text("""
            SELECT
                d.name as driver_name,
                d.abbreviation,
                s.session_type,
                e.event_name,
                COUNT(l.id) as laps_completed,
                MIN(l.lap_time) as best_lap,
                AVG(l.lap_time) as avg_lap,
                MAX(l.lap_time) as worst_lap,
                COUNT(DISTINCT l.tyre_compound) as compounds_used
            FROM laps l
            JOIN drivers d ON l.driver_id = d.id
            JOIN sessions s ON l.session_id = s.id
            JOIN events e ON s.event_id = e.id
            WHERE l.session_id = :session_id AND l.driver_id = :driver_id
            GROUP BY d.name, d.abbreviation, s.session_type, e.event_name
        """)

        result = self.db.execute(
            query, {"session_id": session_id, "driver_id": driver_id}
        ).fetchone()

        if not result:
            raise ValueError(f"No data for driver {driver_id} in session {session_id}")

        # Generate content
        content = f"""Driver Performance: {result.driver_name} ({result.abbreviation})

Event: {result.event_name}
Session: {result.session_type}

Performance Summary:
- Laps Completed: {result.laps_completed}
- Best Lap: {result.best_lap:.3f}s
- Average Lap: {result.avg_lap:.3f}s
- Worst Lap: {result.worst_lap:.3f}s
- Tyre Compounds Used: {result.compounds_used}

{result.driver_name} completed {result.laps_completed} laps during the {result.session_type}
at {result.event_name}. Their fastest lap was {result.best_lap:.3f} seconds, with an average
pace of {result.avg_lap:.3f} seconds per lap. They utilized {result.compounds_used} different
tyre compounds throughout the session."""

        # Create document
        doc = Document(
            doc_type="driver_performance",
            title=f"{result.driver_name} - {result.event_name} {result.session_type}",
            content=content,
            metadata={
                "session_id": session_id,
                "driver_id": driver_id,
                "driver_name": result.driver_name,
                "abbreviation": result.abbreviation,
                "event_name": result.event_name,
                "session_type": result.session_type,
            },
        )
        self.db.add(doc)
        self.db.flush()

        # Chunk and embed
        chunks = self.chunk_text(content)
        embeddings_batch = self.embedding_service.generate_embeddings_batch(chunks)

        for i, (chunk, embedding) in enumerate(zip(chunks, embeddings_batch)):
            emb = Embedding(
                document_id=doc.id,
                chunk_text=chunk,
                chunk_index=i,
                embedding=embedding,
            )
            self.db.add(emb)

        self.db.commit()
        self.db.refresh(doc)
        return doc

    def ingest_custom_document(
        self,
        title: str,
        content: str,
        doc_type: str = "custom",
        source_url: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Document:
        """
        Ingest a custom text document.

        Args:
            title: Document title
            content: Document content
            doc_type: Document type
            source_url: Optional source URL
            metadata: Optional metadata

        Returns:
            Created Document with embeddings
        """
        # Create document
        doc = Document(
            doc_type=doc_type,
            title=title,
            content=content,
            source_url=source_url,
            metadata=metadata or {},
        )
        self.db.add(doc)
        self.db.flush()

        # Chunk and embed
        chunks = self.chunk_text(content)
        embeddings_batch = self.embedding_service.generate_embeddings_batch(chunks)

        for i, (chunk, embedding) in enumerate(zip(chunks, embeddings_batch)):
            emb = Embedding(
                document_id=doc.id,
                chunk_text=chunk,
                chunk_index=i,
                embedding=embedding,
            )
            self.db.add(emb)

        self.db.commit()
        self.db.refresh(doc)
        return doc

    def bulk_ingest_sessions(self, limit: int = 10) -> List[Document]:
        """
        Bulk ingest recent sessions as documents.

        Args:
            limit: Number of recent sessions to ingest

        Returns:
            List of created Documents
        """
        # Get recent sessions that aren't already ingested
        query = text("""
            SELECT s.id
            FROM sessions s
            LEFT JOIN documents d ON d.metadata->>'session_id' = s.id::text
            WHERE d.id IS NULL AND s.is_ingested = true
            ORDER BY s.session_date DESC
            LIMIT :limit
        """)

        session_ids = [row.id for row in self.db.execute(query, {"limit": limit})]

        documents = []
        for session_id in session_ids:
            try:
                doc = self.ingest_session_summary(str(session_id))
                documents.append(doc)
            except Exception as e:
                print(f"Failed to ingest session {session_id}: {e}")
                continue

        return documents

    def get_document_count(self) -> Dict[str, int]:
        """
        Get count of documents by type.

        Returns:
            Dict mapping doc_type to count
        """
        query = text("""
            SELECT doc_type, COUNT(*) as count
            FROM documents
            GROUP BY doc_type
        """)

        results = self.db.execute(query).fetchall()
        return {row.doc_type: row.count for row in results}
