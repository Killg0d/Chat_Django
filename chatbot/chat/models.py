from django.db import models

# Create your models here.

class ChatMessage(models.Model):
    room = models.CharField(max_length=255)
    username = models.CharField(max_length=255)
    message = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.username}: {self.message}"