import json
from pathlib import Path
from typing import Union

from ..dtos.forest_of_hyuksin import ForestOfHyuksinCompanyData
from .exceptions import (
    ReaderEncodingError,
    ReaderInvalidFormatError,
    ReaderValidationError,
)
from .interfaces import JSONDataReader


class ForestOfHyuksinReader(JSONDataReader[ForestOfHyuksinCompanyData]):
    def read(self, file_path: Union[str, Path]) -> ForestOfHyuksinCompanyData:
        file_path = Path(file_path)

        self.validate_file_exists(file_path)

        try:
            with file_path.open("r", encoding="utf-8") as f:
                json_data = json.load(f)

        except json.JSONDecodeError as e:
            raise ReaderInvalidFormatError(str(file_path), "JSON", str(e))

        except UnicodeDecodeError as e:
            raise ReaderEncodingError(str(file_path), "UTF-8", str(e))

        except Exception as e:
            raise ReaderInvalidFormatError(
                str(file_path), "JSON", f"Unexpected error: {e}"
            )

        try:
            company_data = ForestOfHyuksinCompanyData.model_validate(json_data)
            return company_data

        except Exception as e:
            raise ReaderValidationError(str(file_path), "ForestOfHyuksin", str(e))
