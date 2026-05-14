import io
import pytest
from constant import constants_dev as cons_dev
from unittest import mock
from downloader import downloader

patch = mock.patch

@patch('downloader.downloader.open')
@patch('downloader.downloader.requests.get')
def test_download_write_chunks_b(mock_get, mock_open):
    """Make sure that 8192 byte chunks are written correctly."""
    unit = downloader.DatasetDownloader()
    mock_file = io.BytesIO()
    url = cons_dev.mock_url
    mock_response=mock.MagicMock()
    mock_response.status_code=200
    mock_response.headers=cons_dev.mock_content_length
    mock_response.iter_content.return_value=([b'a' * 8192, b'b' * 8192, b'c' * 8192, b'd' * 8192])
    mock_get.return_value=mock_response
    mock_open.return_value.__enter__.return_value=mock_file
    unit._download_file(url, mock_file)
    assert mock_file.getvalue() == b''.join(mock_response.iter_content.return_value)

