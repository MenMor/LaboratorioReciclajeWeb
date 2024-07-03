from django.core.management.base import BaseCommand
from firebase_admin import db
from qr_codes.models import RecyclingTransaction

class Command(BaseCommand):
    help = 'Actualizar los datos de Firebase con la información de categoría'

    def handle(self, *args, **kwargs):
        transactions = RecyclingTransaction.objects.all()
        for transaction in transactions:
            ref = db.reference('recycling_transactions').child(str(transaction.id))
            ref.update({
                'recyclable_category': transaction.recyclable.category.name if transaction.recyclable.category else None,
            })
            self.stdout.write(self.style.SUCCESS(f'Successfully updated transaction {transaction.id}'))
