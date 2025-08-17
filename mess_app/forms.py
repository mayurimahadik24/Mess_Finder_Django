from django import forms
from .models import Mess, MenuItem

class MessForm(forms.ModelForm):
    FOOD_CHOICES = [
        ('Veg', 'Veg'),
        ('Non-Veg', 'Non-Veg'),
        ('Veg / Non-Veg', 'veg / Non-Veg'),
    ]
    food_type = forms.ChoiceField(choices=FOOD_CHOICES, widget=forms.Select)

    class Meta:
        model = Mess
        fields = ['name', 'location', 'pincode', 'contact', 'food_type', 'price', 'description']

    def clean_price(self):
        price = self.cleaned_data.get('price')
        if price > 9999:
            raise forms.ValidationError("Price cannot be more than ₹9999")
        return price


class MenuItemForm(forms.ModelForm):
    class Meta:
        model = MenuItem
        fields = ['name', 'price', 'description', 'photo']
