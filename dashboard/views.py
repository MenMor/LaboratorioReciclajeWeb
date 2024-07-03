from django.shortcuts import render
from firebase_admin import db
from qr_codes.models import Category
from collections import defaultdict
import datetime

def index(request):
    selected_category = request.GET.get('category', None)
    ref = db.reference('recycling_transactions')
    transactions = ref.get()

    # Procesar los datos de las transacciones
    data = defaultdict(lambda: defaultdict(int))  # Estructura: {mes: {material: cantidad}}
    if isinstance(transactions, dict):
        for key, value in transactions.items():
            if value is not None and (not selected_category or value.get('recyclable_category') == selected_category):
                date = datetime.datetime.fromisoformat(value['transaction_date']).strftime('%Y-%m')
                if selected_category:
                    material = value['recyclable']
                    data[date][material] += value['quantity']
                else:
                    category = value['recyclable_category']
                    data[date][category] += value['quantity']
    elif isinstance(transactions, list):
        for item in transactions:
            if item is not None and (not selected_category or item.get('recyclable_category') == selected_category):
                date = datetime.datetime.fromisoformat(item['transaction_date']).strftime('%Y-%m')
                if selected_category:
                    material = item['recyclable']
                    data[date][material] += item['quantity']
                else:
                    category = item.get('recyclable_category')
                    data[date][category] += item.get('quantity')

    # Convertir el defaultdict a una lista de diccionarios
    formatted_data = [{'month': month, 'materials': dict(materials)} for month, materials in data.items()]
    formatted_data.sort(key=lambda x: x['month'])  # Ordenar por mes

    # Obtener todas las categorías para el filtro
    categories = Category.objects.all()

    context = {
        'transactions': formatted_data,
        'categories': categories,
        'selected_category': selected_category
    }
    return render(request, 'dashboard/index.html', context)
