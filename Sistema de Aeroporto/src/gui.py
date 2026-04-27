import customtkinter as ctk
from tkinter import messagebox
import math  # <- NOVO: Necessário para arredondar o número de páginas
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
        self.geometry("1050x750")
        
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # --- VARIÁVEIS DE PAGINAÇÃO ---
        self.pagina_atual = 1
        self.voos_por_pagina = 40  # Quantidade de voos a mostrar por cada página

        self.perfil_atual = None
        self.mostrar_ecra_selecao()

    def limpar_janela(self):
        for widget in self.winfo_children():
            widget.destroy()

    # ==========================================
    # ECRÃ DE SELEÇÃO (LOGIN)
    # ==========================================
    def mostrar_ecra_selecao(self):
        self.limpar_janela()
        frame = ctk.CTkFrame(self)
        frame.place(relx=0.5, rely=0.5, anchor="center")

        ctk.CTkLabel(frame, text="SISTEMA AEROPORTUÁRIO", font=ctk.CTkFont(size=24, weight="bold")).pack(pady=20, padx=40)
        
        ctk.CTkButton(frame, text="✈️ Entrar como Passageiro", command=lambda: self.iniciar_app("cliente"), width=250, height=45).pack(pady=10)
        ctk.CTkButton(frame, text="🛠️ Entrar como Administrador", fg_color="#d35400", hover_color="#e67e22", 
                      command=lambda: self.iniciar_app("admin"), width=250, height=45).pack(pady=10)

    # ==========================================
    # INTERFACE PRINCIPAL (ABAS)
    # ==========================================
    def iniciar_app(self, perfil):
        self.limpar_janela()
        self.perfil_atual = perfil
        
        self.tab_view = ctk.CTkTabview(self)
        self.tab_view.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")
        
        self.tab_painel = self.tab_view.add("🛫 Painel de Voos")
        self.tab_reserva = self.tab_view.add("🎟️ Reservar Bilhete")

        if perfil == "admin":
            self.tab_rotas = self.tab_view.add("🗺️ Rotas")
            self.tab_agendar = self.tab_view.add("➕ Agendar")
            self.tab_estados = self.tab_view.add("🔄 Estados")
            self.tab_passageiros = self.tab_view.add("👥 Passageiros")
            self.tab_listas = self.tab_view.add("📋 Listagens Gerais")
            
            self.setup_gestao_rotas()
            self.setup_agendar_voo()
            self.setup_gestao_estados()
            self.setup_passageiros()
            self.setup_listagens_gerais()

        self.setup_painel_voos()
        self.setup_reservar_bilhete()

        ctk.CTkButton(self, text="Sair", width=80, fg_color="red", hover_color="darkred", 
                      command=self.mostrar_ecra_selecao).place(relx=0.98, rely=0.02, anchor="ne")


    # ==========================================
    # ABA 1: PAINEL DE VOOS (Com Ordenação e Paginação)
    # ==========================================
    def setup_painel_voos(self):
        self.tab_painel.grid_columnconfigure(0, weight=1)
        self.tab_painel.grid_rowconfigure(2, weight=1) # A lista de voos expande
        
        ctk.CTkLabel(self.tab_painel, text="MOVIMENTOS AEROPORTUÁRIOS", font=ctk.CTkFont(size=20, weight="bold")).grid(row=0, column=0, pady=10)
        
        # --- FILTROS ---
        frame_filtros = ctk.CTkFrame(self.tab_painel, fg_color="transparent")
        frame_filtros.grid(row=1, column=0, sticky="ew", padx=20)
        
        ctk.CTkLabel(frame_filtros, text="Ordenar por:").pack(side="left", padx=10)
        
        self.menu_ordem = ctk.CTkOptionMenu(frame_filtros, values=["Data/Hora", "Destino", "Estado", "Rota"], command=self.mudou_ordenacao) 
        self.menu_ordem.pack(side="left", padx=10)
        
        ctk.CTkButton(frame_filtros, text="🔄 Atualizar", width=100, command=self.mudou_ordenacao).pack(side="right", padx=10)

        # --- ÁREA DOS VOOS ---
        self.scroll_painel = ctk.CTkScrollableFrame(self.tab_painel)
        self.scroll_painel.grid(row=2, column=0, sticky="nsew", padx=10, pady=10)
        
        # --- CONTROLOS DE PAGINAÇÃO ---
        self.frame_paginacao = ctk.CTkFrame(self.tab_painel, fg_color="transparent")
        self.frame_paginacao.grid(row=3, column=0, pady=10)
        
        self.btn_ant = ctk.CTkButton(self.frame_paginacao, text="⬅️ Anterior", width=100, command=self.pagina_anterior)
        self.btn_ant.pack(side="left", padx=10)
        
        self.lbl_paginacao = ctk.CTkLabel(self.frame_paginacao, text="Página 1 de 1", font=ctk.CTkFont(weight="bold"))
        self.lbl_paginacao.pack(side="left", padx=20)
        
        self.btn_prox = ctk.CTkButton(self.frame_paginacao, text="Próxima ➡️", width=100, command=self.pagina_seguinte)
        self.btn_prox.pack(side="left", padx=10)

        self.atualizar_painel()

    # Se a ordenação mudar, voltamos à página 1
    def mudou_ordenacao(self, _=None):
        self.pagina_atual = 1
        self.atualizar_painel()

    def pagina_anterior(self):
        if self.pagina_atual > 1:
            self.pagina_atual -= 1
            self.atualizar_painel()

    def pagina_seguinte(self):
        self.pagina_atual += 1
        self.atualizar_painel()

    def atualizar_painel(self):
        for w in self.scroll_painel.winfo_children(): 
            w.destroy()
        
        voos = obter_voos()
        criterio = self.menu_ordem.get()

        # Ordenar (rápido na memória)
        if criterio == "Destino": voos.sort(key=lambda x: x['destino_cidade'])
        elif criterio == "Estado": voos.sort(key=lambda x: x['estado'])
        elif criterio == "Rota": voos.sort(key=lambda x: x['numero_rota'])
        else: voos.sort(key=lambda x: x['data_hora'])

        if not voos:
            ctk.CTkLabel(self.scroll_painel, text="Não existem voos agendados.", text_color="gray").pack(pady=20)
            self.lbl_paginacao.configure(text="Página 0 de 0")
            self.btn_ant.configure(state="disabled")
            self.btn_prox.configure(state="disabled")
            return

        # LÓGICA DE PAGINAÇÃO MATEMÁTICA
        total_voos = len(voos)
        total_paginas = math.ceil(total_voos / self.voos_por_pagina)
        
        # Evitar erros se houver menos voos do que a página onde estamos
        if self.pagina_atual > total_paginas:
            self.pagina_atual = total_paginas

        # Cortar a lista para pegar só na fatia que queremos
        inicio = (self.pagina_atual - 1) * self.voos_por_pagina
        fim = inicio + self.voos_por_pagina
        voos_da_pagina = voos[inicio:fim]

        # Atualizar a UI com os controlos dos botões
        self.lbl_paginacao.configure(text=f"Página {self.pagina_atual} de {total_paginas} (Total: {total_voos})")
        self.btn_ant.configure(state="normal" if self.pagina_atual > 1 else "disabled")
        self.btn_prox.configure(state="normal" if self.pagina_atual < total_paginas else "disabled")

        # Desenhar apenas os voos desta página
        for v in voos_da_pagina:
            f = ctk.CTkFrame(self.scroll_painel)
            f.pack(fill="x", padx=5, pady=5)
            
            codigo = f"{v['numero_rota']}-{v['voo_id']}"
            cor_estado = "orange" if v['estado'] == "Atrasado" else "green" if v['estado'] == "Concluído" else "gray"
            
            ctk.CTkLabel(f, text=f"VOO {codigo}", font=ctk.CTkFont(weight="bold")).grid(row=0, column=0, padx=10, sticky="w")
            ctk.CTkLabel(f, text=f"🕒 {v['data_hora']}", text_color="#3b8ed0").grid(row=0, column=1, padx=10, sticky="w")
            
            ctk.CTkLabel(f, text=f"{v['origem_cidade']} ➔ {v['destino_cidade']}").grid(row=1, column=0, padx=10, sticky="w")
            ctk.CTkLabel(f, text=v['estado'], text_color=cor_estado, font=ctk.CTkFont(weight="bold")).grid(row=1, column=1, padx=10, sticky="e")
            
            total_pass = v.get('total_passageiros', 0)
            cap = v.get('capacidade', 0)
            ctk.CTkLabel(f, text=f"Avião: {v['aviao_modelo']} | Lotação: {total_pass}/{cap}", font=ctk.CTkFont(size=11)).grid(row=2, column=0, columnspan=2, padx=10, sticky="w")

    # ==========================================
    # ABA 2: RESERVAR BILHETE (Pesquisa por Aeroportos)
    # ==========================================
    def setup_reservar_bilhete(self):
        for w in self.tab_reserva.winfo_children(): w.destroy()

        ctk.CTkLabel(self.tab_reserva, text="RESERVA DE BILHETES", font=ctk.CTkFont(size=20, weight="bold")).pack(pady=10)

        # --- PARTE 1: PESQUISAR ---
        frame_pesquisa = ctk.CTkFrame(self.tab_reserva)
        frame_pesquisa.pack(fill="x", padx=20, pady=10)

        ctk.CTkLabel(frame_pesquisa, text="1. Onde quer ir e quantos bilhetes precisa?", font=ctk.CTkFont(weight="bold")).pack(pady=5)

        aeros = [f"{a['sigla']} ({a['cidade']})" for a in obter_aeroportos()]
        
        frame_locais = ctk.CTkFrame(frame_pesquisa, fg_color="transparent")
        frame_locais.pack(pady=5)
        
        self.cb_origem_reserva = ctk.CTkComboBox(frame_locais, values=aeros if aeros else ["Nenhum"], width=170)
        self.cb_origem_reserva.pack(side="left", padx=5)
        
        ctk.CTkLabel(frame_locais, text="➔").pack(side="left", padx=5)
        
        self.cb_destino_reserva = ctk.CTkComboBox(frame_locais, values=aeros if aeros else ["Nenhum"], width=170)
        self.cb_destino_reserva.pack(side="left", padx=5)

        self.ent_qtd_bilhetes = ctk.CTkEntry(frame_pesquisa, placeholder_text="Quantidade de Bilhetes (ex: 2)", width=370)
        self.ent_qtd_bilhetes.pack(pady=10)

        ctk.CTkButton(frame_pesquisa, text="🔍 Procurar Voos", command=self.filtrar_voos_reserva).pack(pady=10)

        # --- PARTE 2: COMPRAR ---
        frame_compra = ctk.CTkFrame(self.tab_reserva)
        frame_compra.pack(fill="x", padx=20, pady=10)

        ctk.CTkLabel(frame_compra, text="2. Selecionar Voo e Inserir Nomes", font=ctk.CTkFont(weight="bold")).pack(pady=5)

        self.cb_voo_filtrado = ctk.CTkComboBox(frame_compra, values=["Faça a pesquisa primeiro..."], width=400)
        self.cb_voo_filtrado.pack(pady=5)

        self.ent_nomes_p = ctk.CTkEntry(frame_compra, placeholder_text="Nome(s) separado(s) por vírgula", width=400)
        self.ent_nomes_p.pack(pady=5)

        ctk.CTkButton(frame_compra, text="Confirmar Compra", fg_color="green", hover_color="darkgreen", command=self.confirmar_reserva).pack(pady=15)

    def filtrar_voos_reserva(self):
        try:
            origem = self.cb_origem_reserva.get().split(" ")[0]
            destino = self.cb_destino_reserva.get().split(" ")[0]
            
            if origem == "Nenhum" or destino == "Nenhum": return
                
            if origem == destino:
                messagebox.showwarning("Aviso", "A origem e o destino não podem ser iguais.")
                return

            qtd_str = self.ent_qtd_bilhetes.get().strip()
            if not qtd_str.isdigit() or int(qtd_str) <= 0:
                messagebox.showwarning("Aviso", "Por favor, introduza uma quantidade válida (número maior que 0).")
                return

            quantidade_pedida = int(qtd_str)
            voos = obter_voos()
            voos_disponiveis = []

            for v in voos:
                lugares_livres = v.get('capacidade', 0) - v.get('total_passageiros', 0)
                
                if (v['origem_sigla'] == origem and 
                    v['destino_sigla'] == destino and 
                    lugares_livres >= quantidade_pedida and 
                    v['estado'] not in ["Cancelado", "Concluído"]):
                    
                    voos_disponiveis.append(f"ID: {v['voo_id']} | Data: {v['data_hora']} | Livres: {lugares_livres}")

            if not voos_disponiveis:
                self.cb_voo_filtrado.configure(values=["Nenhum voo cumpre os requisitos."])
                self.cb_voo_filtrado.set("Nenhum voo cumpre os requisitos.")
                messagebox.showinfo("Pesquisa", f"Não existem voos de {origem} para {destino} com {quantidade_pedida} lugares livres neste momento.")
            else:
                self.cb_voo_filtrado.configure(values=voos_disponiveis)
                self.cb_voo_filtrado.set(voos_disponiveis[0])

        except Exception as e:
            messagebox.showerror("Erro", f"Erro na pesquisa: {e}")

    def confirmar_reserva(self):
        try:
            voo_str = self.cb_voo_filtrado.get()
            if "ID:" not in voo_str:
                messagebox.showwarning("Aviso", "Por favor, procure e selecione um voo válido primeiro.")
                return
            
            v_id = int(voo_str.split("|")[0].replace("ID:", "").strip())
            qtd_pedida = int(self.ent_qtd_bilhetes.get().strip())
            nomes_input = self.ent_nomes_p.get().strip()
            
            if not nomes_input:
                messagebox.showwarning("Aviso", "Tem de introduzir os nomes dos passageiros.")
                return
                
            lista_nomes = [nome.strip() for nome in nomes_input.split(",") if nome.strip()]
            
            if len(lista_nomes) != qtd_pedida:
                messagebox.showerror("Erro", f"Pediu {qtd_pedida} bilhete(s) na pesquisa, mas introduziu {len(lista_nomes)} nome(s). Verifique as vírgulas.")
                return
            
            voos = obter_voos()
            v_escolhido = next((x for x in voos if x['voo_id'] == v_id), None)
            lugares_livres = v_escolhido.get('capacidade', 0) - v_escolhido.get('total_passageiros', 0)
            
            if qtd_pedida <= lugares_livres:
                for nome in lista_nomes:
                    adicionar_passageiro_db(v_id, nome)
                
                messagebox.showinfo("Sucesso", f"✅ {qtd_pedida} Bilhete(s) emitido(s) com sucesso para o Voo {v_id}!")
                
                self.ent_nomes_p.delete(0, 'end')
                self.ent_qtd_bilhetes.delete(0, 'end')
                self.cb_voo_filtrado.configure(values=["Faça a pesquisa primeiro..."])
                self.cb_voo_filtrado.set("Faça a pesquisa primeiro...")
                
                self.atualizar_painel()
            else:
                messagebox.showerror("Erro", "Pedimos desculpa, mas a lotação do voo esgotou-se entretanto.")
                
        except Exception as e:
            messagebox.showerror("Erro", f"Ocorreu um erro na compra: {e}")

    # ==========================================
    # ABA 3 (ADMIN): GESTÃO DE ROTAS
    # ==========================================
    def setup_gestao_rotas(self):
        ctk.CTkLabel(self.tab_rotas, text="CRIAR TRAJETO (ROTA)", font=ctk.CTkFont(size=18, weight="bold")).pack(pady=10)
        
        self.cb_comp = ctk.CTkComboBox(self.tab_rotas, values=[f"{c['sigla']} - {c['nome']}" for c in obter_companhias()], width=300)
        self.cb_comp.pack(pady=5)
        
        self.ent_rota_num = ctk.CTkEntry(self.tab_rotas, placeholder_text="Número Rota (ex: 102)", width=300)
        self.ent_rota_num.pack(pady=5)
        
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

        if ori == des: 
            return messagebox.showerror("Erro", "Origem e destino não podem ser iguais.")
        if rota_existe(num_completo): 
            return messagebox.showerror("Erro", "Esta rota já existe no sistema.")

        adicionar_rota_db(num_completo, sigla_c, ori, des)
        messagebox.showinfo("Sucesso", f"Rota {num_completo} criada!")
        self.setup_agendar_voo()
        self.setup_reservar_bilhete()

    # ==========================================
    # ABA 4 (ADMIN): AGENDAR VOO
    # ==========================================
    def setup_agendar_voo(self):
        for w in self.tab_agendar.winfo_children(): w.destroy()
        ctk.CTkLabel(self.tab_agendar, text="AGENDAR NOVA VIAGEM", font=ctk.CTkFont(size=18, weight="bold")).pack(pady=10)
        
        rotas_list = [f"{r['numero_rota']} ({r['origem_sigla']}➔{r['destino_sigla']})" for r in obter_rotas()]
        self.cb_rota_v = ctk.CTkComboBox(self.tab_agendar, values=rotas_list if rotas_list else ["Nenhuma rota"], width=350)
        self.cb_rota_v.pack(pady=10)
        
        avioes_list = [a['modelo'] for a in obter_avioes()]
        self.cb_aviao_v = ctk.CTkComboBox(self.tab_agendar, values=avioes_list if avioes_list else ["Nenhum avião"], width=350)
        self.cb_aviao_v.pack(pady=10)
        
        self.ent_data_hora = ctk.CTkEntry(self.tab_agendar, placeholder_text="Data e Hora (AAAA-MM-DD HH:MM)", width=350)
        self.ent_data_hora.pack(pady=10)
        
        ctk.CTkButton(self.tab_agendar, text="Agendar Voo", command=self.agendar_voo).pack(pady=20)

    def agendar_voo(self):
        try:
            rota = self.cb_rota_v.get().split(" ")[0]
            if rota == "Nenhuma": return
            
            aviao = self.cb_aviao_v.get()
            data_hora = self.ent_data_hora.get().strip() or "2026-01-01 00:00"
            
            adicionar_voo_db(rota, aviao, data_hora)
            messagebox.showinfo("Sucesso", f"Voo agendado com sucesso para {data_hora}!")
            self.atualizar_painel()
            self.ent_data_hora.delete(0, "end")
            self.setup_passageiros() 
        except Exception as e:
            messagebox.showerror("Erro", "Verifique os dados.")

    # ==========================================
    # ABA 5 (ADMIN): ESTADOS
    # ==========================================
    def setup_gestao_estados(self):
        ctk.CTkLabel(self.tab_estados, text="ALTERAR ESTADO DO VOO", font=ctk.CTkFont(size=18, weight="bold")).pack(pady=10)
        self.ent_id_estado = ctk.CTkEntry(self.tab_estados, placeholder_text="ID Interno do Voo", width=250)
        self.ent_id_estado.pack(pady=10)
        self.cb_novo_est = ctk.CTkComboBox(self.tab_estados, width=250, values=["Programado", "Embarque", "Em voo", "Atrasado", "Concluído", "Cancelado"])
        self.cb_novo_est.pack(pady=10)
        ctk.CTkButton(self.tab_estados, text="Atualizar Estado", fg_color="green", hover_color="darkgreen", command=self.mudar_estado).pack(pady=10)

    def mudar_estado(self):
        try:
            v_id = int(self.ent_id_estado.get())
            novo = self.cb_novo_est.get()
            atualizar_estado_voo_db(v_id, novo)
            messagebox.showinfo("OK", f"Estado alterado para '{novo}'.")
            self.ent_id_estado.delete(0, 'end')
            self.atualizar_painel()
        except ValueError:
            messagebox.showerror("Erro", "ID inválido.")

    # ==========================================
    # ABA 6 (ADMIN): PASSAGEIROS
    # ==========================================
    def setup_passageiros(self):
        for w in self.tab_passageiros.winfo_children(): w.destroy()
        ctk.CTkLabel(self.tab_passageiros, text="MANIFESTO DE PASSAGEIROS", font=ctk.CTkFont(size=18, weight="bold")).pack(pady=10)
        
        voos = obter_voos()
        opcoes_voos = [f"{v['numero_rota']}-{v['voo_id']} ({v['origem_sigla']}➔{v['destino_sigla']})" for v in voos]
        
        frame_selecao = ctk.CTkFrame(self.tab_passageiros, fg_color="transparent")
        frame_selecao.pack(fill="x", padx=20, pady=5)
        ctk.CTkLabel(frame_selecao, text="Selecione o Voo:").pack(side="left", padx=10)
        
        self.cb_voo_pass = ctk.CTkComboBox(frame_selecao, values=opcoes_voos if opcoes_voos else ["Nenhum voo"], width=350, command=self.listar_passageiros_gui)
        self.cb_voo_pass.pack(side="left", padx=10)
        
        self.scroll_pass = ctk.CTkScrollableFrame(self.tab_passageiros, height=400)
        self.scroll_pass.pack(fill="both", expand=True, padx=20, pady=10)

    def listar_passageiros_gui(self, _=None):
        for w in self.scroll_pass.winfo_children(): w.destroy()
        try:
            texto_selecionado = self.cb_voo_pass.get()
            if "Nenhum" in texto_selecionado: return
            voo_id = int(texto_selecionado.split("-")[1].split(" ")[0])
            passageiros = obter_passageiros_voo(voo_id)
            
            if not passageiros:
                ctk.CTkLabel(self.scroll_pass, text="Nenhum passageiro registado.", text_color="gray").pack(pady=20)
                return

            for i, p in enumerate(passageiros, 1):
                f = ctk.CTkFrame(self.scroll_pass)
                f.pack(fill="x", padx=5, pady=2)
                ctk.CTkLabel(f, text=f"{i:02d}. {p['nome']}", font=ctk.CTkFont(size=13)).pack(side="left", padx=15, pady=5)
        except Exception:
            pass

    # ==========================================
    # ABA 7 (ADMIN): LISTAGENS GERAIS
    # ==========================================
    def setup_listagens_gerais(self):
        ctk.CTkLabel(self.tab_listas, text="CONSULTA DE DADOS DO SISTEMA", font=ctk.CTkFont(size=18, weight="bold")).pack(pady=10)
        
        frame_botoes = ctk.CTkFrame(self.tab_listas, fg_color="transparent")
        frame_botoes.pack(pady=5)

        ctk.CTkButton(frame_botoes, text="🗺️ Ver Rotas", command=lambda: self.mostrar_lista("Rotas")).pack(side="left", padx=5)
        ctk.CTkButton(frame_botoes, text="✈️ Ver Aviões", command=lambda: self.mostrar_lista("Aviões")).pack(side="left", padx=5)
        ctk.CTkButton(frame_botoes, text="🏢 Ver Companhias", command=lambda: self.mostrar_lista("Companhias")).pack(side="left", padx=5)
        
        self.txt_listas = ctk.CTkTextbox(self.tab_listas, width=800, height=400, font=ctk.CTkFont(family="Consolas", size=13))
        self.txt_listas.pack(pady=20)

    def mostrar_lista(self, tipo):
        self.txt_listas.delete("1.0", "end")
        texto = f"--- {tipo.upper()} REGISTADAS ---\n\n"
        
        if tipo == "Rotas":
            for r in obter_rotas(): texto += f"[{r['numero_rota']}] {r['companhia_nome']} | {r['origem_cidade']} ➔ {r['destino_cidade']}\n"
        elif tipo == "Aviões":
            for a in obter_avioes(): texto += f"Modelo: {a['modelo']} | Capacidade: {a['capacidade']} lugares\n"
        elif tipo == "Companhias":
            for c in obter_companhias(): texto += f"{c['sigla']} - {c['nome']}\n"
        
        if texto.count('\n') == 2: 
            texto += "Nenhum registo encontrado."
            
        self.txt_listas.insert("1.0", texto)

if __name__ == "__main__":
    app = AeroportoApp()
    app.mainloop()