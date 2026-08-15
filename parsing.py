import re
from typing import List, Optional

EPISODE_NUM_PATTERNS: List[re.Pattern] = [
    re.compile(r"""
        \b                      # Word boundary
        0*                      # Strip leading zeros
        (?:episode|ep|e)        # Episode keyword
        [\W_]*                  # Separator
        0*                      # Strip leading zeros
        (?P<episode>\d+)        # Episode number
        \b                      # Word boundary
    """, re.IGNORECASE | re.VERBOSE),

    re.compile(r"""
        \b                      # Word boundary
        0*                      # Strip leading zeros
        s                       # Season marker
        0*                      # Strip leading zeros
        (?P<season>\d+)         # Season number
        [\W_]*                  # Separator
        e                       # Episode marker
        0*                      # Strip leading zeros
        (?P<episode>\d+)        # Episode number
        \b                      # Word boundary
    """, re.IGNORECASE | re.VERBOSE),
]

SEASON_NUM_PATTERNS: List[re.Pattern] = [
    re.compile(r"""
        \b                      # Word boundary
        (?:season|s)            # Season keyword
        [\W_]*                  # Separator
        0*                      # Strip leading zeros
        (?P<season>\d+)         # Season number
        \b                      # Word boundary
    """, re.IGNORECASE | re.VERBOSE),

    re.compile(r"""
        \b                      # Word boundary
        s                       # Season marker
        0*                      # Strip leading zeros
        (?P<season>\d+)         # Season number
        e                       # Episode marker
        0*                      # Strip leading zeros
        (?P<episode>\d+)        # Episode number       
        \b                      # Word boundary                
    """, re.IGNORECASE | re.VERBOSE),

    re.compile(r"""
        \b                      # Word boundary
        (?P<season>\d{1,2})     # 1–2 digit season number
        (?P<episode>\d{2})      # 2 digit episode number
        \b                      # Word boundary
    """, re.VERBOSE),
]


def build_unmarked_episode_pattern(series_name: str) -> re.Pattern:
    words = [word for word in re.split(r"[\W_]+", series_name) if word]
    escaped_words = [re.escape(word) for word in words]
    series_name_pattern = r"[\W_]+".join(escaped_words)

    return re.compile(rf"""
        \b                      # Word boundary
        {series_name_pattern}   # Series name
        [\W_]+                  # Separator
        0*                      # Strip leading zeros
        (?P<episode>\d+)        # Episode number
        \b                      # Word boundary
    """, re.IGNORECASE | re.VERBOSE)


def extract_episode_num(filename: str, series_name: str) -> Optional[int]:
    for pattern in EPISODE_NUM_PATTERNS:
        match = pattern.search(filename)

        if match:
            return int(match.group("episode"))

    if series_name:
        fallback_pattern = build_unmarked_episode_pattern(series_name)
        fallback_match = fallback_pattern.search(filename)

        if fallback_match:
            return int(fallback_match.group("episode"))

    return None


def extract_season_num(filename: str) -> Optional[int]:
    for pattern in SEASON_NUM_PATTERNS:
        match = pattern.search(filename)

        if match:
            return int(match.group("season"))

    return None
