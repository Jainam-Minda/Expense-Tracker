from decimal import Decimal
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_POST
from django.http import HttpResponseBadRequest
from django.contrib import messages
from django.db.models import Sum, Count, Avg, Max
from .models import Expense
from .forms import ExpenseForm

def get_object_or_400(klass, *args, **kwargs):
    try:
        return get_object_or_404(klass, *args, **kwargs)
    except Exception:
        raise HttpResponseBadRequest("Item not found.")

def dashboard(request):
    if request.method == 'POST':
        form = ExpenseForm(request.POST)
        if form.is_valid():
            exp = form.save()
            messages.success(request, f'Added "{exp.title}" (${exp.amount:.2f}) successfully!')
            return redirect('dashboard')
    else:
        form = ExpenseForm()

    expenses = Expense.objects.all().order_by('-date', '-id')
    total_spent = expenses.aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
    category_totals = Expense.objects.values('category').annotate(total=Sum('amount'), count=Count('id')).order_by('-total')

    context = {
        'expenses': expenses,
        'total_spent': total_spent,
        'form': form,
        'category_totals': category_totals,
        'total_count': expenses.count(),
    }
    return render(request, 'tracker/dashboard.html', context)

@require_POST
def delete_expense(request, pk):
    expense = get_object_or_400(Expense, pk=pk)
    expense.delete()
    messages.success(request, 'Expense deleted successfully.')
    return redirect('dashboard')

def expense_list(request):
    category = request.GET.get('category', '').strip()
    q = request.GET.get('q', '').strip()
    expenses = Expense.objects.all().order_by('-date', '-id')
    if category:
        expenses = expenses.filter(category=category)
    if q:
        expenses = expenses.filter(title__icontains=q)
    total_spent = expenses.aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
    return render(request, 'tracker/expense_list.html', {
        'expenses': expenses,
        'total_spent': total_spent,
        'selected_category': category,
        'categories': [c[0] for c in Expense.CATEGORY_CHOICES],
        'total_count': expenses.count(),
    })

def expense_create(request):
    if request.method == 'POST':
        form = ExpenseForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('dashboard')
    else:
        form = ExpenseForm()
    return render(request, 'tracker/expense_form.html', {'form': form})

def expense_detail(request, pk):
    expense = get_object_or_400(Expense, pk=pk)
    return render(request, 'tracker/expense_detail.html', {'expense': expense})

def expense_confirm_delete(request, pk):
    expense = get_object_or_400(Expense, pk=pk)
    return render(request, 'tracker/expense_confirm_delete.html', {'expense': expense})

def analytics(request):
    expenses = Expense.objects.all()
    total_spent = expenses.aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
    category_stats = []
    if total_spent > Decimal('0.00'):
        for cat_key, cat_name in Expense.CATEGORY_CHOICES:
            cat_sum = expenses.filter(category=cat_key).aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
            pct = round((cat_sum / total_spent) * 100, 1)
            category_stats.append({'name': cat_name, 'total': cat_sum, 'percentage': pct})
    return render(request, 'tracker/analytics.html', {
        'total_spent': total_spent,
        'total_count': expenses.count(),
        'category_stats': category_stats,
    })
