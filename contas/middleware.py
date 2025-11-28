from django.shortcuts import redirect
from django.urls import resolve
from django.contrib import messages

class PapelRequiredMiddleware:
    """
    Middleware para proteger rotas baseadas no papel
    """

    # Rotas divididas por papel
    ROTAS_ALUNO = ['painel_aluno']
    ROTAS_PROFESSOR = ['painel_professor']
    ROTAS_COORDENADOR = [
        'painel_coordenador',
        # Rotas do academico
        'academico:dashboard',
        'academico:listar_turmas', 
        'academico:criar_turma',
        'academico:detalhar_turma',
        'academico:editar_turma',
        'academico:excluir_turma',
        'academico:listar_disciplinas',
        'academico:criar_disciplina', 
        'academico:listar_salas',
        'academico:criar_sala',
        'academico:listar_alunos',
        'academico:listar_professores',
    ]

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if not request.user.is_authenticated:
            return self.get_response(request)

        resolver = request.resolver_match
        if resolver is None:
            return self.get_response(request)

        rota_atual = resolver.url_name
        pessoa = getattr(request.user, 'pessoa', None)

        if pessoa:
            papeis = list(pessoa.papeis.values_list("tipo", flat=True))

            # Proteção de rotas específicas
            if rota_atual in self.ROTAS_ALUNO and "ALUNO" not in papeis:
                return redirect("dashboard")

            if rota_atual in self.ROTAS_PROFESSOR and "PROFESSOR" not in papeis:
                return redirect("dashboard")

            if rota_atual in self.ROTAS_COORDENADOR and "COORDENADOR" not in papeis:
                messages.error(request, "Acesso restrito a coordenadores.")
                return redirect("dashboard")

        return self.get_response(request)

class LoginRequiredMiddleware:
    PUBLIC_PATHS = [
        '/login/',
        '/logout/',
        '/admin/login/',
    ]

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        path = request.path

        if any(path.startswith(p) for p in self.PUBLIC_PATHS):
            return self.get_response(request)

        if not request.user.is_authenticated:
            return redirect('/login/?next=' + path)

        return self.get_response(request)