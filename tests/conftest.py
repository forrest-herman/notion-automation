"""Keep unit tests independent of local configuration and live services."""

import dotenv
import firebase_admin
import google.auth
import pytest
import requests
from firebase_admin import credentials, firestore


def _unexpected_service_call(*args, **kwargs):
    raise AssertionError("Unit tests must mock external services and credentials")


def pytest_configure(config):
    # Configure before collection: several application modules read env at import.
    isolation = pytest.MonkeyPatch()
    config.add_cleanup(isolation.undo)
    for name, value in {
        "NOTION_TOKEN": "test-notion-token",
        "STEAM_API_KEY": "test-steam-key",
        "STEAM_ID": "test-steam-id",
    }.items():
        isolation.setenv(name, value)
    isolation.delenv("GOOGLE_APPLICATION_CREDENTIALS", raising=False)
    isolation.setattr(dotenv, "load_dotenv", lambda *args, **kwargs: False)
    isolation.setattr(requests.sessions.Session, "request", _unexpected_service_call)
    isolation.setattr(google.auth, "default", _unexpected_service_call)
    isolation.setattr(credentials, "Certificate", _unexpected_service_call)
    isolation.setattr(firebase_admin, "initialize_app", _unexpected_service_call)
    isolation.setattr(firestore, "client", _unexpected_service_call)
