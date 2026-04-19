import customtkinter as ctk
from tkinter import messagebox
from database import (
    inicializar_bd, obter_voos, adicionar_voo_db, 
    obter_aeroportos, obter_avioes, adicionar_passageiro_db, 
    obter_companhias, obter_rotas, adicionar_rota_db, 
    rota_existe, atualizar_estado_voo_db, obter_passageiros_voo
)

# Configurações de tema
ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")

class AeroportoApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        inicializar_bd()

        self.title("🌍 Sistema de Gestão Aeroportuária")
        self.geometry("1000x700")
        
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.perfil_atual = None
        self.mostrar_ecra_selecao()

    def limpar_janela(self):
        for widget in self.winfo_children():
            widget.destroy()

    # --- ECRÃ DE SELEÇÃO ---
    def mostrar_ecra_selecao(self):
        self.limpar_janela()
        frame = ctk.CTkFrame(self)
        frame.place(relx=0.5, rely=0.5, anchor="center")

        ctk.CTkLabel(frame, text="SISTEMA AEROPORTUÁRIO", font=ctk.CTkFont(size=24, weight="bold")).pack(pady=20, padx=40)
        
        ctk.CTkButton(frame, text="✈️ Entrar como Passageiro", command=lambda: self.iniciar_app("cliente"), width=250, height=45).pack(pady=10)
        ctk.CTkButton(frame, text="🛠️ Entrar como Administrador", fg_color="#d35400", hover_color="#e67e22", 
                      command=lambda: self.iniciar_app("admin"), width=250, height=45).pack(pady=10)

    def setup_passageiros(self):
        # Limpa a aba para evitar duplicados se a função for chamada novamente
        for w in self.tab_passageiros.winfo_children(): w.destroy()
        
        ctk.CTkLabel(self.tab_passageiros, text="MANIFESTO DE PASSAGEIROS", 
                     font=ctk.CTkFont(size=18, weight="bold")).pack(pady=10)
        
        # Obter lista de voos para colocar na seleção
        voos = obter_voos()
        opcoes_voos = [f"{v['numero_rota']}-{v['voo_id']} ({v['origem_sigla']}➔{v['destino_sigla']})" for v in voos]
        
        frame_selecao = ctk.CTkFrame(self.tab_passageiros, fg_color="transparent")
        frame_selecao.pack(fill="x", padx=20, pady=5)
        
        ctk.CTkLabel(frame_selecao, text="Selecione o Voo:").pack(side="left", padx=10)
        
        # Criar a ComboBox. Quando o utilizador escolhe um voo, chama a função 'listar_passageiros_gui'
        self.cb_voo_pass = ctk.CTkComboBox(frame_selecao, values=opcoes_voos, width=350, 
                                            command=self.listar_passageiros_gui)
        self.cb_voo_pass.pack(side="left", padx=10)
        
        # Área com scroll onde os nomes vão aparecer
        self.scroll_pass = ctk.CTkScrollableFrame(self.tab_passageiros, height=400)
        self.scroll_pass.pack(fill="both", expand=True, padx=20, pady=10)

    # --- INTERFACE PRINCIPAL ---
    def iniciar_app(self, perfil):
        self.limpar_janela()
        self.perfil_atual = perfil
        
        self.tab_view = ctk.CTkTabview(self)
        self.tab_view.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")
        
        # Abas comuns
        self.tab_painel = self.tab_view.add("🛫 Painel de Voos")
        self.tab_reserva = self.tab_view.add("🎟️ Reservar Bilhete")

        # Abas Admin
        if perfil == "admin":
            self.tab_rotas = self.tab_view.add("🗺️ Gestão de Rotas")
            self.tab_agendar = self.tab_view.add("➕ Agendar Voo")
            self.tab_estados = self.tab_view.add("🔄 Estados")
            self.tab_passageiros = self.tab_view.add("👥 Passageiros")
            self.setup_passageiros()
            self.setup_gestao_rotas()
            self.setup_agendar_voo()
            self.setup_gestao_estados()

        self.setup_painel_voos()
        self.setup_reservar_bilhete()

        # Botão Sair
        ctk.CTkButton(self, text="Sair", width=80, command=self.mostrar_ecra_selecao).place(relx=0.98, rely=0.02, anchor="ne")

    # --- ABA: PAINEL DE VOOS ---
    def setup_painel_voos(self):
        self.tab_painel.grid_columnconfigure(0, weight=1)
        self.tab_painel.grid_rowconfigure(2, weight=1) # O scroll fica na linha 2
        
        ctk.CTkLabel(self.tab_painel, text="MOVIMENTOS AEROPORTUÁRIOS", 
                     font=ctk.CTkFont(size=20, weight="bold")).grid(row=0, column=0, pady=10)
        
        # --- NOVO: Menu de Ordenação ---
        frame_filtros = ctk.CTkFrame(self.tab_painel, fg_color="transparent")
        frame_filtros.grid(row=1, column=0, sticky="ew", padx=20)
        
        ctk.CTkLabel(frame_filtros, text="Ordenar por:").pack(side="left", padx=10)
        
        self.menu_ordem = ctk.CTkOptionMenu(frame_filtros, 
                                            values=["Data/Hora", "Destino", "Estado", "Rota"],
                                            command=lambda _: self.atualizar_painel()) # Atualiza ao clicar
        self.menu_ordem.pack(side="left", padx=10)
        
        # Botão de refresh manual ao lado
        ctk.CTkButton(frame_filtros, text="🔄", width=40, command=self.atualizar_painel).pack(side="right", padx=10)

        # Scrollable Frame
        self.scroll_painel = ctk.CTkScrollableFrame(self.tab_painel)
        self.scroll_painel.grid(row=2, column=0, sticky="nsew", padx=10, pady=10)
        
        self.atualizar_painel()

    def atualizar_painel(self):
        # Limpar o painel antes de recarregar
        for w in self.scroll_painel.winfo_children(): 
            w.destroy()
        
        voos = obter_voos()
        criterio = self.menu_ordem.get()

        # Lógica de ordenação (mantida do passo anterior)
        if criterio == "Destino":
            voos.sort(key=lambda x: x['destino_cidade'])
        elif criterio == "Estado":
            voos.sort(key=lambda x: x['estado'])
        elif criterio == "Rota":
            voos.sort(key=lambda x: x['numero_rota'])
        else: # Ordenação por Data/Hora
            voos.sort(key=lambda x: x['data_hora'])

        for v in voos:
            f = ctk.CTkFrame(self.scroll_painel)
            f.pack(fill="x", padx=5, pady=5)
            
            codigo = f"{v['numero_rota']}-{v['voo_id']}"
            cor_estado = "orange" if v['estado'] == "Atrasado" else "green" if v['estado'] == "Concluído" else "gray"
            
            # Linha 0: Identificador do Voo e a Hora
            ctk.CTkLabel(f, text=f"VOO {codigo}", font=ctk.CTkFont(weight="bold")).grid(row=0, column=0, padx=10, sticky="w")
            ctk.CTkLabel(f, text=f"🕒 {v['data_hora']}", text_color="#3b8ed0").grid(row=0, column=1, padx=10, sticky="w")
            
            # Linha 1: Trajeto e Estado atual
            ctk.CTkLabel(f, text=f"{v['origem_cidade']} ➔ {v['destino_cidade']}").grid(row=1, column=0, padx=10, sticky="w")
            ctk.CTkLabel(f, text=v['estado'], text_color=cor_estado, font=ctk.CTkFont(weight="bold")).grid(row=1, column=1, padx=10, sticky="e")
            
            # --- LINHA CORRIGIDA (Linha 2): Avião e Lotação ---
            texto_lotacao = f"Avião: {v['aviao_modelo']} | Lotação: {v['total_passageiros']}/{v['capacidade']}"
            ctk.CTkLabel(f, text=texto_lotacao, font=ctk.CTkFont(size=11)).grid(row=2, column=0, columnspan=2, padx=10, sticky="w")
   
           # --- ABA: RESERVAR ---
    def setup_reservar_bilhete(self):
        ctk.CTkLabel(self.tab_reserva, text="RESERVA DE BILHETE", font=ctk.CTkFont(size=20, weight="bold")).pack(pady=20)
        self.ent_voo_id = ctk.CTkEntry(self.tab_reserva, placeholder_text="ID do Voo (ex: 5)", width=300); self.ent_voo_id.pack(pady=10)
        self.ent_nome_p = ctk.CTkEntry(self.tab_reserva, placeholder_text="Nome do Passageiro", width=300); self.ent_nome_p.pack(pady=10)
        ctk.CTkButton(self.tab_reserva, text="Confirmar Compra", command=self.confirmar_reserva).pack(pady=20)

    def confirmar_reserva(self):
        try:
            v_id = int(self.ent_voo_id.get())
            nome = self.ent_nome_p.get().strip()
            if not nome: raise ValueError
            
            voos = obter_voos()
            v = next((x for x in voos if x['voo_id'] == v_id), None)
            
            if v and v['total_passageiros'] < v['capacidade']:
                adicionar_passageiro_db(v_id, nome)
                messagebox.showinfo("Sucesso", "Bilhete emitido!")
                self.atualizar_painel()
            else:
                messagebox.showerror("Erro", "Voo inválido ou lotado.")
        except:
            messagebox.showwarning("Erro", "Dados inválidos.")

    # --- ABA ADMIN: GESTÃO DE ROTAS ---
    def setup_gestao_rotas(self):
        ctk.CTkLabel(self.tab_rotas, text="CRIAR TRAJETO (ROTA)", font=ctk.CTkFont(size=18, weight="bold")).pack(pady=10)
        
        self.cb_comp = ctk.CTkComboBox(self.tab_rotas, values=[f"{c['sigla']} - {c['nome']}" for c in obter_companhias()], width=300)
        self.cb_comp.pack(pady=5)
        
        self.ent_rota_num = ctk.CTkEntry(self.tab_rotas, placeholder_text="Número Rota (ex: 101)", width=300); self.ent_rota_num.pack(pady=5)
        
        aeros = [f"{a['sigla']} ({a['cidade']})" for a in obter_aeroportos()]
        self.cb_ori = ctk.CTkComboBox(self.tab_rotas, values=aeros, width=300); self.cb_ori.pack(pady=5)
        self.cb_des = ctk.CTkComboBox(self.tab_rotas, values=aeros, width=300); self.cb_des.pack(pady=5)
        
        ctk.CTkButton(self.tab_rotas, text="Criar Rota", command=self.criar_rota).pack(pady=15)

    def criar_rota(self):
        sigla_c = self.cb_comp.get().split(" - ")[0]
        num_r = self.ent_rota_num.get().strip()
        num_completo = f"{sigla_c}{num_r}"
        ori = self.cb_ori.get().split(" ")[0]
        des = self.cb_des.get().split(" ")[0]

        if ori == des: return messagebox.showerror("Erro", "Destino igual à origem.")
        if rota_existe(num_completo): return messagebox.showerror("Erro", "Rota já existe.")

        adicionar_rota_db(num_completo, sigla_c, ori, des)
        messagebox.showinfo("Sucesso", "Rota criada!")
        self.setup_agendar_voo() # Atualiza dropdown de rotas na outra aba

    # --- ABA ADMIN: AGENDAR VOO ---
    def setup_agendar_voo(self):
        for w in self.tab_agendar.winfo_children(): w.destroy()
        ctk.CTkLabel(self.tab_agendar, text="AGENDAR NOVA VIAGEM", font=ctk.CTkFont(size=18, weight="bold")).pack(pady=10)
        
        rotas_list = [f"{r['numero_rota']} ({r['origem_sigla']}➔{r['destino_sigla']})" for r in obter_rotas()]
        self.cb_rota_v = ctk.CTkComboBox(self.tab_agendar, values=rotas_list, width=350); self.cb_rota_v.pack(pady=10)
        
        avioes_list = [a['modelo'] for a in obter_avioes()]
        self.cb_aviao_v = ctk.CTkComboBox(self.tab_agendar, values=avioes_list, width=350); self.cb_aviao_v.pack(pady=10)
        
        ctk.CTkButton(self.tab_agendar, text="Agendar Voo (ID Automático)", command=self.agendar_voo).pack(pady=20)

    def agendar_voo(self):
        rota = self.cb_rota_v.get().split(" ")[0]
        aviao = self.cb_aviao_v.get()
        adicionar_voo_db(rota, aviao)
        messagebox.showinfo("Sucesso", "Voo agendado com sucesso!")
        self.atualizar_painel()

    # --- ABA ADMIN: GESTÃO DE ESTADOS ---
    def setup_gestao_estados(self):
        ctk.CTkLabel(self.tab_estados, text="ALTERAR ESTADO DO VOO", font=ctk.CTkFont(size=18, weight="bold")).pack(pady=10)
        
        self.ent_id_estado = ctk.CTkEntry(self.tab_estados, placeholder_text="ID do Voo (ex: 12)", width=200); self.ent_id_estado.pack(pady=10)
        
        self.cb_novo_est = ctk.CTkComboBox(self.tab_estados, values=["Programado", "Embarque", "Em voo", "Atrasado", "Concluído", "Cancelado"])
        self.cb_novo_est.pack(pady=10)
        
        ctk.CTkButton(self.tab_estados, text="Atualizar Estado", fg_color="green", command=self.mudar_estado).pack(pady=10)

    def mudar_estado(self):
        try:
            v_id = int(self.ent_id_estado.get())
            novo = self.cb_novo_est.get()
            atualizar_estado_voo_db(v_id, novo)
            messagebox.showinfo("OK", "Estado atualizado!")
            self.atualizar_painel()
        except:
            messagebox.showerror("Erro", "ID inválido.")
    def listar_passageiros_gui(self, _=None):
        # Limpa a lista atual de nomes antes de mostrar os novos
        for w in self.scroll_pass.winfo_children(): w.destroy()
        
        try:
            # Lógica para extrair o ID: "TP102-5 (LIS➔OPO)" -> pegamos no "5"
            texto_selecionado = self.cb_voo_pass.get()
            voo_id = int(texto_selecionado.split("-")[1].split(" ")[0])
            
            # Chama a função que criámos no database.py
            passageiros = obter_passageiros_voo(voo_id)
            
            if not passageiros:
                ctk.CTkLabel(self.scroll_pass, text="Nenhum passageiro registado neste voo.",
                             text_color="gray").pack(pady=20)
                return

            # Cria uma linha para cada passageiro
            for i, p in enumerate(passageiros, 1):
                f = ctk.CTkFrame(self.scroll_pass)
                f.pack(fill="x", padx=5, pady=2)
                ctk.CTkLabel(f, text=f"{i:02d}. {p['nome']}", 
                             font=ctk.CTkFont(size=13)).pack(side="left", padx=15, pady=5)
        except Exception as e:
            print(f"Erro ao listar: {e}")
if __name__ == "__main__":
    app = AeroportoApp()
    app.mainloop()