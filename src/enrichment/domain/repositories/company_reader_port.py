from abc import ABC, abstractmethod
from pathlib import Path
from typing import Union

from enrichment.domain.aggregates.company_aggregate import CompanyAggregate

from ..exceptions.company_reader_exceptions import ReaderFileNotFoundError


class CompanyReaderPort(ABC):
    @abstractmethod
    def read(self, file_path: Union[str, Path]) -> CompanyAggregate:
        pass

    def validate_file_exists(self, file_path: Path) -> None:
        if not file_path.exists():
            raise ReaderFileNotFoundError(str(file_path))

        if not file_path.is_file():
            raise ReaderFileNotFoundError(str(file_path))
