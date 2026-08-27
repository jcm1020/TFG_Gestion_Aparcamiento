from django.shortcuts import render

# Create your views here.

# Vista index (Home)
def index(request):
    return render(request, 'index.html')
    
# Vista login
def login(request):
    return render(request, 'login/login.html')
    
# Vista registro
def registro(request):
    return render(request, 'login/registro.html')
