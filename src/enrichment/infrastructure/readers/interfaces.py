from abc import ABC, abstractmethod
from pathlib import Path
from typing import Generic, TypeVar, Union

from .exceptions import ReaderFileNotFoundError

T = TypeVar("T", covariant=True)


class JSONDataReader(ABC, Generic[T]):
    @abstractmethod
    def read(self, file_path: Union[str, Path]) -> T:
        pass

    def validate_file_exists(self, file_path: Path) -> None:
        if not file_path.exists():
            raise ReaderFileNotFoundError(str(file_path))

        if not file_path.is_file():
            raise ReaderFileNotFoundError(str(file_path))

