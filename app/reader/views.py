from django.views.generic import TemplateView
from django.views.generic.edit import FormView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy

from .forms import ArticleForm
from .models import Article


class HomeView(LoginRequiredMixin, FormView):
    template_name = 'home.html'
    form_class = ArticleForm
    success_url = reverse_lazy('home')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['articles'] = Article.objects.all().order_by('-requested_at')
        return context

    def form_valid(self, form):
        form.instance.requested_by = self.request.user
        form.save()
        return super().form_valid(form)


class LoginView(TemplateView):
    template_name = 'login.html'

