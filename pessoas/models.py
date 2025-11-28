from django.db import models
from django.contrib.auth.models import User

#dados comuns a todos os usuarios
class Pessoa(models.Model):
    #verbose_name é um atributo do Django para que no Admin 
    #sejam mostradas informações de forma mais "humana"
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)
    nome = models.CharField(max_length=100, verbose_name='Nome completo')
    cpf = models.CharField(max_length=14, unique=True, verbose_name='CPF')
    data_nascimento = models.DateField(verbose_name='Data de nascimento')
    email = models.EmailField(blank=True, verbose_name='E-mail')
    telefone = models.CharField(max_length=15, blank=True, verbose_name='Telefone')
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)
    #implementar validações?
    
    def __str__(self):
        return self.nome

#Todo usuario possui um papel (mudar para vinculo?)
class Papel(models.Model):
    ALUNO = 'ALUNO'
    PROFESSOR = 'PROFESSOR'
    COORDENADOR = 'COORDENADOR'
    #Lista das opções que irão aparecer no Admin durante a atribuição de um papel
    TIPOS_PAPEL = [
        (ALUNO, 'Aluno'),
        (PROFESSOR, 'Professor'),
        (COORDENADOR, 'Coordenador'),
    ]
    #related_name é usado para realizar a busca inversa, para facilitar a busca
    pessoa = models.ForeignKey(Pessoa, on_delete=models.CASCADE, related_name='papeis')
    tipo = models.CharField(max_length=20, choices=TIPOS_PAPEL, verbose_name='Tipo de papel')
    ativo = models.BooleanField(default=True, verbose_name='Ativo')
    data_inicio = models.DateField(auto_now_add=True, verbose_name='Data de início')
    data_fim = models.DateField(null=True, blank=True, verbose_name='Data de fim')
    
    def __str__(self):
        return f"{self.pessoa.nome} - {self.get_tipo_display()}"

#Um aluno COMPÕE suas informações + informações do seu papel + informações do usuario
class AlunoInfo(models.Model):
    papel = models.OneToOneField(Papel, on_delete=models.CASCADE, related_name='aluno_info')
    matricula = models.CharField(max_length=20, unique=True, verbose_name='Matrícula')
    data_ingresso = models.DateField(auto_now_add=True, verbose_name='Data de ingresso')
    
    def __str__(self):
        return f"Aluno: {self.papel.pessoa.nome} - {self.matricula}"

#Um professor COMPÕE suas informações + informações do seu papel + informações do usuario
class ProfessorInfo(models.Model):
    papel = models.OneToOneField(Papel, on_delete=models.CASCADE, related_name='professor_info')
    codigo_funcional = models.CharField(max_length=20, unique=True, verbose_name='Código Funcional')
    formacao = models.CharField(max_length=100, blank=True, verbose_name='Formação')
    
    def __str__(self):
        return f"Professor: {self.papel.pessoa.nome} - {self.codigo_funcional}"