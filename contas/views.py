from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import date

from contas.forms import CriarUsuarioForm
from pessoas.models import Pessoa, Papel, AlunoInfo, ProfessorInfo
from academico.models import Turma, Chamada


def login_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect("dashboard")
        else:
            messages.error(request, "Usuário ou senha inválidos.")
    
    return render(request, "contas/login.html")


def logout_view(request):
    logout(request)
    return redirect("contas_login") 


@login_required
def criar_usuario(request):
    if request.user.is_superuser:
        has_permission = True
    else:
        pessoa = getattr(request.user, "pessoa", None)
        has_permission = (
            pessoa and 
            pessoa.papeis.filter(tipo=Papel.COORDENADOR).exists()
        )

    if not has_permission:
        messages.error(request, "Apenas coordenadores podem criar usuários.")
        return redirect("dashboard")

    # Processamento do formulário
    if request.method == "POST":
        form = CriarUsuarioForm(request.POST)

        if form.is_valid():
            user = User.objects.create_user(
                username=form.cleaned_data["username"],
                password=form.cleaned_data["senha"]
            )

            pessoa = Pessoa.objects.create(
                user=user,
                nome=form.cleaned_data["nome"],
                cpf=form.cleaned_data["cpf"],
                data_nascimento=form.cleaned_data["data_nascimento"],
                email=form.cleaned_data["email"],
                telefone=form.cleaned_data["telefone"],
            )

            papel = Papel.objects.create(
                pessoa=pessoa,
                tipo=form.cleaned_data["tipo_papel"]
            )

            if papel.tipo == Papel.ALUNO:
                AlunoInfo.objects.create(
                    papel=papel,
                    matricula=form.cleaned_data["matricula"]
                )
            elif papel.tipo == Papel.PROFESSOR:
                ProfessorInfo.objects.create(
                    papel=papel,
                    codigo_funcional=form.cleaned_data["codigo_funcional"],
                    formacao=form.cleaned_data["formacao"]
                )

            messages.success(request, "Usuário criado com sucesso!")
            return redirect("dashboard")
    
    else:
        form = CriarUsuarioForm()

    return render(request, "criar_usuario.html", {"form": form})


@login_required
def dashboard(request):
    try:
        pessoa = Pessoa.objects.get(user=request.user)
    except Pessoa.DoesNotExist:
        pessoa = None
    
    if not pessoa:
        return render(request, 'contas/dashboard.html', {
            'sem_vinculo': True,
            'user': request.user
        })
    
    # Determinar papéis do usuário
    papeis_ativos = pessoa.papeis.filter(ativo=True)
    tipos_papeis = list(papeis_ativos.values_list("tipo", flat=True))
    
    is_coordenador = Papel.COORDENADOR in tipos_papeis
    is_professor = Papel.PROFESSOR in tipos_papeis
    is_aluno = Papel.ALUNO in tipos_papeis
    
    context = {
        'pessoa': pessoa,
        'is_coordenador': is_coordenador,
        'is_professor': is_professor,
        'is_aluno': is_aluno,
        'papeis': tipos_papeis,
    }
    
    # Dados para Coordenador
    if is_coordenador:
        context.update({
            'total_alunos': AlunoInfo.objects.filter(papel__ativo=True).count(),
            'total_professores': ProfessorInfo.objects.filter(papel__ativo=True).count(),
            'total_turmas': Turma.objects.filter(ativa=True).count(),
            'turmas_sem_professor': Turma.objects.filter(ativa=True, professor__isnull=True).count(),
        })
    
    # Dados para Professor
    if is_professor:
        try:
            professor_info = ProfessorInfo.objects.get(papel__pessoa=pessoa, papel__ativo=True)
            turmas_professor = Turma.objects.filter(professor=professor_info, ativa=True)
            
            context.update({
                'minhas_turmas': turmas_professor,
                'total_minhas_turmas': turmas_professor.count(),
            })
        except ProfessorInfo.DoesNotExist:
            context.update({
                'minhas_turmas': [],
                'total_minhas_turmas': 0,
            })
    
    # Dados para Aluno
    if is_aluno:
        try:
            aluno_info = AlunoInfo.objects.get(papel__pessoa=pessoa, papel__ativo=True)
            minhas_turmas = Turma.objects.filter(matriculas__aluno=aluno_info, matriculas__ativa=True)
            
            context.update({
                'minhas_turmas_aluno': minhas_turmas,
                'presencas_hoje': Chamada.objects.filter(
                    aluno=aluno_info, 
                    aula__data=date.today(),
                    presente=True
                ).count(),
                'faltas_mes': Chamada.objects.filter(
                    aluno=aluno_info,
                    aula__data__month=date.today().month,
                    aula__data__year=date.today().year,
                    presente=False
                ).count(),
            })
        except AlunoInfo.DoesNotExist:
            context.update({
                'minhas_turmas_aluno': [],
                'presencas_hoje': 0,
                'faltas_mes': 0,
            })
    
    return render(request, 'contas/dashboard.html', context)
