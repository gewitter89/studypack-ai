"""Tests for core.multimedia module."""
import pytest
import tempfile
import os
from core.multimedia import (
    generate_tts_for_instructions,
    generate_page_audio,
    create_qr_codes_for_audio,
    pack_has_multimedia_support,
)


class TestPackMultimediaSupport:
    def test_returns_bool(self):
        result = pack_has_multimedia_support()
        assert isinstance(result, bool)


class TestGenerateTTS:
    def test_no_dependencies_returns_none_list(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            tasks = [
                {"instruction": "Test", "question": "1+1=?"}
            ]
            result = generate_tts_for_instructions(tasks, tmpdir, "en")
            assert isinstance(result, list)

    def test_empty_tasks(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            result = generate_tts_for_instructions([], tmpdir, "en")
            assert result == []


class TestGeneratePageAudio:
    def test_no_instruction_returns_none(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            page_data = {"instruction": "", "tasks": []}
            result = generate_page_audio(page_data, tmpdir, 0, "en")
            assert result is None

    def test_returns_optional_str(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            page_data = {"instruction": "Solve the problems", "tasks": []}
            result = generate_page_audio(page_data, tmpdir, 0, "en")
            # May be None if gTTS not installed
            assert result is None or isinstance(result, str)


class TestCreateQRCodes:
    def test_none_audio_returns_none_list(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            result = create_qr_codes_for_audio([None, None], tmpdir, "")
            assert result == [None, None]

    def test_empty_list(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            result = create_qr_codes_for_audio([], tmpdir, "")
            assert result == []

    def test_no_dependencies_returns_none_list(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            fake_path = os.path.join(tmpdir, "fake.mp3")
            result = create_qr_codes_for_audio([fake_path], tmpdir, "http://example.com")
            assert isinstance(result, list)
