from pessoas.models import Pessoa, Papel

def perfil_usuario(request):
    if not request.user.is_authenticated:
        return {}

    try:
        pessoa = Pessoa.objects.get(user=request.user)
    except Pessoa.DoesNotExist:
        return {}

    papel = pessoa.papeis.filter(ativo=True).first()

    return {
        "pessoa_logada": pessoa,
        "papel_logado": papel,
    }
