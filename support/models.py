# models.py
from django.db import models
from django.contrib.auth.models import AbstractUser  ,Group, Permission

class User(AbstractUser):

    is_agent = models.BooleanField(default=False)
    class Meta:
        indexes = [
            models.Index(fields=['is_agent']),
        ]

class Ticket(models.Model):
    STATUS_CHOICES = [
        ('open', 'Open'),
        ('assigned', 'Assigned'),
        ('resolved', 'Resolved'),
        ('closed', 'Closed'),
    ]
    
    title = models.CharField(max_length=200)
    description = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='open')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_tickets')

    class Meta:
        ordering = ['created_at']
        indexes = [
            models.Index(fields=['status']),
            models.Index(fields=['created_at']),
        ]

class TicketAssignment(models.Model):
    ticket = models.ForeignKey(Ticket, on_delete=models.CASCADE, related_name='assignments')
    agent = models.ForeignKey(User, on_delete=models.CASCADE, related_name='ticket_assignments')
    assigned_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        unique_together = ('ticket', 'agent')
        indexes = [
            models.Index(fields=['agent', 'is_active']),
        ]