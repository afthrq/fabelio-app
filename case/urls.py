from django.urls import path
from case import views

urlpatterns = [
    path('', views.page_one, name='page_one'),
    path('table', views.page_two, name='page_two'),
    path('product/<int:id>/', views.page_three, name='page_three'),
    path('urlcheck/', views.url_check, name='url_check'),
    path('getpid/', views.get_pid, name='get_pid'),
]
