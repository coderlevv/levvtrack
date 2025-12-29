from django.urls import path
from . import views

app_name = "track"
urlpatterns = [
    path("view", views.entry_show, name="entry_show"),
    path("entry", views.entry_create, name="entry_create"),
    path("entry/<int:entry_id>", views.entry_update, name="entry_update"),
    path("entry/delete/<int:entry_id>", views.entry_delete, name="entry_delete"),
    path("item", views.item_show, name="item_show"),
    path("item/create", views.item_create, name="item_create"),
    path("item/<int:item_id>", views.item_update, name="item_update"),
    path("item/delete/<int:item_id>", views.item_delete, name="item_delete"),
    path("item/nutrient", views.item_nutrient_create, name="item_nutrient_create"),
    path("nutrient", views.nutrient_show, name="nutrient_show"),
    path("nutrient/create", views.nutrient_create, name="nutrient_create"),
    path("nutrient/<int:nutrient_id>", views.nutrient_update, name="nutrient_update"),
    path("nutrient/delete/<int:nutrient_id>", views.nutrient_delete, name="nutrient_delete"),
    path('export', views.export_options, name='export_options'),
    path('export/csv/', views.export_csv, name='export_csv'),
    path('export/item/', views.export_item_csv, name='export_item_csv'),
]