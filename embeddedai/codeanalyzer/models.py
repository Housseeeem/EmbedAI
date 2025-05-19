from django.db import models
from django.contrib.auth.models import User  # <-- Import User model

class CodeUpload(models.Model):
    file = models.FileField(upload_to='uploads/')
    uploaded_at = models.DateTimeField(auto_now_add=True)

class CodeAnalysis(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    filename = models.CharField(max_length=255)
    analysis_output = models.TextField()
    severity = models.CharField(max_length=50)
    suggestion = models.TextField()
    code_quality_score = models.IntegerField()
    analyzed_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.filename} - {self.code_quality_score}/100"
