from pathlib import Path

from enrichment.application.dtos.file_process import FileProcessResult
from enrichment.infrastructure.repositories.company_repository import CompanyRepository
from enrichment.infrastructure.readers.interfaces import JSONDataReader


class CompanyInfoWriter:
    def __init__(self, reader: JSONDataReader, repository: CompanyRepository):
        self.reader = reader
        self.repository = repository

    async def process_file(self, file_path: str) -> FileProcessResult:
        path = Path(file_path)
        if not path.exists():
            return FileProcessResult(
                success=False, message=f"File not found: {file_path}"
            )

        try:
            aggregate = self.reader.read(file_path)
            await self.repository.save(aggregate)

            return FileProcessResult(success=True, company_id=aggregate.company.id)
        except Exception as e:
            return FileProcessResult(success=False, message=str(e))
