from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect
from django.views.generic import ListView, DetailView, UpdateView, CreateView, DeleteView, TemplateView
from .models import Post, Category, Author
from datetime import datetime
from .filters import PostFilter
from .forms import PostForm, SubForm
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from .signals import check_post_today


class Search(ListView):
    model = Post
    template_name = 'search.html'
    context_object_name = 'post'
    ordering = ['-time_create']

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['filter'] = PostFilter(self.request.GET, queryset=self.get_queryset())

        return context


class PostList(ListView):
    model = Post
    template_name = 'news.html'
    form_class = PostForm
    context_object_name = 'post'
    queryset = Post.objects.order_by('-time_create')
    paginate_by = 10

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['time_now'] = datetime.utcnow()
        return context


class PostDetailView(DetailView):
    template_name = 'post_detail.html'
    queryset = Post.objects.all()


class PostCreateView(PermissionRequiredMixin, CreateView):
    template_name = 'post_create.html'
    permission_required = ('news.add_post',)
    form_class = PostForm

    def post(self, request, *args, **kwargs):
        cats_id_list = list(map(int, request.POST.getlist('category')))
        category = Category.objects.filter(pk__in=cats_id_list)
        new_post = Post(type=request.POST['type'],
                        header=request.POST['header'],
                        text=request.POST['text'],
                        author=Author.objects.get(pk=request.POST['author']),
                        )
        if check_post_today(sender=Post, instance=new_post, **kwargs) < 3:
            new_post.save()
            for cat in category:
                new_post.category.add(cat)

        return redirect('/news/')

    def get_initial(self):
        initial = super().get_initial()
        user = self.request.user
        author = Author.objects.get(user=user)
        initial['author'] = author
        return initial


class PostUpdateView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    template_name = 'post_create.html'
    permission_required = ('news.change_post',)
    form_class = PostForm

    def get_object(self, **kwargs):
        id = self.kwargs.get('pk')
        return Post.objects.get(pk=id)


class PostDeleteView(PermissionRequiredMixin, DeleteView):
    template_name = 'post_delete.html'
    permission_required = ('news.delete_post',)
    queryset = Post.objects.all()
    success_url = '/news/'


class SubscribeView(PermissionRequiredMixin, CreateView):
    template_name = 'subscribe.html'
    permission_required = ('news.add_post',)
    form_class = SubForm
    success_url = '/'

    def get_initial(self):
        initial = super().get_initial()
        initial['user'] = self.request.user
        return initial
