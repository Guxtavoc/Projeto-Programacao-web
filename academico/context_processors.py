from pessoas.models import Papel

def tipo_papel(request):
    if request.user.is_authenticated:
        try:
            papel = Papel.objects.get(pessoa__user=request.user, ativo=True)
            return {'tipo_papel': papel.tipo}
        except Papel.DoesNotExist:
            pass
    return {'tipo_papel': None}
