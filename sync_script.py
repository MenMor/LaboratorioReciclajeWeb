import os
import django
import firebase_admin
from firebase_admin import credentials, db

# Configura el entorno de Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'djangoReciclaje.settings')
django.setup()

# Importa tus modelos
from qr_codes.models import Recyclable, Category

# Inicializa Firebase
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FIREBASE_CREDENTIALS_PATH = os.path.join(BASE_DIR, 'credentials', 'laboratorioreciclajea.json')
cred = credentials.Certificate(FIREBASE_CREDENTIALS_PATH)
firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://laboratorioreciclajea-default-rtdb.firebaseio.com/'
}, name='sync_app')

def sync_categories():
    categories_ref = db.reference('categories', app=firebase_admin.get_app('sync_app'))
    categories = Category.objects.all()
    for category in categories:
        category_ref = categories_ref.child(str(category.id))
        category_data = {
            'name': category.name
        }
        category_ref.update(category_data)

def sync_recyclables():
    recyclables_ref = db.reference('recyclables', app=firebase_admin.get_app('sync_app'))
    recyclables = Recyclable.objects.all()
    for recyclable in recyclables:
        recyclable_ref = recyclables_ref.child(str(recyclable.id))
        recyclable_data = {
            'description': recyclable.description,
            'value': recyclable.value,
            'category_id': recyclable.category.id if recyclable.category else None
        }
        recyclable_ref.update(recyclable_data)

if __name__ == '__main__':
    sync_categories()
    sync_recyclables()
    print("Data synced to Firebase!")
