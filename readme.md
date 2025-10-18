# Sistema Acadêmico - Projeto Django

## Descrição

Sistema de gerenciamento acadêmico desenvolvido em Django para a disciplina de Programação Web 2025/2. Controle de alunos, professores, turmas, notas e frequência.

## Tecnologias Utilizadas

- **Backend:** Django 4.2
- **Banco de Dados:** PostgreSQL
- **Containerização:** Docker e Docker Compose
- **Frontend:** HTML5, CSS3, JavaScript

## Funcionalidades Principais

- Gestão de usuários com papéis flexíveis (Aluno, Professor, Coordenador)
- Controle de turmas e disciplinas
- Lançamento de notas e frequência
- Geração de boletins
- Interface administrativa completa
- Design responsivo

## Estrutura do Projeto

projeto-academico/
├── app_principal/ # Aplicação principal
├── pessoas/ # Gestão de usuários e papéis
├── academico/ # Lógica acadêmica
├── static/ # Arquivos estáticos
├── templates/ # Templates HTML
├── docker-compose.yml # Orquestração de containers
└── requirements.txt # Dependências Python

## Modelagem de Dados

O sistema utiliza uma abordagem de composição para papéis de usuário:
Pessoa: Dados básicos do usuário
Papel: Define funções (Aluno, Professor, Coordenador)
Turma/Disciplina: Estrutura acadêmica
Nota/Boletim: Avaliações e resultados

## Pré-requisitos

- Docker
- Docker Compose

## Instalação e Execução

### 1. Clone o repositório

```bash
git clone [https://github.com/Guxtavoc/Projeto-Programacao-web.git]
cd projeto-academico
```

## Configure as variáveis de ambiente .env (Opcional)

DEBUG=1
SECRET_KEY=sua-chave-secreta-aqui
DB_NAME=projeto_academico
DB_USER=usuario_db
DB_PASSWORD=senha_db
DB_HOST=db
DB_PORT=5432

## Execute com Docker

```bash
docker-compose up --build
```

## Acesse a aplicação

Aplicação: http://localhost:8000

## Comandos Uteis

```bash
# Criar superusuário

docker-compose exec web python manage.py createsuperuser

# Executar migrações

docker-compose exec web python manage.py migrate

# Coletar arquivos estáticos

docker-compose exec web python manage.py collectstatic
```
