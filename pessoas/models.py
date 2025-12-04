from datetime import date
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

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

    @property
    def idade(self):
        hoje = date.today()
        return hoje.year - self.data_nascimento.year - (
            (hoje.month, hoje.day) < (self.data_nascimento.month, self.data_nascimento.day)
        )
    
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
    matricula = models.CharField(max_length=20, unique=True, verbose_name='Matrícula', blank=True)
    data_ingresso = models.DateField(auto_now_add=True, verbose_name='Data de ingresso')
    
    def save(self, *args, **kwargs):
        if not self.matricula:
            ano = timezone.now().year
            # Pega o último número sequencial para o ano atual
            ultimas = AlunoInfo.objects.filter(matricula__startswith=str(ano)).order_by('-matricula')
            if ultimas.exists():
                ultimo_numero = int(ultimas.first().matricula[-4:])
                sequencial = ultimo_numero + 1
            else:
                sequencial = 1
            # Gera matrícula com zeros à esquerda
            self.matricula = f"{ano}{sequencial:04d}"
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"Aluno: {self.papel.pessoa.nome} - {self.matricula}"

#Um professor COMPÕE suas informações + informações do seu papel + informações do usuario
class ProfessorInfo(models.Model):
    papel = models.OneToOneField(Papel, on_delete=models.CASCADE, related_name='professor_info')
    codigo_funcional = models.CharField(max_length=20, unique=True, verbose_name='Código Funcional')
    formacao = models.CharField(max_length=100, blank=True, verbose_name='Formação')
    
    def __str__(self):
        return f"Professor: {self.papel.pessoa.nome} - {self.codigo_funcional}"