from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Count, Q
from django.core.paginator import Paginator
from django.utils import timezone
from .models import Chamada, Nota, Turma, Disciplina, Matricula
from .forms import TurmaForm, DisciplinaForm, AlunoEditForm
from pessoas.models import AlunoInfo, Papel, ProfessorInfo, Pessoa

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
    is_coordenador = (
    hasattr(request.user, "pessoa") and
    request.user.pessoa.papeis.filter(tipo=Papel.COORDENADOR).exists()
)
    context = {
        'turma': turma,
        'matriculas': matriculas,
        "is_coordenador": is_coordenador,
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
    
    # Adicionar aluno à turma manualmente
    if request.method == 'POST' and 'adicionar_aluno' in request.POST:
        aluno_id = request.POST.get('aluno_id')
        if aluno_id:
            try:
                aluno = AlunoInfo.objects.get(pk=aluno_id, papel__ativo=True)
                if not turma.alunos.filter(pk=aluno.pk).exists():
                    Matricula.objects.create(
                        aluno=aluno,
                        turma=turma,
                        situacao='ATIVA',
                        ativa=True
                    )
                    messages.success(request, f'Aluno {aluno.papel.pessoa.nome} adicionado à turma!')
                else:
                    messages.warning(request, 'Aluno já está na turma.')
            except AlunoInfo.DoesNotExist:
                messages.error(request, 'Aluno não encontrado.')
        return redirect('academico:gerenciar_alunos_turma', pk=pk)
    
    # Adição automática baseada na idade
    if request.method == 'POST' and 'adicionar_automaticamente' in request.POST:
        # Defina aqui o intervalo de idade por série
        idade_minima, idade_maxima = {
            '1': (6, 7),
            '2': (7, 8),
            '3': (8, 9),
            # Adicione mais séries conforme necessidade
        }.get(str(turma.serie), (0, 100))
        
        adicionados = 0
        for aluno in alunos_disponiveis:
            if idade_minima <= aluno.papel.pessoa.idade <= idade_maxima:
                Matricula.objects.create(
                    aluno=aluno,
                    turma=turma,
                    situacao='ATIVA',
                    ativa=True
                )
                adicionados += 1

        if adicionados > 0:
            messages.success(request, f'{adicionados} aluno(s) automaticamente matriculado(s) na turma!')
        else:
            messages.info(request, 'Nenhum aluno apropriado para a série foi encontrado.')
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

        # Buscar matrícula ativa
        matricula_qs = Matricula.objects.filter(
            turma=turma,
            aluno=aluno,
            ativa=True
        )

        if matricula_qs.exists():
            matricula = matricula_qs.first()
            matricula.ativa = False
            matricula.situacao = 'CANCELADA'
            matricula.save()
            messages.success(request, f'Aluno {aluno.papel.pessoa.nome} removido da turma!')
        else:
            messages.warning(request, f'Aluno {aluno.papel.pessoa.nome} não possui matrícula ativa nesta turma.')

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

@login_required
def minhas_turmas_professor(request):
    """Listar todas as turmas em que o professor ministra alguma disciplina"""
    try:
        professor_info = ProfessorInfo.objects.get(
            papel__pessoa__user=request.user, 
            papel__ativo=True
        )
    except ProfessorInfo.DoesNotExist:
        messages.error(request, "Você não tem permissão de professor ativo.")
        return redirect('dashboard')
    
    # Turmas ativas onde o professor ministra alguma disciplina
    turmas = Turma.objects.filter(
        ativa=True,
        disciplinas__professor=professor_info
    ).distinct().prefetch_related('disciplinas', 'disciplinas__professor').order_by('serie', 'nome')
    
    return render(request, 'academico/professores/minhas_turmas.html', {
        'professor': professor_info,
        'turmas': turmas
    })


@login_required
def detalhar_turma_professor(request, pk):
    """Detalhar uma turma específica do professor com suas matrículas e alunos"""
    try:
        professor_info = ProfessorInfo.objects.get(
            papel__pessoa__user=request.user, 
            papel__ativo=True
        )
    except ProfessorInfo.DoesNotExist:
        messages.error(request, "Você não tem permissão de professor ativo.")
        return redirect('dashboard')
    
    turma = Turma.objects.filter(
        pk=pk,
        ativa=True,
        disciplinas__professor=professor_info
    ).distinct().first()

    if not turma:
        messages.error(request, "Turma não encontrada ou você não tem acesso.")
        return redirect('academico:minhas_turmas_professor')
    
    matriculas = Matricula.objects.filter(
        turma=turma,
        aluno__papel__ativo=True
    ).select_related('aluno__papel__pessoa').order_by('aluno__papel__pessoa__nome')

    disciplinas_turma = turma.disciplinas.filter(
        professor=professor_info,
        ativa=True
    )

    return render(request, 'academico/turmas/detalhar.html', {
        'turma': turma,
        'matriculas': matriculas,
        'disciplinas_turma': disciplinas_turma,
        'total_alunos': matriculas.count(),
        'professor': professor_info
    })

@login_required
def alunos_turma_professor(request, turma_pk):
    """Listar alunos de uma turma específica (professor)"""
    try:
        professor_info = ProfessorInfo.objects.get(
            papel__pessoa__user=request.user,
            papel__ativo=True
        )
    except ProfessorInfo.DoesNotExist:
        messages.error(request, "Você não tem permissão de professor ativo.")
        return redirect('dashboard')
    
    turma = Turma.objects.filter(
        pk=turma_pk,
        ativa=True,
        disciplinas__professor=professor_info
    ).distinct().first()

    if not turma:
        messages.error(request, "Turma não encontrada ou você não tem acesso.")
        return redirect('academico:minhas_turmas_professor')
    
    alunos = AlunoInfo.objects.filter(
        turmas=turma,
        papel__ativo=True
    ).select_related('papel__pessoa').order_by('papel__pessoa__nome')

    today = timezone.now().date()
    for aluno in alunos:
        aluno.idade = today.year - aluno.papel.pessoa.data_nascimento.year - (
            (today.month, today.day) < 
            (aluno.papel.pessoa.data_nascimento.month, aluno.papel.pessoa.data_nascimento.day)
        )

    return render(request, 'academico/professores/alunos_turma.html', {
        'turma': turma,
        'alunos': alunos,
        'professor': professor_info
    })

@login_required
def chamada(request, turma_id):
    try:
        professor = ProfessorInfo.objects.get(
            papel__pessoa__user=request.user,
            papel__ativo=True
        )
    except ProfessorInfo.DoesNotExist:
        messages.error(request, "Você não tem permissão de professor ativo.")
        return redirect('dashboard')

    turma = Turma.objects.filter(
        id=turma_id,
        ativa=True,
        disciplinas__professor=professor
    ).distinct().first()

    if not turma:
        messages.error(request, "Turma não encontrada ou você não tem acesso.")
        return redirect('academico:minhas_turmas_professor')

    data_hoje = timezone.now().date()

    matriculas = Matricula.objects.filter(
        turma=turma,
        ativa=True
    ).select_related('aluno__papel__pessoa').order_by('aluno__papel__pessoa__nome')

    # Cria registros de chamada do dia se não existirem
    for matricula in matriculas:
        Chamada.objects.get_or_create(
            turma=turma,
            aluno=matricula.aluno,
            data=data_hoje
        )

    chamadas = Chamada.objects.filter(
        turma=turma,
        data=data_hoje
    ).select_related('aluno__papel__pessoa').order_by('aluno__papel__pessoa__nome')

    if request.method == "POST":
        for chamada_obj in chamadas:
            chamada_obj.presente = request.POST.get(f"presente_{chamada_obj.id}") == "on"
            chamada_obj.save()
        messages.success(request, "Chamada registrada com sucesso!")
        return redirect('academico:fazer_chamada_professor', turma_id=turma.id)

    return render(request, 'academico/professores/chamada.html', {
        'turma': turma,
        'chamadas': chamadas,
        'data_hoje': data_hoje
    })

@login_required
def diario_professor(request):
    try:
        professor = ProfessorInfo.objects.get(papel__pessoa__user=request.user, papel__ativo=True)
    except ProfessorInfo.DoesNotExist:
        return redirect('dashboard')

    turmas = Turma.objects.filter(ativa=True).filter(disciplinas__professor=professor).distinct()
    
    turma_id = request.POST.get('turma') or request.GET.get('turma')
    turma = None
    alunos_data = []

    if turma_id:
        turma = get_object_or_404(Turma, pk=turma_id, ativa=True)
        alunos = turma.matriculas.filter(ativa=True).select_related('aluno__papel__pessoa')
        disciplinas = turma.disciplinas.filter(professor=professor, ativa=True)

        if request.method == 'POST':
            for key, value in request.POST.items():
                if key.startswith('nota_'):
                    try:
                        _, aluno_id, disciplina_id, bimestre_index = key.split('_')
                        bimestre = int(bimestre_index) + 1
                        if value.strip():
                            nota_val = float(value.replace(',', '.'))
                            Nota.objects.update_or_create(
                                aluno_id=aluno_id,
                                disciplina_id=disciplina_id,
                                turma=turma,
                                bimestre=bimestre,
                                defaults={'nota': nota_val}
                            )
                        else:
                            Nota.objects.filter(
                                aluno_id=aluno_id,
                                disciplina_id=disciplina_id,
                                turma=turma,
                                bimestre=bimestre
                            ).delete()
                    except Exception:
                        continue
            messages.success(request, "Notas salvas com sucesso!")
            return redirect(f'{request.path}?turma={turma_id}')

        # Monta dados para template
        for matricula in alunos:
            aluno = matricula.aluno
            disciplinas_data = []
            for disciplina in disciplinas:
                notas_qs = Nota.objects.filter(aluno=aluno, disciplina=disciplina, turma=turma).order_by('bimestre')
                notas_lista = [''] * 4
                for nota_obj in notas_qs:
                    idx = nota_obj.bimestre - 1
                    if 0 <= idx < 4:
                        notas_lista[idx] = format(nota_obj.nota, '.1f') if nota_obj.nota is not None else ''
                disciplinas_data.append({
                    'disciplina': disciplina,
                    'notas': notas_lista
                })
            alunos_data.append({
                'aluno': aluno,
                'disciplinas': disciplinas_data
            })

    context = {
        'professor': professor,
        'turmas': turmas,
        'turma_selecionada': int(turma_id) if turma_id else None,
        'alunos_data': alunos_data,
    }
    return render(request, 'academico/professores/diario.html', context)

@login_required
def meu_boletim(request):
    user = request.user
    try:
        aluno = AlunoInfo.objects.get(papel__pessoa__user=user)
    except AlunoInfo.DoesNotExist:
        return render(request, "academico/erro.html", {"mensagem": "Você não possui perfil de aluno."})
    
    turmas = aluno.turmas.filter(ativa=True)
    boletim = []

    for turma in turmas:
        professor_nome = turma.professor.papel.pessoa.nome if turma.professor else "Não atribuído"
        disciplinas = turma.disciplinas.all()
        notas_disciplinas = []

        for disciplina in disciplinas:
            notas_obj = Nota.objects.filter(aluno=aluno, turma=turma, disciplina=disciplina).order_by('bimestre')
            notas = [n.nota for n in notas_obj]
            notas_completas = [notas[i] if i < len(notas) else None for i in range(4)]

            notas_validas = [n for n in notas_completas if n is not None]
            if notas_validas:
                media = round(sum(notas_validas) / len(notas_validas), 2)
            else:
                media = None

            notas_disciplinas.append({
                "disciplina": disciplina.get_nome_display(),
                "notas": notas_completas,
                "media": media
            })

        boletim.append({
            "turma": turma,
            "professor": professor_nome,
            "disciplinas": notas_disciplinas
        })

    context = {
        "aluno": aluno,
        "boletim": boletim
    }

    return render(request, "academico/alunos/meu_boletim.html", context)

@login_required
def minha_frequencia(request):
    """View para aluno visualizar sua frequência"""
    try:
        aluno = AlunoInfo.objects.get(papel__pessoa__user=request.user, papel__ativo=True)
    except AlunoInfo.DoesNotExist:
        messages.error(request, "Você não tem permissão de aluno ativo.")
        return redirect('dashboard')
    
    # Buscar todas as matrículas ativas do aluno
    matriculas = Matricula.objects.filter(aluno=aluno, ativa=True).select_related('turma')
    
    # Estrutura para armazenar dados de frequência por turma
    frequencias_data = []
    
    for matricula in matriculas:
        turma = matricula.turma
        
        # Buscar todas as chamadas do aluno nesta turma
        chamadas = Chamada.objects.filter(
            aluno=aluno,
            turma=turma
        ).order_by('data')
        
        # Calcular estatísticas
        total_aulas = chamadas.count()
        total_presente = chamadas.filter(presente=True).count()
        total_faltas = chamadas.filter(presente=False).count()
        
        if total_aulas > 0:
            percentual_presenca = (total_presente / total_aulas) * 100
        else:
            percentual_presenca = 0
        
        # Agrupar por mês/ano
        frequencia_mensal = []
        for chamada in chamadas:
            mes_ano = f"{chamada.data.month:02d}/{chamada.data.year}"
            
            # Verificar se já existe esse mês na lista
            encontrado = False
            for item in frequencia_mensal:
                if item['mes_ano'] == mes_ano:
                    item['total_aulas'] += 1
                    if chamada.presente:
                        item['presentes'] += 1
                    else:
                        item['faltas'] += 1
                    encontrado = True
                    break
            
            if not encontrado:
                frequencia_mensal.append({
                    'mes_ano': mes_ano,
                    'mes': chamada.data.month,
                    'ano': chamada.data.year,
                    'total_aulas': 1,
                    'presentes': 1 if chamada.presente else 0,
                    'faltas': 0 if chamada.presente else 1,
                })
        
        # Calcular percentual para cada mês
        for item in frequencia_mensal:
            if item['total_aulas'] > 0:
                item['percentual'] = (item['presentes'] / item['total_aulas']) * 100
            else:
                item['percentual'] = 0
        
        frequencias_data.append({
            'turma': turma,
            'total_aulas': total_aulas,
            'total_presente': total_presente,
            'total_faltas': total_faltas,
            'percentual_presenca': percentual_presenca,
            'frequencia_mensal': sorted(frequencia_mensal, key=lambda x: (x['ano'], x['mes']), reverse=True),
            'primeira_aula': chamadas.first().data if chamadas.exists() else None,
            'ultima_aula': chamadas.last().data if chamadas.exists() else None,
        })
    
    return render(request, 'academico/alunos/frequencia.html', {
        'aluno': aluno,
        'frequencias_data': frequencias_data,
        'hoje': timezone.now().date(),
    })

