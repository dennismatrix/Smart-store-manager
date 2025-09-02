from django import forms
from .models import Item, Category, Sale

class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name']

class ItemForm(forms.ModelForm):
    class Meta:
        model = Item
        fields = ['name', 'category', 'buying_price', 'selling_price', 'quantity', 'low_stock_threshold']
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['category'].queryset = Category.objects.all()
        self.fields['category'].empty_label = "Select a category"
    
    def clean(self):
        cleaned_data = super().clean()
        buying_price = cleaned_data.get('buying_price')
        selling_price = cleaned_data.get('selling_price')
        
        if buying_price and selling_price:
            if buying_price > selling_price:
                self.add_error('selling_price', 'Selling price should be higher than buying price')
        
        return cleaned_data

class SaleForm(forms.ModelForm):
    class Meta:
        model = Sale
        fields = ['item', 'quantity_sold', 'selling_price']
        
    def __init__(self, *args, **kwargs):
        item_id = kwargs.pop('item_id', None)
        super().__init__(*args, **kwargs)
        
        if item_id:
            item = Item.objects.get(id=item_id)
            self.fields['item'].initial = item
            self.fields['item'].widget = forms.HiddenInput()
            self.fields['selling_price'].initial = item.selling_price
            
            # Limit quantity_sold to available quantity
            self.fields['quantity_sold'].widget.attrs['max'] = item.quantity
            self.fields['quantity_sold'].widget.attrs['min'] = 1
    
    def clean_quantity_sold(self):
        quantity_sold = self.cleaned_data.get('quantity_sold')
        item = self.cleaned_data.get('item')
        
        if quantity_sold > item.quantity:
            raise forms.ValidationError(f"Cannot sell more than available quantity ({item.quantity}).")
        
        if quantity_sold <= 0:
            raise forms.ValidationError("Quantity sold must be greater than zero.")
        
        return quantity_sold

class SearchForm(forms.Form):
    search_query = forms.CharField(max_length=100, required=False, label='',
                                  widget=forms.TextInput(attrs={'placeholder': 'Search items by name or category...'}))
    category = forms.ModelChoiceField(
        queryset=Category.objects.all(),
        required=False,
        empty_label="All Categories"
    )