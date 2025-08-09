from typing import Optional


class ReaderError(Exception):
    def __init__(self, message: str, file_path: Optional[str] = None):
        self.file_path = file_path
        super().__init__(message)


class ReaderFileNotFoundError(ReaderError):
    def __init__(self, file_path: str):
        super().__init__(f"File not found: {file_path}", file_path)


class ReaderInvalidFormatError(ReaderError):
    def __init__(self, file_path: str, format_type: str, details: str):
        message = f"Invalid {format_type} format in {file_path}: {details}"
        super().__init__(message, file_path)


class ReaderValidationError(ReaderError):
    def __init__(self, file_path: str, schema_name: str, details: str):
        message = (
            f"Schema validation failed for {schema_name} in {file_path}: {details}"
        )
        super().__init__(message, file_path)


class ReaderEncodingError(ReaderError):
    def __init__(self, file_path: str, encoding: str, details: str):
        message = f"Encoding error ({encoding}) in {file_path}: {details}"
        super().__init__(message, file_path)


class ReaderAccessError(ReaderError):
    def __init__(self, file_path: str, details: str):
        message = f"Access denied for {file_path}: {details}"
        super().__init__(message, file_path)
