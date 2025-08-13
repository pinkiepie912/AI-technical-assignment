from dataclasses import dataclass
from uuid import UUID


@dataclass
class NewsChunk:
    id: int
    company_id: UUID
    title: str
    contents: str
    similarity: float
