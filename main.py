import psycopg2
import customtkinter as ctk

# Configurações globais de tema institucional
ctk.set_appearance_mode("Light") 
ctk.set_default_color_theme("dark-blue")

class SistemaAcademico(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Portal Acadêmico - Pesquisa e Extensão")
        self.geometry("1100x750")
        self.configure(fg_color="#F0F2F5") # Fundo cinza bem claro (estilo web)
        
        # Conexão com o banco (Ajuste com seus dados)
        try:
            self.conn = psycopg2.connect(
                dbname="projeto_main",
                user="usuario",
                password="teste123",
                host="localhost"
            )
            self.cur = self.conn.cursor()
        except Exception as e:
            print("Erro de conexão:", e)

        # Configuração do Grid
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # ================= FRAME LATERAL (MENU INSTITUCIONAL) =================
        self.sidebar_frame = ctk.CTkFrame(self, width=250, corner_radius=0, fg_color="#003366")
        self.sidebar_frame.grid(row=0, column=0, sticky="nsew")
        self.sidebar_frame.grid_rowconfigure(10, weight=1)

        self.logo_label = ctk.CTkLabel(
            self.sidebar_frame, 
            text="SIGA\n Grupo 9", 
            font=ctk.CTkFont(family="Segoe UI", size=24, weight="bold"),
            text_color="white"
        )
        self.logo_label.grid(row=0, column=0, padx=20, pady=(30, 30))

        # Estilo dos botões do menu
        botoes = [
            ("Cadastrar Aluno", self.mostrar_cadastrar_aluno),
            ("Listar Alunos", self.mostrar_listar_alunos),
            ("Listar Projetos", self.mostrar_listar_projetos),
            ("Projetos do Aluno", self.mostrar_projetos_aluno),
            ("Orientador do Projeto", self.mostrar_orientador_projeto),
            ("Cadastrar Projeto", self.mostrar_cadastrar_projeto),
            ("Busca Científica (GIN)", self.mostrar_busca),
            ("Dashboard Gerencial", self.mostrar_dashboard)
        ]

        for i, (texto, comando) in enumerate(botoes, start=1):
            btn = ctk.CTkButton(
                self.sidebar_frame, 
                text=texto, 
                command=comando, 
                anchor="w",
                fg_color="transparent",
                text_color="white",
                hover_color="#004080",
                font=ctk.CTkFont(family="Segoe UI", size=15)
            )
            btn.grid(row=i, column=0, padx=10, pady=5, sticky="ew")

        # ================= FRAME PRINCIPAL (CONTEÚDO) =================
        self.main_frame = ctk.CTkFrame(self, corner_radius=15, fg_color="#F0F2F5")
        self.main_frame.grid(row=0, column=1, padx=20, pady=20, sticky="nsew")
        
        # Inicia mostrando o dashboard
        self.mostrar_dashboard()

    def limpar_main_frame(self):
        for widget in self.main_frame.winfo_children():
            widget.destroy()

    def limpar_container(self, container):
        for widget in container.winfo_children():
            widget.destroy()

    # ================= MÉTODOS DE INTERFACE E BANCO =================

    def mostrar_cadastrar_aluno(self):
        self.limpar_main_frame()
        conteudo = ctk.CTkScrollableFrame(self.main_frame, fg_color="white", corner_radius=15)
        conteudo.pack(fill="both", expand=True)

        ctk.CTkLabel(conteudo, text="Cadastrar Novo Aluno", font=ctk.CTkFont(family="Segoe UI", size=26, weight="bold"), text_color="#333333").pack(pady=(20, 30))

        self.ent_cpf = ctk.CTkEntry(conteudo, placeholder_text="CPF (11 dígitos)", width=350, height=40)
        self.ent_cpf.pack(pady=10)
        self.ent_nome = ctk.CTkEntry(conteudo, placeholder_text="Nome Completo", width=350, height=40)
        self.ent_nome.pack(pady=10)
        self.ent_email = ctk.CTkEntry(conteudo, placeholder_text="E-mail Institucional", width=350, height=40)
        self.ent_email.pack(pady=10)
        self.ent_telefone = ctk.CTkEntry(conteudo, placeholder_text="Telefone", width=350, height=40)
        self.ent_telefone.pack(pady=10)
        self.ent_ra = ctk.CTkEntry(conteudo, placeholder_text="RA", width=350, height=40)
        self.ent_ra.pack(pady=10)
        self.ent_ira = ctk.CTkEntry(conteudo, placeholder_text="IRA (0 a 20000)", width=350, height=40)
        self.ent_ira.pack(pady=10)

        self.lbl_msg_aluno = ctk.CTkLabel(conteudo, text="", font=ctk.CTkFont(size=14))
        self.lbl_msg_aluno.pack(pady=10)

        ctk.CTkButton(conteudo, text="Salvar Registro", command=self.executar_cadastro_aluno, width=200, height=40, font=ctk.CTkFont(weight="bold")).pack(pady=20)

    def executar_cadastro_aluno(self):
        try:
            cpf, nome = self.ent_cpf.get(), self.ent_nome.get()
            email, telefone = self.ent_email.get(), self.ent_telefone.get()
            ra, ira = self.ent_ra.get(), int(self.ent_ira.get())

            self.cur.execute("INSERT INTO Pessoa (cpf, nome, email, telefone) VALUES (%s, %s, %s, %s)", (cpf, nome, email, telefone))
            self.cur.execute("INSERT INTO Aluno (ra, cpf_aluno, ira) VALUES (%s, %s, %s)", (ra, cpf, ira))
            self.conn.commit()
            self.lbl_msg_aluno.configure(text="✔ Aluno cadastrado com sucesso no sistema.", text_color="#28a745")
        except Exception as e:
            self.conn.rollback()
            self.lbl_msg_aluno.configure(text=f"✖ Erro ao salvar: {e}", text_color="#dc3545")

    def mostrar_listar_alunos(self):
        self.limpar_main_frame()
        ctk.CTkLabel(self.main_frame, text="Relação de Alunos Matriculados", font=ctk.CTkFont(family="Segoe UI", size=26, weight="bold"), text_color="#333333").pack(pady=(10, 10))
        
        container = ctk.CTkScrollableFrame(self.main_frame, fg_color="transparent")
        container.pack(fill="both", expand=True, padx=20, pady=10)
        
        try:
            self.cur.execute("SELECT a.ra, p.nome, p.email, a.ira FROM Aluno a JOIN Pessoa p ON a.cpf_aluno = p.cpf ORDER BY p.nome")
            resultados = self.cur.fetchall()
            
            for a in resultados:
                # Criando um Card para cada aluno
                card = ctk.CTkFrame(container, fg_color="white", border_width=1, border_color="#DDDDDD", corner_radius=8)
                card.pack(fill="x", pady=6, padx=10)
                
                ctk.CTkLabel(card, text=a[1], font=ctk.CTkFont(family="Segoe UI", size=17, weight="bold"), text_color="#003366").pack(anchor="w", padx=15, pady=(10, 0))
                ctk.CTkLabel(card, text=f"RA: {a[0]}   |   E-mail: {a[2]}   |   IRA: {a[3]}", font=ctk.CTkFont(family="Segoe UI", size=14), text_color="#555555").pack(anchor="w", padx=15, pady=(2, 10))
        except Exception as e:
            ctk.CTkLabel(container, text=f"Erro: {e}", text_color="red").pack()

    def mostrar_listar_projetos(self):
        self.limpar_main_frame()
        ctk.CTkLabel(self.main_frame, text="Catálogo de Projetos (Pesquisa e Extensão)", font=ctk.CTkFont(family="Segoe UI", size=26, weight="bold"), text_color="#333333").pack(pady=(10, 10))
        
        container = ctk.CTkScrollableFrame(self.main_frame, fg_color="transparent")
        container.pack(fill="both", expand=True, padx=20, pady=10)
        
        try:
            self.cur.execute("SELECT id_projeto, titulo, tipo, data_ini, data_fim FROM Projeto ORDER BY id_projeto")
            for p in self.cur.fetchall():
                # Card de Projeto
                card = ctk.CTkFrame(container, fg_color="white", border_width=1, border_color="#DDDDDD", corner_radius=8)
                card.pack(fill="x", pady=6, padx=10)
                
                ctk.CTkLabel(card, text=p[1], font=ctk.CTkFont(family="Segoe UI", size=16, weight="bold"), text_color="#003366").pack(anchor="w", padx=15, pady=(10, 0))
                ctk.CTkLabel(card, text=f"ID: {p[0]}   |   Modalidade: {p[2]}   |   Vigência: {p[3]} a {p[4]}", font=ctk.CTkFont(family="Segoe UI", size=14), text_color="#555555").pack(anchor="w", padx=15, pady=(2, 10))
        except Exception as e:
            ctk.CTkLabel(container, text=f"Erro: {e}", text_color="red").pack()

    def mostrar_projetos_aluno(self):
        self.limpar_main_frame()
        ctk.CTkLabel(self.main_frame, text="Histórico de Vínculo do Discente", font=ctk.CTkFont(family="Segoe UI", size=26, weight="bold"), text_color="#333333").pack(pady=(10, 10))

        busca_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        busca_frame.pack(pady=10)

        self.ent_busca_ra = ctk.CTkEntry(busca_frame, placeholder_text="Insira o RA do Discente", width=350, height=40)
        self.ent_busca_ra.pack(side="left", padx=10)
        ctk.CTkButton(busca_frame, text="Consultar Vínculos", command=self.executar_projetos_aluno, height=40, font=ctk.CTkFont(weight="bold")).pack(side="left")

        self.container_projetos_aluno = ctk.CTkScrollableFrame(self.main_frame, fg_color="transparent")
        self.container_projetos_aluno.pack(fill="both", expand=True, padx=20, pady=10)

    def executar_projetos_aluno(self):
        ra = self.ent_busca_ra.get()
        self.limpar_container(self.container_projetos_aluno)

        try:
            self.cur.execute("""
                SELECT p.id_projeto, p.titulo, p.tipo 
                FROM Projeto p JOIN Participa pa ON p.id_projeto = pa.id_projeto 
                WHERE pa.ra = %s ORDER BY p.titulo
            """, (ra,))
            resultados = self.cur.fetchall()
            
            if not resultados:
                ctk.CTkLabel(self.container_projetos_aluno, text="Nenhum vínculo ativo ou histórico encontrado para este RA.", text_color="#555555").pack(pady=20)
            else:
                for p in resultados:
                    card = ctk.CTkFrame(self.container_projetos_aluno, fg_color="white", border_width=1, border_color="#DDDDDD", corner_radius=8)
                    card.pack(fill="x", pady=5, padx=10)
                    ctk.CTkLabel(card, text=p[1], font=ctk.CTkFont(family="Segoe UI", size=16, weight="bold"), text_color="#003366").pack(anchor="w", padx=15, pady=(10, 0))
                    ctk.CTkLabel(card, text=f"ID: {p[0]}   |   Modalidade: {p[2]}", font=ctk.CTkFont(family="Segoe UI", size=14), text_color="#555555").pack(anchor="w", padx=15, pady=(2, 10))
        except Exception as e:
            ctk.CTkLabel(self.container_projetos_aluno, text=f"Erro: {e}", text_color="red").pack()

    def mostrar_orientador_projeto(self):
        self.limpar_main_frame()
        ctk.CTkLabel(self.main_frame, text="Consulta de Coordenação de Projeto", font=ctk.CTkFont(family="Segoe UI", size=26, weight="bold"), text_color="#333333").pack(pady=(10, 10))

        busca_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        busca_frame.pack(pady=10)

        self.ent_busca_id_proj = ctk.CTkEntry(busca_frame, placeholder_text="Insira o ID do Projeto", width=350, height=40)
        self.ent_busca_id_proj.pack(side="left", padx=10)
        ctk.CTkButton(busca_frame, text="Consultar Docente", command=self.executar_orientador_projeto, height=40, font=ctk.CTkFont(weight="bold")).pack(side="left")

        self.container_orientador = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        self.container_orientador.pack(fill="both", expand=True, padx=20, pady=20)

    def executar_orientador_projeto(self):
        id_proj = self.ent_busca_id_proj.get()
        self.limpar_container(self.container_orientador)

        try:
            self.cur.execute("""
                SELECT pe.nome, pr.departamento, pr.n_lattes 
                FROM Professor pr JOIN Pessoa pe ON pr.cpf_professor = pe.cpf
                JOIN Orienta o ON pr.cod_func = o.cod_func WHERE o.id_projeto = %s
            """, (id_proj,))
            resultados = self.cur.fetchall()
            
            if not resultados:
                ctk.CTkLabel(self.container_orientador, text="Projeto sem docente vinculado ou ID inválido na base.", text_color="#555555").pack(pady=20)
            else:
                for prof in resultados:
                    card = ctk.CTkFrame(self.container_orientador, fg_color="white", border_width=1, border_color="#DDDDDD", corner_radius=10)
                    card.pack(fill="x", pady=5, padx=20)
                    ctk.CTkLabel(card, text=f"Prof(a). {prof[0]}", font=ctk.CTkFont(family="Segoe UI", size=18, weight="bold"), text_color="#003366").pack(anchor="w", padx=20, pady=(15, 0))
                    ctk.CTkLabel(card, text=f"Departamento: {prof[1]}   |   Lattes: {prof[2]}", font=ctk.CTkFont(family="Segoe UI", size=15), text_color="#555555").pack(anchor="w", padx=20, pady=(5, 15))
        except Exception as e:
            ctk.CTkLabel(self.container_orientador, text=f"Erro: {e}", text_color="red").pack()

    def mostrar_cadastrar_projeto(self):
        self.limpar_main_frame()
        conteudo = ctk.CTkScrollableFrame(self.main_frame, fg_color="white", corner_radius=15)
        conteudo.pack(fill="both", expand=True)

        ctk.CTkLabel(conteudo, text="Submissão de Novo Projeto", font=ctk.CTkFont(family="Segoe UI", size=26, weight="bold"), text_color="#333333").pack(pady=(20, 20))

        self.ent_id_proj = ctk.CTkEntry(conteudo, placeholder_text="ID do Projeto", width=350, height=40)
        self.ent_id_proj.pack(pady=5)
        
        self.ent_titulo_proj = ctk.CTkEntry(conteudo, placeholder_text="Título do Projeto", width=350, height=40)
        self.ent_titulo_proj.pack(pady=5)
        
        self.combo_tipo = ctk.CTkComboBox(conteudo, values=["Pesquisa", "Extensao"], width=350, height=40)
        self.combo_tipo.set("Pesquisa")
        self.combo_tipo.pack(pady=5)
        
        self.ent_data_ini = ctk.CTkEntry(conteudo, placeholder_text="Data de Início (AAAA-MM-DD)", width=350, height=40)
        self.ent_data_ini.pack(pady=5)
        
        self.ent_data_fim = ctk.CTkEntry(conteudo, placeholder_text="Data de Término (AAAA-MM-DD)", width=350, height=40)
        self.ent_data_fim.pack(pady=5)
        
        self.ent_id_edital = ctk.CTkEntry(conteudo, placeholder_text="ID do Edital Vinculado", width=350, height=40)
        self.ent_id_edital.pack(pady=5)

        self.txt_resumo = ctk.CTkTextbox(conteudo, width=500, height=120, border_width=1, border_color="#DDDDDD", fg_color="#F8F9FA", text_color="black")
        self.txt_resumo.insert("0.0", "Insira o resumo do projeto aqui...")
        self.txt_resumo.pack(pady=15)

        self.lbl_msg_proj = ctk.CTkLabel(conteudo, text="", font=ctk.CTkFont(size=14))
        self.lbl_msg_proj.pack(pady=5)

        ctk.CTkButton(conteudo, text="Submeter Projeto", command=self.executar_cadastro_projeto, width=200, height=40, font=ctk.CTkFont(weight="bold")).pack(pady=10)

    def executar_cadastro_projeto(self):
        try:
            id_proj = int(self.ent_id_proj.get())
            titulo = self.ent_titulo_proj.get()
            tipo = self.combo_tipo.get()
            dt_ini = self.ent_data_ini.get()
            dt_fim = self.ent_data_fim.get()
            id_edital = int(self.ent_id_edital.get())
            resumo = self.txt_resumo.get("0.0", "end").strip()

            self.cur.execute("""
                INSERT INTO Projeto (id_projeto, titulo, tipo, resumo, data_ini, data_fim, id_edital)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, (id_proj, titulo, tipo, resumo, dt_ini, dt_fim, id_edital))
            
            self.conn.commit()
            self.lbl_msg_proj.configure(text="✔ Projeto submetido com sucesso!", text_color="#28a745")
        except Exception as e:
            self.conn.rollback()
            self.lbl_msg_proj.configure(text=f"✖ Erro ao salvar: {e}", text_color="#dc3545")

    def mostrar_busca(self):
        self.limpar_main_frame()
        ctk.CTkLabel(self.main_frame, text="Repositório Institucional (Busca Textual GIN)", font=ctk.CTkFont(family="Segoe UI", size=26, weight="bold"), text_color="#333333").pack(pady=(10, 10))

        busca_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        busca_frame.pack(pady=10)

        self.entry_busca = ctk.CTkEntry(busca_frame, placeholder_text="Termo de pesquisa no resumo...", width=450, height=40)
        self.entry_busca.pack(side="left", padx=10)
        ctk.CTkButton(busca_frame, text="Buscar no Acervo", command=self.executar_busca, height=40, font=ctk.CTkFont(weight="bold")).pack(side="left")

        self.container_busca = ctk.CTkScrollableFrame(self.main_frame, fg_color="transparent")
        self.container_busca.pack(fill="both", expand=True, padx=20, pady=10)

    def executar_busca(self):
        palavra = self.entry_busca.get()
        self.limpar_container(self.container_busca)

        try:
            self.cur.execute("""
                SELECT id_projeto, titulo, tipo FROM Projeto
                WHERE to_tsvector('portuguese', resumo) @@ to_tsquery('portuguese', %s)
            """, (palavra,))
            resultados = self.cur.fetchall()
            
            if not resultados:
                ctk.CTkLabel(self.container_busca, text=f"Nenhum registro localizado para: '{palavra}'.", text_color="#555555").pack(pady=20)
            else:
                # Texto de contagem de resultados
                ctk.CTkLabel(self.container_busca, text=f"Termo localizado em {len(resultados)} registro(s):", font=ctk.CTkFont(weight="bold"), text_color="#003366").pack(anchor="w", padx=10, pady=(0, 10))
                
                for p in resultados:
                    card = ctk.CTkFrame(self.container_busca, fg_color="white", border_width=1, border_color="#DDDDDD", corner_radius=8)
                    card.pack(fill="x", pady=5, padx=10)
                    ctk.CTkLabel(card, text=p[1], font=ctk.CTkFont(family="Segoe UI", size=16, weight="bold"), text_color="#003366").pack(anchor="w", padx=15, pady=(10, 0))
                    ctk.CTkLabel(card, text=f"ID: {p[0]}   |   Modalidade: {p[2]}", font=ctk.CTkFont(family="Segoe UI", size=14), text_color="#555555").pack(anchor="w", padx=15, pady=(2, 10))
        except Exception as e:
            ctk.CTkLabel(self.container_busca, text=f"Erro: {e}", text_color="red").pack()

    def mostrar_dashboard(self):
        self.limpar_main_frame()
        ctk.CTkLabel(self.main_frame, text="Painel Gerencial de Indicadores", font=ctk.CTkFont(family="Segoe UI", size=26, weight="bold"), text_color="#333333").pack(pady=(10, 20))

        container = ctk.CTkScrollableFrame(self.main_frame, fg_color="transparent")
        container.pack(fill="both", expand=True, padx=30, pady=10)
        
        try:
            # ==== CARD: INDICADOR 1 ====
            card_ind1 = ctk.CTkFrame(container, fg_color="white", border_width=1, border_color="#DDDDDD", corner_radius=10)
            card_ind1.pack(fill="x", pady=10)
            
            ctk.CTkLabel(card_ind1, text="DISTRIBUIÇÃO INSTITUCIONAL", font=ctk.CTkFont(family="Segoe UI", size=18, weight="bold"), text_color="#003366").pack(anchor="w", padx=25, pady=(20, 10))
            
            self.cur.execute("SELECT tipo, COUNT(*) FROM Projeto GROUP BY tipo ORDER BY count DESC")
            for t in self.cur.fetchall():
                ctk.CTkLabel(card_ind1, text=f"■ {t[0].upper()}:  {t[1]} projeto(s) ativos", font=ctk.CTkFont(family="Segoe UI", size=16), text_color="#444444").pack(anchor="w", padx=35, pady=5)
            
            ctk.CTkLabel(card_ind1, text="").pack(pady=5) # Espaçamento final
            
            # ==== CARD: INDICADOR 2 ====
            card_ind2 = ctk.CTkFrame(container, fg_color="white", border_width=1, border_color="#DDDDDD", corner_radius=10)
            card_ind2.pack(fill="x", pady=20)
            
            ctk.CTkLabel(card_ind2, text="PRODUTIVIDADE DOCENTE (TOP 5)", font=ctk.CTkFont(family="Segoe UI", size=18, weight="bold"), text_color="#003366").pack(anchor="w", padx=25, pady=(20, 10))
            
            self.cur.execute("""
                SELECT pe.nome, COUNT(o.id_projeto) as qtd_projetos
                FROM Professor pr
                JOIN Pessoa pe ON pr.cpf_professor = pe.cpf
                LEFT JOIN Orienta o ON pr.cod_func = o.cod_func
                GROUP BY pe.nome ORDER BY qtd_projetos DESC LIMIT 5
            """)
            for i, prof in enumerate(self.cur.fetchall(), start=1):
                linha = ctk.CTkFrame(card_ind2, fg_color="transparent")
                linha.pack(fill="x", padx=35, pady=5)
                ctk.CTkLabel(linha, text=f"{i}º LUGAR", font=ctk.CTkFont(family="Segoe UI", size=16, weight="bold"), text_color="#003366", width=80, anchor="w").pack(side="left")
                ctk.CTkLabel(linha, text=f"Prof(a). {prof[0]}", font=ctk.CTkFont(family="Segoe UI", size=16), text_color="#333333").pack(side="left", padx=10)
                ctk.CTkLabel(linha, text=f"({prof[1]} orientações)", font=ctk.CTkFont(family="Segoe UI", size=15), text_color="#777777").pack(side="right", padx=10)

            ctk.CTkLabel(card_ind2, text="").pack(pady=5) # Espaçamento final

        except Exception as e:
            ctk.CTkLabel(container, text=f"Erro ao compilar indicadores: {e}", text_color="red").pack()

if __name__ == "__main__":
    app = SistemaAcademico()
    app.mainloop()
