from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Count, Q
from django.core.paginator import Paginator
from django.utils import timezone
from .models import Turma, Disciplina, Matricula
from .forms import TurmaForm, DisciplinaForm, AlunoEditForm
from pessoas.models import AlunoInfo, ProfessorInfo, Pessoa

@login_required
def dashboard_academico(request):
    turmas_recentes = Turma.objects.filter(ativa=True).order_by('-data_criacao')[:5]
    
    context = {
        'total_turmas': Turma.objects.filter(ativa=True).count(),
        'total_disciplinas': Disciplina.objects.filter(ativa=True).count(),
        'total_alunos': AlunoInfo.objects.filter(papel__ativo=True).count(),
        'total_professores': ProfessorInfo.objects.filter(papel__ativo=True).count(),
        'turmas_recentes': turmas_recentes,
    }
    return render(request, 'academico/dashboard.html', context)

@login_required
def listar_turmas(request):
    turmas = Turma.objects.filter(ativa=True).select_related('professor')
    context = {'turmas': turmas}
    return render(request, 'academico/turmas/listar.html', context)

@login_required
def criar_turma(request):
    if request.method == 'POST':
        form = TurmaForm(request.POST)
        if form.is_valid():
            turma = form.save()
            messages.success(request, f'Turma "{turma.nome}" criada com sucesso!')
            return redirect('academico:listar_turmas')
        else:
            messages.error(request, 'Por favor, corrija os erros no formulário.')
    else:
        form = TurmaForm()
    
    context = {
        'form': form,
        'titulo': 'Criar Nova Turma'
    }
    return render(request, 'academico/turmas/form.html', context)

@login_required
def detalhar_turma(request, pk):
    turma = get_object_or_404(Turma, pk=pk)
    matriculas = turma.matriculas.filter(ativa=True).select_related('aluno')
    context = {
        'turma': turma,
        'matriculas': matriculas,
    }
    return render(request, 'academico/turmas/detalhar.html', context)

@login_required
def editar_turma(request, pk):
    turma = get_object_or_404(Turma, pk=pk)
    
    if request.method == 'POST':
        form = TurmaForm(request.POST, instance=turma)
        if form.is_valid():
            turma = form.save()
            messages.success(request, f'Turma "{turma.nome}" atualizada com sucesso!')
            return redirect('academico:listar_turmas')
        else:
            messages.error(request, 'Por favor, corrija os erros no formulário.')
    else:
        form = TurmaForm(instance=turma)
    
    context = {
        'form': form,
        'titulo': f'Editar Turma: {turma.nome}',
        'turma': turma
    }
    return render(request, 'academico/turmas/form.html', context)

@login_required
def excluir_turma(request, pk):
    turma = get_object_or_404(Turma, pk=pk)
    
    if request.method == 'POST':
        turma.ativa = False
        turma.save()
        messages.success(request, f'Turma "{turma.nome}" excluída com sucesso!')
        return redirect('academico:listar_turmas')
    
    context = {'turma': turma}
    return render(request, 'academico/turmas/excluir.html', context)

@login_required
def listar_disciplinas(request):
    disciplinas = Disciplina.objects.filter(ativa=True).select_related('professor')
    context = {'disciplinas': disciplinas}
    return render(request, 'academico/disciplinas/listar.html', context)

@login_required
def criar_disciplina(request):
    if request.method == 'POST':
        form = DisciplinaForm(request.POST)
        if form.is_valid():
            disciplina = form.save()
            messages.success(request, f'Disciplina "{disciplina.get_nome_display()}" criada com sucesso!')
            return redirect('academico:listar_disciplinas')
        else:
            messages.error(request, 'Por favor, corrija os erros no formulário.')
    else:
        form = DisciplinaForm()
    
    context = {
        'form': form,
        'titulo': 'Criar Nova Disciplina'
    }
    return render(request, 'academico/disciplinas/form.html', context)

@login_required
def editar_disciplina(request, pk):
    disciplina = get_object_or_404(Disciplina, pk=pk)
    
    if request.method == 'POST':
        form = DisciplinaForm(request.POST, instance=disciplina)
        if form.is_valid():
            disciplina = form.save()
            messages.success(request, f'Disciplina "{disciplina.get_nome_display()}" atualizada com sucesso!')
            return redirect('academico:listar_disciplinas')
        else:
            messages.error(request, 'Por favor, corrija os erros no formulário.')
    else:
        form = DisciplinaForm(instance=disciplina)
    
    context = {
        'form': form,
        'titulo': f'Editar Disciplina: {disciplina.get_nome_display()}',
        'disciplina': disciplina
    }
    return render(request, 'academico/disciplinas/form.html', context)

@login_required
def excluir_disciplina(request, pk):
    disciplina = get_object_or_404(Disciplina, pk=pk)
    
    if request.method == 'POST':
        disciplina.ativa = False
        disciplina.save()
        messages.success(request, f'Disciplina "{disciplina.get_nome_display()}" excluída com sucesso!')
        return redirect('academico:listar_disciplinas')
    
    context = {'disciplina': disciplina}
    return render(request, 'academico/disciplinas/excluir.html', context)

@login_required
def listar_alunos(request):
    """Listar alunos com paginação e filtros"""
    alunos_list = AlunoInfo.objects.filter(
        papel__ativo=True
    ).select_related(
        'papel__pessoa'
    ).prefetch_related(
        'turmas'
    ).order_by('papel__pessoa__nome')
    
    # Filtros
    search_query = request.GET.get('search', '')
    status_filter = request.GET.get('status', '')
    turma_filter = request.GET.get('turma', '')
    
    if search_query:
        alunos_list = alunos_list.filter(
            Q(papel__pessoa__nome__icontains=search_query) |
            Q(matricula__icontains=search_query) |
            Q(papel__pessoa__email__icontains=search_query)
        )
    
    if status_filter:
        if status_filter == 'ativo':
            alunos_list = alunos_list.filter(papel__ativo=True)
        elif status_filter == 'inativo':
            alunos_list = alunos_list.filter(papel__ativo=False)
    
    if turma_filter:
        alunos_list = alunos_list.filter(turmas__id=turma_filter)
    
    # Paginação
    paginator = Paginator(alunos_list, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Estatísticas
    total_alunos = AlunoInfo.objects.count()
    alunos_ativos = AlunoInfo.objects.filter(papel__ativo=True).count()
    alunos_inativos = AlunoInfo.objects.filter(papel__ativo=False).count()
    
    # Alunos sem turma
    alunos_sem_turma = AlunoInfo.objects.annotate(
        num_turmas=Count('turmas')
    ).filter(num_turmas=0, papel__ativo=True).count()
    
    # Todas as turmas para o filtro
    turmas = Turma.objects.filter(ativa=True)
    
    # Adicionar dados extras para cada aluno
    for aluno in page_obj:
        # Calcular idade
        today = timezone.now().date()
        aluno.idade = today.year - aluno.papel.pessoa.data_nascimento.year - (
            (today.month, today.day) < 
            (aluno.papel.pessoa.data_nascimento.month, aluno.papel.pessoa.data_nascimento.day)
        )
        
        # IDs das turmas para filtro JavaScript
        aluno.turmas_ids = list(aluno.turmas.values_list('id', flat=True))
        aluno.turmas_ativas = aluno.turmas.filter(ativa=True)
    
    context = {
        'alunos': page_obj,
        'page_obj': page_obj,
        'is_paginated': page_obj.has_other_pages(),
        'total_alunos': total_alunos,
        'alunos_ativos': alunos_ativos,
        'alunos_inativos': alunos_inativos,
        'alunos_sem_turma': alunos_sem_turma,
        'turmas': turmas,
    }
    return render(request, 'academico/alunos/listar.html', context)

@login_required
def detalhar_aluno(request, pk):
    """Detalhar informações de um aluno específico"""
    aluno = get_object_or_404(AlunoInfo.objects.select_related(
        'papel__pessoa'
    ).prefetch_related('turmas'), pk=pk)
    
    # Calcular idade
    today = timezone.now().date()
    aluno.idade = today.year - aluno.papel.pessoa.data_nascimento.year - (
        (today.month, today.day) < 
        (aluno.papel.pessoa.data_nascimento.month, aluno.papel.pessoa.data_nascimento.day)
    )
    
    context = {
        'aluno': aluno,
        'turmas_aluno': aluno.turmas.filter(ativa=True),
    }
    return render(request, 'academico/alunos/detalhar.html', context)

@login_required
@login_required
def editar_aluno(request, pk):
    """Editar informações de um aluno - APENAS matrícula"""
    aluno = get_object_or_404(AlunoInfo, pk=pk)
    
    if request.method == 'POST':
        form = AlunoEditForm(request.POST)
        if form.is_valid():
            # Atualiza apenas a matrícula manualmente
            aluno.matricula = form.cleaned_data['matricula']
            aluno.save()
            messages.success(request, f'Aluno {aluno.papel.pessoa.nome} atualizado com sucesso!')
            return redirect('academico:listar_alunos')
        else:
            messages.error(request, 'Por favor, corrija os erros no formulário.')
    else:
        # Preenche o form com os dados atuais
        form = AlunoEditForm(initial={'matricula': aluno.matricula})
    
    context = {
        'form': form,
        'aluno': aluno,
        'titulo': f'Editar Aluno: {aluno.papel.pessoa.nome}'
    }
    return render(request, 'academico/alunos/editar.html', context)

@login_required
def toggle_aluno_status(request, pk):
    """Ativar/desativar aluno"""
    if request.method == 'POST':
        aluno = get_object_or_404(AlunoInfo, pk=pk)
        aluno.papel.ativo = not aluno.papel.ativo
        aluno.papel.save()
        
        status = "ativado" if aluno.papel.ativo else "desativado"
        messages.success(request, f'Aluno {aluno.papel.pessoa.nome} {status} com sucesso!')
    
    return redirect('academico:listar_alunos')

@login_required
def listar_professores(request):
    professores = ProfessorInfo.objects.filter(papel__ativo=True).select_related('papel__pessoa')
    
    # Calcular idade para cada professor
    today = timezone.now().date()
    for professor in professores:
        professor.idade = today.year - professor.papel.pessoa.data_nascimento.year - (
            (today.month, today.day) < 
            (professor.papel.pessoa.data_nascimento.month, professor.papel.pessoa.data_nascimento.day)
        )
    
    context = {'professores': professores}
    return render(request, 'academico/professores/listar.html', context)

@login_required
def gerenciar_alunos_turma(request, pk):
    """Gerenciar alunos em uma turma específica"""
    turma = get_object_or_404(Turma, pk=pk)
    
    # Alunos já matriculados na turma (ativos)
    alunos_na_turma = AlunoInfo.objects.filter(
        turmas=turma,
        papel__ativo=True
    ).select_related('papel__pessoa')
    
    # Alunos disponíveis para adicionar (não estão na turma e estão ativos)
    alunos_disponiveis = AlunoInfo.objects.filter(
        papel__ativo=True
    ).exclude(
        turmas=turma
    ).select_related('papel__pessoa').order_by('papel__pessoa__nome')
    
    # Adicionar aluno à turma
    if request.method == 'POST' and 'adicionar_aluno' in request.POST:
        aluno_id = request.POST.get('aluno_id')
        if aluno_id:
            try:
                aluno = AlunoInfo.objects.get(pk=aluno_id, papel__ativo=True)
                # Verificar se já não está matriculado
                if not turma.alunos.filter(pk=aluno.pk).exists():
                    # Criar matrícula
                    Matricula.objects.create(
                        aluno=aluno,
                        turma=turma,
                        situacao='ATIVA',
                        ativa=True
                    )
                    messages.success(request, f'Aluno {aluno.papel.pessoa.nome} adicionado à turma!')
                else:
                    messages.warning(request, f'Aluno já está na turma.')
            except AlunoInfo.DoesNotExist:
                messages.error(request, 'Aluno não encontrado.')
            return redirect('academico:gerenciar_alunos_turma', pk=pk)
    
    context = {
        'turma': turma,
        'alunos_na_turma': alunos_na_turma,
        'alunos_disponiveis': alunos_disponiveis,
    }
    return render(request, 'academico/turmas/gerenciar_alunos.html', context)

@login_required
def remover_aluno_turma(request, turma_pk, aluno_pk):
    """Remover aluno da turma (desativar matrícula)"""
    if request.method == 'POST':
        turma = get_object_or_404(Turma, pk=turma_pk)
        aluno = get_object_or_404(AlunoInfo, pk=aluno_pk)
        
        # Encontrar e desativar a matrícula
        matricula = get_object_or_404(
            Matricula, 
            turma=turma, 
            aluno=aluno, 
            ativa=True
        )
        
        matricula.ativa = False
        matricula.situacao = 'CANCELADA'
        matricula.save()
        
        messages.success(request, f'Aluno {aluno.papel.pessoa.nome} removido da turma!')
    
    return redirect('academico:gerenciar_alunos_turma', pk=turma_pk)

@login_required
def adicionar_alunos_em_lote(request, pk):
    """Adicionar múltiplos alunos de uma vez"""
    turma = get_object_or_404(Turma, pk=pk)
    
    if request.method == 'POST':
        aluno_ids = request.POST.getlist('alunos_selecionados')
        alunos_adicionados = 0
        
        for aluno_id in aluno_ids:
            try:
                aluno = AlunoInfo.objects.get(pk=aluno_id, papel__ativo=True)
                # Verificar se já não está matriculado
                if not turma.alunos.filter(pk=aluno.pk).exists():
                    Matricula.objects.create(
                        aluno=aluno,
                        turma=turma,
                        situacao='ATIVA',
                        ativa=True
                    )
                    alunos_adicionados += 1
            except AlunoInfo.DoesNotExist:
                continue
        
        if alunos_adicionados > 0:
            messages.success(request, f'{alunos_adicionados} aluno(s) adicionado(s) à turma!')
        else:
            messages.warning(request, 'Nenhum aluno foi adicionado.')
        
        return redirect('academico:gerenciar_alunos_turma', pk=pk)
    
    # Alunos disponíveis para adicionar
    alunos_disponiveis = AlunoInfo.objects.filter(
        papel__ativo=True
    ).exclude(
        turmas=turma
    ).select_related('papel__pessoa').order_by('papel__pessoa__nome')
    
    context = {
        'turma': turma,
        'alunos_disponiveis': alunos_disponiveis,
    }
    return render(request, 'academico/turmas/adicionar_em_lote.html', context)