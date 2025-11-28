from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin
from .models import Pessoa, Papel, AlunoInfo, ProfessorInfo

# ---- Admin Pessoa ----
@admin.register(Pessoa)
class PessoaAdmin(admin.ModelAdmin):
    list_display = ['nome', 'cpf', 'email', 'telefone', 'criado_em']
    search_fields = ['nome', 'cpf', 'email']
    list_filter = ['criado_em']
    ordering = ['nome']

# ---- Admin Papel ----
@admin.register(Papel)
class PapelAdmin(admin.ModelAdmin):
    list_display = ['pessoa', 'tipo', 'ativo', 'data_inicio', 'data_fim']
    list_filter = ['tipo', 'ativo', 'data_inicio']
    search_fields = ['pessoa__nome', 'pessoa__cpf']
    ordering = ['-data_inicio']

# ---- Admin Aluno ----
@admin.register(AlunoInfo)
class AlunoInfoAdmin(admin.ModelAdmin):
    list_display = ['papel', 'matricula', 'data_ingresso']
    search_fields = ['papel__pessoa__nome', 'matricula']
    list_filter = ['data_ingresso']

# ---- Admin Professor ----
@admin.register(ProfessorInfo)
class ProfessorInfoAdmin(admin.ModelAdmin):
    list_display = ['papel', 'codigo_funcional', 'formacao']
    search_fields = ['papel__pessoa__nome', 'codigo_funcional']
    list_filter = ['formacao']

# ---- Inline para vínculo User -> Pessoa ----
class PessoaInline(admin.StackedInline):
    model = Pessoa
    can_delete = False

class UserCustomAdmin(UserAdmin):
    inlines = (PessoaInline, )

admin.site.unregister(User)
admin.site.register(User, UserCustomAdmin)

