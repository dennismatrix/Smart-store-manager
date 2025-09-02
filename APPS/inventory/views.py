from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db.models import Q
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.http import JsonResponse
from calendar import monthrange  # Make sure this import is here and not commented

from .models import Item, Category, Sale, StockAlert
from .forms import ItemForm, CategoryForm, SaleForm, SearchForm
from django.http import HttpResponse
from django.db.models import Sum
from django.utils.timezone import now, timedelta
from django.template.loader import get_template
from xhtml2pdf import pisa
from .models import Sale
# Item Management Views
class ItemListView(ListView):
    model = Item
    template_name = 'inventory/item_list.html'
    context_object_name = 'items'
    
    def get_queryset(self):
        queryset = Item.objects.all()
        form = SearchForm(self.request.GET)
        
        if form.is_valid():
            search_query = form.cleaned_data.get('search_query')
            category = form.cleaned_data.get('category')
            
            if search_query:
                queryset = queryset.filter(
                    Q(name__icontains=search_query) | 
                    Q(category__name__icontains=search_query)
                )
            
            if category:
                queryset = queryset.filter(category=category)
                
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_form'] = SearchForm(self.request.GET)
        
        # Get low stock alerts
        low_stock_items = Item.objects.filter(quantity__lte=Item.objects.values('low_stock_threshold'))
        context['low_stock_items'] = low_stock_items
        
        return context

class ItemCreateView(CreateView):
    model = Item
    form_class = ItemForm
    template_name = 'inventory/item_form.html'
    success_url = reverse_lazy('item_list')
    
    def form_valid(self, form):
        response = super().form_valid(form)
        
        # Create stock alert for the new item
        StockAlert.objects.create(item=self.object)
        
        messages.success(self.request, f"Item '{self.object.name}' added successfully!")
        return response

class ItemUpdateView(UpdateView):
    model = Item
    form_class = ItemForm
    template_name = 'inventory/item_form.html'
    success_url = reverse_lazy('item_list')
    
    def form_valid(self, form):
        response = super().form_valid(form)
        
        # Update stock alert
        alert, created = StockAlert.objects.get_or_create(item=self.object)
        alert.check_stock()
        
        messages.success(self.request, f"Item '{self.object.name}' updated successfully!")
        return response

class ItemDeleteView(DeleteView):
    model = Item
    template_name = 'inventory/item_confirm_delete.html'
    success_url = reverse_lazy('item_list')
    
    def delete(self, request, *args, **kwargs):
        item = self.get_object()
        response = super().delete(request, *args, **kwargs)
        messages.success(request, f"Item '{item.name}' deleted successfully!")
        return response

# Category Management Views
class CategoryCreateView(CreateView):
    model = Category
    form_class = CategoryForm
    template_name = 'inventory/category_form.html'
    success_url = reverse_lazy('item_list')
    
    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, f"Category '{self.object.name}' created successfully!")
        return response

# Sales Management Views
def sell_item_view(request, item_id):
    item = get_object_or_404(Item, id=item_id)
    
    if request.method == 'POST':
        form = SaleForm(request.POST, item_id=item_id)
        if form.is_valid():
            sale = form.save(commit=False)
            
            # Attempt to sell the item
            success = item.sell_item(
                quantity_sold=sale.quantity_sold,
                selling_price=sale.selling_price
            )
            
            if success:
                # Check if stock alert needs to be activated
                alert, created = StockAlert.objects.get_or_create(item=item)
                alert.check_stock()
                
                messages.success(request, 
                    f"Sold {sale.quantity_sold} of {item.name}. "
                    f"Profit: ${sale.profit():.2f}"
                )
                return redirect('item_list')
            else:
                messages.error(request, "Sale failed. Not enough stock.")
    else:
        form = SaleForm(item_id=item_id)
    
    return render(request, 'inventory/sell_item.html', {
        'form': form,
        'item': item
    })

# Ajax view for checking stock
def check_stock_view(request):
    if request.is_ajax():
        item_id = request.GET.get('item_id')
        try:
            item = Item.objects.get(id=item_id)
            return JsonResponse({
                'quantity': item.quantity,
                'is_low_stock': item.is_low_stock(),
            })
        except Item.DoesNotExist:
            return JsonResponse({'error': 'Item not found'}, status=404)
    return JsonResponse({'error': 'Invalid request'}, status=400)

# Dashboard and Reports
def dashboard_view(request):
    # Get low stock alerts
    low_stock_items = Item.objects.filter(quantity__lte=Item.objects.values('low_stock_threshold'))
    
    # Get recent sales (last 10)
    recent_sales = Sale.objects.order_by('-sold_at')[:10]
    # Get total items and categories
    total_items = Item.objects.count()
    total_worth = Item.objects.aggregate(total=Sum('buying_price'))['total'] or 0

    total_categories = Category.objects.count()
    
    return render(request, 'inventory/dashboard.html', {
        'low_stock_items': low_stock_items,
        'recent_sales': recent_sales,
        'total_items': total_items,
        'total_categories': total_categories,
        'total_worth': total_worth,  # Pass computed total worth

        
    })


def generate_report(timeframe):
    """Helper function to filter sales data based on timeframe."""
    today = now().date()
    
    if timeframe == 'daily':
        start_date = today
        end_date = today
    
    elif timeframe == 'weekly':
        start_date = today - timedelta(days=today.weekday())  # Start of the week (Monday)
        end_date = start_date + timedelta(days=6)  # Full week
    
    elif timeframe == 'monthly':
        start_date = today.replace(day=1)  # First day of the current month
        _, last_day = monthrange(today.year, today.month)  # Get last day of the month
        end_date = today.replace(day=last_day)  # Last day of the month
    
    else:
        return Sale.objects.none(), 0  # Return empty result if timeframe is unknown

    # Convert to datetime for more precise filtering
    from datetime import datetime, time
    from django.utils.timezone import make_aware

    start_datetime = make_aware(datetime.combine(start_date, time.min))
    end_datetime = make_aware(datetime.combine(end_date, time.max))

    sales = Sale.objects.filter(sold_at__range=[start_datetime, end_datetime])
    total_profit = sum(sale.profit() for sale in sales)

    return sales, total_profit

def report_view(request):
    """Render the report page with sales data."""
    reports = [
        ('Daily', *generate_report('daily')),
        ('Weekly', *generate_report('weekly')),
        ('Monthly', *generate_report('monthly')),
    ]
    return render(request, 'inventory/report.html', {'reports': reports})

def download_report(request, timeframe):
    """Generate a PDF report based on the selected timeframe."""
    sales, total_profit = generate_report(timeframe)
    
    # You could include date information if needed for the PDF
    today = now().date()
    
    if timeframe == 'daily':
        report_title = f"Daily Sales Report - {today}"
    elif timeframe == 'weekly':
        start_of_week = today - timedelta(days=today.weekday())
        end_of_week = start_of_week + timedelta(days=6)
        report_title = f"Weekly Sales Report - {start_of_week} to {end_of_week}"
    elif timeframe == 'monthly':
        report_title = f"Monthly Sales Report - {today.strftime('%B %Y')}"
    else:
        report_title = f"Sales Report"
    
    template_path = 'inventory/report_pdf.html'
    context = {
        'sales': sales, 
        'total_profit': total_profit, 
        'timeframe': timeframe,
        'report_title': report_title,
        'generated_on': now()
    }
    
    template = get_template(template_path)
    html = template.render(context)

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{timeframe}_report.pdf"'

    pisa_status = pisa.CreatePDF(html, dest=response)
    if pisa_status.err:
        return HttpResponse('Error generating PDF', content_type='text/plain')

    return response