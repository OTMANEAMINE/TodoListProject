from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, logout
from django.db.models import Q
from django.core.paginator import Paginator
from .models import Task, Category
from .forms import TaskForm, CustomUserCreationForm, CategoryForm
from django.http import JsonResponse
from django.contrib.admin.views.decorators import staff_member_required

# Create your views here.

@login_required
def home(request):
    return render(request, 'todos/home.html')

def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('task_list')
    else:
        form = CustomUserCreationForm()
    return render(request, 'registration/register.html', {'form': form})

@login_required
def task_list(request):
    # Récupérer toutes les tâches si l'utilisateur est admin, sinon seulement les siennes
    if request.user.is_staff:
        tasks = Task.objects.all().select_related('user', 'category').prefetch_related('subtasks')
    else:
        tasks = Task.objects.filter(user=request.user).select_related('category').prefetch_related('subtasks')
    
    # Recherche
    search_query = request.GET.get('search', '')
    if search_query:
        tasks = tasks.filter(
            Q(title__icontains=search_query) |
            Q(user__username__icontains=search_query)
        )
    
    # Filtrage par statut
    status_filter = request.GET.get('status', '')
    if status_filter:
        tasks = tasks.filter(status=status_filter)
    
    # Filtrage par catégorie
    category_filter = request.GET.get('category', '')
    if category_filter:
        tasks = tasks.filter(category_id=category_filter)
    
    # Récupérer les catégories de l'utilisateur pour le filtre
    user_categories = Category.objects.filter(user=request.user)
    
    # Pagination
    paginator = Paginator(tasks, 10)  # 10 tâches par page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'todos/task_list.html', {
        'page_obj': page_obj,
        'search_query': search_query,
        'status_filter': status_filter,
        'category_filter': category_filter,
        'status_choices': Task.STATUS_CHOICES,
        'user_categories': user_categories,
        'is_staff': request.user.is_staff
    })

@login_required
def task_create(request):
    # Récupérer l'ID de la tâche parente s'il existe
    parent_id = request.GET.get('parent')
    parent_task = None
    if parent_id:
        parent_task = get_object_or_404(Task, pk=parent_id, user=request.user)

    if request.method == 'POST':
        form = TaskForm(request.POST, user=request.user)
        if form.is_valid():
            task = form.save(commit=False)
            task.user = request.user
            # Si on crée une sous-tâche, on définit la tâche parente
            if parent_task:
                task.parent_task = parent_task
            task.save()
            # Mettre à jour le statut de la tâche parente si nécessaire
            if parent_task:
                parent_task.update_status_based_on_subtasks()
            return redirect('task_list')
    else:
        initial = {}
        if parent_task:
            initial['category'] = parent_task.category
            initial['due_date'] = parent_task.due_date
        form = TaskForm(user=request.user, initial=initial)
    
    context = {
        'form': form,
        'title': f'Nouvelle sous-tâche pour "{parent_task.title}"' if parent_task else 'Nouvelle tâche'
    }
    return render(request, 'todos/task_form.html', context)

@login_required
def task_update(request, pk):
    task = get_object_or_404(Task, pk=pk, user=request.user)
    if request.method == 'POST':
        form = TaskForm(request.POST, instance=task, user=request.user)
        if form.is_valid():
            task = form.save()
            # Mettre à jour le statut de la tâche parente si nécessaire
            if task.parent_task:
                task.parent_task.update_status_based_on_subtasks()
            return redirect('task_list')
    else:
        form = TaskForm(instance=task, user=request.user)
    return render(request, 'todos/task_form.html', {'form': form, 'title': 'Modifier la tâche'})

@login_required
def task_delete(request, pk):
    task = get_object_or_404(Task, pk=pk, user=request.user)
    parent_task = task.parent_task
    if request.method == 'POST':
        task.delete()
        # Mettre à jour le statut de la tâche parente si nécessaire
        if parent_task:
            parent_task.update_status_based_on_subtasks()
        return redirect('task_list')
    return render(request, 'todos/task_confirm_delete.html', {'task': task})

def logout_view(request):
    logout(request)
    return redirect('login')

@login_required
def category_list(request):
    categories = Category.objects.filter(user=request.user)
    return render(request, 'todos/category_list.html', {'categories': categories})

@login_required
def category_create(request):
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            category = form.save(commit=False)
            category.user = request.user
            category.save()
            return redirect('category_list')
    else:
        form = CategoryForm()
    return render(request, 'todos/category_form.html', {'form': form, 'title': 'Nouvelle catégorie'})

@login_required
def category_update(request, pk):
    category = get_object_or_404(Category, pk=pk, user=request.user)
    if request.method == 'POST':
        form = CategoryForm(request.POST, instance=category)
        if form.is_valid():
            form.save()
            return redirect('category_list')
    else:
        form = CategoryForm(instance=category)
    return render(request, 'todos/category_form.html', {'form': form, 'title': 'Modifier la catégorie'})

@login_required
def category_delete(request, pk):
    category = get_object_or_404(Category, pk=pk, user=request.user)
    if request.method == 'POST':
        category.delete()
        return redirect('category_list')
    return render(request, 'todos/category_confirm_delete.html', {'category': category})

@staff_member_required
def admin_categories_for_user(request):
    user_id = request.GET.get('user')
    if user_id:
        categories = Category.objects.filter(user_id=user_id).values('id', 'name', 'color')
        return JsonResponse(list(categories), safe=False)
    return JsonResponse([], safe=False)

@login_required
def task_toggle_status(request, pk):
    task = get_object_or_404(Task, pk=pk, user=request.user)
    if task.status == 'completed':
        task.status = 'pending'
    else:
        task.status = 'completed'
    task.save()
    
    # Mettre à jour le statut de la tâche parente si nécessaire
    if task.parent_task:
        task.parent_task.update_status_based_on_subtasks()
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({
            'status': task.status,
            'status_display': task.get_status_display(),
            'parent_progress': task.parent_task.get_progress() if task.parent_task else None
        })
    return redirect('task_list')
