"""PostgreSQL database setup and session management."""

import logging
import os
from datetime import datetime
from typing import Optional

from sqlalchemy import create_engine, Column, String, DateTime, Text, Integer, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import NullPool

logger = logging.getLogger(__name__)

# Database URL from environment or default
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://deepresearch:deepresearch@localhost/deepresearch"
)

# Create engine with connection pooling
engine = create_engine(
    DATABASE_URL,
    echo=os.getenv("SQL_ECHO", "false").lower() == "true",
    pool_pre_ping=True,
    connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


class ResearchTask(Base):
    """PostgreSQL model for research tasks."""

    __tablename__ = "research_tasks"

    id = Column(Integer, primary_key=True, index=True)
    research_id = Column(String(255), unique=True, index=True, nullable=False)
    query = Column(Text, nullable=False)
    research_type = Column(String(50), nullable=False)  # 'supervisor' or 'researcher'
    status = Column(String(50), nullable=False)  # pending, running, completed, failed
    result = Column(JSON, nullable=True)  # Stores result dict as JSON
    error = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)


def init_db():
    """Initialize database tables."""
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")
        raise


def get_db() -> Session:
    """Get database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


class ResearchRepository:
    """Repository for research tasks database operations."""

    @staticmethod
    def create(
        db: Session,
        research_id: str,
        query: str,
        research_type: str,
        status: str = "pending",
    ) -> ResearchTask:
        """Create a new research task."""
        task = ResearchTask(
            research_id=research_id,
            query=query,
            research_type=research_type,
            status=status,
        )
        db.add(task)
        db.commit()
        db.refresh(task)
        logger.info(f"Created research task: {research_id}")
        return task

    @staticmethod
    def get_by_id(db: Session, research_id: str) -> Optional[ResearchTask]:
        """Get research task by ID."""
        return db.query(ResearchTask).filter(
            ResearchTask.research_id == research_id
        ).first()

    @staticmethod
    def update_status(db: Session, research_id: str, status: str):
        """Update research task status."""
        task = db.query(ResearchTask).filter(
            ResearchTask.research_id == research_id
        ).first()
        if task:
            task.status = status
            task.updated_at = datetime.utcnow()
            db.commit()
            db.refresh(task)
            logger.info(f"Updated research {research_id} status to {status}")
        return task

    @staticmethod
    def update_result(db: Session, research_id: str, result: dict):
        """Update research task with result."""
        task = db.query(ResearchTask).filter(
            ResearchTask.research_id == research_id
        ).first()
        if task:
            task.result = result
            task.status = "completed"
            task.updated_at = datetime.utcnow()
            db.commit()
            db.refresh(task)
            logger.info(f"Updated research {research_id} with results")
        return task

    @staticmethod
    def update_error(db: Session, research_id: str, error: str):
        """Update research task with error."""
        task = db.query(ResearchTask).filter(
            ResearchTask.research_id == research_id
        ).first()
        if task:
            task.error = error
            task.status = "failed"
            task.updated_at = datetime.utcnow()
            db.commit()
            db.refresh(task)
            logger.info(f"Updated research {research_id} with error")
        return task

    @staticmethod
    def get_all(db: Session, limit: int = 100, offset: int = 0) -> list[ResearchTask]:
        """Get all research tasks with pagination."""
        return db.query(ResearchTask).order_by(
            ResearchTask.created_at.desc()
        ).limit(limit).offset(offset).all()

    @staticmethod
    def get_all_by_status(
        db: Session, status: str, limit: int = 100, offset: int = 0
    ) -> list[ResearchTask]:
        """Get research tasks filtered by status."""
        return db.query(ResearchTask).filter(
            ResearchTask.status == status
        ).order_by(
            ResearchTask.created_at.desc()
        ).limit(limit).offset(offset).all()

    @staticmethod
    def delete(db: Session, research_id: str) -> bool:
        """Delete a research task."""
        task = db.query(ResearchTask).filter(
            ResearchTask.research_id == research_id
        ).first()
        if task:
            db.delete(task)
            db.commit()
            logger.info(f"Deleted research {research_id}")
            return True
        return False
