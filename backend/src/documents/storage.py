from __future__ import annotations

import os
import re
import unicodedata
from contextlib import suppress
from pathlib import Path
from uuid import uuid4


class LocalDocumentStorage:
    """Stores originals outside the request layer using document-scoped paths."""

    def __init__(self, root_path: Path) -> None:
        self._root_path = root_path.resolve()

    def store(self, *, document_id: str, filename: str, content: bytes) -> str:
        destination = self._root_path / document_id / filename
        destination.parent.mkdir(parents=True, exist_ok=True)

        temporary_path = destination.with_name(f".{destination.name}.{uuid4().hex}.tmp")
        try:
            temporary_path.write_bytes(content)
            os.replace(temporary_path, destination)
        finally:
            temporary_path.unlink(missing_ok=True)

        return str(destination)

    def delete(self, storage_path: str) -> None:
        path = Path(storage_path).resolve()
        if path.is_relative_to(self._root_path):
            path.unlink(missing_ok=True)
            with suppress(OSError):
                path.parent.rmdir()

    def exists(self, storage_path: str) -> bool:
        path = Path(storage_path).resolve()
        return path.is_relative_to(self._root_path) and path.is_file()


def sanitize_filename(filename: str | None) -> str:
    """Reduce a client filename to a safe, portable basename."""
    raw_name = (filename or "").replace("\\", "/").rsplit("/", maxsplit=1)[-1]
    normalized = unicodedata.normalize("NFKD", raw_name).encode("ascii", "ignore").decode()
    sanitized = re.sub(r"[^A-Za-z0-9._-]+", "-", normalized).strip("._-")

    if not sanitized:
        raise ValueError("the upload filename must contain at least one valid character")

    return sanitized[:255]
