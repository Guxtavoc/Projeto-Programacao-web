from django import forms
from django.contrib.auth.models import User
from pessoas.models import Pessoa, Papel, AlunoInfo, ProfessorInfo

class CriarUsuarioForm(forms.Form):
    # Dados do User
    username = forms.CharField(label="Username")
    senha = forms.CharField(widget=forms.PasswordInput, label="Senha")

    # Dados da Pessoa
    nome = forms.CharField(label="Nome completo")
    cpf = forms.CharField(label="CPF")
    data_nascimento = forms.DateField(widget=forms.DateInput(attrs={"type": "date"}))
    email = forms.EmailField(required=False)
    telefone = forms.CharField(required=False)

    # Papel
    tipo_papel = forms.ChoiceField(choices=Papel.TIPOS_PAPEL, label="Papel")

    # Campos opcionais específicos
    matricula = forms.CharField(required=False)
    codigo_funcional = forms.CharField(required=False)
    formacao = forms.CharField(required=False)
