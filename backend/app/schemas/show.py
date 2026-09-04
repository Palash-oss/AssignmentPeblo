from pydantic import BaseModel, ConfigDict
from typing import List, Optional
from datetime import datetime

class ArtworkBase(BaseModel):
    id: str
    episode_id: str
    artwork_type: str
    url: str
    width: int
    height: int
    file_size_kb: float

    model_config = ConfigDict(from_attributes=True)

class EpisodeBase(BaseModel):
    id: str
    show_id: str
    season_id: str
    episode_number: int
    episode_title: str
    duration_seconds: Optional[int] = None
    language: str
    content_group: str
    status: str
    created_at: datetime
    artworks: List[ArtworkBase] = []

    model_config = ConfigDict(from_attributes=True)

class EpisodeCreate(BaseModel):
    show_id: str
    season_number: int = 1
    episode_number: int
    episode_title: str
    duration_seconds: Optional[int] = None
    language: str
    content_group: str
    status: str = "draft"

class EpisodeUpdate(BaseModel):
    episode_title: Optional[str] = None
    duration_seconds: Optional[int] = None
    language: Optional[str] = None
    content_group: Optional[str] = None
    status: Optional[str] = None
    season_number: Optional[int] = None

class ShowBase(BaseModel):
    id: str
    title: str
    slug: str
    section: Optional[str] = None
    categories: List[str] = []
    synopsis: Optional[str] = None
    created_at: datetime
    episodes: List[EpisodeBase] = []

    model_config = ConfigDict(from_attributes=True)

class ShowCreate(BaseModel):
    title: str
    slug: str
    section: Optional[str] = None
    categories: List[str] = []
    synopsis: Optional[str] = None

class ShowUpdate(BaseModel):
    title: Optional[str] = None
    slug: Optional[str] = None
    section: Optional[str] = None
    categories: Optional[List[str]] = None
    synopsis: Optional[str] = None
