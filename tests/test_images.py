import io
from unittest.mock import MagicMock, patch

from PIL import Image

from anki_agent.images import download_image, resize_image, search_image


def _make_image(width: int, height: int) -> bytes:
    img = Image.new("RGB", (width, height), color="red")
    buf = io.BytesIO()
    img.save(buf, format="PNG")

    return buf.getvalue()


@patch("anki_agent.images.DDGS")
def test_search_returns_top_result_url(mock_ddgs_cls):
    mock_ddgs = MagicMock()
    mock_ddgs_cls.return_value = mock_ddgs
    mock_ddgs.images.return_value = [{"image": "http://example.com/dog.jpg"}]

    result = search_image("brown dog")

    assert result == "http://example.com/dog.jpg"


@patch("anki_agent.images.DDGS")
def test_search_returns_none_when_no_results(mock_ddgs_cls):
    mock_ddgs = MagicMock()
    mock_ddgs_cls.return_value = mock_ddgs
    mock_ddgs.images.return_value = []

    result = search_image("xyznonexistent")

    assert result is None


@patch("anki_agent.images.httpx")
def test_download_image_returns_bytes(mock_httpx):
    response = MagicMock()
    response.content = b"fake-image-data"
    response.raise_for_status = MagicMock()
    mock_httpx.get.return_value = response

    result = download_image("http://example.com/img.png")

    assert result == b"fake-image-data"


@patch("anki_agent.images.httpx")
def test_download_image_returns_none_on_error(mock_httpx):
    import httpx

    mock_httpx.get.side_effect = httpx.HTTPError("fail")
    mock_httpx.HTTPError = httpx.HTTPError

    result = download_image("http://example.com/img.png")

    assert result is None


def test_resize_tall_image_proportionally():
    data = _make_image(400, 800)

    result = resize_image(data, max_height=200)

    img = Image.open(io.BytesIO(result))
    assert img.height <= 200
    assert img.width < 400


def test_resize_small_image_left_as_is():
    data = _make_image(100, 100)

    result = resize_image(data, max_height=200)

    img = Image.open(io.BytesIO(result))
    assert img.height == 100
    assert img.width == 100


def test_resize_preserves_aspect_ratio():
    data = _make_image(600, 400)

    result = resize_image(data, max_height=200)

    img = Image.open(io.BytesIO(result))
    assert img.height <= 200
    ratio = 600 / 400
    assert abs(img.width / img.height - ratio) < 0.1
