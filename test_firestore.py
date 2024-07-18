import os
import django
import firebase_admin
from firebase_admin import credentials, firestore

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'djangoReciclaje.settings')
django.setup()

# Inicializa Firebase
if not firebase_admin._apps:
    cred = credentials.Certificate('credentials/laboratorioreciclajea.json')
    firebase_admin.initialize_app(cred)

# Acceder a Firestore
db = firestore.client()
try:
    docs = db.collection('recyclables').limit(1).get()
    for doc in docs:
        print(doc.to_dict())  # Imprime los datos para verificar
except Exception as e:
    print(f"Error accessing Firestore: {str(e)}")
