import uuid
from datetime import datetime
from sqlalchemy import Column, String, Integer, Float, Text, DateTime, ForeignKey, UniqueConstraint, JSON
from sqlalchemy.orm import relationship
from app.core.db import Base

def generate_uuid():
    return str(uuid.uuid4())

class Show(Base):
    __tablename__ = "shows"

    id = Column(String, primary_key=True, default=generate_uuid)
    title = Column(String, nullable=False, unique=True, index=True)
    slug = Column(String, nullable=False, unique=True, index=True)
    section = Column(String, nullable=True, index=True)
    categories = Column(JSON, nullable=False, default=list)
    synopsis = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    seasons = relationship("Season", back_populates="show", cascade="all, delete-orphan")
    episodes = relationship("Episode", back_populates="show", cascade="all, delete-orphan")

class Season(Base):
    __tablename__ = "seasons"

    id = Column(String, primary_key=True, default=generate_uuid)
    show_id = Column(String, ForeignKey("shows.id", ondelete="CASCADE"), nullable=False)
    season_number = Column(Integer, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    show = relationship("Show", back_populates="seasons")
    episodes = relationship("Episode", back_populates="season", cascade="all, delete-orphan")

    __table_args__ = (
        UniqueConstraint("show_id", "season_number", name="uq_show_season_number"),
    )

class Episode(Base):
    __tablename__ = "episodes"

    id = Column(String, primary_key=True, default=generate_uuid)
    show_id = Column(String, ForeignKey("shows.id", ondelete="CASCADE"), nullable=False)
    season_id = Column(String, ForeignKey("seasons.id", ondelete="CASCADE"), nullable=False)
    episode_number = Column(Integer, nullable=False)
    episode_title = Column(String, nullable=False)
    duration_seconds = Column(Integer, nullable=True)
    language = Column(String, nullable=False)
    content_group = Column(String, nullable=False, index=True)
    status = Column(String, nullable=False, default="draft", index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    show = relationship("Show", back_populates="episodes")
    season = relationship("Season", back_populates="episodes")
    artworks = relationship("Artwork", back_populates="episode", cascade="all, delete-orphan")

    __table_args__ = (
        UniqueConstraint("content_group", "language", name="uq_content_group_language"),
    )

class Artwork(Base):
    __tablename__ = "artworks"

    id = Column(String, primary_key=True, default=generate_uuid)
    episode_id = Column(String, ForeignKey("episodes.id", ondelete="CASCADE"), nullable=False)
    artwork_type = Column(String, nullable=False) # 'poster', 'banner', 'thumbnail'
    file_path = Column(String, nullable=False)
    url = Column(String, nullable=False)
    width = Column(Integer, nullable=False)
    height = Column(Integer, nullable=False)
    file_size_kb = Column(Float, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    episode = relationship("Episode", back_populates="artworks")

    __table_args__ = (
        UniqueConstraint("episode_id", "artwork_type", name="uq_episode_artwork_type"),
    )

class PublishRun(Base):
    __tablename__ = "publish_runs"

    id = Column(String, primary_key=True, default=generate_uuid)
    published_at = Column(DateTime, default=datetime.utcnow)
    published_by = Column(String, nullable=False, default="admin")
    status = Column(String, nullable=False) # 'success', 'failed'
    item_counts = Column(JSON, nullable=False, default=dict)
    error_summary = Column(Text, nullable=True)
    catalog_key = Column(String, nullable=False, default="catalog.json")
