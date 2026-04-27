import sys
from database import (
    inicializar_bd, obter_voos, adicionar_voo_db, voo_existe, 
    obter_aeroportos, obter_avioes, adicionar_passageiro_db, 
    obter_companhias, obter_rotas, adicionar_rota_db, rota_existe, atualizar_estado_voo_db, obter_passageiros_voo
)

# ==========================================
# CLASSE DE INTERFACE (VISUALIZAÇÃO E AÇÕES)
# ==========================================
class TerminalUI:
    def __init__(self):
        pass

    # --- LISTAGENS ---
    def listar_voos_ui(self):
        voos = obter_voos()
        
        print("\n--- ⚖️ OPÇÕES DE ORDENAÇÃO ---")
        print("1. Por Data/Hora (Padrão)")
        print("2. Por Destino")
        print("3. Por Estado")
        print("4. Por Rota")
        
        escolha = input("Escolha como ordenar (Enter para padrão): ")

        # Lógica de ordenação em Python
        match escolha:
            case "2":
                voos.sort(key=lambda x: x['destino_cidade'])
            case "3":
                voos.sort(key=lambda x: x['estado'])
            case "4":
                voos.sort(key=lambda x: x['numero_rota'])
            case _:
                voos.sort(key=lambda x: x['data_hora'])

        print("\n" + "="*65)
        print(" 🛫 PAINEL DE VOOS 🛬")
        print("="*65)
        
        if not voos:
            print(" Não há voos agendados.")
            return

        for v in voos:
            # Recuperar os valores da lotação
            lugar_ocupados = v.get('total_passageiros', 0)
            cap = v.get('capacidade', 0)
            
            codigo_visual = f"{v['numero_rota']}-{v['voo_id']}"
            
            print(f" VOO: {codigo_visual} | DATA/HORA: {v['data_hora']}") 
            print(f" Rota: {v['origem_cidade']} ➔ {v['destino_cidade']} | Estado: {v['estado']}")
            print(f" Avião: {v['aviao_modelo']} | Lotação: {lugar_ocupados}/{cap}")
            print("-" * 65)

    def listar_companhias_ui(self):
        comps = obter_companhias()
        print("\n--- COMPANHIAS AÉREAS ---")
        if not comps:
            print(" Nenhuma companhia registada.")
            return
        for c in comps:
            print(f" {c['sigla']}: {c['nome']}")

    def listar_avioes_ui(self):
        avs = obter_avioes()
        print("\n--- FROTA DE AVIÕES ---")
        if not avs:
            print(" Nenhum avião registado.")
            return
        for a in avs:
            print(f" {a['modelo']} | Capacidade: {a['capacidade']} passageiros")

    def listar_rotas_ui(self):
        rotas = obter_rotas()
        print("\n--- ROTAS CONFIGURADAS NO SISTEMA ---")
        if not rotas:
            print(" Nenhuma rota registada.")
            return
        for r in rotas:
            print(f" [{r['numero_rota']}] {r['companhia_nome']}: {r['origem_cidade']} ➔ {r['destino_cidade']}")

    def listar_passageiros_ui(self):
        self.listar_voos_ui()
        try:
            v_id = int(input("\nDigite o ID do voo para ver a lista de passageiros: "))
            passageiros = obter_passageiros_voo(v_id)
            
            print(f"\n--- 👥 PASSAGEIROS DO VOO ID {v_id} ---")
            if not passageiros:
                print("Nenhum passageiro encontrado.")
            else:
                for i, p in enumerate(passageiros, 1):
                    print(f"{i}. {p['nome']}")
            print("-" * 30)
        except ValueError:
            print("❌ ID Inválido.")

    # --- FUNÇÕES DE SELEÇÃO AJUDANTES ---
    def selecionar_rota(self):
        rotas = obter_rotas()
        if not rotas:
            print("❌ Erro: Não existem rotas criadas. Crie uma rota primeiro.")
            return None
        
        self.listar_rotas_ui()
        while True:
            num = input("\nDigite o número da Rota pretendida (ex: TP102): ").upper().strip()
            if any(r['numero_rota'] == num for r in rotas):
                return num
            print("❌ Erro: Rota inválida.")

    def selecionar_companhia(self):
        comps = obter_companhias()
        for c in comps: print(f" - {c['sigla']}: {c['nome']}")
        while True:
            s = input("Sigla Companhia: ").upper().strip()
            if any(c['sigla'] == s for c in comps): return s
            print("❌ Inválida.")

    def selecionar_aeroporto(self, msg):
        aeros = obter_aeroportos()
        for a in aeros: print(f" - {a['sigla']}: {a['cidade']}")
        while True:
            s = input(msg).upper().strip()
            if any(a['sigla'] == s for a in aeros): return s
            print("❌ Inválido.")

    def selecionar_aviao(self):
        avs = obter_avioes()
        for i, a in enumerate(avs, 1): print(f" {i}. {a['modelo']}")
        while True:
            try:
                escolha = int(input("Escolha o Avião (Nº): "))
                return avs[escolha-1]['modelo']
            except: print("❌ Inválido.")

    # --- AÇÕES DO ADMINISTRADOR ---
    def adicionar_rota_ui(self):
        print("\n--- 🗺️ CRIAR NOVA ROTA ---")
        comp = self.selecionar_companhia()
        
        while True:
            num = input(f"Número da Rota (ex: 102 para {comp}102): ").strip()
            num_rota = f"{comp}{num}"
            if rota_existe(num_rota):
                print("❌ Esta rota já existe.")
            else: break
        
        ori = self.selecionar_aeroporto("Origem: ")
        des = self.selecionar_aeroporto("Destino: ")
        
        if ori == des:
            print("❌ Origem e destino iguais!")
            return

        adicionar_rota_db(num_rota, comp, ori, des)
        print(f"✅ Rota {num_rota} criada com sucesso!")

    def adicionar_voo_ui(self):
        print("\n--- ➕ AGENDAR NOVO VOO ---")
        rota = self.selecionar_rota()
        if not rota: return
        
        data_hora = input("Introduza a Data e Hora (AAAA-MM-DD HH:MM): ").strip()
        if not data_hora:
            data_hora = "2026-01-01 00:00"

        aviao = self.selecionar_aviao()
        
        adicionar_voo_db(rota, aviao, data_hora)
        print(f"\n✅ SUCESSO: Voo agendado para {data_hora}!")

    def mudar_estado_voo_ui(self):
        self.listar_voos_ui()
        
        try:
            voo_id = int(input("\nDigite o ID do voo que deseja alterar (número após o traço): "))
        except ValueError:
            print("❌ Erro: ID inválido.")
            return

        voos = obter_voos()
        voo_alvo = next((v for v in voos if v['voo_id'] == voo_id), None)
        
        if not voo_alvo:
            print("❌ Erro: Voo não encontrado.")
            return

        print(f"\nEstado atual do voo {voo_alvo['numero_rota']}-{voo_id}: {voo_alvo['estado']}")
        print("Novos estados possíveis:")
        estados = ["Programado", "Embarque", "Em voo", "Atrasado", "Concluído", "Cancelado"]
        
        for i, est in enumerate(estados, 1):
            print(f" {i}. {est}")
        
        try:
            opcao = int(input("Escolha o novo estado (número): "))
            if 1 <= opcao <= len(estados):
                novo_estado = estados[opcao - 1]
                atualizar_estado_voo_db(voo_id, novo_estado)
                print(f"✅ SUCESSO: O estado do voo foi alterado para '{novo_estado}'.")
            else:
                print("❌ Opção inválida.")
        except ValueError:
            print("❌ Erro: Entrada inválida.")

    # --- AÇÕES DO PASSAGEIRO ---
    def comprar_bilhete_ui(self):
        self.listar_voos_ui()
        print("\nPara comprar bilhete, identifique o voo pelo seu ID interno (o número a seguir ao traço, ex: se for TP102-5, digite 5)")
        
        try:
            voo_id = int(input("ID do Voo: "))
        except ValueError:
            print("❌ Erro: Por favor insira apenas o número (ID).")
            return
        
        voos = obter_voos()
        v_escolhido = next((v for v in voos if v['voo_id'] == voo_id), None)
        
        if not v_escolhido:
            print("❌ Voo não encontrado.")
            return
        
        # Calcular os lugares livres
        lugares_livres = v_escolhido.get('capacidade', 0) - v_escolhido.get('total_passageiros', 0)
        
        if lugares_livres <= 0:
            print("❌ Voo lotado!")
            return
            
        print("\nPara comprar vários bilhetes de uma vez, separe os nomes por vírgula.")
        print(f"\nTemos {lugares_livres} lugares disponíveis.")
        nomes_input = input("Seu(s) Nome(s): ").strip()
        
        if not nomes_input:
            print("❌ Nenhuma operação realizada.")
            return
            
        # Transforma o texto numa lista de nomes
        lista_nomes = [nome.strip() for nome in nomes_input.split(",") if nome.strip()]
        quantidade = len(lista_nomes)
        
        # O ciclo for entra em ação se houver capacidade
        if quantidade <= lugares_livres:
            for nome in lista_nomes:
                adicionar_passageiro_db(voo_id, nome)
            print(f"✅ {quantidade} Bilhete(s) confirmado(s) com sucesso!")
        else:
            print(f"❌ Erro: O voo não tem lugares suficientes! Restam apenas {lugares_livres} lugares.")


# ==========================================
# MENUS DO SISTEMA
# ==========================================

def menu_listas(interface):
    while True:
        print("\n--- 📋 MENU DE LISTAGENS ---")
        print("1. Listar Rotas")
        print("2. Listar Voos")
        print("3. Listar Companhias")
        print("4. Listar Aviões")
        print("5. Ver Passageiros por Voo")
        print("6. Voltar ao Menu Anterior")

        op = input("Opção: ")
        
        match op:
            case "1":
                interface.listar_rotas_ui()
            case "2":
                interface.listar_voos_ui()
            case "3":
                interface.listar_companhias_ui()
            case "4":
                interface.listar_avioes_ui()
            case "5":
                interface.listar_passageiros_ui()
            case "6":
                break  
            case _:
                print("⚠️ Opção inválida! Tente novamente.")

def menu_admin(interface):
    while True:
        print("\n--- 🛠️ MENU ADMINISTRADOR ---")
        print("1. Criar Rota")
        print("2. Agendar Voo")
        print("3. Alterar Estado de um Voo")
        print("4. Ver Listas")
        print("5. Voltar ao login")
        
        op = input("Opção: ")
        
        match op:
            case "1":
                interface.adicionar_rota_ui()
            case "2":
                interface.adicionar_voo_ui()
            case "3":
                interface.mudar_estado_voo_ui()
            case "4":
                menu_listas(interface)
            case "5":
                break
            case _:
                print("⚠️ Opção inválida! Tente novamente.")

def menu_utilizador(interface):
    while True:
        print("\n--- ✈️ PASSAGEIRO ---")
        print("1. Consultar Painel de Voos")
        print("2. Comprar Bilhete")
        print("3. Voltar")
        
        op = input("Opção: ")
        
        match op:
            case "1":
                interface.listar_voos_ui()
            case "2":
                interface.comprar_bilhete_ui()
            case "3":
                break
            case _:
                print("⚠️ Opção inválida! Tente novamente.")

def menu_principal():
    inicializar_bd()
    interface = TerminalUI()  # Instanciamos a classe uma única vez
    
    while True:
        print("\n=== SISTEMA DE AEROPORTO ===")
        print("1. Administrador")
        print("2. Passageiro")
        print("3. Sair")
        
        op = input("Perfil: ")
        
        match op:
            case "1":
                menu_admin(interface)
            case "2":
                menu_utilizador(interface)
            case "3":
                print("A encerrar o sistema...")
                sys.exit(0)
            case _:
                print("⚠️ Perfil inexistente!")

if __name__ == "__main__":
    menu_principal()