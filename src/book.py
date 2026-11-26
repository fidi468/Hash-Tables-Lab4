from dataclasses import dataclass


@dataclass(frozen=True)
class Book:
    """Kitab strukturu (Fidan). Açar: isbn."""
    isbn: str
    title: str = ""
    author: str = ""
