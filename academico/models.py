from django.db import models
from pessoas.models import ProfessorInfo, AlunoInfo
from django.utils import timezone
from django.core.validators import MinValueValidator, MaxValueValidator
class Disciplina(models.Model):
    DISCIPLINA_CHOICES = (
        ("POR", "Língua Portuguesa"),
        ("MAT", "Matemática"), 
        ("CIE", "Ciências"),
        ("HIS", "História"),
        ("GEO", "Geografia"),
        ("ING", "Inglês"),
        ("ART", "Artes"),
        ("EDF", "Educação Física"),
    )
    
    nome = models.CharField(
        max_length=3,
        choices=DISCIPLINA_CHOICES, 
        verbose_name='Nome da Disciplina'
    )
    professor = models.ForeignKey(
        ProfessorInfo, 
        on_delete=models.SET_NULL,
        null=True, 
        blank=True,
        related_name='disciplinas',
        verbose_name='Professor responsável'
    )
    carga_horaria = models.IntegerField(default=80, verbose_name='Carga horária (horas)')
    ativa = models.BooleanField(default=True, verbose_name='Disciplina ativa')
    
    class Meta:
        verbose_name = 'Disciplina'
        verbose_name_plural = 'Disciplinas'
        ordering = ['nome']
    
    def __str__(self):
        return self.get_nome_display()

class Turma(models.Model):
    PERIODO_CHOICES = [
        ('MATUTINO', 'Matutino'),
        ('VESPERTINO', 'Vespertino'),
        ('INTEGRAL', 'Integral'),
    ]
    
    SERIE_CHOICES = [
        ('1ANO', '1º Ano'),
        ('2ANO', '2º Ano'),
        ('3ANO', '3º Ano'),
        ('4ANO', '4º Ano'),
        ('5ANO', '5º Ano'),
        ('6ANO', '6º Ano'),
        ('7ANO', '7º Ano'),
        ('8ANO', '8º Ano'),
        ('9ANO', '9º Ano'),
    ]
    
    nome = models.CharField(max_length=100, verbose_name='Nome da turma')
    serie = models.CharField(max_length=4, choices=SERIE_CHOICES, verbose_name='Série')
    periodo = models.CharField(max_length=10, choices=PERIODO_CHOICES, verbose_name='Período')
    ano_letivo = models.IntegerField(default=timezone.now().year, verbose_name='Ano letivo')
    professor = models.ForeignKey(
        ProfessorInfo,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='turmas',
        verbose_name='Professor responsável'
    )
    alunos = models.ManyToManyField(
        AlunoInfo,
        through='Matricula',
        related_name='turmas',
        verbose_name='Alunos'
    )
    disciplinas = models.ManyToManyField(
        Disciplina,
        related_name='turmas',
        verbose_name='Disciplinas'
    )
    ativa = models.BooleanField(default=True, verbose_name='Turma ativa')
    data_criacao = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Turma'
        verbose_name_plural = 'Turmas'
        ordering = ['ano_letivo', 'serie', 'nome']
        unique_together = ['nome', 'ano_letivo']
    
    def __str__(self):
        return f"{self.nome} - {self.get_serie_display()} ({self.ano_letivo})"
    
    @property
    def total_alunos(self):
        return self.matriculas.filter(ativa=True).count()

class Matricula(models.Model):
    SITUACAO_CHOICES = [
        ('ATIVA', 'Ativa'),
        ('TRANCADA', 'Trancada'),
        ('CANCELADA', 'Cancelada'),
        ('TRANSFERIDA', 'Transferida'),
    ]
    
    aluno = models.ForeignKey(
        AlunoInfo,
        on_delete=models.CASCADE,
        related_name='matriculas',
        verbose_name='Aluno'
    )
    turma = models.ForeignKey(
        Turma,
        on_delete=models.CASCADE,
        related_name='matriculas',
        verbose_name='Turma'
    )
    data_matricula = models.DateField(default=timezone.now, verbose_name='Data de matrícula')
    situacao = models.CharField(
        max_length=15,
        choices=SITUACAO_CHOICES,
        default='ATIVA',
        verbose_name='Situação'
    )
    ativa = models.BooleanField(default=True, verbose_name='Matrícula ativa')
    
    class Meta:
        verbose_name = 'Matrícula'
        verbose_name_plural = 'Matrículas'
        unique_together = ['aluno', 'turma']
        ordering = ['-data_matricula']
    
    def __str__(self):
        return f"{self.aluno} - {self.turma}"

class Aula(models.Model):
    turma = models.ForeignKey(
        Turma,
        on_delete=models.CASCADE,
        related_name='aulas',
        verbose_name='Turma'
    )
    disciplina = models.ForeignKey(
        Disciplina,
        on_delete=models.CASCADE,
        related_name='aulas',
        verbose_name='Disciplina'
    )
    data = models.DateField(default=timezone.now, verbose_name='Data da aula')
    horario_inicio = models.TimeField(verbose_name='Horário de início')
    horario_fim = models.TimeField(verbose_name='Horário de término')
    conteudo = models.TextField(blank=True, verbose_name='Conteúdo ministrado')
    observacoes = models.TextField(blank=True, verbose_name='Observações')
    
    class Meta:
        verbose_name = 'Aula'
        verbose_name_plural = 'Aulas'
        ordering = ['data', 'horario_inicio']
    
    def __str__(self):
        return f"{self.turma} - {self.disciplina} - {self.data}"

class Chamada(models.Model):
    aula = models.ForeignKey(
        Aula,
        on_delete=models.CASCADE,
        related_name='chamadas',
        verbose_name='Aula'
    )
    aluno = models.ForeignKey(
        AlunoInfo,
        on_delete=models.CASCADE,
        related_name='chamadas',
        verbose_name='Aluno'
    )
    presente = models.BooleanField(default=True, verbose_name='Presente')
    observacao = models.TextField(blank=True, verbose_name='Observação')
    
    class Meta:
        verbose_name = 'Chamada'
        verbose_name_plural = 'Chamadas'
        unique_together = ['aula', 'aluno']
        ordering = ['aula__data', 'aluno']
    
    def __str__(self):
        status = "Presente" if self.presente else "Faltou"
        return f"{self.aluno} - {self.aula} - {status}"

class Nota(models.Model):
    BIMESTRE_CHOICES = [
        (1, '1º Bimestre'),
        (2, '2º Bimestre'),
        (3, '3º Bimestre'),
        (4, '4º Bimestre'),
    ]
    
    aluno = models.ForeignKey(
        AlunoInfo,
        on_delete=models.CASCADE,
        related_name='notas',
        verbose_name='Aluno'
    )
    disciplina = models.ForeignKey(
        Disciplina,
        on_delete=models.CASCADE,
        related_name='notas',
        verbose_name='Disciplina'
    )
    turma = models.ForeignKey(
        Turma,
        on_delete=models.CASCADE,
        related_name='notas',
        verbose_name='Turma'
    )
    bimestre = models.IntegerField(choices=BIMESTRE_CHOICES, verbose_name='Bimestre')
    nota = models.DecimalField(
        max_digits=4,
        decimal_places=2,
        verbose_name='Nota',
        validators=[MinValueValidator(0), MaxValueValidator(10)]  # Corrigido
    )
    data_lancamento = models.DateTimeField(auto_now_add=True, verbose_name='Data de lançamento')
    
    class Meta:
        verbose_name = 'Nota'
        verbose_name_plural = 'Notas'
        unique_together = ['aluno', 'disciplina', 'turma', 'bimestre']
        ordering = ['turma', 'disciplina', 'bimestre', 'aluno']
    
    def __str__(self):
        return f"{self.aluno} - {self.disciplina} - {self.get_bimestre_display()}: {self.nota}"

class Frequencia(models.Model):
    aluno = models.ForeignKey(
        AlunoInfo,
        on_delete=models.CASCADE,
        related_name='frequencias',
        verbose_name='Aluno'
    )
    turma = models.ForeignKey(
        Turma,
        on_delete=models.CASCADE,
        related_name='frequencias',
        verbose_name='Turma'
    )
    mes = models.IntegerField(
        verbose_name='Mês',
        validators=[MinValueValidator(1), MaxValueValidator(12)]  # Corrigido
    )
    ano = models.IntegerField(verbose_name='Ano')
    total_aulas = models.IntegerField(default=0, verbose_name='Total de aulas')
    total_presencas = models.IntegerField(default=0, verbose_name='Total de presenças')
    total_faltas = models.IntegerField(default=0, verbose_name='Total de faltas')
    
    class Meta:
        verbose_name = 'Frequência'
        verbose_name_plural = 'Frequências'
        unique_together = ['aluno', 'turma', 'mes', 'ano']
        ordering = ['ano', 'mes', 'aluno']
    
    def __str__(self):
        return f"{self.aluno} - {self.mes}/{self.ano} - {self.total_presencas}/{self.total_aulas}"
    
    @property
    def percentual_presenca(self):
        if self.total_aulas > 0:
            return (self.total_presencas / self.total_aulas) * 100
        return 0