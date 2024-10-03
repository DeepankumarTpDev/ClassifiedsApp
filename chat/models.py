from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone

class Chat(models.Model):
    sender = models.ForeignKey(User, related_name='sent_messages', blank=False, null=False, on_delete=models.CASCADE)
    receiver = models.ForeignKey(User, related_name='received_messages', blank=False, null=False, on_delete=models.CASCADE)
    message = models.TextField()
    timestamp = models.DateTimeField(default=timezone.now)
    conversation_id = models.CharField(max_length=255, editable=False, null= False)

    def save(self, *args, **kwargs):
        if not self.conversation_id:
            self.conversation_id = f'{self.sender.username}_{self.sender.id}_to_{self.receiver.username}_{self.receiver.id}'
        
        super().save(*args, **kwargs)

    def __str__(self):
        return self.conversation_id


    class Meta:
        ordering = ['timestamp']
