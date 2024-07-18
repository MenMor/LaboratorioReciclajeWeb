import os
import django
import firebase_admin
from firebase_admin import credentials, db
from firebase_app import get_firebase_app

# Importación de los modelos necesarios
from qr_codes.models import RecyclingTransaction

firebase_admin = get_firebase_app()

def sync_recycling_transactions():
    transactions_ref = db.reference('recycling_transactions', app=firebase_admin)
    transactions = RecyclingTransaction.objects.all()
    for transaction in transactions:
        transaction_data = {
            'user_id': transaction.user_id,
            'quantity': transaction.quantity,
            'recyclable': transaction.recyclable,
            'transaction_date': transaction.transaction_date.strftime('%Y-%m-%dT%H:%M:%S')
        }
        transactions_ref.child(str(transaction.id)).set(transaction_data)
        print(f"Sincronizado ID de Transacción: {transaction.id}")

if __name__ == '__main__':
    sync_recycling_transactions()
    print("Sincronización de transacciones de reciclaje a Firebase completada.")
