from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('expenses/', views.expense_list, name='expense_list'),
    path('expenses/add/', views.expense_create, name='expense_create'),
    path('expenses/<int:pk>/', views.expense_detail, name='expense_detail'),
    path('expenses/<int:pk>/delete/', views.delete_expense, name='expense_delete'),
    path('expenses/<int:pk>/confirm-delete/', views.expense_confirm_delete, name='expense_confirm_delete'),
    path('analytics/', views.analytics, name='analytics'),
]
