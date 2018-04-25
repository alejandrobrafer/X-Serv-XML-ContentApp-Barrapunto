from django.db import models

# Create your models here.

class Gestor(models.Model):
    title = models.TextField()
    url = models.TextField()
    content = models.TextField()
