"""
Type definitions for the CCC Media API Client.
"""

from typing import List, TypedDict, Any, Protocol


class RelatedEvent(TypedDict):
    """Type definition for a related event."""

    guid: str
    title: str
    url: str


class Recording(TypedDict):
    """Type definition for a recording object."""

    size: int
    length: int
    mime_type: str
    language: str
    filename: str
    state: str
    folder: str
    high_quality: bool
    width: int
    height: int
    updated_at: str
    recording_url: str
    url: str
    event_url: str
    conference_url: str


class Event(TypedDict, total=False):
    """Type definition for an event object."""

    guid: str
    title: str
    subtitle: str | None
    slug: str
    link: str
    description: str
    original_language: str
    persons: List[str]
    tags: List[str]
    view_count: int
    promoted: bool
    date: str
    release_date: str
    updated_at: str
    length: int
    duration: int
    thumb_url: str
    poster_url: str
    timeline_url: str
    thumbnails_url: str
    frontend_link: str
    url: str
    conference_title: str
    conference_url: str
    related: List[RelatedEvent]
    recordings: List[Recording] | None


class Conference(TypedDict):
    """Type definition for a conference object."""

    acronym: str
    aspect_ratio: str
    updated_at: str
    title: str
    schedule_url: str
    slug: str
    event_last_released_at: str
    link: str
    description: str
    webgen_location: str
    logo_url: str
    images_url: str
    recordings_url: str
    url: str
    events: List[Event]


class ConferencesResponse(TypedDict):
    """Type definition for the conferences response."""

    conferences: List[Conference]


class DictResponse(Protocol):
    """Protocol for dictionary responses."""

    def __getitem__(self, key: str) -> Any: ...


class Subtitle(TypedDict):
    """Type definition for a subtitle object."""

    language: str
    url: str
    content: str | None
