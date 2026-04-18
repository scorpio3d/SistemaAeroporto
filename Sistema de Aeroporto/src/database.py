import sqlite3
import os

DB_PATH = os.path.join('data', 'aeroporto.db')

def conectar():
    os.makedirs('data', exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row 
    conn.execute("PRAGMA foreign_keys = ON") 
    return conn

def inicializar_bd():
    conn = conectar()
    cursor = conn.cursor()
    
    # 1. Tabela de Aeroportos
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS aeroportos (
            sigla TEXT PRIMARY KEY,
            nome TEXT NOT NULL,
            cidade TEXT NOT NULL
        )
    ''')
    
    # 2. Tabela de Aviões (NOVA)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS avioes (
            modelo TEXT PRIMARY KEY,
            capacidade INTEGER NOT NULL
        )
    ''')
    
    # 3. Tabela de Voos (Agora usa o modelo do avião em vez da capacidade manual)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS voos (
            numero_voo TEXT PRIMARY KEY,
            origem_sigla TEXT NOT NULL,
            destino_sigla TEXT NOT NULL,
            aviao_modelo TEXT NOT NULL,
            estado TEXT NOT NULL,
            FOREIGN KEY (origem_sigla) REFERENCES aeroportos (sigla),
            FOREIGN KEY (destino_sigla) REFERENCES aeroportos (sigla),
            FOREIGN KEY (aviao_modelo) REFERENCES avioes (modelo)
        )
    ''')
    
    # 4. Tabela de Passageiros
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS passageiros (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            voo_numero TEXT NOT NULL,
            nome TEXT NOT NULL,
            FOREIGN KEY (voo_numero) REFERENCES voos (numero_voo)
        )
    ''')
    
    # Inserir aeroportos iniciais
    cursor.execute("SELECT COUNT(*) FROM aeroportos")
    if cursor.fetchone()[0] == 0:
        aeroportos_iniciais = [
            ('LIS', 'Humberto Delgado', 'Lisboa'),
            ('OPO', 'Francisco Sá Carneiro', 'Porto'),
            ('FNC', 'Cristiano Ronaldo', 'Funchal'),
            ('FAO', 'Gago Coutinho', 'Faro'),
            ('PDL', 'João Paulo II', 'Ponta Delgada')
        ]
        cursor.executemany("INSERT INTO aeroportos (sigla, nome, cidade) VALUES (?, ?, ?)", aeroportos_iniciais)

    # Inserir aviões iniciais
    cursor.execute("SELECT COUNT(*) FROM avioes")
    if cursor.fetchone()[0] == 0:
        avioes_iniciais = [
            ('Airbus A320', 150),
            ('Boeing 737', 180),
            ('Embraer E195', 118),
            ('ATR 72', 70)
        ]
        cursor.executemany("INSERT INTO avioes (modelo, capacidade) VALUES (?, ?)", avioes_iniciais)
    
    conn.commit()
    conn.close()

def obter_aeroportos():
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM aeroportos ORDER BY cidade")
    aeroportos = cursor.fetchall()
    conn.close()
    return aeroportos

def obter_avioes():
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM avioes ORDER BY capacidade DESC")
    avioes = cursor.fetchall()
    conn.close()
    return avioes

def obter_voos():
    conn = conectar()
    cursor = conn.cursor()
    # JOIN agora inclui a tabela de aviões para sabermos a capacidade
    cursor.execute('''
        SELECT v.numero_voo, v.estado, v.aviao_modelo,
               a.capacidade,
               o.nome as origem_nome, o.sigla as origem_sigla, o.cidade as origem_cidade,
               d.nome as destino_nome, d.sigla as destino_sigla, d.cidade as destino_cidade
        FROM voos v
        JOIN aeroportos o ON v.origem_sigla = o.sigla
        JOIN aeroportos d ON v.destino_sigla = d.sigla
        JOIN avioes a ON v.aviao_modelo = a.modelo
    ''')
    voos = cursor.fetchall()
    
    voos_completos = []
    for v in voos:
        v_dict = dict(v)
        cursor.execute("SELECT COUNT(*) as total FROM passageiros WHERE voo_numero = ?", (v['numero_voo'],))
        v_dict['total_passageiros'] = cursor.fetchone()['total']
        voos_completos.append(v_dict)
        
    conn.close()
    return voos_completos

def voo_existe(numero_voo):
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("SELECT 1 FROM voos WHERE numero_voo = ?", (numero_voo,))
    existe = cursor.fetchone() is not None
    conn.close()
    return existe

def adicionar_voo_db(numero, origem_sigla, destino_sigla, aviao_modelo, estado="Programado"):
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO voos (numero_voo, origem_sigla, destino_sigla, aviao_modelo, estado)
        VALUES (?, ?, ?, ?, ?)
    ''', (numero, origem_sigla, destino_sigla, aviao_modelo, estado))
    conn.commit()
    conn.close()