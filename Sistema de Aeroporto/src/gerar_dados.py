import random
from datetime import datetime, timedelta
from database import (
    inicializar_bd, obter_aeroportos, obter_avioes, obter_companhias,
    adicionar_rota_db, rota_existe, adicionar_voo_db, adicionar_passageiro_db, obter_voos
)

def gerar_dados_teste(qtd_rotas=20, qtd_voos=5, qtd_passageiros=500):
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
    # 3. GERAR VOOS (COM DATA E HORA)
    # ---------------------------------------------------------
    print(f"\n🛫 A AGENDAR {qtd_voos} VOOS...")
    estados = ["Programado", "Embarque", "Atrasado", "Concluído", "Cancelado"]
    pesos = [50, 20, 10, 15, 5] 
    
    # Vamos usar o dia de hoje/agora como ponto de partida
    data_base = datetime.now()
    
    for _ in range(qtd_voos):
        rota = random.choice(rotas_geradas)
        aviao = random.choice(avioes)
        estado = random.choices(estados, weights=pesos, k=1)[0]
        
        # Sorteia um número de minutos entre 0 e o próximo ano (365 * 24h * 60m)
        minutos_aleatorios = random.randint(0, 365 * 24 * 60)
        data_voo = data_base + timedelta(minutes=minutos_aleatorios)
        data_hora_str = data_voo.strftime("%Y-%m-%d %H:%M")
        
        adicionar_voo_db(rota, aviao, data_hora_str, estado)
        print(f"  ✅ Voo agendado para a rota {rota} às {data_hora_str} ({estado})")

    # ---------------------------------------------------------
    # 4. GERAR PASSAGEIROS (OTIMIZADO)
    # ---------------------------------------------------------
    voos_na_bd = obter_voos()

    # Excluímos voos Cancelados e Concluídos das contas, já que não recebem mais passageiros
    estados_excluidos = ["Cancelado", "Concluído"]

    # Calcula a capacidade e passageiros usando apenas os dados fornecidos pelo obter_voos()
    capacidade_total = sum(v['capacidade'] for v in voos_na_bd if v['estado'] not in estados_excluidos)
    total_passageiros_atuais = sum(v['total_passageiros'] for v in voos_na_bd if v['estado'] not in estados_excluidos)

    # Lugares que efetivamente sobram
    capacidade_disponivel = max(0, capacidade_total - total_passageiros_atuais)

    # Ajusta os passageiros a gerar
    qtd_passageiros = min(qtd_passageiros, capacidade_disponivel)

    print(f"\n🎟️ A VENDER {qtd_passageiros} BILHETES ALEATÓRIOS...")
    nomes_primeiro = ["João", "Maria", "Ana", "Pedro", "Rui", "Sofia", "Tiago", "Inês", "Miguel", "Beatriz", "Carlos", "Marta", "Janaína"]
    nomes_apelido = ["Silva", "Santos", "Costa", "Pereira", "Martins", "Gomes", "Ferreira", "Rodrigues", "Oliveira", "Lopes", "Morais"]
    
    pass_registados = 0

    # Criamos a montra de voos que ainda têm vagas
    voos_com_vagas = [
        v for v in voos_na_bd 
        if v['estado'] not in estados_excluidos and v['total_passageiros'] < v['capacidade']
    ]

    while pass_registados < qtd_passageiros:
        # Se ficarmos sem voos com vagas a meio do processo, paramos
        if not voos_com_vagas:
            print("⚠️ Todos os voos válidos estão agora lotados. A parar as vendas.")
            break
            
        voo = random.choice(voos_com_vagas)
        
        nome = f"{random.choice(nomes_primeiro)} {random.choice(nomes_apelido)}"
        
        adicionar_passageiro_db(voo['voo_id'], nome)
        
        voo['total_passageiros'] += 1 
        pass_registados += 1
        
        # A MÁGICA DA PERFORMANCE: Voo encheu? Sai imediatamente da lista de opções!
        if voo['total_passageiros'] >= voo['capacidade']:
            voos_com_vagas.remove(voo)
        
        codigo_visual = f"{voo['numero_rota']}-{voo['voo_id']}"
        print(f"  ✅ Bilhete de {nome} emitido para o {codigo_visual}")

    print("\n🎉 DADOS DE TESTE GERADOS COM SUCESSO!")
    print(f"Resumo: {qtd_rotas} Rotas | {qtd_voos} Voos | {pass_registados} Passageiros")

if __name__ == "__main__":
    gerar_dados_teste()