"""
Test script for the CCC Media API Client.
This script demonstrates the usage of the SDK and tests its main functionality.
"""

import sys
from c3media import CCCMediaClient, Conference, Event, Recording
import requests

from c3media.constants import COMMON_LANGUAGES


def test_conferences(client: CCCMediaClient) -> None:
    """Test conference-related functionality."""
    print("\n=== Testing Conference Functions ===")

    # Get all conferences
    conferences: list[Conference] = client.get_conferences()
    print(f"Found {len(conferences)} conferences")

    # Get a specific conference by acronym
    conference: Conference | None = client.get_conference_by_acronym("38c3")
    if conference:
        print(f"\nConference: {conference['title']}")
        print(f"Description: {conference['description'][:100]}...")
        print(f"Recordings URL: {client.get_conference_recordings_url(conference)}")
        print(f"Logo URL: {client.get_conference_logo_url(conference)}")
        print(f"Images URL: {client.get_conference_images_url(conference)}")
    else:
        print("Conference '38c3' not found")


def test_events(client: CCCMediaClient, conference: Conference) -> None:
    """Test event-related functionality."""
    print("\n=== Testing Event Functions ===")

    # Get all events for the conference
    events: list[Event] = client.get_conference_events(conference)
    print(f"Found {len(events)} events in conference {conference['acronym']}")

    if events:
        # Get the first event
        event: Event = events[0]
        print(f"\nFirst Event: {event['title']}")
        print(f"Description: {event['description'][:100]}...")
        print(f"Persons: {', '.join(event['persons'])}")
        print(f"Tags: {', '.join(event['tags'])}")

        # Get events by person
        person: str = event["persons"][0]
        person_events: list[Event] = client.get_events_by_person(conference, person)
        print(f"\nFound {len(person_events)} events by {person}")

        # Get events by tag
        tag: str = event["tags"][0]
        tag_events: list[Event] = client.get_events_by_tag(conference, tag)
        print(f"Found {len(tag_events)} events with tag {tag}")


def test_recordings(client: CCCMediaClient, event: Event) -> None:
    """Test recording-related functionality."""
    print("\n=== Testing Recording Functions ===")

    # Get the full event details to ensure we have recordings
    full_event: Event = client.get_event(event["guid"])

    # Get all recordings for the event
    recordings: list[Recording] = client.get_event_recordings(full_event)
    print(f"Found {len(recordings)} recordings for event {full_event['title']}")

    if recordings:
        # Get recordings by language
        print("Getting recordings by language")
        language: str = "eng"
        lang_recordings: list[Recording] = client.get_event_recordings_by_language(
            full_event, language
        )
        print(f"\nFound {len(lang_recordings)} recordings in {language}")

        # Get recordings by format
        print("Getting recordings by format")
        mime_type: str = "video/mp4"
        format_recordings: list[Recording] = client.get_event_recordings_by_format(
            full_event, mime_type
        )
        print(f"Found {len(format_recordings)} recordings in {mime_type}")

        # Get best recording
        best_recording: Recording | None = client.get_event_best_recording(full_event)
        if best_recording:
            print(f"\nBest recording: {best_recording['filename']}")
            print(f"Size: {best_recording['size']}MB")
            print(
                f"Quality: {'High' if best_recording['high_quality'] else 'Standard'}"
            )
            print(f"Dimensions: {best_recording['width']}x{best_recording['height']}")
            print(f"MIME Type: {best_recording['mime_type']}")
            print(f"Language: {best_recording['language']}")
            print(f"Recording URL: {best_recording['recording_url']}")

        # Get audio recording
        audio_recording: Recording | None = client.get_event_audio_recording(full_event)
        if audio_recording:
            print(f"\nAudio recording: {audio_recording['filename']}")
            print(f"Format: {audio_recording['mime_type']}")
            print(f"Language: {audio_recording['language']}")
            print(f"Size: {audio_recording['size']}MB")
            print(f"Duration: {audio_recording['length']} seconds")
            print(f"Recording URL: {audio_recording['recording_url']}")

        # Test getting recording by URL
        if recordings:
            recording_url: str = recordings[0]["url"]
            recording_by_url: Recording | None = client.get_recording_by_url(
                recording_url
            )
            if recording_by_url:
                print(f"\nRecording by URL: {recording_by_url['filename']}")
                print(f"State: {recording_by_url['state']}")
                print(f"Folder: {recording_by_url['folder']}")
                print(f"Updated at: {recording_by_url['updated_at']}")


def test_subtitles(client: CCCMediaClient, event: Event) -> None:
    """Test subtitle-related functionality."""
    print("\n=== Testing Subtitle Functions ===")

    # Get the full event details to ensure we have recordings
    full_event: Event = client.get_event(event["guid"])

    # Get all recordings for the event
    recordings: list[Recording] = client.get_event_recordings(full_event)
    print(f"Found {len(recordings)} recordings for event {full_event['title']}")

    if recordings:
        # Get the best recording to test subtitles
        best_recording: Recording | None = client.get_event_best_recording(full_event)
        if best_recording:
            print(f"\nTesting subtitles for recording: {best_recording['filename']}")

            # Get available subtitles
            subtitles = client.get_recording_subtitles(best_recording)
            print(f"Found {len(subtitles)} subtitle files")

            # Print details for each subtitle
            for subtitle in subtitles:
                print(
                    f"\nSubtitle in {subtitle['language']} ({COMMON_LANGUAGES.get(subtitle['language'], 'Unknown')})"
                )
                print(f"URL: {subtitle['url']}")

                # Try to fetch the subtitle content
                try:
                    content = client.get_subtitle_content(subtitle)
                    if content:
                        print("Content preview (first 100 chars):")
                        print(content[:100] + "...")
                except requests.RequestException as e:
                    print(f"Could not fetch subtitle content: {e}")


def main() -> None:
    """Main test function."""
    # Initialize the client
    client: CCCMediaClient = CCCMediaClient()

    # Test conference functionality
    test_conferences(client)

    # Get a specific conference for further testing
    conference: Conference | None = client.get_conference_by_acronym("38c3")
    if not conference:
        print("Could not find conference '38c3', exiting...")
        sys.exit(1)

    # Test event functionality
    test_events(client, conference)

    # Get a specific event for recording testing
    events: list[Event] = client.get_conference_events(conference)
    if not events:
        print("No events found in conference, exiting...")
        sys.exit(1)

    # get events by fuzzy title
    fuzzy_events: list[Event] = client.get_events_by_fuzzy_title(
        conference, "wo dein Auto steht"
    )
    if not events:
        print("Could not find event 'wo dein Auto steht', exiting...")
        sys.exit(1)

    # Test recording functionality
    test_recordings(client, fuzzy_events[0])


if __name__ == "__main__":
    main()
