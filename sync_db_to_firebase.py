import os
import django
import firebase_admin
from firebase_admin import credentials, db

# Configura el entorno de Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'djangoReciclaje.settings')
django.setup()

# Importa tus modelos
from rewards.models import Reward
from questions.models import Question
from qr_codes.models import Recyclable, RecyclingTransaction, QRCode, UserPoints
from users.models import User
from events.models import Event, UserEvent

# Inicializa Firebase
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FIREBASE_CREDENTIALS_PATH = os.path.join(BASE_DIR, 'credentials', 'laboratorioreciclajea.json')
cred = credentials.Certificate(FIREBASE_CREDENTIALS_PATH)
firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://laboratorioreciclajea-default-rtdb.firebaseio.com/'
}, name='sync_app')

def sync_rewards():
    rewards_ref = db.reference('rewards', app=firebase_admin.get_app('sync_app'))
    rewards = Reward.objects.all()
    for reward in rewards:
        reward_data = {
            'name': reward.name,
            'description': reward.description,
            'points': reward.points,
            'image_url': reward.image.url if reward.image else None,
            'expiration_date': reward.expiration_date.isoformat(),
            'category': reward.category.name  
        }
        rewards_ref.child(str(reward.id)).set(reward_data)

def sync_questions():
    questions_ref = db.reference('questions', app=firebase_admin.get_app('sync_app'))
    questions = Question.objects.all()
    for question in questions:
        question_data = {
            'question': question.question,
            'answer1': question.answer1,
            'answer2': question.answer2,
            'answer3': question.answer3,
            'answer4': question.answer4,
            'correct_reply_index': question.correct_reply_index
        }
        questions_ref.child(str(question.id)).set(question_data)

def sync_recyclables():
    recyclables_ref = db.reference('recyclables', app=firebase_admin.get_app('sync_app'))
    recyclables = Recyclable.objects.all()
    for recyclable in recyclables:
        recyclable_data = {
            'description': recyclable.description,
            'value': recyclable.value
        }
        recyclables_ref.child(str(recyclable.id)).set(recyclable_data)

def sync_recycling_transactions():
    transactions_ref = db.reference('recycling_transactions', app=firebase_admin.get_app('sync_app'))
    transactions = RecyclingTransaction.objects.all()
    for transaction in transactions:
        transaction_data = {
            'user': transaction.user.username,
            'quantity': transaction.quantity,
            'recyclable': transaction.recyclable.description,
            'transaction_date': transaction.transaction_date.isoformat()
        }
        transactions_ref.child(str(transaction.id)).set(transaction_data)

def sync_qr_codes():
    qr_codes_ref = db.reference('qr_codes', app=firebase_admin.get_app('sync_app'))
    qr_codes = QRCode.objects.all()
    for qr_code in qr_codes:
        qr_code_data = {
            'code': qr_code.code,
            'transaction': qr_code.transaction.id
        }
        qr_codes_ref.child(str(qr_code.id)).set(qr_code_data)

def sync_user_points():
    user_points_ref = db.reference('user_points', app=firebase_admin.get_app('sync_app'))
    user_points = UserPoints.objects.all()
    for user_point in user_points:
        user_point_data = {
            'user': user_point.user.username,
            'points': user_point.points,
            'transaction_type': user_point.transaction_type,
            'transaction_date': user_point.transaction_date.isoformat(),
            'transaction': user_point.transaction.id if user_point.transaction else None
        }
        user_points_ref.child(str(user_point.id)).set(user_point_data)

def sync_users():
    users_ref = db.reference('users', app=firebase_admin.get_app('sync_app'))
    users = User.objects.all()
    for user in users:
        user_data = {
            'username': user.username,
            'email': user.email,
            'is_superuser': user.is_superuser,
            'is_staff': user.is_staff,
            'date_joined': user.date_joined.isoformat()
        }
        users_ref.child(str(user.id)).set(user_data)

def sync_events():
    events_ref = db.reference('events', app=firebase_admin.get_app('sync_app'))
    events = Event.objects.all()
    for event in events:
        event_data = {
            'title': event.title,
            'description': event.description,
            'event_date': event.event_date.isoformat()
        }
        events_ref.child(str(event.id)).set(event_data)

def sync_user_events():
    user_events_ref = db.reference('user_events', app=firebase_admin.get_app('sync_app'))
    user_events = UserEvent.objects.all()
    for user_event in user_events:
        user_event_data = {
            'user': user_event.user.username,
            'event': user_event.event.title,
            'registered_at': user_event.registered_at.isoformat()
        }
        user_events_ref.child(str(user_event.id)).set(user_event_data)

if __name__ == '__main__':
    sync_rewards()
    sync_questions()
    sync_recyclables()
    sync_recycling_transactions()
    sync_qr_codes()
    sync_user_points()
    sync_users()
    sync_events()
    sync_user_events()
    print("Data synced to Firebase!")
