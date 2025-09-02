from django.urls import path
from . import views

app_name = 'repair_tracker'

urlpatterns = [
    path('', views.RepairListView.as_view(), name='repair_list'),
    path('repair/new/', views.RepairCreateView.as_view(), name='repair-create'),
    path('repair/<int:pk>/edit/', views.RepairUpdateView.as_view(), name='repair-update'),
    path('report/', views.report_view, name='report'),
    path('report/pdf/<str:timeframe>/', views.download_report_pdf, name='download_report_pdf'),
]
