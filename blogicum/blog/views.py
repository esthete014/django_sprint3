"""Views of blog app."""
from django.shortcuts import render
from django.http import Http404
from django.db.models import Q
from django.utils import timezone
from django.views.generic import ListView
from django.shortcuts import get_object_or_404

from .models import Post, Category


class IndexView(ListView):
    model = Post
    queryset = Post.objects.prefetch_related('Category')
    template_name = 'blog/index.html'

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context["post_list"] = Post.objects.filter(
            Q(is_published=True)
            & Q(pub_date__lte=timezone.now())
            & Q(category__is_published=True)
        )[0:5]
        return context


def post_detail(request, post_id):
    """Render index detail page."""
    cur = get_object_or_404(
        Post,
        pk=post_id,
        is_published=True,
        pub_date__lte=timezone.now(),
        category__is_published=True
    )
    return render(request, 'blog/detail.html', {"post": cur})


class CategoryListView(ListView):
    model = Category
    queryset = Category.objects.prefetch_related('Post')
    template_name = 'blog/category.html'

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        slug = self.kwargs['category_slug']
        Cat = get_object_or_404(
            Category,
            slug=slug
        )
        context['category'] = Cat
        if not Cat.is_published:
            raise Http404(f"Category with slug = {slug} does not exist")
        context['post_list'] = (
            Cat.post.filter(
                is_published=True,
                pub_date__lte=timezone.now()
            )
        )
        return context
