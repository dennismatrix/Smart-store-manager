# repair_tracker/models.py
from django.db import models
from django.utils import timezone

class Repair(models.Model):
    STATUS_CHOICES = [
        ('IN_PROGRESS', 'In Progress'),
        ('COMPLETED', 'Completed'),
        ('COLLECTED', 'Collected'),
    ]
    
    owner_name = models.CharField(max_length=100)
    owner_phone = models.CharField(max_length=20)
    phone_name = models.CharField(max_length=100)
    phone_model = models.CharField(max_length=100)
    issue_description = models.TextField()
    charges = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='IN_PROGRESS')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    collected_at = models.DateTimeField(null=True, blank=True)
    
    def mark_as_collected(self):
        self.status = 'COLLECTED'
        self.collected_at = timezone.now()
        self.save()
    
    def __str__(self):\
        return f"{self.owner_name} - {self.phone_name} ({self.status})"

class Revenue(models.Model):
    repair = models.OneToOneField(Repair, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    collected_at = models.DateTimeField()
    
    def __str__(self):
        return f"Revenue from {self.repair.owner_name} - ${self.amount}"
