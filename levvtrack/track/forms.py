from django import forms
from .models import Item, QtyItem, Entry, Nutrient, ItemNutrient, Unit

class ItemForm(forms.ModelForm):
    class Meta:
        model = Item
        fields = "__all__"

class ItemCartForm(forms.ModelForm):
    nutrient = forms.ModelChoiceField(queryset=Nutrient.objects.all(), required=False)
    nutrient_val = forms.FloatField(min_value=0.0, widget=forms.NumberInput(attrs={'step': '0.01'}), required=False)
    nutrient_unit = forms.ModelChoiceField(queryset=Unit.objects.all(), required=False)
    nutrient_ref_val = forms.IntegerField(min_value=0, required=False)
    nutrient_ref_unit = forms.ModelChoiceField(queryset=Unit.objects.all(), required=False)

    class Meta:
        model = Item
        fields = [
            'item_name',
            'item_brand',
            'item_ref_kcal',
            'item_ref_val',
            'item_unit',
            'item_nutrients',
            'nutrient',
            'nutrient_val',
            'nutrient_unit',
            'nutrient_ref_val',
            'nutrient_ref_unit'
        ]

class NutrientForm(forms.ModelForm):
    class Meta:
        model = Nutrient
        fields = "__all__"

class ItemNutrientForm(forms.ModelForm):
    class Meta:
        model = ItemNutrient
        fields = "__all__"

class QtyItemForm(forms.ModelForm):
    class Meta:
        model = QtyItem
        fields = "__all__"

class EntryForm(forms.ModelForm):
    class Meta:
        model = Entry
        fields = [
            "entry_name",
            "entry_date",
            "entry_main",
            "entry_total_kcal"
        ]

class EntryCartForm(forms.ModelForm):
    copy_entry = forms.ModelChoiceField(queryset=Entry.objects.all().order_by("-entry_date"), required=False)
    item = forms.ModelChoiceField(queryset=Item.objects.all(), required=False)
    qty = forms.IntegerField(required=False, min_value=1)

    class Meta:
        model = Entry
        fields = [
            "copy_entry",
            "entry_name",
            "entry_date",
            "entry_main",
            "entry_total_kcal",
            "item",
            "qty"
        ]


class EntryDateForm(forms.Form):
    showDate = forms.DateField(
        widget = forms.DateInput(
            attrs = {
                'type': 'date',
                'id': 'date-picker'
            }
        )
    )