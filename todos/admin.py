from django.contrib import admin
from .models import Task, Category

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'color', 'user')
    list_filter = ('user',)
    search_fields = ('name', 'user__username')
    ordering = ('user', 'name')
    list_display_links = None  # Désactive les liens d'édition dans la liste
    
    def has_add_permission(self, request):
        return False
        
    def has_change_permission(self, request, obj=None):
        return False
        
    def has_delete_permission(self, request, obj=None):
        return False

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related('user')

@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ('title', 'user', 'category', 'status', 'due_date', 'created_date')
    list_filter = ('status', 'category', 'user', 'created_date', 'due_date')
    search_fields = ('title', 'description', 'user__username', 'category__name')
    ordering = ('-created_date',)
    date_hierarchy = 'due_date'
    list_per_page = 20
    list_display_links = None  # Désactive les liens d'édition dans la liste
    
    def has_add_permission(self, request):
        return False
        
    def has_change_permission(self, request, obj=None):
        return False
        
    def has_delete_permission(self, request, obj=None):
        return False

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related('user', 'category')

    class Media:
        js = ('admin/js/task_admin.js',)
