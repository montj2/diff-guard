"""Database models base (placeholder)."""

from __future__ import annotations

from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):  # pragma: no cover - no behavior
    pass


__all__ = ["Base"]
