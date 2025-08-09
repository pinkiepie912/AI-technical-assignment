from dataclasses import dataclass
from typing import Optional
from uuid import UUID


@dataclass
class FileProcessResult:
    success: bool
    company_id: Optional[UUID] = None
    message: Optional[str] = None
