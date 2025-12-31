from decimal import ROUND_HALF_UP, Decimal
from math import ceil

from django.db import models
from django.utils import timezone


class Nutrient(models.Model):
    """A dietary nutrient, like fat, protein, carbohydrates."""
    nutrient_name = models.CharField(max_length=100)
    nutrient_description = models.CharField(max_length=500, null=True, blank=True)

    def __str__(self):
        return f"{self.nutrient_name}"

class Unit(models.Model):
    """Units of a nutrient, default is in gramm."""
    unit_name = models.CharField(max_length=50)
    unit_description = models.CharField(max_length=200, null=True, blank=True)

    @classmethod
    def get_default_unit(cls):
        default_unit, created = cls.objects.get_or_create(unit_name="g", unit_description="gramm")
        return default_unit.pk

    def __str__(self):
        return f"{self.unit_name}"

class ItemNutrient(models.Model):
    """Nutrients of an item.
    
    This basically should represent the food label info."""

    class Meta:
        ordering = ('itemnut_name__nutrient_name', 'itemnut_val')

    itemnut_name = models.ForeignKey(Nutrient, on_delete=models.RESTRICT)
    itemnut_val = models.DecimalField(max_digits=5, decimal_places=2)
    itemnut_unit = models.ForeignKey(Unit, on_delete=models.SET_DEFAULT,
                                default=Unit.get_default_unit, related_name="nutrients")
    itemnut_ref_val = models.PositiveIntegerField(default=100)
    itemnut_ref_unit = models.ForeignKey(Unit, on_delete=models.SET_DEFAULT,
                                default=Unit.get_default_unit, related_name="nutrients_ref")
    
    def __str__(self):
        return f"{self.itemnut_name.nutrient_name} {self.itemnut_val} {self.itemnut_unit.unit_name}/{self.itemnut_ref_val} {self.itemnut_ref_unit.unit_name}"


class Item(models.Model):
    """A basic item that can be listed in an entry."""

    item_name = models.CharField(max_length=200)
    item_brand = models.CharField(max_length=200, blank=True, null=True)
    item_ref_kcal = models.PositiveIntegerField()
    item_ref_val = models.PositiveIntegerField(default=100)
    item_unit = models.ForeignKey(Unit, on_delete=models.SET_DEFAULT, default=Unit.get_default_unit)
    item_nutrients = models.ManyToManyField(ItemNutrient, blank=True)

    def __str__(self):
        brand = self.item_brand + ', ' if self.item_brand else ''
        return f"{self.item_name} ({brand}{self.item_ref_kcal} kcal/{self.item_ref_val} {self.item_unit.unit_name})"
    
    class Meta:
        ordering = ('item_name',)

class QtyItem(models.Model):
    """An item together with it's quantity.
    
    Now that the item is quantified, kcal and nutrient content can be computed.
    """
    
    qty_item = models.ForeignKey(Item, on_delete=models.PROTECT, null=False)
    qty_quantity = models.PositiveIntegerField()

    @property
    def kcal(self):
        return ceil(self.qty_quantity / self.qty_item.item_ref_val * self.qty_item.item_ref_kcal)

    def __str__(self):
        return f"{self.qty_quantity} {self.qty_item.item_unit.unit_name} {self.qty_item}"
    
    class Meta:
        ordering = ('qty_item', 'qty_quantity')


class Entry(models.Model):
    """A food tracker entry."""

    entry_name = models.CharField(max_length=500, blank=True, null=True)
    entry_date = models.DateTimeField(default=timezone.now)
    entry_items = models.ManyToManyField(QtyItem, blank=True)
    entry_main = models.BooleanField(default=False) # main course
    entry_total_kcal = models.PositiveIntegerField(null=True, blank=True)

    def compute_total(self):
        t = 0
        for i in self.entry_items.all():
            t += i.kcal
        return ceil(t)

    # If not null, entry_total_kcal overrides the sum of kcal of the items 
    @property
    def total_kcal(self):
        if self.entry_total_kcal:
            return self.entry_total_kcal 
        return self.compute_total()
    
    # use case for setting entry_total_kcal manually is if only a fraction
    # of an entry is consumed. Given a manually set entry_total_kcal and
    # entry items, this fraction is provided as an attribute
    @property
    def entry_factor(self):
        if self.entry_total_kcal and self.entry_items is not None:
            return Decimal(self.entry_total_kcal / self.compute_total()).quantize(Decimal("0.01"), ROUND_HALF_UP)
        return Decimal("1.00")
    
    def __str__(self):
        entry_name = f", {self.entry_name}" if self.entry_name else ""
        if self.entry_total_kcal and len(self.entry_items.all()) > 0:
            pct = Decimal(self.entry_factor * 100).quantize(Decimal("0.1"), ROUND_HALF_UP)
            entry_name += f" ({pct}% of {self.compute_total()} kcal)" if self.entry_total_kcal and self.compute_total() > 0 else ""
        return f"{self.total_kcal} kcal{entry_name}"
