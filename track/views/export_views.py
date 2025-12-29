import csv
from collections import defaultdict
from datetime import datetime

from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.http import HttpResponse

from ..models import Entry, Nutrient, Item


@login_required
def export_options(request):
     return render(request, "track/export_options.html", {})


@login_required
def export_csv(request):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    stats_file = f"levvtrack_nutrient_stats_{timestamp}.csv"
    response = HttpResponse(
        content_type='text/csv; charset=utf-8',
        headers={'Content-Disposition': f'attachment; filename="{stats_file}"'},
    )
    unique_dates = set()
    for e in Entry.objects.all():
        unique_dates.add((str(e.entry_date.date())))
    nutrient_all = Nutrient.objects.all()
    nutrient_names = ["total_kcal"] + [n.nutrient_name for n in nutrient_all]
    writer = csv.writer(response, delimiter=";")
    writer.writerow(["date"] + [n for n in nutrient_names])
    for dt in sorted(unique_dates):
        total_nutrient = defaultdict(list)
        total_kcal = 0
        entries = Entry.objects.filter(entry_date__contains=dt)
        for e in entries:
            total_kcal += e.total_kcal
            qi_list = e.entry_items.all()
            for qi in qi_list:
                for nt in qi.qty_item.item_nutrients.all():
                    if nt.itemnut_ref_unit == qi.qty_item.item_unit:
                        total_nutrient[nt.itemnut_name.nutrient_name] += [e.entry_factor * (nt.itemnut_val/nt.itemnut_ref_val) * qi.qty_quantity]
        totals = sorted([(k, float(sum(v))) for k, v in total_nutrient.items()])
        totals.append(("total_kcal", total_kcal))
        totals_names = [t[0] for t in totals]
        vals = []
        vals.append(str(dt))
        for name in nutrient_names:
            try:
                idx = totals_names.index(name)
                vals.append(totals[idx][1])
            except:
                vals.append(None)
        writer.writerow(vals)
        
    return response

@login_required
def export_item_csv(request):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    stats_file = f"levvtrack_item_data_{timestamp}.csv"
    response = HttpResponse(
        content_type='text/csv; charset=utf-8',
        headers={'Content-Disposition': f'attachment; filename="{stats_file}"'},
    )
    nutrient_all = Nutrient.objects.all()
    nutrient_names = [n.nutrient_name for n in nutrient_all]
    col_names = ["item"] + nutrient_names
    writer = csv.writer(response, delimiter=";")
    writer.writerow(col_names)
    for item in Item.objects.all():
        item_data = [str(item)]
        item_nuts = item.item_nutrients.all()
        for name in nutrient_names:
            try:
                idx = [n.itemnut_name.nutrient_name for n in item_nuts].index(name)
                item_data.append(item_nuts[idx].itemnut_val)
            except:
                item_data.append(None)
        writer.writerow(item_data)
        
    return response