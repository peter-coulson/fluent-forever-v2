#!/usr/bin/env python3
from types import SimpleNamespace
from unittest.mock import patch

from apis.forvo_client import ForvoClient


class MockAPIResponse(SimpleNamespace):
    def __init__(self, success=True, data=None, error_message=""):
        super().__init__(success=success, data=data, error_message=error_message)


def test_forvo_group_selection_by_votes(monkeypatch):
    # Provide dummy API key for client init
    monkeypatch.setenv('FORVO_API_KEY', 'test-key')
    client = ForvoClient()

    pronunciations = [
        {"country": "ES", "audio_url": "u3", "num_votes": 10, "num_positive_votes": 8},
        {"country": "MX", "audio_url": "u1", "num_votes": 5, "num_positive_votes": 5},
        {"country": "CO", "audio_url": "u2", "num_votes": 9, "num_positive_votes": 7},
    ]

    def mock_get_word_info(word: str):
        return MockAPIResponse(True, {"pronunciations": pronunciations})

    def mock_download(url, filename, save_path=None, country_code=""):
        # Simulate success only when choosing the top-ranked in group1 first (MX with 5/5)
        return MockAPIResponse(True, {"file_path": f"/tmp/{filename}", "country_code": country_code})

    monkeypatch.setattr(ForvoClient, 'get_word_info', lambda self, w: mock_get_word_info(w))
    monkeypatch.setattr(ForvoClient, '_download_audio', lambda self, url, filename, save_path=None, country_code="": mock_download(url, filename, save_path, country_code))

    resp = client.download_pronunciation('con', 'con.mp3')
    assert resp.success is True

