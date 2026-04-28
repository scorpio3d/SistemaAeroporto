import sqlite3
import os
import json
from contextlib import contextmanager

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, 'data')

os.makedirs(DATA_DIR, exist_ok=True)

DB_PATH = os.path.join(DATA_DIR, 'voos.db')
JSON_AEROPORTOS = os.path.join(DATA_DIR, 'airports.json')
JSON_AVIOES = os.path.join(DATA_DIR, 'airplanes.json')
JSON_COMPANHIAS = os.path.join(DATA_DIR, 'aircompanies.json')

@contextmanager

def db_session():

    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row 
    conn.execute("PRAGMA foreign_keys = ON") 

    try:
        yield conn
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()

def inicializar_bd():
    with db_session() as conn:
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

        #Sincronização DE COMPANHIAS (JSON)
        if os.path.exists(JSON_COMPANHIAS):
            try:
                with open(JSON_COMPANHIAS, 'r', encoding='utf-8') as f:
                    dados_json = json.load(f)
                    companhias_lista = [(c['sigla'], c['nome']) for c in dados_json]
               
                    cursor.executemany('''
                        INSERT INTO companhias (sigla, nome) 
                        VALUES (?, ?) 
                        ON CONFLICT(sigla) 
                        DO UPDATE SET nome = excluded.nome
                    ''', companhias_lista)

                    print(f"Sincronizadas {len(companhias_lista)} companhias carregadas de {JSON_COMPANHIAS}")
            except Exception as e:
                print(f"Erro ao ler JSON de companhias: {e}")
        else:
            print(f"Ficheiro {JSON_COMPANHIAS} não encontrado.")

        #Sincronização DE AEROPORTOS (JSON)
        if os.path.exists(JSON_AEROPORTOS):
            try:
                with open(JSON_AEROPORTOS, 'r', encoding='utf-8') as f:
                    dados_json = json.load(f)
                    aeroportos_lista = [(a['sigla'], a['nome'], a['cidade']) for a in dados_json]
                
                    cursor.executemany('''
                        INSERT INTO aeroportos (sigla, nome, cidade) 
                        VALUES (?, ?, ?) 
                        ON CONFLICT(sigla) 
                        DO UPDATE SET 
                            nome = excluded.nome,
                            cidade = excluded.cidade
                    ''', aeroportos_lista)

                    print(f"Sincronizados {len(aeroportos_lista)} aeroportos carregados de {JSON_AEROPORTOS}")
            except Exception as e:
                print(f"Erro ao ler JSON de aeroportos: {e}")
        else:
            print(f"Ficheiro {JSON_AEROPORTOS} não encontrado.")

        #Sincronização DE AVIÕES (JSON)
        if os.path.exists(JSON_AVIOES):
            try:
                with open(JSON_AVIOES, 'r', encoding='utf-8') as f:
                    dados_json = json.load(f)
                    avioes_lista = [(av['modelo'], av['capacidade']) for av in dados_json]
                
                    cursor.executemany('''
                        INSERT INTO avioes (modelo, capacidade) 
                        VALUES (?, ?) 
                        ON CONFLICT(modelo) 
                        DO UPDATE SET capacidade = excluded.capacidade
                    ''', avioes_lista)

                    print(f"Sincronizados {len(avioes_lista)} aviões carregados de {JSON_AVIOES}")
            except Exception as e:
                print(f"Erro ao ler JSON de aviões: {e}")
        else:
            print(f"Ficheiro {JSON_AVIOES} não encontrado.")
    

#FUNÇÕES DE CONSULTA BASE
def obter_companhias():
    with db_session() as conn:
        return[dict(r) for r in conn.execute("SELECT * FROM companhias ORDER BY nome").fetchall()]

def obter_aeroportos():
    with db_session() as conn:
        return [dict(r) for r in conn.execute("SELECT * FROM aeroportos ORDER BY cidade, nome").fetchall()]
def obter_avioes():
    with db_session() as conn:
        return [dict(r) for r in conn.execute("SELECT * FROM avioes ORDER BY modelo").fetchall()]

#FUNÇÕES DE ROTAS (NOVAS)
def obter_rotas():
    with db_session() as conn:
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
        return [dict(r) for r in cursor.fetchall()]

def rota_existe(numero_rota):
    with db_session() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT 1 FROM rotas WHERE numero_rota = ?", (numero_rota,))
        existe = cursor.fetchone() is not None
    return existe

def adicionar_rota_db(numero_rota, companhia_sigla, origem_sigla, destino_sigla):
    with db_session() as conn:
        cursor = conn.cursor()

        cursor.execute('''
            INSERT INTO rotas (numero_rota, companhia_sigla, origem_sigla, destino_sigla)
            VALUES (?, ?, ?, ?)
        ''', (numero_rota, companhia_sigla, origem_sigla, destino_sigla))

#FUNÇÕES DE VOOS
def obter_voos():
    with db_session() as conn:
        cursor= conn.cursor()
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

        return [dict(r) for r in cursor.fetchall()]

def obter_passageiros_voo(voo_id):
    with db_session() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT nome FROM passageiros WHERE voo_id = ? ORDER BY nome", (voo_id,))
        return [dict(r) for r in cursor.fetchall()]

def voo_existe(numero_voo):
    with db_session() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT 1 FROM voos WHERE numero_voo = ?", (numero_voo,))
        return cursor.fetchone() is not None

def adicionar_voo_db(numero_rota, aviao_modelo, data_hora, estado="Programado"):
    with db_session() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO voos (numero_rota, aviao_modelo, data_hora, estado)
            VALUES (?, ?, ?, ?)
        ''', (numero_rota, aviao_modelo, data_hora, estado))
      
def atualizar_estado_voo_db(voo_id, novo_estado):
    with db_session() as conn:
        cursor = conn.cursor()
    
        if novo_estado == "Atrasado":
            # Atualiza o estado e adiciona 1 hora à coluna data_hora
            cursor.execute('''
                UPDATE voos 
                SET estado = ?, 
                    data_hora = datetime(data_hora, '+1 hour')
                WHERE id = ?
            ''', (novo_estado, voo_id))
        else:
            # Atualiza apenas o estado para as restantes opções
            cursor.execute('''
                UPDATE voos 
                SET estado = ? 
                WHERE id = ?
            ''', (novo_estado, voo_id))

#FUNÇÕES DE PASSAGEIROS
def adicionar_passageiro_db(voo_id, nome):
    with db_session() as conn:
        cursor =conn.cursor()
        cursor.execute('''
            INSERT INTO passageiros (voo_id, nome)
            VALUES (?, ?)
        ''', (voo_id, nome))