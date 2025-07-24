from django.urls import reverse_lazy
from django.views import generic
from .forms import CustomUserCreationForm
from .models import InviteCode
from django.shortcuts import render, redirect
from django.contrib import messages


'''
class SignupPageView(generic.CreateView):
    form_class = CustomUserCreationForm
    success_url = reverse_lazy('login')
    template_name = 'registration/signup.html'
'''

def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        
        invite_code = request.POST['invite_code']
        invite_queryset = InviteCode.objects.filter(invite_code__exact=invite_code)
        
        try:
            invite = invite_queryset.get()
        except:
            invite = None
    
        if invite:
            if form.is_valid():
                user = form.save()
                user.org = invite.organization_id
                username = form.cleaned_data.get('username')
                user.username = username
                user.save()
                messages.success(request, f'Account created for {username}!')
                return redirect('login')
        else:
            messages.warning(request, 'Incorrect invite code')
            pass
    else:
        form = CustomUserCreationForm()
    return render(request, 'registration/signup.html', {'form': form})