# CCC Media API Client

A Python client for the media.ccc.de API, which provides access to recordings of Chaos Computer Club events.

## Installation

```bash
pip install c3media
```

## Usage

```python
from c3media import CCCMediaClient

# Initialize the client
client = CCCMediaClient()

# Get all conferences
conferences = client.get_conferences()

# Get a specific conference by acronym
conference = client.get_conference_by_acronym("38c3")

# Get a specific conference by ID
conference = client.get_conference(conference_id="38c3")

# Get all events for a conference
events = client.get_conference_events(conference)

# Get events by person
person_events = client.get_events_by_person(conference, "John Doe")

# Get events by tag
tagged_events = client.get_events_by_tag(conference, "security")

# Get events by fuzzy title matching
fuzzy_events = client.get_events_by_fuzzy_title(conference, "wo dein Auto steht")

# Get a specific event
event = client.get_event(event_guid="123")

# Get all recordings for an event
recordings = client.get_event_recordings(event)

# Get recordings by language
language_recordings = client.get_event_recordings_by_language(event, "eng")

# Get recordings by format
format_recordings = client.get_event_recordings_by_format(event, "video/mp4")

# Get the best quality recording
best_recording = client.get_event_best_recording(event)

# Get the audio recording
audio_recording = client.get_event_audio_recording(event)

# Get available subtitles for a recording (experimental)
subtitles = client.get_recording_subtitles(recording)

# Get subtitle content (experimental)
subtitle_content = client.get_subtitle_content(subtitle)

# Get conference metadata
recordings_url = client.get_conference_recordings_url(conference)
logo_url = client.get_conference_logo_url(conference)
images_url = client.get_conference_images_url(conference)
```

## Requirements

- Python 3.12+
- requests>=2.25.0
- fuzzywuzzy (optional, for fuzzy title matching)
- python-Levenshtein (optional, for improved fuzzy matching performance)

## License

MIT License 