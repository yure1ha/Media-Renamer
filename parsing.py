import re
from typing import List, Optional

# Bracketed tags (e.g. [1080p])
TAG_PREFIX = r"(?:\[[^]]+]\s*)*"

EPISODE_NUM_PATTERNS: List[re.Pattern] = [
    re.compile(rf"""
        {TAG_PREFIX}
        (?:Episode|Ep|E)        # Episode keyword
        [\W_]*                  # Separator
        0*                      # Strip leading zeros before capturing
        (?P<episode>\d+)        # Episode number
    """, re.IGNORECASE | re.VERBOSE),

    re.compile(rf"""
        {TAG_PREFIX}
        S                       # Season marker
        0*                      # Strip leading zeros before capturing
        (?P<season>\d+)         # Season number
        [\W_]*                  # Separator
        E                       # Episode marker
        0*                      # Strip leading zeros before capturing
        (?P<episode>\d+)        # Episode number
    """, re.IGNORECASE | re.VERBOSE),
]

SEASON_DIR_PATTERN: re.Pattern = re.compile(rf"""
    {TAG_PREFIX}
    (?:Season|S)                # Season keyword
    [\W_]*                      # Separator
    0*                          # Strip leading zeros before capturing
    (?P<season>\d+)             # Season number
""", re.IGNORECASE | re.VERBOSE)


def fallback_episode_number_pattern(series_name: str) -> re.Pattern:
    escaped_series_name = re.escape(series_name).replace(r"\ ", r"[\W_ ]+")

    return re.compile(
        rf"(?:\[[^]]+]\s*)*{escaped_series_name}[\W_ ]+(?:-\s*)?0*(\d+)",
        re.IGNORECASE
    )


def zero_pad_number(number: int, maximum_number: int) -> str:
    padding_length = len(str(maximum_number))
    return str(number).zfill(padding_length)


def extract_episode_number(filename: str, series_name: Optional[str] = None) -> Optional[int]:
    for pattern in EPISODE_NUM_PATTERNS:
        match = pattern.search(filename)
        if not match:
            continue

        groups = match.groups()
        if len(groups) == 2:
            return int(groups[1])
        elif len(groups) == 1:
            episode_code = groups[0]
            return int(episode_code)

    if series_name:
        fallback_pattern = fallback_episode_number_pattern(series_name)
        fallback_match = fallback_pattern.search(filename)
        if fallback_match:
            return int(fallback_match.group(1))

    return None


def extract_season_number(filename: str) -> Optional[int]:
    season_directory_match = SEASON_DIR_PATTERN.search(filename)
    if season_directory_match:
        return int(season_directory_match.group(1))

    season_episode_match = re.search(r"[Ss]0*(\d+)[Ee]0*\d+", filename)
    if season_episode_match:
        season_number = int(season_episode_match.group(1))
        return season_number

    numeric_season_episode_match = re.search(r"\b(\d{3,4})\b", filename)
    if numeric_season_episode_match:
        season_episode_code = numeric_season_episode_match.group(1)
        season_number_part = int(season_episode_code[:-2])
        episode_number_part = int(season_episode_code[-2:])
        if season_number_part >= 1 and 1 <= episode_number_part <= 99:
            return season_number_part

    return None
