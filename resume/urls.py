from django.urls import path
from . import views

urlpatterns = [
    path('', views.upload_resume),
        path('resume_summary/<int:resume_id>', views.summarize_text, name='resume_summary'),

]
