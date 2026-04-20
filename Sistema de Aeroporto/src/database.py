import sqlite3
import os
import json

DB_PATH = os.path.join('data', 'voos.db')
JSON_AEROPORTOS = os.path.join('data', 'airports.json')
JSON_AVIOES = os.path.join('data', 'airplanes.json')

def conectar():
    os.makedirs('data', exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row 
    conn.execute("PRAGMA foreign_keys = ON") 
    return conn

def inicializar_bd():
    conn = conectar()
    cursor = conn.cursor()
    
    # 1. Tabela de Companhias Aéreas
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS companhias (
            sigla TEXT PRIMARY KEY,
            nome TEXT NOT NULL
        )
    ''')
    
    # 2. Tabela de Aeroportos
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS aeroportos (
            sigla TEXT PRIMARY KEY,
            nome TEXT NOT NULL,
            cidade TEXT NOT NULL
        )
    ''')
    
    # 3. Tabela de Aviões
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS avioes (
            modelo TEXT PRIMARY KEY,
            capacidade INTEGER NOT NULL
        )
    ''')

    # 4. Tabela de Rotas
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS rotas (
            numero_rota TEXT PRIMARY KEY,
            companhia_sigla TEXT NOT NULL,
            origem_sigla TEXT NOT NULL,
            destino_sigla TEXT NOT NULL,
            FOREIGN KEY (companhia_sigla) REFERENCES companhias (sigla),
            FOREIGN KEY (origem_sigla) REFERENCES aeroportos (sigla),
            FOREIGN KEY (destino_sigla) REFERENCES aeroportos (sigla)
        )
    ''')
    
    # 5. Tabela de Voos
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS voos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            numero_rota TEXT NOT NULL,
            aviao_modelo TEXT NOT NULL,
            data_hora TEXT NOT NULL,
            estado TEXT NOT NULL,
            FOREIGN KEY (numero_rota) REFERENCES rotas (numero_rota),
            FOREIGN KEY (aviao_modelo) REFERENCES avioes (modelo)
        )
    ''')
    
    # 6. Tabela de Passageiros
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS passageiros (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            voo_id INTEGER NOT NULL,
            nome TEXT NOT NULL,
            FOREIGN KEY (voo_id) REFERENCES voos (id)
        )
    ''')

    # --- INSERÇÃO DE COMPANHIAS ---
    cursor.execute("SELECT COUNT(*) FROM companhias")
    if cursor.fetchone()[0] == 0:
        cursor.executemany("INSERT INTO companhias (sigla, nome) VALUES (?, ?)", [
            ('TP', 'TAP Air Portugal'), ('FR', 'Ryanair'),
            ('U2', 'EasyJet'), ('S4', 'SATA Azores Airlines')
        ])
    
    # --- INSERÇÃO DE AEROPORTOS (JSON + CÓDIGO ANTIGO COMENTADO) ---
    cursor.execute("SELECT COUNT(*) FROM aeroportos")
    if cursor.fetchone()[0] == 0:
        if os.path.exists(JSON_AEROPORTOS):
            try:
                with open(JSON_AEROPORTOS, 'r', encoding='utf-8') as f:
                    dados_json = json.load(f)
                    aeroportos_lista = [(a['sigla'], a['nome'], a['cidade']) for a in dados_json]
                    cursor.executemany("INSERT INTO aeroportos (sigla, nome, cidade) VALUES (?, ?, ?)", aeroportos_lista)
                    print(f"✅ {len(aeroportos_lista)} aeroportos carregados de {JSON_AEROPORTOS}")
            except Exception as e:
                print(f"❌ Erro ao ler JSON de aeroportos: {e}")
        else:
            print(f"⚠️ Ficheiro {JSON_AEROPORTOS} não encontrado.")
            
        # --- CÓDIGO ANTIGO COMENTADO ---
        # cursor.executemany("INSERT INTO aeroportos (sigla, nome, cidade) VALUES (?, ?, ?)", [
        #     ('LIS', 'Humberto Delgado', 'Lisboa'), ('OPO', 'Francisco Sá Carneiro', 'Porto'),
        #     ('FNC', 'Cristiano Ronaldo', 'Funchal'), ('FAO', 'Gago Coutinho', 'Faro'),
        #     ('PDL', 'João Paulo II', 'Ponta Delgada')
        # ])

    # --- INSERÇÃO DE AVIÕES (JSON + CÓDIGO ANTIGO COMENTADO) ---
    cursor.execute("SELECT COUNT(*) FROM avioes")
    if cursor.fetchone()[0] == 0:
        if os.path.exists(JSON_AVIOES):
            try:
                with open(JSON_AVIOES, 'r', encoding='utf-8') as f:
                    dados_json = json.load(f)
                    avioes_lista = [(av['modelo'], av['capacidade']) for av in dados_json]
                    cursor.executemany("INSERT INTO avioes (modelo, capacidade) VALUES (?, ?)", avioes_lista)
                    print(f"✅ {len(avioes_lista)} aviões carregados de {JSON_AVIOES}")
            except Exception as e:
                print(f"❌ Erro ao ler JSON de aviões: {e}")
        else:
             print(f"⚠️ Ficheiro {JSON_AVIOES} não encontrado.")

        # --- CÓDIGO ANTIGO COMENTADO ---
        # cursor.executemany("INSERT INTO avioes (modelo, capacidade) VALUES (?, ?)", [
        #     ('Airbus A320', 150), ('Boeing 737', 180),
        #     ('Embraer E195', 118), ('ATR 72', 70)
        # ])
    
    conn.commit()
    conn.close()

# --- FUNÇÕES DE CONSULTA BASE ---
def obter_companhias():
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM companhias ORDER BY nome")
    resultado = cursor.fetchall()
    conn.close()
    return [dict(r) for r in resultado]

def obter_aeroportos():
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM aeroportos ORDER BY cidade")
    resultado = cursor.fetchall()
    conn.close()
    return [dict(r) for r in resultado]

def obter_avioes():
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM avioes ORDER BY capacidade DESC")
    resultado = cursor.fetchall()
    conn.close()
    return [dict(r) for r in resultado]

# --- FUNÇÕES DE ROTAS (NOVAS) ---
def obter_rotas():
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT r.numero_rota, r.companhia_sigla, c.nome as companhia_nome,
               r.origem_sigla, o.cidade as origem_cidade,
               r.destino_sigla, d.cidade as destino_cidade
        FROM rotas r
        JOIN companhias c ON r.companhia_sigla = c.sigla
        JOIN aeroportos o ON r.origem_sigla = o.sigla
        JOIN aeroportos d ON r.destino_sigla = d.sigla
    ''')
    resultado = cursor.fetchall()
    conn.close()
    return [dict(r) for r in resultado]

def rota_existe(numero_rota):
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("SELECT 1 FROM rotas WHERE numero_rota = ?", (numero_rota,))
    existe = cursor.fetchone() is not None
    conn.close()
    return existe

def adicionar_rota_db(numero_rota, companhia_sigla, origem_sigla, destino_sigla):
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO rotas (numero_rota, companhia_sigla, origem_sigla, destino_sigla)
        VALUES (?, ?, ?, ?)
    ''', (numero_rota, companhia_sigla, origem_sigla, destino_sigla))
    conn.commit()
    conn.close()

# --- FUNÇÕES DE VOOS ---
def obter_voos():
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT v.id as voo_id, v.estado, v.aviao_modelo, v.data_hora,
               r.numero_rota, c.nome as companhia_nome,
               a.capacidade,
               o.nome as origem_nome, o.sigla as origem_sigla, o.cidade as origem_cidade,
               d.nome as destino_nome, d.sigla as destino_sigla, d.cidade as destino_cidade,
               COUNT(p.id) as total_passageiros
        FROM voos v
        JOIN rotas r ON v.numero_rota = r.numero_rota
        JOIN companhias c ON r.companhia_sigla = c.sigla
        JOIN aeroportos o ON r.origem_sigla = o.sigla
        JOIN aeroportos d ON r.destino_sigla = d.sigla
        JOIN avioes a ON v.aviao_modelo = a.modelo
        LEFT JOIN passageiros p ON v.id = p.voo_id
        GROUP BY v.id
        ORDER BY v.data_hora ASC
    ''')
    resultado = cursor.fetchall()
    conn.close()
    return [dict(r) for r in resultado]

def obter_passageiros_voo(voo_id):
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("SELECT nome FROM passageiros WHERE voo_id = ? ORDER BY nome", (voo_id,))
    resultado = cursor.fetchall()
    conn.close()
    return [dict(r) for r in resultado]

def voo_existe(numero_voo):
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("SELECT 1 FROM voos WHERE numero_voo = ?", (numero_voo,))
    existe = cursor.fetchone() is not None
    conn.close()
    return existe

def adicionar_voo_db(numero_rota, aviao_modelo, data_hora, estado="Programado"):
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO voos (numero_rota, aviao_modelo, data_hora, estado)
        VALUES (?, ?, ?, ?)
    ''', (numero_rota, aviao_modelo, data_hora, estado))
    conn.commit()
    conn.close()

def atualizar_estado_voo_db(voo_id, novo_estado):
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute('''
        UPDATE voos 
        SET estado = ? 
        WHERE id = ?
    ''', (novo_estado, voo_id))
    conn.commit()
    conn.close()

# --- FUNÇÕES DE PASSAGEIROS ---
def adicionar_passageiro_db(voo_id, nome):
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO passageiros (voo_id, nome)
        VALUES (?, ?)
    ''', (voo_id, nome))
    conn.commit()
    conn.close()