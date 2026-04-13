#!/usr/bin/env python3

import os
import re
import sys
import urllib.parse
import urllib.request
import webbrowser
import subprocess
from datetime import datetime

# ============================================
# Configuration via Environment Variables
# ============================================
DEBUG = os.getenv("IMDB_DEBUG", "0") == "1"
CONFIRM = os.getenv("IMDB_CONFIRM", "0") == "1"
LOGFILE = os.path.expanduser("~/.cache/open_imdb.log")
USER_AGENT = "Mozilla/5.0"

os.makedirs(os.path.dirname(LOGFILE), exist_ok=True)

def get_filepath():
    """Retrieve the full filepath passed by Nemo."""
    if len(sys.argv) < 2:
        log("No file provided.")
        sys.exit(1)

    # Join all arguments in case Nemo splits them
    filepath = " ".join(sys.argv[1:])
    log(f"Raw argv: {sys.argv}")
    log(f"Resolved filepath: {filepath}")
    return filepath





def log(message):
    """Write debug messages to a log file."""
    if DEBUG:
        with open(LOGFILE, "a", encoding="utf-8") as f:
            f.write(f"{datetime.now()} [DEBUG] {message}\n")


def debug_header():
    if DEBUG:
        with open(LOGFILE, "a", encoding="utf-8") as f:
            f.write("\n-----------------------------\n")
            f.write(f"{datetime.now()} New session\n")


def clean_filename(filepath):
    """Extract and normalize the filename."""
    filename = os.path.basename(filepath)
    name, _ = os.path.splitext(filename)

    log(f"Original filename: {filename}")
    log(f"Name without extension: {name}")

    # Replace separators with spaces
    clean = re.sub(r"[._]+", " ", name)
    clean = re.sub(r"-", " ", clean)

    # Remove brackets and their contents
    clean = re.sub(r"\[[^\]]*\]", "", clean)
    clean = re.sub(r"\([^\)]*\)", "", clean)
    clean = re.sub(r"\{[^}]*\}", "", clean)

    clean = re.sub(r"\s+", " ", clean).strip()

    log(f"Normalized name: {clean}")
    return clean


def detect_title(clean):
    """Detect whether the file is a TV show or movie."""
    is_tv = False
    title = clean

    patterns = [
        r"\bS\d{1,2}E\d{1,2}\b",
        r"\b\d{1,2}x\d{1,2}\b",
        r"\b(19|20)\d{2}[ ._-]\d{2}[ ._-]\d{2}\b",
    ]

    for pattern in patterns:
        match = re.search(pattern, clean, re.IGNORECASE)
        if match:
            is_tv = True
            title = clean[:match.start()].strip()
            log(f"Detected TV pattern: {pattern}")
            break

    return title, is_tv


def remove_torrent_tags(title):
    """Remove common torrent tags."""
    tags = [
        "480p", "576p", "720p", "1080p", "2160p", "4320p",
        "4K", "8K", "HDR", "HDR10", "DV",
        "BluRay", "BRRip", "BDRip", "WEBRip", "WEB-DL",
        "DVDRip", "HDTV", "REMUX", "CAM", "TS",
        "HEVC", "AVC", "x264", "x265", "H264", "H265", "AV1",
        "AAC", "DDP5.1", "DD5.1", "DTS", "Atmos", "TRUEHD",
        "YTS", "RARBG", "AMZN", "NF", "HULU", "DSNP", "MAX",
        "MULTI", "SUBBED", "DUBBED", "EXTENDED", "REMASTERED",
        "PROPER", "REPACK", "LIMITED", "INTERNAL", "READNFO",
        "FENIX"
    ]

    pattern = r"\b(" + "|".join(tags) + r")\b"
    title = re.sub(pattern, "", title, flags=re.IGNORECASE)

    # Remove standalone year
    title = re.sub(r"\b(19|20)\d{2}\b", "", title)

    title = re.sub(r"\s+", " ", title).strip()
    return title


def build_search_url(title, is_tv):
    """Construct IMDb search URL."""
    query = urllib.parse.quote_plus(title)
    if is_tv:
        url = f"https://www.imdb.com/find?q={query}&s=tt&ttype=tv"
    else:
        url = f"https://www.imdb.com/find?q={query}&s=tt"
    log(f"Search URL: {url}")
    return url


def fetch_first_imdb_result(search_url):
    """Fetch the first IMDb result."""
    try:
        req = urllib.request.Request(
            search_url,
            headers={"User-Agent": USER_AGENT}
        )
        with urllib.request.urlopen(req) as response:
            html = response.read().decode("utf-8", errors="ignore")

        match = re.search(r"/title/(tt\d+)/", html)
        if match:
            imdb_url = f"https://www.imdb.com/title/{match.group(1)}/"
            log(f"First IMDb result: {imdb_url}")
            return imdb_url
    except Exception as e:
        log(f"Error fetching IMDb result: {e}")

    log("Falling back to search page.")
    return search_url



def main():
    debug_header()
    filepath = get_filepath()

    clean = clean_filename(filepath)
    title, is_tv = detect_title(clean)
    title = remove_torrent_tags(title)

    if not title:
        title = clean

    log(f"Final extracted title: {title}")
    log(f"Is TV Series: {is_tv}")

    search_url = build_search_url(title, is_tv)
    imdb_url = fetch_first_imdb_result(search_url)

    webbrowser.open(imdb_url)


if __name__ == "__main__":
    main()
