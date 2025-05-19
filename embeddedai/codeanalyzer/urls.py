from django.urls import path
from . import views

from codeanalyzer import views

urlpatterns = [
    
    path('upload/', views.upload_code, name='upload_code'),
    path('history/', views.analysis_history, name='analysis_history'),  # 👈 ADD THIS
    path('export_pdf/<int:analysis_id>/', views.export_pdf, name='export_pdf'),
    
    
     # 🆕 New:
    path('ide/', views.ide_view, name='ide'),
    path('analyze_code_online/', views.analyze_code_online, name='analyze_code_online'),
]