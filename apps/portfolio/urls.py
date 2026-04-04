from django.urls import path
from . import views

app_name = 'portfolio'

urlpatterns = [
    path('', views.PortfolioListView.as_view(), name='list'),
    path('<slug:slug>/', views.PortfolioDetailView.as_view(), name='detail'),
    path('api/track-click/', views.track_portfolio_click, name='track_click'),
]
