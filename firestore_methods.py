from datetime import datetime, timezone
import firebase_admin
from firebase_admin import firestore, credentials
from google.cloud import firestore_v1


def retrieve_firestore() -> firestore_v1.Client:
    """Start Firebase app and return Firestore client"""
    try:
        cred = credentials.Certificate("credentials/daily-automations-firebase-admin-sdk.json")
    except FileNotFoundError:
        cred = None
        print("Firebase credentials file not found. Using Application Default Credentials.")

    if not len(firebase_admin._apps):
        firebase_admin.initialize_app(cred)
    else:
        firebase_admin.get_app()

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
        return {}
    

def get_firestore_collection(collection_path: str, return_type: str = 'dict'):
    col_ref = retrieve_doc_ref(collection_path)

    collection = col_ref.stream()
    if return_type == 'dict':
        return {doc.id: doc.to_dict() for doc in collection}
    elif return_type == 'list':
        return [doc.to_dict() for doc in collection]
    return [doc.to_dict() for doc in collection]


def set_firestore_document(document_path: str, data: dict, merge: bool = False):
    doc_ref = retrieve_doc_ref(document_path)
    doc_ref.set(data, merge=merge)


def add_document_to_collection(collection_path: str, data: dict):
    col_ref = retrieve_doc_ref(collection_path)
    col_ref.add(data)


# utility functions

def set_last_updated(document: str, new_date: datetime=datetime.now(timezone.utc)):
    data = {'lastUpdated': new_date}
    set_firestore_document(f'logs/{document}', data)


def convert_timestamp_to_datetime(timestamp: datetime):
    if isinstance(timestamp, datetime):
        return datetime.fromtimestamp(timestamp.timestamp())
    return None


def get_last_updated(document: str):
    last_updated = get_firestore_document(f'logs/{document}').get('lastUpdated')
    return convert_timestamp_to_datetime(last_updated)


def get_current_books_from_store():
    return get_firestore_collection('data/books/currentlyReading')


def add_current_book_to_store(book_details: dict):
    title = book_details.get('title', None)
    author = book_details.get('author_name', '')
    book_details['last_updated'] = datetime.now()
    if title is None:
        add_document_to_collection('data/books/currentlyReading', book_details)
    else:
        set_firestore_document(f'data/books/currentlyReading/{title}, {author}', book_details, merge=False)


def log_error(title: str, error='', location: str = "", data: dict = {}):
    print(error)
    timestamp = datetime.now()
    data = {
        'title': title,
        'error': str(error),
        'location': location,
        'data': data
    }
    set_firestore_document(f'errors/{timestamp}', data)



db = retrieve_firestore()


if __name__ == '__main__':
    # set_last_updated('gamingTracker', datetime.now())
    # last_updated = get_firestore_document_simple('logs', 'gamingTracker')['lastUpdated']
    test = get_firestore_document('data/books/currentlyReading/test')
    print(test)
    last_updated = get_firestore_document('logs/gamingTracker')['lastUpdated']
    print(last_updated.date())

    print("currentBooks",get_current_books_from_store())

    # log_error(
    #     title='Error getting extra book details',
    #     error='e',
    #     location='Notion Reading List, Create Book Page', 
    #     data={"test": "test"}
    # )