from django.db import models
from django.contrib.auth.models import User
from django.db.models import Count, Q

class Category(models.Model):
    name = models.CharField(max_length=100, verbose_name='Nom')
    color = models.CharField(max_length=7, verbose_name='Couleur', default='#000000')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='categories')

    class Meta:
        verbose_name = 'Catégorie'
        verbose_name_plural = 'Catégories'
        ordering = ['name']
        unique_together = ['name', 'user']  # Un utilisateur ne peut pas avoir deux catégories du même nom

    def __str__(self):
        return self.name

class Task(models.Model):
    STATUS_CHOICES = [
        ('pending', 'En attente'),
        ('in_progress', 'En cours'),
        ('completed', 'Terminée'),
    ]

    title = models.CharField(max_length=200, verbose_name='Titre')
    description = models.TextField(blank=True, verbose_name='Description')
    created_date = models.DateTimeField(auto_now_add=True, verbose_name='Date de création')
    due_date = models.DateTimeField(verbose_name='Date limite')
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending',
        verbose_name='Statut'
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='tasks',
        verbose_name='Utilisateur'
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='tasks',
        verbose_name='Catégorie'
    )
    parent_task = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='subtasks',
        verbose_name='Tâche parente'
    )

    class Meta:
        ordering = ['due_date', 'created_date']
        verbose_name = 'Tâche'
        verbose_name_plural = 'Tâches'

    def __str__(self):
        return self.title

    def get_progress(self):
        """Calcule le pourcentage de progression basé sur les sous-tâches complétées"""
        if not self.subtasks.exists():
            return 100 if self.status == 'completed' else 0
        
        total_subtasks = self.subtasks.count()
        completed_subtasks = self.subtasks.filter(status='completed').count()
        
        if total_subtasks > 0:
            return int((completed_subtasks / total_subtasks) * 100)
        return 0

    def update_status_based_on_subtasks(self):
        """Met à jour le statut de la tâche en fonction des sous-tâches"""
        if not self.subtasks.exists():
            return
        
        total_subtasks = self.subtasks.count()
        completed_subtasks = self.subtasks.filter(status='completed').count()
        in_progress_subtasks = self.subtasks.filter(status='in_progress').count()
        
        if completed_subtasks == total_subtasks:
            self.status = 'completed'
        elif completed_subtasks > 0 or in_progress_subtasks > 0:
            self.status = 'in_progress'
        else:
            self.status = 'pending'
        
        self.save()
