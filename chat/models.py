from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone
from ads.models import Ads

class Chat(models.Model):
    sender = models.ForeignKey(User, related_name='sent_messages', blank=False, null=False, on_delete=models.CASCADE)
    receiver = models.ForeignKey(User, related_name='received_messages', blank=False, null=False, on_delete=models.CASCADE)
    message = models.TextField()
    ad = models.ForeignKey(Ads, on_delete=models.CASCADE, related_name='chats', null=False, blank=False)
    timestamp = models.DateTimeField(default=timezone.now)
    conversation_id = models.CharField(max_length=255, editable=False, null= False)

    def save(self, *args, **kwargs):
        if not self.conversation_id:
            self.conversation_id = self.generate_conversation_id()
        
        super().save(*args, **kwargs)

    def generate_conversation_id(self):
        """ create unique conversation_id using the sender and receiver details """
        
        if self.sender.id > self.receiver.id:
            user1, user2 = self.receiver, self.sender
        else:
            user1, user2 = self.sender, self.receiver

        return f"{user1.id}-{user1.username}-{self.ad.slug}-{user2.id}-{user2.username}"

    def __str__(self):
        return self.conversation_id


    class Meta:
        ordering = ['timestamp']
