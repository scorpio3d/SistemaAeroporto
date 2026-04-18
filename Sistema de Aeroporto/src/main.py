from database import inicializar_bd, obter_voos, adicionar_voo_db, voo_existe, obter_aeroportos, obter_avioes

# --- FUNÇÕES DE INTERAÇÃO ---

def selecionar_aeroporto(mensagem):
    aeroportos = obter_aeroportos()
    print("\n🌍 Aeroportos Disponíveis:")
    for a in aeroportos:
        print(f"[{a['sigla']}] - {a['nome']} ({a['cidade']})")
    
    while True:
        sigla = input(mensagem).upper().strip()
        if any(a['sigla'] == sigla for a in aeroportos):
            return sigla
        print("❌ Erro: Sigla inválida. Escolha apenas uma das siglas listadas acima.")

def selecionar_aviao():
    avioes = obter_avioes()
    print("\n✈️ Aviões Disponíveis:")
    for a in avioes:
        print(f"[{a['modelo']}] - Capacidade: {a['capacidade']} passageiros")
    
    while True:
        escolha = input("\nEscreva o modelo do avião: ").strip()
        # Procura o avião ignorando maiúsculas e minúsculas
        for a in avioes:
            if a['modelo'].lower() == escolha.lower():
                return a['modelo'] # Retorna o nome exato formatado da BD
        print("❌ Erro: Modelo inválido. Escreva o nome de um dos modelos listados.")

def adicionar_voo_ui():
    while True:
        num = input("\nNúmero do Voo: ").upper().strip()
        if voo_existe(num):
            print(f"❌ Erro: O voo {num} já existe na base de dados!")
        else:
            break

    origem = selecionar_aeroporto("\nSigla do aeroporto de Origem: ")
    destino = selecionar_aeroporto("\nSigla do aeroporto de Destino: ")
    
    if origem == destino:
        print("❌ Erro: A origem e o destino não podem ser o mesmo aeroporto!")
        return

    # Nova lógica: Em vez de perguntar capacidade, escolhe o avião
    aviao = selecionar_aviao()

    adicionar_voo_db(num, origem, destino, aviao)
    print(f"\n✅ Voo {num} registado com sucesso usando um {aviao}!")

def listar_voos_ui():
    voos = obter_voos()
    if not voos:
        print("\n[!] Não existem voos agendados no sistema.")
        return

    print("\n" + "="*55)
    print("                 PAINEL DE VOOS")
    print("="*55)
    for v in voos:
        print(f"✈️ Voo: {v['numero_voo']} | Aeronave: {v['aviao_modelo']}")
        print(f"De:   {v['origem_cidade']} ({v['origem_sigla']}) - {v['origem_nome']}")
        print(f"Para: {v['destino_cidade']} ({v['destino_sigla']}) - {v['destino_nome']}")
        print(f"Estado: {v['estado']} | Lugares Ocupados: {v['total_passageiros']}/{v['capacidade']}")
        print("-" * 55)

# --- MENUS COM MATCH-CASE ---

def menu_admin():
    while True:
        print("\n--- 🛠️ GESTÃO (ADMIN) ---")
        print("1. Listar Voos")
        print("2. Adicionar Voo")
        print("3. Voltar ao Menu Inicial")
        
        opcao = input("Escolha: ")
        match opcao:
            case "1":
                listar_voos_ui()
            case "2":
                adicionar_voo_ui()
            case "3":
                break
            case _:
                print("⚠️ Opção inválida no Menu Admin.")

def menu_utilizador():
    while True:
        print("\n--- ✈️ PASSAGEIRO ---")
        print("1. Consultar Painel de Voos")
        print("2. Voltar ao Menu Inicial")
        
        opcao = input("Escolha: ")
        match opcao:
            case "1":
                listar_voos_ui()
            case "2":
                break
            case _:
                print("⚠️ Opção inválida no Menu Utilizador.")

# --- PONTO DE ENTRADA PRINCIPAL ---

if __name__ == "__main__":
    inicializar_bd() 
    
    while True:
        print("\n" + "#"*25)
        print("  SISTEMA AEROPORTUÁRIO")
        print("#"*25)
        print("1. Entrar como Administrador")
        print("2. Entrar como Utilizador")
        print("3. Sair do Sistema")
        
        perfil = input("\nSelecione o perfil: ")
        
        match perfil:
            case "1":
                menu_admin()
            case "2":
                menu_utilizador()
            case "3":
                print("Encerrando... Até à próxima!")
                break
            case _:
                print("❌ Perfil não reconhecido. Tente 1, 2 ou 3.")