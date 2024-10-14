from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone
from ads.models import Ads


class Chat(models.Model):
    ad = models.ForeignKey(Ads, on_delete=models.CASCADE)  
    created_on = models.DateTimeField(auto_now_add=True)  
    users = models.ManyToManyField(User) 

    def __str__(self):
        return f"Chat for {self.ad} with users {', '.join([user.username for user in self.users.all()])}"


class Message(models.Model):
    sender = models.ForeignKey(User, related_name='sent_messages', blank=False, null=False, on_delete=models.CASCADE)
    receiver = models.ForeignKey(User, related_name='received_messages', blank=False, null=False, on_delete=models.CASCADE)
    message = models.TextField()
    chat = models.ForeignKey(Chat, on_delete=models.CASCADE, related_name='messages', null=False, blank=False)
    created_on  = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_on']
