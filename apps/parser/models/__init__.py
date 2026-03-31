"""
Data models module
"""

from .peraturan import (
    PeraturanBase,
    PeraturanCreate,
    PeraturanUpdate,
    PeraturanInDB,
    PeraturanResponse,
    PeraturanListResponse,
    PeraturanFilter,
    PeraturanSummary,
    PeraturanDetail,
    PeraturanMetadata,
    ParseResult,
    PeraturanFullResponse,
    AyatNode,
    PasalNode,
    BabNode,
    PeraturanTreeResponse,
)

from .bab import (
    BabBase,
    BabCreate,
    BabUpdate,
    BabInDB,
    BabResponse,
    BabWithPasalCount,
    BabWithPeraturanInfo,
    BabListResponse,
    BabFilter,
)

from .pasal import (
    PasalBase,
    PasalCreate,
    PasalUpdate,
    PasalInDB,
    PasalResponse,
    PasalWithAyatCount,
    PasalWithBabPeraturan,
    PasalListResponse,
    PasalFilter,
)

from .ayat import (
    AyatBase,
    AyatCreate,
    AyatUpdate,
    AyatInDB,
    AyatResponse,
    AyatWithPasalInfo,
    AyatWithBabInfo,
    AyatWithPasalBabPeraturan,
    AyatListResponse,
    AyatFilter,
)

from .ai_parse import (
    AIParseRequest,
    AIParseResult,
    AIParsePerPageResult,
    AIParsingStatus,
    AIBatchParseRequest,
    AIBatchParseResult,
    GLMConfigModel,
    AyatParsedNode,
    PasalParsedNode,
    BabParsedNode,
    AIParseTreeResult,
)

__all__ = [
    # Peraturan
    "PeraturanBase",
    "PeraturanCreate",
    "PeraturanUpdate",
    "PeraturanInDB",
    "PeraturanResponse",
    "PeraturanListResponse",
    "PeraturanFilter",
    "PeraturanSummary",
    "PeraturanDetail",
    "PeraturanMetadata",
    "ParseResult",
    "PeraturanFullResponse",
    # Tree structure models
    "AyatNode",
    "PasalNode",
    "BabNode",
    "PeraturanTreeResponse",
    # Bab
    "BabBase",
    "BabCreate",
    "BabUpdate",
    "BabInDB",
    "BabResponse",
    "BabWithPasalCount",
    "BabWithPeraturanInfo",
    "BabListResponse",
    "BabFilter",
    # Pasal
    "PasalBase",
    "PasalCreate",
    "PasalUpdate",
    "PasalInDB",
    "PasalResponse",
    "PasalWithAyatCount",
    "PasalWithBabPeraturan",
    "PasalListResponse",
    "PasalFilter",
    # Ayat
    "AyatBase",
    "AyatCreate",
    "AyatUpdate",
    "AyatInDB",
    "AyatResponse",
    "AyatWithPasalInfo",
    "AyatWithBabInfo",
    "AyatWithPasalBabPeraturan",
    "AyatListResponse",
    "AyatFilter",
    # AI Parse
    "AIParseRequest",
    "AIParseResult",
    "AIParsePerPageResult",
    "AIParsingStatus",
    "AIBatchParseRequest",
    "AIBatchParseResult",
    "GLMConfigModel",
    # AI Parse Tree Models
    "AyatParsedNode",
    "PasalParsedNode",
    "BabParsedNode",
    "AIParseTreeResult",
]
