from faker import Faker
import random
from datetime import timedelta
import psycopg2

fake = Faker("pt_BR")

# =========================
# CONEXÃO
# =========================


conn = psycopg2.connect(
    host="localhost",
    database="projeto_main",
    user="postgres",
    password="projeto"
)

cursor = conn.cursor()

# =========================
# QUANTIDADES
# =========================

QTD_PESSOAS = 1500
QTD_ALUNOS = 1000
QTD_PROFESSORES = 200
QTD_EDITAIS = 100
QTD_PROJETOS = 300
QTD_BOLSAS = 400
QTD_PUBLICACOES = 500
QTD_PARTICIPACOES = 1500

# =========================
# PESSOAS
# =========================

print("Inserindo pessoas...")

cpfs = []

for _ in range(QTD_PESSOAS):

    cpf = ''.join(filter(str.isdigit, fake.unique.cpf()))

    cpfs.append(cpf)

    cursor.execute("""
        INSERT INTO Pessoa
        (CPF, Nome, Email, Telefone)
        VALES (%s, %s, %s, %s)
    """, (
        cpf,_
        fake.name(),
        fake.unique.email(),
        fake.phone_number()
    ))

# =========================
# ALUNOS
# =========================

print("Inserindo alunos...")

alunos = []

cpfs_alunos = random.sample(cpfs, QTD_ALUNOS)

for i, cpf in enumerate(cpfs_alunos, start=1):

    ra = str(i).zfill(6)

    alunos.append(ra)

    cursor.execute("""
        INSERT INTO Aluno
        (RA, CPF_aluno, IRA)
        VALUES (%s, %s, %s)
    """, (
        ra,
        cpf,
        random.randint(5000, 20000)
    ))

# =========================
# PROFESSORES
# =========================

print("Inserindo professores...")

professores = []

cpfs_professores = list(set(cpfs) - set(cpfs_alunos))

departamentos = [
    "Computação",
    "Matemática",
    "Física",
    "Estatística",
    "Engenharia"
]

for i in range(QTD_PROFESSORES):

    cod_func = i + 1

    professores.append(cod_func)

    cursor.execute("""
        INSERT INTO Professor
        (cod_func, CPF_professor, n_lattes, departamento)
        VALUES (%s, %s, %s, %s)
    """, (
        cod_func,
        cpfs_professores[i],
        fake.unique.uuid4(),
        random.choice(departamentos)
    ))

# =========================
# PROFESSOR_AREAS
# =========================

print("Inserindo áreas dos professores...")

areas = [
    "Inteligência Artificial",
    "Banco de Dados",
    "Redes",
    "Segurança",
    "Computação Gráfica",
    "Visão Computacional",
    "Engenharia de Software",
    "Sistemas Distribuídos"
]

for professor in professores:

    qtd = random.randint(1, 3)

    for area in random.sample(areas, qtd):

        cursor.execute("""
            INSERT INTO Professor_Areas
            (cod_func, area_pesquisa)
            VALUES (%s, %s)
        """, (
            professor,
            area
        ))

# =========================
# EDITAIS
# =========================

print("Inserindo editais...")

editais = []

for i in range(1, QTD_EDITAIS + 1):

    editais.append(i)

    data_ini = fake.date_between(
        start_date="-2y",
        end_date="today"
    )

    data_fim = data_ini + timedelta(days=365)

    cursor.execute("""
        INSERT INTO Edital
        (id_edital, titulo, texto, data_ini, data_fim, qtd_bolsas)
        VALUES (%s, %s, %s, %s, %s, %s)
    """, (
        i,
        f"Edital {i}",
        fake.text(max_nb_chars=300),
        data_ini,
        data_fim,
        random.randint(5, 20)
    ))

# =========================
# PROJETOS
# =========================

print("Inserindo projetos...")

projetos = []

for i in range(1, QTD_PROJETOS + 1):

    projetos.append(i)

    data_ini = fake.date_between(
        start_date="-1y",
        end_date="today"
    )

    data_fim = data_ini + timedelta(days=365)

    cursor.execute("""
        INSERT INTO Projeto
        (
            id_projeto,
            titulo,
            tipo,
            resumo,
            data_ini,
            data_fim,
            id_edital
        )
        VALUES (%s,%s,%s,%s,%s,%s,%s)
    """, (
        i,
        f"Projeto {i}",
        random.choice(["Pesquisa", "Extensao"]),
        fake.text(max_nb_chars=500),
        data_ini,
        data_fim,
        random.choice(editais)
    ))

# =========================
# ORIENTA
# =========================

print("Inserindo orientações...")

for projeto in projetos:

    cursor.execute("""
        INSERT INTO Orienta
        (cod_func, id_projeto)
        VALUES (%s, %s)
    """, (
        random.choice(professores),
        projeto
    ))

# =========================
# PARTICIPA
# =========================

print("Inserindo participações...")

participacoes = set()

tentativas = 0

while len(participacoes) < QTD_PARTICIPACOES:

    tentativas += 1

    if tentativas > 10000:
        break

    ra = random.choice(alunos)
    projeto = random.choice(projetos)

    if (ra, projeto) in participacoes:
        continue

    participacoes.add((ra, projeto))

    data_ini = fake.date_between(
        start_date="-1y",
        end_date="today"
    )

    cursor.execute("""
        INSERT INTO Participa
        (RA, id_projeto, data_ini, data_fim)
        VALUES (%s, %s, %s, NULL)
    """, (
        ra,
        projeto,
        data_ini
    ))

# =========================
# BOLSAS
# =========================

print("Inserindo bolsas...")

bolsas = []

agencias = [
    "CNPq",
    "CAPES",
    "FAPESP",
    "FINEP"
]

for i in range(1, QTD_BOLSAS + 1):

    bolsas.append(i)

    cursor.execute("""
        INSERT INTO Bolsa
        (
            id_bolsa,
            valor,
            agencia_fomento,
            id_edital
        )
        VALUES (%s,%s,%s,%s)
    """, (
        i,
        round(random.uniform(400, 1800), 2),
        random.choice(agencias),
        random.choice(editais)
    ))

# =========================
# RECEBE
# =========================

print("Inserindo bolsas recebidas...")

participacoes_lista = list(participacoes)

for bolsa in bolsas:

    ra, projeto = random.choice(participacoes_lista)

    data_ini = fake.date_between(
        start_date="-1y",
        end_date="today"
    )

    cursor.execute("""
        INSERT INTO Recebe
        (
            id_bolsa,
            RA,
            id_projeto,
            data_ini,
            data_fim
        )
        VALUES (%s,%s,%s,%s,NULL)
    """, (
        bolsa,
        ra,
        projeto,
        data_ini
    ))

# =========================
# PUBLICAÇÕES
# =========================

print("Inserindo publicações...")

for i in range(1, QTD_PUBLICACOES + 1):

    cursor.execute("""
        INSERT INTO Publicacao
        (
            id_pub,
            titulo_publicacao,
            ano_pub,
            tipo,
            id_projeto
        )
        VALUES (%s,%s,%s,%s,%s)
    """, (
        i,
        fake.sentence(nb_words=6),
        random.randint(2020, 2026),
        random.choice(["Artigo", "Livro"]),
        random.choice(projetos)
    ))

# =========================
# FINALIZAÇÃO
# =========================

conn.commit()

cursor.close()
conn.close()

print("Banco populado com sucesso!")