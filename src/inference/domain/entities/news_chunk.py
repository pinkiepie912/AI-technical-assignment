from dataclasses import dataclass
from uuid import UUID


@dataclass(frozen=True)
class NewsChunk:
    company_id: UUID
    title: str
    contents: str
