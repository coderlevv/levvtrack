from collections import defaultdict
from datetime import datetime
from math import ceil

from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.shortcuts import get_object_or_404, redirect, render

from ..forms import EntryCartForm, EntryDateForm
from ..models import Entry, Item, QtyItem


@login_required
def entry_create(request):
    # get all entries for today and calculate total kcal so far
    by_date = datetime.now().date()
    entries = Entry.objects.filter(entry_date__contains=by_date)
    date_total = 0
    for entry in entries:
        date_total += entry.total_kcal
    
    if request.method == "POST":
        form = EntryCartForm(request.POST)
        
        # if delete request, post contains one element delete-n
        # with n being the index of the entry to be deleted
        delete_key = [k for k in request.POST.keys() if k.startswith("delete")]
        if len(delete_key) > 0:
            delete_idx = int(delete_key[0].split("-")[1])
            request.session["cart"].pop(delete_idx)
            # It's not the session object itself that is directly
            # modified, but the list
            # so tell django that session obj was modified
            request.session.modified = True
        if "clear" in request.POST:
            request.session["cart"] = []
        if "add" in request.POST:
            if form.is_valid():
                cart = request.session.get("cart", [])
                copy_entry = form.cleaned_data["copy_entry"]
                # if a copy entry was given copy items to cart
                if copy_entry:
                    for qi in copy_entry.entry_items.all():
                        tup = [qi.qty_item.pk, qi.qty_quantity]
                        if tup not in cart:
                            cart += [tup]
                item = form.cleaned_data["item"]
                qty = form.cleaned_data["qty"]
                # selected items and quantities are kept in a list of tuples
                # stored on the request.session object
                # request.session objects can only store values which are
                # serializable, so the actual item cannot be stored
                if item and qty:
                    if "cart" in request.session:
                        request.session["cart"] += [[item.pk, qty]]
                    else:
                        request.session["cart"] = [[item.pk, qty]]
                request.session.modified = True
        if "save" in request.POST:
            # do a pre-validation check on form data
            # entry_total_kcal or items must be given 
            cart = request.session.get("cart", [])
            entry_total_kcal = form.data.get("entry_total_kcal")
            if entry_total_kcal == "" and len(cart) == 0:
                form.add_error(None, "If there are no items, total kcal must be set manually!")
            
            if form.is_valid():
                with transaction.atomic():
                    entry = form.save()
                    # if there is only one cart item and entry name is not given
                    # use item name as the entry name
                    if len(cart) == 1 and form.cleaned_data["entry_name"] is None:
                        item = Item.objects.get(pk = cart[0][0])
                        entry.entry_name = item.item_name
                        entry.save()
                    if len(cart) > 0:
                        for tup in cart:
                            qty_item, created = QtyItem.objects.get_or_create(
                                qty_item = Item.objects.get(pk=tup[0]),
                                qty_quantity = tup[1]
                            )
                            entry.entry_items.add(qty_item)
               
                # reset cart
                request.session["cart"] = []
                return redirect("track:entry_show")
    else:
        form = EntryCartForm(initial={
            "entry_date": datetime.now(),
            #"qty": 1,
            #"item": Item.objects.first()
        })

    context = {
        "cart_list": [],
        "total_kcal": 0,
        "date_total": date_total,
        "form": form,
    }
    cart = request.session.get("cart", [])
    if len(cart) > 0:
        cart_list = []
        total_kcal = 0
        for tup in cart:
            i = Item.objects.get(pk=tup[0])
            q = tup[1]
            kcal = ceil(q / i.item_ref_val * i.item_ref_kcal)
            total_kcal += kcal
            out = (f"{q} {i.item_unit.unit_name} {i.item_name}", kcal)
            cart_list.append(out)
        context["total_kcal"] = total_kcal
        context["date_total"] += total_kcal
        context["cart_list"] = cart_list

    return render(request, "track/entry_create.html", context)


@login_required
def entry_show(request):
    if request.method == "POST":
        form = EntryDateForm(request.POST)
        if form.is_valid():
            # Store date in session
            print(f"post: {str(form.cleaned_data['showDate'])}")
            request.session['entry_show_date'] = str(form.cleaned_data['showDate'])
            # avoid POST resubmission:
            # prevent unwanted duplicate submissions by redirecting the user to
            # a fresh page right after processing the POST data.
            return redirect("track:entry_show")
    
    by_date_str = request.session.get('entry_show_date', None)
    if by_date_str:
        by_date = datetime.strptime(by_date_str, '%Y-%m-%d').date()
    else:
        by_date = datetime.now().date()
    
    form = EntryDateForm(initial={'showDate': by_date})
    entries = Entry.objects.filter(entry_date__contains=by_date).order_by("entry_date")
    total = 0
    nutrients = defaultdict(list)
    nutrient_unit = dict()
    for e in entries:
        total += e.total_kcal
        for qi in e.entry_items.all():
            for nt in qi.qty_item.item_nutrients.all():
                if nt.itemnut_name.nutrient_name not in nutrient_unit:
                    nutrient_unit[nt.itemnut_name.nutrient_name] = nt.itemnut_unit
                if nt.itemnut_ref_unit == qi.qty_item.item_unit:
                    nutrients[nt.itemnut_name.nutrient_name] += [e.entry_factor * (nt.itemnut_val/nt.itemnut_ref_val) * qi.qty_quantity]
    total_nuts = [(k, float(sum(v)), nutrient_unit[k]) for k, v in nutrients.items()]
    context = {
        "entries": entries,
        "total_kcal": total,
        "total_nuts": total_nuts,
        "by_date": by_date,
        "form": form
    }
    return render(request, "track/entry_show.html", context)


@login_required
def entry_update(request, entry_id):
    entry = get_object_or_404(Entry, pk=entry_id)
    request.session["entry_id_update"] = entry.id

    if request.method == "POST":
        form = EntryCartForm(request.POST, instance=entry)

        delete_key = [k for k in request.POST.keys() if k.startswith("delete")]
        if len(delete_key) > 0:
            delete_idx = int(delete_key[0].split("-")[1])
            request.session["cart"].pop(delete_idx)
            # It's not the session object itself that is directly
            # modified, but the list
            # so tell django that session obj was modified
            request.session.modified = True
        if "add" in request.POST:
            #form = EntryCartForm(request.POST)
            if form.is_valid():
                item = form.cleaned_data["item"]
                qty = form.cleaned_data["qty"]
                # selected items and quantities are kept in a list of tuples
                # stored on the request.session object
                # request.session objects can only store values which are
                # serializable, so the actual item cannot be stored
                if item and qty:
                    if "cart" in request.session:
                        request.session["cart"] += [[item.pk, qty]]
                    else:
                        request.session["cart"] = [[item.pk, qty]]
                request.session.modified = True
        if "save" in request.POST:
            # do a pre-validation check on form data
            # entry_total_kcal or items must be given 
            cart = request.session.get("cart", [])
            entry_total_kcal = form.data.get("entry_total_kcal")
            if entry_total_kcal == "" and len(cart) == 0:
                form.add_error(None, "If there are no items, total kcal must be set manually!")
            #form = EntryCartForm(request.POST, instance=entry)
            if form.is_valid():
                with transaction.atomic():
                    form.save()
                    #cart = request.session.get("cart", [])
                    entry.entry_items.clear()
                    for tup in cart:
                        qty_item, created = QtyItem.objects.get_or_create(
                                qty_item = Item.objects.get(pk=tup[0]),
                                qty_quantity = tup[1])
                        entry.entry_items.add(qty_item)
                # reset cart
                request.session["cart"] = []
                return redirect("track:entry_show") 
    else:
        # in case of a get request, build cart from entry
        cart = []
        for qi in entry.entry_items.all():
            cart.append( [qi.qty_item.pk, qi.qty_quantity] )
        request.session["cart"] = cart
        
        inital_qty_item = entry.entry_items.first()
        if inital_qty_item is not None:
            form = EntryCartForm(instance=entry, initial={
                    "qty": inital_qty_item.qty_quantity,
                    "item": inital_qty_item.qty_item
                })
        else:
            form = EntryCartForm(instance=entry)
    
    context = {
        "total_kcal": 0,
        "form": form,
        "entry": entry
    }
    cart = request.session.get("cart", [])
    cart_list = []
    total_kcal = 0
    for tup in cart:
        i = Item.objects.get(pk=tup[0])
        q = tup[1]
        kcal = ceil(q / i.item_ref_val * i.item_ref_kcal)
        total_kcal += kcal
        out = (f"{q} {i.item_unit.unit_name} {i.item_name}", kcal)
        cart_list.append(out)
    context["cart_list"] = cart_list
    
    return render(request, "track/entry_update.html", context)


@login_required
def entry_delete(request, entry_id):
    entry = Entry.objects.get(pk=entry_id)
    context = { "entry": entry }
    if request.method == "POST":
        entry.delete()
        return redirect("track:entry_show")
    return render(request, "track/entry_delete.html", context)

