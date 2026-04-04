from django.shortcuts import render, get_object_or_404
from django.views.generic import ListView, DetailView
from .models import BlogArticle


class BlogListView(ListView):
    """Blog list view."""
    model = BlogArticle
    template_name = 'blog/blog_list.html'
    context_object_name = 'articles'
    paginate_by = 10

    def get_queryset(self):
        return BlogArticle.objects.filter(is_published=True)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = BlogArticle.objects.filter(
            is_published=True
        ).values_list('category', flat=True).distinct()
        return context


class BlogDetailView(DetailView):
    """Blog detail view."""
    model = BlogArticle
    template_name = 'blog/blog_detail.html'
    context_object_name = 'article'
    slug_field = 'slug'

    def get_queryset(self):
        return BlogArticle.objects.filter(is_published=True)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        article = self.get_object()
        context['related_articles'] = BlogArticle.objects.filter(
            is_published=True,
            category=article.category
        ).exclude(id=article.id)[:3]
        return context
