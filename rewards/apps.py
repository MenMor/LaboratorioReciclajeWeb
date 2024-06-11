from django.apps import AppConfig
import firebase_admin
from firebase_admin import credentials
import os

class RewardsConfig(AppConfig):
    name = 'rewards'

    def ready(self):
        if not firebase_admin._apps:
            BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            FIREBASE_CREDENTIALS_PATH = os.path.join(BASE_DIR, 'credentials', 'laboratorioreciclajea.json')
            cred = credentials.Certificate(FIREBASE_CREDENTIALS_PATH)
            firebase_admin.initialize_app(cred, {
                'databaseURL': 'https://laboratorioreciclajea-default-rtdb.firebaseio.com/'
            })