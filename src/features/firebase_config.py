import firebase_admin
from firebase_admin import credentials, firestore

# Initialize Firebase with your service account key
cred = credentials.Certificate("path/to/your/serviceAccountKey.json")
firebase_admin.initialize_app(cred)

# Get Firestore client
db = firestore.client()

class FirebaseManager:
    @staticmethod
    def save_recording(recording_data, recording_id):
        """Save recording data to Firebase"""
        try:
            doc_ref = db.collection('recordings').document(recording_id)
            doc_ref.set(recording_data)
            return True
        except Exception as e:
            print(f"Error saving to Firebase: {e}")
            return False

    @staticmethod
    def get_recording(recording_id):
        """Get recording data from Firebase"""
        try:
            doc_ref = db.collection('recordings').document(recording_id)
            doc = doc_ref.get()
            return doc.to_dict() if doc.exists else None
        except Exception as e:
            print(f"Error retrieving from Firebase: {e}")
            return None

    @staticmethod
    def delete_recording(recording_id):
        """Delete recording from Firebase"""
        try:
            db.collection('recordings').document(recording_id).delete()
            return True
        except Exception as e:
            print(f"Error deleting from Firebase: {e}")
            return False

    @staticmethod
    def list_recordings():
        """List all recordings from Firebase"""
        try:
            docs = db.collection('recordings').stream()
            return [doc.id for doc in docs]
        except Exception as e:
            print(f"Error listing recordings: {e}")
            return []
