import pytest

from app.core.config import settings


@pytest.fixture(autouse=True)
def disable_external_llm_calls(monkeypatch):
    monkeypatch.setattr(settings, "openai_api_key", None)
    monkeypatch.setattr(settings, "gemini_api_key", None)
