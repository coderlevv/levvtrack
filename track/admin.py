from django.contrib import admin

# Register your models here.
from .models import Unit, Nutrient, ItemNutrient, Item, QtyItem, Entry

class QtyItemAdmin(admin.ModelAdmin):
    #list_display = ["qty_item__item_name"]
    pass

admin.site.register(Item)
admin.site.register(QtyItem, QtyItemAdmin)
admin.site.register(Entry)
admin.site.register(Nutrient)
admin.site.register(ItemNutrient)
admin.site.register(Unit)
