from django.shortcuts import render

def visualizarHome(request):
    
    return render(request, 'index.html')