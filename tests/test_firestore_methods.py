import importlib
from unittest.mock import Mock

import pytest
from google.auth.exceptions import DefaultCredentialsError

import firestore_methods as store


@pytest.fixture(autouse=True)
def clear_client_cache():
    store.retrieve_firestore.cache_clear()
    yield
    store.retrieve_firestore.cache_clear()


def test_imports_do_not_load_credentials():
    # The session guards reject certificate reads, ADC discovery, Firebase
    # initialization, and client creation, including during module imports.
    for name in (
        'firestore_methods', 'goodreads', 'notion_api_methods',
        'notion_daily_journal', 'tracking_games.track_games_methods',
    ):
        importlib.reload(importlib.import_module(name))
    assert store.retrieve_firestore.cache_info().currsize == 0


@pytest.fixture
def firebase(monkeypatch):
    certificate = Mock(return_value=object())
    initialize = Mock()
    client = Mock()
    monkeypatch.setattr(store.credentials, 'Certificate', certificate)
    monkeypatch.setattr(store.firebase_admin, '_apps', {})
    monkeypatch.setattr(store.firebase_admin, 'initialize_app', initialize)
    monkeypatch.setattr(store.firestore, 'client', client)
    return certificate, initialize, client


def test_database_operations_initialize_once_and_reuse_client(firebase):
    certificate, initialize, client = firebase
    document = client.return_value.collection.return_value.document.return_value
    document.get.return_value.to_dict.return_value = {'title': 'Example'}

    assert store.get_firestore_document_simple('books', 'example') == {'title': 'Example'}
    store.set_firestore_document('books/example', {'title': 'Updated'}, merge=True)

    certificate.assert_called_once_with('credentials/daily-automations-firebase-admin-sdk.json')
    initialize.assert_called_once_with(certificate.return_value)
    client.assert_called_once_with()
    document.set.assert_called_once_with({'title': 'Updated'}, merge=True)


def test_missing_certificate_uses_adc(firebase):
    certificate, initialize, client = firebase
    certificate.side_effect = FileNotFoundError

    assert store.retrieve_firestore() is client.return_value
    initialize.assert_called_once_with(None)


def test_existing_firebase_app_is_reused(firebase, monkeypatch):
    _, initialize, client = firebase
    get_app = Mock()
    monkeypatch.setattr(store.firebase_admin, '_apps', {'[DEFAULT]': object()})
    monkeypatch.setattr(store.firebase_admin, 'get_app', get_app)

    assert store.retrieve_firestore() is client.return_value
    initialize.assert_not_called()
    get_app.assert_called_once_with()


def test_invalid_certificate_propagates(firebase):
    certificate, initialize, client = firebase
    certificate.side_effect = ValueError('Invalid certificate')
    with pytest.raises(ValueError, match='Invalid certificate'):
        store.get_firestore_document('books/example')
    initialize.assert_not_called()
    client.assert_not_called()


def test_missing_adc_propagates_and_can_be_retried(firebase):
    certificate, initialize, client = firebase
    certificate.side_effect = FileNotFoundError
    client.side_effect = DefaultCredentialsError('Missing ADC')

    with pytest.raises(DefaultCredentialsError, match='Missing ADC'):
        store.get_firestore_document('books/example')
    assert store.retrieve_firestore.cache_info().currsize == 0

    client.side_effect = None
    assert store.retrieve_firestore() is client.return_value
