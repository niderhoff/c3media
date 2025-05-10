"""
CCC Media API Client
A Python client for the media.ccc.de API.
"""

from .client import CCCMediaClient
from .models import (
    Conference,
    Event,
    Recording,
    Subtitle,
    RelatedEvent,
    ConferencesResponse,
    DictResponse,
)
from .constants import BASE_URL, CDN_URL, COMMON_LANGUAGES

__version__ = "0.1.0"

__all__ = [
    "CCCMediaClient",
    "Conference",
    "Event",
    "Recording",
    "Subtitle",
    "RelatedEvent",
    "ConferencesResponse",
    "DictResponse",
    "BASE_URL",
    "CDN_URL",
    "COMMON_LANGUAGES",
]
