from django.contrib import admin
from .models import *

@admin.register(Disciplina)
class DisciplinaAdmin(admin.ModelAdmin):
    list_display = ['nome', 'professor', 'carga_horaria', 'ativa']
    list_filter = ['ativa', 'professor']
    search_fields = ['nome']

@admin.register(Turma)
class TurmaAdmin(admin.ModelAdmin):
    list_display = ['nome', 'serie', 'periodo', 'ano_letivo', 'professor', 'ativa', 'total_alunos']
    list_filter = ['ativa', 'ano_letivo', 'serie', 'periodo', 'professor']
    search_fields = ['nome']
    filter_horizontal = ['disciplinas']

@admin.register(Matricula)
class MatriculaAdmin(admin.ModelAdmin):
    list_display = ['aluno', 'turma', 'data_matricula', 'situacao', 'ativa']
    list_filter = ['ativa', 'situacao', 'turma', 'data_matricula']
    search_fields = ['aluno__papel__pessoa__nome', 'turma__nome']

@admin.register(Aula)
class AulaAdmin(admin.ModelAdmin):
    list_display = ['turma', 'disciplina', 'data', 'horario_inicio', 'horario_fim']
    list_filter = ['turma', 'disciplina', 'data']
    search_fields = ['turma__nome', 'disciplina__nome']

@admin.register(Chamada)
class ChamadaAdmin(admin.ModelAdmin):
    list_display = ['aula', 'aluno', 'presente']
    list_filter = ['presente', 'aula__data', 'aula__turma']
    search_fields = ['aluno__papel__pessoa__nome', 'aula__turma__nome']

@admin.register(Nota)
class NotaAdmin(admin.ModelAdmin):
    list_display = ['aluno', 'disciplina', 'turma', 'bimestre', 'nota', 'data_lancamento']
    list_filter = ['bimestre', 'disciplina', 'turma']
    search_fields = ['aluno__papel__pessoa__nome', 'disciplina__nome']

@admin.register(Frequencia)
class FrequenciaAdmin(admin.ModelAdmin):
    list_display = ['aluno', 'turma', 'mes', 'ano', 'total_aulas', 'total_presencas', 'total_faltas', 'percentual_presenca']
    list_filter = ['turma', 'mes', 'ano']
    search_fields = ['aluno__papel__pessoa__nome']