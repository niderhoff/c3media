"""
Utility functions for the CCC Media API Client.
"""

import re


def extract_recording_id(recording_url: str) -> str | None:
    """
    Extract the recording ID from a recording URL.

    Args:
        recording_url: The URL of the recording

    Returns:
        The recording ID if found, None otherwise
    """
    match = re.search(r"/recordings/(\d+)$", recording_url)
    return match.group(1) if match else None
