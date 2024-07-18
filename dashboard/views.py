from django.shortcuts import render
from firebase_admin import db
from qr_codes.models import Category
from collections import defaultdict
import datetime
import requests
import time
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.http import require_http_methods

@csrf_protect
@require_http_methods(["GET"]) 
def index(request):
    selected_category = request.GET.get('category', None)
    ref = db.reference('recycling_transactions')
    transactions = ref.get()

    # Obtener los nombres de las categorías y reciclables
    categories_ref = db.reference('categories')
    categories_data = categories_ref.get() or {}
    recyclables_ref = db.reference('recyclables')
    recyclables_data = recyclables_ref.get() or {}

    # Crear diccionarios para categorías y reciclables
    if isinstance(categories_data, dict):
        categories_dict = {str(key): value['name'] for key, value in categories_data.items()}
    else:
        categories_dict = {str(item): categories_data[item]['name'] for item in range(len(categories_data)) if categories_data[item]}

    if isinstance(recyclables_data, dict):
        recyclables_dict = {str(key): value for key, value in recyclables_data.items()}
    else:
        recyclables_dict = {str(item): recyclables_data[item] for item in range(len(recyclables_data)) if recyclables_data[item]}

    # Depuración: Imprimir los diccionarios de categorías y reciclables
    #print(f"Categories Dict: {categories_dict}")
    #print(f"Recyclables Dict: {recyclables_dict}")

    # Procesar los datos de las transacciones
    data = defaultdict(lambda: defaultdict(int))  # Estructura: {mes: {categoría/material: cantidad}}
    if isinstance(transactions, dict):
        for key, value in transactions.items():
            if value is not None:
                transaction_date = value.get('transaction_date')
                recyclable_id = value.get('recyclable')
                if transaction_date and recyclable_id:
                    recyclable = recyclables_dict.get(recyclable_id)
                    if recyclable:
                        category_id = str(recyclable['category_id'])
                        date = datetime.datetime.fromisoformat(transaction_date).strftime('%Y-%m')
                        if not selected_category:
                            category_name = categories_dict[category_id]
                            data[date][category_name] += value.get('quantity', 0)
                        elif categories_dict[category_id] == selected_category:
                            material = recyclable['description']
                            data[date][material] += value.get('quantity', 0)
    elif isinstance(transactions, list):
        for item in transactions:
            if item is not None:
                transaction_date = item.get('transaction_date')
                recyclable_id = item.get('recyclable')
                if transaction_date and recyclable_id:
                    recyclable = recyclables_dict.get(recyclable_id)
                    if recyclable:
                        category_id = str(recyclable['category_id'])
                        date = datetime.datetime.fromisoformat(transaction_date).strftime('%Y-%m')
                        if not selected_category:
                            category_name = categories_dict[category_id]
                            data[date][category_name] += item.get('quantity', 0)
                        elif categories_dict[category_id] == selected_category:
                            material = recyclable['description']
                            data[date][material] += item.get('quantity', 0)

    # Depuración: Imprimir los datos procesados
    print(f"Data: {data}")

    # Convertir el defaultdict a una lista de diccionarios
    formatted_data = [{'month': month, 'materials': dict(materials)} for month, materials in data.items()]
    formatted_data.sort(key=lambda x: x['month'])  # Ordenar por mes

    # Depuración: Imprimir datos formateados
    print(f"Formatted Data: {formatted_data}")

    # Obtener todas las categorías para el filtro
    categories = Category.objects.all()

    context = {
        'transactions': formatted_data,
        'categories': categories,
        'selected_category': selected_category
    }
    return render(request, 'dashboard/index.html', context)


# Vista para mostrar categorías por sectores de ubicación

def get_location_name(latitude, longitude):
    try:
        # Asegurarse de que las coordenadas sean de tipo float
        latitude = float(latitude)
        longitude = float(longitude)
        url = f"https://nominatim.openstreetmap.org/reverse?lat={latitude}&lon={longitude}&format=json"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, como Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            data = response.json()
            if 'address' in data and 'city_district' in data['address']:
                return data['address']['city_district']
            elif 'address' in data and 'village' in data['address']:
                return data['address']['village']
            else:
                return "Pusuqui"
        else:
            return f"Error en la solicitud: {response.status_code}"
    except Exception as e:
        print(f"Error al obtener el nombre de la ubicación: {e}")
        return "Error en la solicitud"

@csrf_protect
@require_http_methods(["GET"])
def dashboard_by_location(request):
    ref = db.reference('userposition')
    user_positions = ref.get()

    print(f"Raw User Positions: {user_positions}")

    location_data = defaultdict(lambda: defaultdict(int))

    # Crear un diccionario para almacenar nombres de sectores de coordenadas únicas
    unique_coordinates = {}
    for key, value in user_positions.items():
        latitude = value.get('latitude')
        longitude = value.get('longitude')
        if latitude and longitude:
            coord_key = (latitude, longitude)
            if coord_key not in unique_coordinates:
                sector_name = get_location_name(latitude, longitude)
                unique_coordinates[coord_key] = sector_name

    for key, value in user_positions.items():
        latitude = value.get('latitude')
        longitude = value.get('longitude')
        category = value.get('categoryreciclying')
        if latitude and longitude and category:
            coord_key = (latitude, longitude)
            sector_name = unique_coordinates.get(coord_key, "Nombre de ubicación no encontrado")
            location_data[sector_name][category] += 1

    print(f"Location Data: {location_data}")

    formatted_location_data = [{'sector': sector, 'categories': dict(categories)} for sector, categories in location_data.items()]
    formatted_location_data.sort(key=lambda x: x['sector'])

    print(f"Formatted Location Data: {formatted_location_data}")

    categories = Category.objects.all()

    context = {
        'location_data': formatted_location_data,
        'categories': categories
    }
    return render(request, 'dashboard/dashboard_by_location.html', context)
