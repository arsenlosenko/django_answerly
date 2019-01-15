from django.contrib.auth.forms import UserCreationForm
from django.views.generic import CreateView


class RegisterView(CreateView):
    template_name = 'user/register.html'
    form_class = UserCreationForm
