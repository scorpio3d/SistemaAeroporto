import random
from datetime import datetime, timedelta  # <--- NOVA IMPORTAÇÃO
from database import (
    inicializar_bd, obter_aeroportos, obter_avioes, obter_companhias,
    adicionar_rota_db, rota_existe, adicionar_voo_db, adicionar_passageiro_db, obter_voos
)

def gerar_dados_teste(qtd_rotas=10, qtd_voos=25, qtd_passageiros=50):
    # 1. Garantir que as tabelas existem
    inicializar_bd()
    
    aeroportos = [a['sigla'] for a in obter_aeroportos()]
    companhias = [c['sigla'] for c in obter_companhias()]
    avioes = [av['modelo'] for av in obter_avioes()]
    
    if not aeroportos or not companhias or not avioes:
        print("❌ Erro: Faltam dados base (aeroportos, companhias ou aviões).")
        return

    # ---------------------------------------------------------
    # 2. GERAR ROTAS
    # ---------------------------------------------------------
    print(f"\n🗺️ A GERAR {qtd_rotas} ROTAS ALEATÓRIAS...")
    rotas_geradas = []
    
    while len(rotas_geradas) < qtd_rotas:
        comp = random.choice(companhias)
        num = str(random.randint(100, 999))
        numero_rota = f"{comp}{num}"
        
        if rota_existe(numero_rota):
            continue # Se por azar a rota já existir, tenta outra vez
            
        origem = random.choice(aeroportos)
        destino = random.choice(aeroportos)
        
        if origem == destino:
            continue
            
        adicionar_rota_db(numero_rota, comp, origem, destino)
        rotas_geradas.append(numero_rota)
        print(f"  ✅ Rota criada: {numero_rota} ({origem} ➔ {destino})")

    # ---------------------------------------------------------
    # 3. GERAR VOOS (AGORA COM DATA E HORA)
    # ---------------------------------------------------------
    print(f"\n🛫 A AGENDAR {qtd_voos} VOOS...")
    estados = ["Programado", "Embarque", "Atrasado", "Concluído", "Cancelado"]
    pesos = [50, 20, 10, 15, 5] 
    
    # Vamos usar o dia de hoje/agora como ponto de partida
    data_base = datetime.now()
    
    # Podemos usar um simples ciclo 'for' porque o AUTOINCREMENT 
    # garante que não há erros de colisão de IDs
    for _ in range(qtd_voos):
        rota = random.choice(rotas_geradas)
        aviao = random.choice(avioes)
        estado = random.choices(estados, weights=pesos, k=1)[0]
        
        # --- LÓGICA DE DATA E HORA ---
        # Sorteia um número de minutos entre 0 e os próximos 7 dias (7 * 24h * 60m)
        minutos_aleatorios = random.randint(0, 7 * 24 * 60)
        data_voo = data_base + timedelta(minutes=minutos_aleatorios)
        # Formata a data para a base de dados (ex: "2026-04-22 14:30")
        data_hora_str = data_voo.strftime("%Y-%m-%d %H:%M")
        # -----------------------------
        
        # A Base de Dados trata de atribuir o ID sozinha
        adicionar_voo_db(rota, aviao, data_hora_str, estado)
        print(f"  ✅ Voo agendado para a rota {rota} às {data_hora_str} ({estado})")

    # ---------------------------------------------------------
    # 4. GERAR PASSAGEIROS (USANDO O ID REAL)
    # ---------------------------------------------------------
    print(f"\n🎟️ A VENDER {qtd_passageiros} BILHETES ALEATÓRIOS...")
    nomes_primeiro = ["João", "Maria", "Ana", "Pedro", "Rui", "Sofia", "Tiago", "Inês", "Miguel", "Beatriz", "Carlos", "Marta"]
    nomes_apelido = ["Silva", "Santos", "Costa", "Pereira", "Martins", "Gomes", "Ferreira", "Rodrigues", "Oliveira", "Lopes"]
    
    pass_registados = 0
    # Pedimos à BD a lista de voos para sabermos quais foram os IDs gerados!
    voos_na_bd = obter_voos() 
    
    while pass_registados < qtd_passageiros:
        # Excluir voos onde não faz sentido vender bilhetes
        voos_validos = [v for v in voos_na_bd if v['estado'] not in ["Cancelado", "Concluído"]]
        if not voos_validos:
            print("⚠️ Todos os voos estão cancelados, concluídos ou lotados. A parar as vendas.")
            break
            
        voo = random.choice(voos_validos)
        
        # Só vende se houver lugares no avião
        if voo['total_passageiros'] < voo['capacidade']:
            nome = f"{random.choice(nomes_primeiro)} {random.choice(nomes_apelido)}"
            
            # Guardamos na BD usando o ID real do voo (inteiro)
            adicionar_passageiro_db(voo['voo_id'], nome)
            
            voo['total_passageiros'] += 1 
            pass_registados += 1
            
            # Juntamos a rota e o ID só para ficar visualmente bonito no terminal
            codigo_visual = f"{voo['numero_rota']}-{voo['voo_id']}"
            print(f"  ✅ Bilhete de {nome} emitido para o {codigo_visual}")

    print("\n🎉 DADOS DE TESTE GERADOS COM SUCESSO!")
    print(f"Resumo: {qtd_rotas} Rotas | {qtd_voos} Voos | {pass_registados} Passageiros")

if __name__ == "__main__":
    gerar_dados_teste()