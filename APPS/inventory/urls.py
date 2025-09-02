from django.urls import path
from . import views
from .views import report_view, download_report

urlpatterns = [
    # Dashboard
    path('', views.dashboard_view, name='dashboard'),
    
    # Item management
    path('items/', views.ItemListView.as_view(), name='item_list'),
    path('items/add/', views.ItemCreateView.as_view(), name='item_create'),
    path('items/<int:pk>/edit/', views.ItemUpdateView.as_view(), name='item_update'),
    path('items/<int:pk>/delete/', views.ItemDeleteView.as_view(), name='item_delete'),
    
    # Category management
    path('categories/add/', views.CategoryCreateView.as_view(), name='category_create'),
    
    # Sales
    path('items/<int:item_id>/sell/', views.sell_item_view, name='sell_item'),
    
    # Ajax endpoints
    path('api/check-stock/', views.check_stock_view, name='check_stock'),

    path('report/', report_view, name='report'),
    path('report/download/<str:timeframe>/', download_report, name='download_report'),
]