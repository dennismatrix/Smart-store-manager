from django import forms
from .models import Repair

class RepairForm(forms.ModelForm):
    class Meta:
        model = Repair
        fields = ['owner_name', 'owner_phone', 'phone_name', 'phone_model', 
                 'issue_description', 'charges', 'status']
        widgets = {
            'issue_description': forms.Textarea(attrs={'rows': 4}),
        }
