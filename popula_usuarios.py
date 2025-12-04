import os
import django
import unicodedata
from faker import Faker
from random import randint
from datetime import date, timedelta

# Configura Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "POA.settings")
django.setup()

from django.contrib.auth.models import User
from pessoas.models import Pessoa, Papel, AlunoInfo, ProfessorInfo

fake = Faker("pt_BR")

def remove_acentos(txt):
    return ''.join(
        c for c in unicodedata.normalize('NFKD', txt)
        if not unicodedata.combining(c)
    )

def cria_aluno():
    nome = fake.name()[:100]  # limita a 100 chars
    data_nascimento = fake.date_of_birth(minimum_age=6, maximum_age=18)
    email = fake.email()[:254]  # max do EmailField Django
    telefone = fake.phone_number()[:15]  # limita a 15 chars
    cpf = fake.unique.cpf()[:14]  # limita a 14 chars

    # username e senha
    username = remove_acentos(nome)[:150]  # username max 150
    senha = "aluno"

    # Cria User
    user = User.objects.create_user(username=username, password=senha)

    # Cria Pessoa
    pessoa = Pessoa.objects.create(
        user=user,
        nome=nome,
        cpf=cpf,
        data_nascimento=data_nascimento,
        email=email,
        telefone=telefone
    )

    # Cria Papel
    papel = Papel.objects.create(
        pessoa=pessoa,
        tipo=Papel.ALUNO
    )

    # Cria AlunoInfo
    AlunoInfo.objects.create(
        papel=papel
    )

    print(f"Aluno criado: {nome} / username: {username} / senha: {senha}")

def cria_professor():
    nome = fake.name()[:100]
    data_nascimento = fake.date_of_birth(minimum_age=25, maximum_age=65)
    email = fake.email()[:254]
    telefone = fake.phone_number()[:15]
    cpf = fake.unique.cpf()[:14]
    codigo_funcional = str(randint(1000, 9999))[:15]  # limita a 15 chars
    formacao = fake.job()[:100]  # formacao max 100

    # username e senha
    username = remove_acentos(nome)[:150]
    senha = "professor"

    # Cria User
    user = User.objects.create_user(username=username, password=senha)

    # Cria Pessoa
    pessoa = Pessoa.objects.create(
        user=user,
        nome=nome,
        cpf=cpf,
        data_nascimento=data_nascimento,
        email=email,
        telefone=telefone
    )

    # Cria Papel
    papel = Papel.objects.create(
        pessoa=pessoa,
        tipo=Papel.PROFESSOR
    )

    # Cria ProfessorInfo
    ProfessorInfo.objects.create(
        papel=papel,
        codigo_funcional=codigo_funcional,
        formacao=formacao
    )

    print(f"Professor criado: {nome} / username: {username} / senha: {senha}")

def main():
    print("===== Populador de Usuários =====")
    papel = input("Digite o papel a ser criado (ALUNO/PROFESSOR): ").strip().upper()
    quantidade = int(input("Quantidade de registros: "))

    if papel not in ["ALUNO", "PROFESSOR"]:
        print("Papel inválido!")
        return

    for _ in range(quantidade):
        if papel == "ALUNO":
            cria_aluno()
        else:
            cria_professor()

if __name__ == "__main__":
    main()
