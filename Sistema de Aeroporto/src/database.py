import json
import os

DATA_PATH = os.path.join('data', 'voos.json')

def ler_voos():
    if not os.path.exists('data'):
        os.makedirs('data')
    try:
        with open(DATA_PATH, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return []

def guardar_voos(lista_voos):
    with open(DATA_PATH, 'w', encoding='utf-8') as f:
        json.dump(lista_voos, f, indent=4)