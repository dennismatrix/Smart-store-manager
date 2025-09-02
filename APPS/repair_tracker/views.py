from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.views.generic import ListView, CreateView, UpdateView
from django.urls import reverse_lazy
from django.utils import timezone
from django.db.models import Sum
from django.http import HttpResponse
from django.template.loader import get_template
from xhtml2pdf import pisa
from datetime import timedelta
from .models import Repair, Revenue
from .forms import RepairForm


class RepairListView(ListView):
    model = Repair
    template_name = 'repair_tracker/repair_list.html'
    context_object_name = 'repairs'

    def get_queryset(self):
        return Repair.objects.exclude(status='COLLECTED').order_by('-created_at')


class RepairCreateView(CreateView):
    model = Repair
    form_class = RepairForm
    template_name = 'repair_tracker/repair_form.html'
    success_url = reverse_lazy('repair_tracker:repair_list')

    def form_valid(self, form):
        messages.success(self.request, 'Repair ticket created successfully.')
        return super().form_valid(form)


class RepairUpdateView(UpdateView):
    model = Repair
    form_class = RepairForm
    template_name = 'repair_tracker/repair_form.html'
    success_url = reverse_lazy('repair_tracker:repair_list')

    def form_valid(self, form):
        response = super().form_valid(form)
        repair = self.object

        if repair.status == 'COLLECTED':
            # Ensure collected_at is set properly
            if not repair.collected_at:
                repair.collected_at = timezone.now()
                repair.save()

            # Create Revenue entry if it doesn't exist
            Revenue.objects.get_or_create(
                repair=repair,
                defaults={'amount': repair.charges, 'collected_at': repair.collected_at}
            )

            messages.success(self.request, 'Repair marked as collected and revenue recorded.')
        else:
            messages.success(self.request, 'Repair updated successfully.')

        return response

def report_view(request):
    today = timezone.now().date()
    
    # Get proper start and end dates
    start_of_week = today - timedelta(days=today.weekday())  # Start of the week (Monday)
    end_of_week = start_of_week + timedelta(days=6)  # End of the week (Sunday)
    
    start_of_month = today.replace(day=1)  # First day of the current month
    next_month = (today.replace(day=1) + timedelta(days=32)).replace(day=1)  # First day of next month
    end_of_month = next_month - timedelta(days=1)  # Last day of current month

    # Corrected query filters
    daily_repairs = Repair.objects.filter(collected_at__date=today)
    weekly_repairs = Repair.objects.filter(collected_at__date__range=[start_of_week, end_of_week])
    monthly_repairs = Repair.objects.filter(collected_at__date__range=[start_of_month, end_of_month])

    # Aggregate revenue correctly
    daily_revenue = daily_repairs.aggregate(Sum('charges'))['charges__sum'] or 0
    weekly_revenue = weekly_repairs.aggregate(Sum('charges'))['charges__sum'] or 0
    monthly_revenue = monthly_repairs.aggregate(Sum('charges'))['charges__sum'] or 0

    context = {
        'daily_repairs': daily_repairs,
        'weekly_repairs': weekly_repairs,
        'monthly_repairs': monthly_repairs,
        'daily_revenue': daily_revenue,
        'weekly_revenue': weekly_revenue,
        'monthly_revenue': monthly_revenue,
        'today': today,
        'start_of_week': start_of_week,
        'end_of_week': end_of_week,
        'start_of_month': start_of_month,
        'end_of_month': end_of_month,
    }
    
    return render(request, 'repair_tracker/report.html', context)


def download_report_pdf(request, timeframe):
    """Generate a PDF report for repairs and revenue based on the selected timeframe."""
    today = timezone.now().date()

    # Determine the timeframe filters with proper end dates
    if timeframe == 'daily':
        repairs = Repair.objects.filter(collected_at__date=today)
        title = f"Daily Report - {today}"
    elif timeframe == 'weekly':
        start_of_week = today - timedelta(days=today.weekday())
        end_of_week = start_of_week + timedelta(days=6)
        repairs = Repair.objects.filter(collected_at__date__range=[start_of_week, end_of_week])
        title = f"Weekly Report - {start_of_week} to {end_of_week}"
    elif timeframe == 'monthly':
        start_of_month = today.replace(day=1)
        next_month = (today.replace(day=1) + timedelta(days=32)).replace(day=1)
        end_of_month = next_month - timedelta(days=1)
        repairs = Repair.objects.filter(collected_at__date__range=[start_of_month, end_of_month])
        title = f"Monthly Report - {start_of_month.strftime('%B %Y')}"
    else:
        return HttpResponse("Invalid timeframe", status=400)

    # Calculate total revenue using the same approach as report_view
    total_revenue = repairs.aggregate(Sum('charges'))['charges__sum'] or 0

    # Load the template and render HTML
    template = get_template('repair_tracker/report_pdf.html')
    context = {
        'repairs': repairs,
        'total_revenue': total_revenue,
        'timeframe': timeframe,
        'title': title,
        'generation_date': timezone.now(),
    }
    html = template.render(context)

    # Generate PDF response
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{timeframe}_report.pdf"'

    pisa_status = pisa.CreatePDF(html, dest=response)
    if pisa_status.err:
        return HttpResponse('Error generating PDF', content_type='text/plain')

    return response