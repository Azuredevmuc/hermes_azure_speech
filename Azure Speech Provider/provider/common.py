# provider/common.py

from __future__ import annotations

import queue
from pathlib import Path
import tempfile
import threading
from typing import Iterable


def ensure_parent_dir(path: str | Path) -> Path:
    """Ensure the parent directory of a path exists and return the resolved Path."""
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    return p


def read_text_file(path: str | Path, encoding: str = "utf-8") -> str:
    """Read a UTF-8 text file and strip surrounding whitespace."""
    p = Path(path)
    return p.read_text(encoding=encoding).strip()


def write_text_file(path: str | Path, content: str, encoding: str = "utf-8") -> Path:
    """Write text content to a file, creating parent directories as needed."""
    p = ensure_parent_dir(path)
    p.write_text(content, encoding=encoding)
    return p


def temp_file_path(suffix: str = "") -> Path:
    """Create a unique temp file path without writing content yet."""
    handle = tempfile.NamedTemporaryFile(delete=False, suffix=suffix)
    try:
        return Path(handle.name)
    finally:
        handle.close()


def temp_dir_path(prefix: str = "azure_speech_") -> Path:
    """Create and return a temporary directory path."""
    return Path(tempfile.mkdtemp(prefix=prefix))


def normalize_whitespace(text: str) -> str:
    """Collapse whitespace to single spaces and strip the result."""
    return " ".join(text.split())


def chunk_text(text: str, max_chars: int) -> list[str]:
    """
    Split text into chunks no longer than max_chars.
    Prefers paragraph and sentence boundaries, but falls back to hard slicing.
    """
    normalized = text.strip()
    if not normalized:
        return []

    if len(normalized) <= max_chars:
        return [normalized]

    paragraphs = [p.strip() for p in normalized.split("\n\n") if p.strip()]
    chunks: list[str] = []
    current = ""

    for paragraph in paragraphs:
        candidate = f"{current}\n\n{paragraph}".strip() if current else paragraph
        if len(candidate) <= max_chars:
            current = candidate
            continue

        if current:
            chunks.append(current)
            current = ""

        if len(paragraph) <= max_chars:
            current = paragraph
            continue

        sentences = [s.strip() for s in paragraph.replace("\n", " ").split(". ") if s.strip()]
        for sentence in sentences:
            sentence = sentence if sentence.endswith(".") else f"{sentence}."
            candidate = f"{current} {sentence}".strip() if current else sentence
            if len(candidate) <= max_chars:
                current = candidate
            else:
                if current:
                    chunks.append(current)
                current = sentence

    if current:
        chunks.append(current)

    return chunks


def safe_delete(path: str | Path) -> None:
    """Delete a file if it exists."""
    p = Path(path)
    try:
        if p.exists() and p.is_file():
            p.unlink()
    except OSError:
        # Best-effort cleanup only.
        pass


def existing_paths(paths: Iterable[str | Path]) -> list[Path]:
    """Return only paths that currently exist."""
    result: list[Path] = []
    for raw in paths:
        p = Path(raw)
        if p.exists():
            result.append(p)
    return result


def wait_for_sdk_future(result_future: object, timeout_seconds: int):
    """Wait for an Azure SDK future that exposes a blocking zero-arg get()."""
    outcome: queue.Queue[tuple[str, object]] = queue.Queue(maxsize=1)

    def _runner() -> None:
        try:
            result = result_future.get()
        except Exception as exc:  # pragma: no cover - exercised through callers
            outcome.put(("error", exc))
            return
        outcome.put(("result", result))

    thread = threading.Thread(target=_runner, daemon=True)
    thread.start()
    thread.join(timeout_seconds)

    if thread.is_alive():
        raise TimeoutError(f"Azure SDK future exceeded {timeout_seconds} seconds.")

    kind, value = outcome.get_nowait()
    if kind == "error":
        raise value
    return value