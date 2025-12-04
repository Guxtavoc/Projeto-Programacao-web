from django import forms
from .models import Turma, Disciplina
from pessoas.models import AlunoInfo, ProfessorInfo

class TurmaForm(forms.ModelForm):
    professor = forms.ModelChoiceField(
        queryset=ProfessorInfo.objects.filter(papel__ativo=True),
        required=False,
        label='Professor Responsável',
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    disciplinas = forms.ModelMultipleChoiceField(
        queryset=Disciplina.objects.filter(ativa=True),
        widget=forms.SelectMultiple(attrs={
            'class': 'form-control select2-multiple',
            'data-placeholder': 'Selecione as disciplinas...'
        }),
        required=False,
        label='Disciplinas (com professor)'
    )

    class Meta:
        model = Turma
        fields = ['nome', 'serie', 'periodo', 'ano_letivo', 'professor', 'disciplinas']
        widgets = {
            'nome': forms.TextInput(attrs={'class': 'form-control'}),
            'serie': forms.Select(attrs={'class': 'form-control'}),
            'periodo': forms.Select(attrs={'class': 'form-control'}),
            'ano_letivo': forms.NumberInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Label personalizada das disciplinas com professor
        self.fields['disciplinas'].label_from_instance = lambda obj: f"{obj.get_nome_display()} - {obj.professor.papel.pessoa.nome if obj.professor else 'Sem professor'}"
        
class DisciplinaForm(forms.ModelForm):
    class Meta:
        model = Disciplina
        fields = ['nome', 'professor', 'carga_horaria']
        widgets = {
            'nome': forms.Select(attrs={'class': 'form-control'}),
            'professor': forms.Select(attrs={'class': 'form-control'}),
            'carga_horaria': forms.NumberInput(attrs={'class': 'form-control'}),
        }

class AlunoEditForm(forms.Form):
    matricula = forms.CharField(
        max_length=20,
        label='Matrícula',
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )