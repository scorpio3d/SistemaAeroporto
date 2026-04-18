from database import ler_voos, guardar_voos
from models import Voo, verificar_duplicado

# --- FUNÇÕES DE INTERAÇÃO ---

def adicionar_voo_ui():
    voos = ler_voos()
    
    while True:
        num = input("Número do Voo: ").upper().strip()
        if verificar_duplicado(num, voos):
            print(f"❌ Erro: O voo {num} já existe!")
        else:
            break

    origem = input("Origem: ").strip()
    destino = input("Destino: ").strip()
    try:
        capacidade = int(input("Capacidade de passageiros: "))
    except ValueError:
        print("Capacidade inválida. Definida para 30 por defeito.")
        capacidade = 30

    novo_voo_obj = Voo(num, origem, destino, capacidade)
    voos.append(novo_voo_obj.to_dict())
    
    guardar_voos(voos)
    print(f"\n✅ Voo {num} registado com sucesso!")

def listar_voos_ui():
    voos = ler_voos()
    if not voos:
        print("\n[!] Não existem voos no sistema.")
        return

    print("\n" + "="*30)
    print("      PAINEL DE VOOS")
    print("="*30)
    for v in voos:
        print(f"Voo: {v['numero_voo']} | {v['origem']} -> {v['destino']}")
        print(f"Estado: {v['estado']} | Lugares: {len(v['passageiros'])}/{v['capacidade']}")
        print("-" * 30)

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
        print("1. Consultar Painel")
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