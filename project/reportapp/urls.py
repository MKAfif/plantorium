from django.urls import path
from . import views

urlpatterns = [

    path('report-pdf-order/', views.report_pdf_order, name='report_pdf_order'),
    path('chart-demo/', views.chart_demo, name='chart_demo'),
    # path('chart-customer-dashboard-order/', views.chart_customer_dashboard_order, name='chart_customer_dashboard_order'),


]