"""Image search, download, and resize utilities."""

import io
import logging

import httpx
from duckduckgo_search import DDGS
from PIL import Image

from anki_agent.config import MAX_IMAGE_HEIGHT

logger = logging.getLogger(__name__)


def search_image(description: str) -> str | None:
    """Search DuckDuckGo Images and return the URL of the top result.

    Parameters
    ----------
    description : str
        Search query for DuckDuckGo Images.

    Returns
    -------
    str or None
        URL of the top image result, or None if no results found.
    """
    try:
        results = DDGS().images(description, max_results=1)
        result = results[0]["image"] if results else None
    except Exception:
        logger.warning("Image search failed for '%s'", description)
        result = None

    return result


def download_image(url: str) -> bytes | None:
    """Download an image from a URL.

    Parameters
    ----------
    url : str
        URL of the image to download.

    Returns
    -------
    bytes or None
        Raw image bytes, or None if the download fails.
    """
    try:
        response = httpx.get(url, follow_redirects=True, timeout=10)
        response.raise_for_status()
        result = response.content
    except httpx.HTTPError:
        logger.warning("Failed to download image from '%s'", url)
        result = None

    return result


def resize_image(
    data: bytes,
    max_height: int = MAX_IMAGE_HEIGHT,
) -> bytes:
    """Resize an image proportionally if it exceeds `max_height`.

    Parameters
    ----------
    data : bytes
        Raw image bytes.

    max_height : int
        Maximum height in pixels. Width scales proportionally.

    Returns
    -------
    bytes
        PNG image bytes.
    """
    img = Image.open(io.BytesIO(data))
    if img.height > max_height:
        img.thumbnail((img.width, max_height), Image.Resampling.LANCZOS)

    buf = io.BytesIO()
    img.save(buf, format="PNG")

    return buf.getvalue()
