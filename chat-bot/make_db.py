"""
Criação do Bando de Dados para o Chat Bot conseguir fazer o Information Retrieval.
"""

from langchain_openai import ChatOpenAI
from langchain.agents import create_agent
from langchain.tools import InjectedToolCallId
from datetime import datetime
import json
import sqlite3

# =========================
# Simular o Bando de Dados
# =========================
VOOS_DATABASE = {
    ("São Paulo", "Rio de Janeiro", "2025-01-15"): [
        {"id": "VG001", "horario": "08:00", "preco": 250, "assentos": 45},
        {"id": "VG002", "horario": "14:00", "preco": 200, "assentos": 10},
        {"id": "VG003", "horario": "20:00", "preco": 180, "assentos":5},
    ],
    ("São Paulo", "Rio de Janeiro", "2025-01-16"): [
        {"id": "AZ001", "horario": "06:30", "preco": 280, "assentos": 30},
        {"id": "AZ002", "horario": "16:45", "preco": 220, "assentos": 20},
    ]
}

HOTEIS_DATABASE = {
    "Rio de Janeiro": [
        {
            "id": "H001",
            "nome": "Hotel Copacabana Palace",
            "estrelas": 5,
            "preco_noite": 450,
            "quartos disponiveis": 3,
            "conforto": "Luxo com vista para o mar",
        },
        {
            "id": "H002",
            "nome": "Hotel Centro RJ",
            "estrelas": 3,
            "preco_noite": 120,
            "quartos disponiveis": 10,
            "conforto": "Confortável e econômico",
        },
        {
            "id": "H003",
            "nome": "Hostel Ipanema",
            "estrelas": 2,
            "preco_noite": 60,
            "quartos disponiveis": 20,
            "conforto": "Básico, bom para mochileiros",
        }
    ]
}

# =========================
# Salvar no banco de dados SQLite real
# =========================
db_path = "chat-bot/database.sqlite"
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# 1. Tabela de Voos
cursor.execute('''
CREATE TABLE IF NOT EXISTS voos (
    id TEXT PRIMARY KEY,
    origem TEXT,
    destino TEXT,
    data TEXT,
    horario TEXT,
    preco REAL,
    assentos INTEGER
)
''')
cursor.execute('DELETE FROM voos') # Limpa para não duplicar se rodar de novo

for (origem, destino, data), voos in VOOS_DATABASE.items():
    for voo in voos:
        cursor.execute('''
        INSERT INTO voos (id, origem, destino, data, horario, preco, assentos)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (voo["id"], origem, destino, data, voo["horario"], voo["preco"], voo["assentos"]))

# 2. Tabela de Hotéis
cursor.execute('''
CREATE TABLE IF NOT EXISTS hoteis (
    id TEXT PRIMARY KEY,
    cidade TEXT,
    nome TEXT,
    estrelas INTEGER,
    preco_noite REAL,
    quartos_disponiveis INTEGER,
    conforto TEXT
)
''')
cursor.execute('DELETE FROM hoteis') # Limpa para não duplicar

for cidade, hoteis in HOTEIS_DATABASE.items():
    for hotel in hoteis:
        cursor.execute('''
        INSERT INTO hoteis (id, cidade, nome, estrelas, preco_noite, quartos_disponiveis, conforto)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            hotel["id"], 
            cidade, 
            hotel["nome"], 
            hotel["estrelas"], 
            hotel["preco_noite"], 
            hotel["quartos disponiveis"], 
            hotel["conforto"]
        ))

conn.commit()
conn.close()

print(f"Banco de dados criado com sucesso em: {db_path} com as tabelas 'voos' e 'hoteis'.")
