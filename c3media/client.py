"""
Main client implementation for the CCC Media API.
"""

import requests
from typing import Type, cast, TypeVar

from .models import (
    Conference,
    Event,
    Recording,
    Subtitle,
    ConferencesResponse,
)
from .constants import BASE_URL, COMMON_LANGUAGES
from .utils import extract_recording_id

T = TypeVar("T")


class CCCMediaClient:
    """Client for interacting with the media.ccc.de API."""

    def __init__(self) -> None:
        """Initialize the CCC Media API client."""
        self.session = requests.Session()

    def close(self) -> None:
        """Close the session and clean up resources."""
        self.session.close()

    def __enter__(self) -> "CCCMediaClient":
        """Support for context manager protocol."""
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: object | None,
    ) -> None:
        """Clean up resources when exiting context."""
        self.close()

    def _make_request(self, endpoint: str, response_type: Type[T]) -> T:
        """
        Make a request to the API.

        Args:
            endpoint: The API endpoint to call
            response_type: The expected response type

        Returns:
            The JSON response from the API cast to the specified type

        Raises:
            requests.RequestException: If the request fails
        """
        url = f"{BASE_URL}/{endpoint}"
        response = self.session.get(url)
        response.raise_for_status()
        return cast(T, response.json())

    def get_conferences(self) -> list[Conference]:
        """
        Get all conferences.

        Returns:
            List of conference objects
        """
        response = self._make_request("conferences", ConferencesResponse)
        return response["conferences"]

    def get_conference_by_acronym(self, acronym: str) -> Conference | None:
        """
        Get a specific conference by its acronym.

        Args:
            acronym: The acronym of the conference (e.g., '38c3')

        Returns:
            Conference object if found, None otherwise
        """
        conferences = self.get_conferences()
        for conference in conferences:
            if conference["acronym"].lower() == acronym.lower():
                return conference
        return None

    def get_conference(self, conference_id: str) -> Conference:
        """
        Get a specific conference by ID.

        Args:
            conference_id: The ID of the conference

        Returns:
            Conference object

        Raises:
            requests.RequestException: If the request fails
        """
        response = self._make_request(f"conferences/{conference_id}", Conference)
        return response

    def get_event(self, event_guid: str) -> Event:
        """
        Get a specific event by its GUID.

        Args:
            event_guid: The GUID of the event

        Returns:
            Event object

        Raises:
            requests.RequestException: If the request fails
        """
        return self._make_request(f"events/{event_guid}", Event)

    def get_recording(self, recording_id: str) -> Recording:
        """
        Get a specific recording by ID.

        Args:
            recording_id: The ID of the recording

        Returns:
            Recording object

        Raises:
            requests.RequestException: If the request fails
        """
        return self._make_request(f"recordings/{recording_id}", Recording)

    def get_conference_recordings_url(self, conference: Conference) -> str:
        """
        Get the recordings URL for a conference.

        Args:
            conference: The conference object

        Returns:
            The recordings URL
        """
        return conference["recordings_url"]

    def get_conference_logo_url(self, conference: Conference) -> str:
        """
        Get the logo URL for a conference.

        Args:
            conference: The conference object

        Returns:
            The logo URL
        """
        return conference["logo_url"]

    def get_conference_images_url(self, conference: Conference) -> str:
        """
        Get the images URL for a conference.

        Args:
            conference: The conference object

        Returns:
            The images URL
        """
        return conference["images_url"]

    def _get_conference_id(self, conference: Conference) -> str:
        """
        Get the conference ID from a conference object.

        Args:
            conference: The conference object

        Returns:
            The conference ID (acronym)
        """
        return conference["acronym"]

    def get_conference_events(self, conference: Conference) -> list[Event]:
        """
        Get all events for a conference.

        Args:
            conference: The conference object

        Returns:
            List of event objects
        """
        conference_id = self._get_conference_id(conference)
        # Fetch events for this conference
        response = self._make_request(f"conferences/{conference_id}", dict)
        events: list[Event] = response["events"]
        return events

    def get_event_by_guid(self, guid: str) -> Event | None:
        """
        Get a specific event by its GUID.

        Args:
            guid: The GUID of the event

        Returns:
            Event object if found, None otherwise
        """
        return self._make_request(f"events/{guid}", Event)

    def get_events_by_person(self, conference: Conference, person: str) -> list[Event]:
        """
        Get all events by a specific person in a conference.

        Args:
            conference: The conference object
            person: The name of the person

        Returns:
            List of event objects
        """
        return [
            event
            for event in self.get_conference_events(conference)
            if person in event["persons"]
        ]

    def get_events_by_tag(self, conference: Conference, tag: str) -> list[Event]:
        """
        Get all events with a specific tag in a conference.

        Args:
            conference: The conference object
            tag: The tag to search for

        Returns:
            List of event objects
        """
        return [
            event
            for event in self.get_conference_events(conference)
            if tag in event["tags"]
        ]

    def get_events_by_fuzzy_title(
        self, conference: Conference, search_title: str, threshold: int = 70
    ) -> list[Event]:
        """
        Get events by fuzzy matching on the title.

        Args:
            conference: The conference object
            search_title: The title to search for
            threshold: The minimum similarity score (0-100) to consider a match (default: 80)

        Returns:
            List of event objects whose titles match the search title above the threshold
        """
        try:
            from fuzzywuzzy import fuzz
        except ImportError:
            raise ImportError(
                "The fuzzywuzzy package is required for fuzzy title matching. "
                "Please install it with: pip install fuzzywuzzy python-Levenshtein"
            )

        events = self.get_conference_events(conference)
        return [
            event
            for event in events
            if fuzz.ratio(search_title.lower(), event["title"].lower()) >= threshold
        ]

    def get_event_recordings(self, event: Event) -> list[Recording]:
        """
        Get all recordings for an event.

        Args:
            event: The event object

        Returns:
            List of recording objects
        """
        # If recordings are already in the event, return them
        if event.get("recordings"):
            return event.get("recordings") or []

        # Otherwise, fetch the full event details to get recordings
        full_event = self.get_event(event["guid"])
        # Ensure we always return a list, even if recordings is None
        return full_event.get("recordings") or []

    def get_event_recordings_by_language(
        self, event: Event, language: str
    ) -> list[Recording]:
        """
        Get recordings for an event in a specific language.

        Args:
            event: The event object
            language: The language code (e.g., 'eng', 'deu', 'eng-deu')

        Returns:
            List of recording objects
        """
        return [
            recording
            for recording in self.get_event_recordings(event)
            if recording["language"] == language
        ]

    def get_event_recordings_by_format(
        self, event: Event, mime_type: str
    ) -> list[Recording]:
        """
        Get recordings for an event in a specific format.

        Args:
            event: The event object
            mime_type: The MIME type (e.g., 'video/mp4', 'audio/mpeg')

        Returns:
            List of recording objects
        """
        return [
            recording
            for recording in self.get_event_recordings(event)
            if recording["mime_type"] == mime_type
        ]

    def get_event_best_recording(
        self, event: Event, mime_type: str = "video/mp4"
    ) -> Recording | None:
        """
        Get the highest quality recording for an event in the specified format.

        Args:
            event: The event object
            mime_type: The MIME type (defaults to 'video/mp4')

        Returns:
            The highest quality recording object, or None if no recordings found
        """
        recordings = self.get_event_recordings_by_format(event, mime_type)
        if not recordings:
            return None

        # Sort by size (larger file = higher quality) and take the first one
        return sorted(recordings, key=lambda x: x["size"], reverse=True)[0]

    def get_event_audio_recording(
        self, event: Event, language: str = "eng"
    ) -> Recording | None:
        """
        Get the audio recording for an event in the specified language.

        Args:
            event: The event object
            language: The language code (defaults to 'eng')

        Returns:
            The audio recording object, or None if no audio recording found
        """
        recordings = self.get_event_recordings_by_language(event, language)
        audio_recordings = [
            r for r in recordings if r["mime_type"].startswith("audio/")
        ]
        if not audio_recordings:
            return None

        # Prefer opus format if available, otherwise return the first audio recording
        opus_recording = next(
            (r for r in audio_recordings if r["mime_type"] == "audio/opus"), None
        )
        return opus_recording or audio_recordings[0]

    def get_recording_by_url(self, recording_url: str) -> Recording | None:
        """
        Get a specific recording by its URL.

        Args:
            recording_url: The URL of the recording

        Returns:
            Recording object if found, None otherwise
        """
        recording_id = extract_recording_id(recording_url)
        if not recording_id:
            return None
        return self.get_recording(recording_id)

    def get_event_recording_by_id(
        self, event: Event, recording_id: str
    ) -> Recording | None:
        """
        Get a specific recording from an event by its ID.

        Args:
            event: The event object
            recording_id: The ID of the recording

        Returns:
            Recording object if found, None otherwise
        """
        for recording in self.get_event_recordings(event):
            if extract_recording_id(recording["url"]) == recording_id:
                return recording
        return None

    def get_recording_subtitles(self, recording: Recording) -> list[Subtitle]:
        """
        Get all available subtitles for a recording.

        Args:
            recording: The recording object

        Returns:
            List of subtitle objects containing language and URL

        Note:
            This method attempts to find subtitle files in the same directory as the recording.
            The actual availability of subtitles depends on whether they were provided for the recording.
        """
        if not recording["recording_url"]:
            return []

        # Get the base URL by removing the folder from the recording URL and changing domain
        base_url = recording["recording_url"].replace(f"/{recording['folder']}/", "/")
        base_url = base_url.replace("cdn.media.ccc.de", "static.media.ccc.de")
        base_url = base_url.replace("/congress/", "/media/congress/")
        event_guid = recording["event_url"].split("/")[-1]

        subtitles = []
        # Common subtitle formats and languages
        for lang in COMMON_LANGUAGES.keys():
            # Try different subtitle formats
            for ext in ["srt", "vtt"]:
                subtitle_url = f"{base_url.rsplit('/', 1)[0]}/{event_guid}-{lang}.{ext}"
                # Check if the subtitle file exists
                try:
                    response = self.session.head(subtitle_url)
                    if response.status_code == 200:
                        subtitle = Subtitle(
                            language=lang, url=subtitle_url, content=None
                        )
                        subtitles.append(subtitle)
                except requests.RequestException:
                    continue

        return subtitles

    def get_subtitle_content(self, subtitle: Subtitle) -> str | None:
        """
        Fetch the content of a subtitle file.

        Args:
            subtitle: The subtitle object

        Returns:
            The subtitle content as a string, or None if the request fails

        Raises:
            requests.RequestException: If the request fails
        """
        if not subtitle["url"]:
            return None

        response = self.session.get(subtitle["url"])
        response.raise_for_status()
        return response.text
