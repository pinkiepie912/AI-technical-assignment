from typing import Optional


class RepositoryError(Exception):
    def __init__(self, message: str, file_path: Optional[str] = None):
        self.file_path = file_path
        super().__init__(message)


class DuplicatedCompanyError(RepositoryError):
    def __init__(self):
        super().__init__("Duplicated company found in the repository.")
