from django.urls import path
from case import views

urlpatterns = [
    path('', views.page_one, name='page_one'),
    path('table', views.page_two, name='page_two'),
    path('product/<uuid:uuid>/', views.page_three, name='page_three'),
]
