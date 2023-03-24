from datetime import datetime
import firebase_admin
from firebase_admin import firestore, credentials
from google.cloud import firestore_v1


def retrieve_firestore() -> firestore_v1.Client:
    """Start Firebase app and return Firestore client"""
    cred = credentials.Certificate("credentials/daily-automations-firebase-admin-sdk.json")
    firebase_admin.initialize_app(cred)

    # TODO: add try except block for login if json file is not found

    db = firestore.client()
    return db


def retrieve_doc_ref(document_path: str):
    """document_path is a string of the form 'collection_1/document_1/collection_2/document_2'"""

    doc_ref = db

    for i, _ref in enumerate(document_path.split('/')):
        if i % 2 == 0:  # even is collection
            doc_ref = doc_ref.collection(_ref)
        else:  # odd is document
            doc_ref = doc_ref.document(_ref)

    return doc_ref


def get_firestore_document_simple(collection: str, document: str):
    doc_ref = db.collection(collection).document(document)
    doc = doc_ref.get()
    if doc.exists:
        return doc.to_dict()
    else:
        return None


def get_firestore_document(document_path: str):
    doc_ref = retrieve_doc_ref(document_path)

    doc = doc_ref.get()
    if doc.exists:
        return doc.to_dict()
    else:
        return None
    

def get_firestore_collection(collection_path: str):
    col_ref = retrieve_doc_ref(collection_path)

    collection = col_ref.stream()
    return [doc.to_dict() for doc in collection]


def set_firestore_document(document_path: str, data: dict, merge: bool = False):
    doc_ref = retrieve_doc_ref(document_path)
    doc_ref.set(data, merge=merge)


def add_document_to_collection(collection_path: str, data: dict):
    col_ref = retrieve_doc_ref(collection_path)
    col_ref.add(data)


# utility functions

def set_last_updated(document: str, new_date: datetime):
    data = {
        'lastUpdated': new_date
    }
    set_firestore_document(f'logs/{document}', data)


# TODO: add functions for current books, etc.
def get_current_books_from_store():
    return get_firestore_collection('data/books/currentlyReading')
    # return get_firestore_document('data/books/currentlyReading/').get('currentBook', None)


def add_current_book_to_store(book_details: dict):
    title = book_details.get('title', None)
    book_details['lastUpdated'] = datetime.now()
    if title is None:
        add_document_to_collection('data/books/currentlyReading', book_details)
    else:
        set_firestore_document(f'data/books/currentlyReading/{title}', book_details, merge=True)


db = retrieve_firestore()


if __name__ == '__main__':
    # set_last_updated('gamingTracker', datetime.now())
    # last_updated = get_firestore_document_simple('logs', 'gamingTracker')['lastUpdated']
    test = get_firestore_document('data/books/currentlyReading/test')
    print(test)
    last_updated = get_firestore_document('logs/gamingTracker')['lastUpdated']
    print(last_updated.date())

    print("currentBooks",get_current_books_from_store())