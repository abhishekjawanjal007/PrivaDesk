from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class IncidentReport(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True)
    issue_type = models.CharField(max_length=100)
    date_time = models.DateTimeField(auto_now_add=True)
    location = models.CharField(max_length=255)
    description = models.TextField()
    witness = models.CharField(max_length=255)
    evidence = models.FileField(upload_to='evidence/', blank=True, null=True)
    created_anonymously = models.BooleanField(default=False)
    status = models.CharField(max_length=100, default='Pending')
    assigned_to = models.ForeignKey(
        User, related_name='assigned_tickets', null=True, blank=True, on_delete=models.SET_NULL
    )
    assigned_at = models.DateTimeField(null=True, blank=True)
    seen_by_assigned = models.BooleanField(default=False)

    def __str__(self):
        return f"Issue: {self.issue_type}, Status: {self.status}"

class Comment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    ticket = models.ForeignKey(IncidentReport, on_delete=models.CASCADE)
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Comment by {self.user.username} on Ticket {self.ticket.id}"

class ChatMessage(models.Model):
    sender = models.ForeignKey(User, related_name='sent_messages', on_delete=models.CASCADE)
    receiver = models.ForeignKey(User, related_name='received_messages', on_delete=models.CASCADE)
    message = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    admin_reply = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"From {self.sender.username} to {self.receiver.username}: {self.message}"
