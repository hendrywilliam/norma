"""
Repositories module
"""

from .bab import BabRepository, bab_repository
from .pasal import PasalRepository, pasal_repository
from .peraturan import PeraturanRepository, peraturan_repository

__all__ = [
    "BabRepository",
    "bab_repository",
    "PasalRepository",
    "pasal_repository",
    "PeraturanRepository",
    "peraturan_repository"
]
