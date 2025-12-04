from django.urls import path
from . import views

app_name = 'academico'

urlpatterns = [
    path('', views.dashboard_academico, name='dashboard'),
    path('turmas/', views.listar_turmas, name='listar_turmas'),
    path('turmas/criar/', views.criar_turma, name='criar_turma'),
    path('turmas/<int:pk>/', views.detalhar_turma, name='detalhar_turma'),
    path('turmas/<int:pk>/editar/', views.editar_turma, name='editar_turma'),
    path('turmas/<int:pk>/excluir/', views.excluir_turma, name='excluir_turma'),
    path('turmas/<int:pk>/alunos/', views.gerenciar_alunos_turma, name='gerenciar_alunos_turma'),
    path('turmas/<int:turma_pk>/alunos/<int:aluno_pk>/remover/', views.remover_aluno_turma, name='remover_aluno_turma'),
    path('turmas/<int:pk>/alunos/adicionar-lote/', views.adicionar_alunos_em_lote, name='adicionar_alunos_em_lote'),
    
    path('disciplinas/', views.listar_disciplinas, name='listar_disciplinas'),
    path('disciplinas/criar/', views.criar_disciplina, name='criar_disciplina'),
    path('disciplinas/<int:pk>/editar/', views.editar_disciplina, name='editar_disciplina'),
    path('disciplinas/<int:pk>/excluir/', views.excluir_disciplina, name='excluir_disciplina'),
    
    # Alunos
    path('alunos/', views.listar_alunos, name='listar_alunos'),
    path('alunos/<int:pk>/', views.detalhar_aluno, name='detalhar_aluno'),
    path('alunos/<int:pk>/editar/', views.editar_aluno, name='editar_aluno'),
    path('alunos/<int:pk>/toggle-status/', views.toggle_aluno_status, name='toggle_aluno_status'),
    path('meu_boletim/', views.meu_boletim, name='meu_boletim'),
    path('minha_frequencia/', views.minha_frequencia, name='minha_frequencia'),
    
    path('professores/', views.listar_professores, name='listar_professores'),
    path('professor/minhas-turmas/', views.minhas_turmas_professor, name='minhas_turmas_professor'),
    path('professor/turmas/<int:pk>/', views.detalhar_turma_professor, name='detalhar_turma_professor'),
    path('professor/turmas/<int:turma_pk>/alunos/', views.alunos_turma_professor, name='alunos_turma_professor'),
    path('professor/aula/<int:turma_id>/chamada/', views.chamada, name='fazer_chamada_professor'),
    path('professor/diario/', views.diario_professor, name='diario_professor'),
]