from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.shortcuts import get_object_or_404, redirect, render

from ..forms import ItemCartForm, ItemNutrientForm
from ..models import Item, ItemNutrient, Nutrient, Unit


@login_required
def item_show(request):
    item_list = Item.objects.all()
    context = { 'item_list': item_list }
    return render(request, "track/item_show.html", context)


@login_required
def item_delete(request, item_id):
    item = get_object_or_404(Item, pk=item_id)
    context = { "item": item }
    if request.method == "POST":
        with transaction.atomic():
            item.delete()
        return redirect("track:item_show")
    return render(request, "track/item_delete.html", context)


@login_required
def item_nutrient_create(request):
    if request.method == "POST":
        form = ItemNutrientForm(request.POST)
        if form.is_valid():
            # check if already available
            name = form.cleaned_data['itemnut_name']
            val = form.cleaned_data['itemnut_val']
            unit = form.cleaned_data['itemnut_unit']
            ref_val = form.cleaned_data['itemnut_ref_val']
            ref_unit = form.cleaned_data['itemnut_ref_unit']
            # Check if an instance with the same values exists
            exists = ItemNutrient.objects.filter(
                itemnut_name=name,
                itemnut_val=val,
                itemnut_unit=unit,
                itemnut_ref_val=ref_val,
                itemnut_ref_unit=ref_unit).exists()
            if not exists:
                with transaction.atomic():
                    # Save the new instance
                    form.save()
            return redirect("track:item_show")
    form = ItemNutrientForm()
    context = { 'form': form }
    return render(request, "track/item_nutrient_create.html", context)


@login_required
def item_create(request):
    if request.method == "POST":
        form = ItemCartForm(request.POST)
        # if delete request, list contains one element delete-n
        # with n being the index of the entry to be deleted
        delete_key = [k for k in request.POST.keys() if k.startswith("delete")]
        if "clear" in request.POST:
            request.session["nutrient_cart"] = []
        if "add" in request.POST:
            if form.is_valid():
                nutrient = form.cleaned_data["nutrient"]
                nutrient_val = form.cleaned_data["nutrient_val"]
                nutrient_unit = form.cleaned_data["nutrient_unit"]
                nutrient_ref_val = form.cleaned_data["nutrient_ref_val"]
                nutrient_ref_unit = form.cleaned_data["nutrient_ref_unit"]
                if nutrient:
                    if "nutrient_cart" in request.session:
                        request.session["nutrient_cart"] += [[nutrient.pk, nutrient_val, nutrient_unit.pk, nutrient_ref_val, nutrient_ref_unit.pk]]
                    else:
                        request.session["nutrient_cart"] = [[nutrient.pk, nutrient_val, nutrient_unit.pk, nutrient_ref_val, nutrient_ref_unit.pk]]
        if len(delete_key) > 0:
            delete_idx = int(delete_key[0].split("-")[1])
            request.session["nutrient_cart"].pop(delete_idx)
            request.session.modified = True
        if "save" in request.POST:
            if form.is_valid():
                with transaction.atomic():
                    item = form.save()
                    cart = request.session.get("nutrient_cart", [])
                    if len(cart) > 0:
                        for tup in cart:
                            itemnut, created = ItemNutrient.objects.get_or_create(
                                itemnut_name=Nutrient.objects.get(pk=tup[0]),
                                itemnut_val=tup[1],
                                itemnut_unit=Unit.objects.get(pk=tup[2]),
                                itemnut_ref_val=tup[3],
                                itemnut_ref_unit=Unit.objects.get(pk=tup[4]))
                            item.item_nutrients.add(itemnut)
                # reset cart
                request.session["nutrient_cart"] = []
                return redirect("track:item_show")
    else:
        form = ItemCartForm(
            initial={
            "nutrient_unit": Unit.get_default_unit(),
            "nutrient_ref_val": 100,
            "nutrient_ref_unit": Unit.get_default_unit(),
            }
        )

    cart = request.session.get("nutrient_cart", [])
    cart_list = []
    for tup in cart:
        cart_list.append((
            Nutrient.objects.get(pk=tup[0]),
            tup[1],
            Unit.objects.get(pk=tup[2]),
            tup[3],
            Unit.objects.get(pk=tup[4])
        ))
    context = {
        "cart_list": cart_list,
        "form": form,
    }

    return render(request, "track/item_create.html", context)


@login_required
def item_update(request, item_id):
    item = get_object_or_404(Item, pk=item_id)
    delete_key = [k for k in request.POST.keys() if k.startswith("delete")]
    if request.method == "POST":
        if "add" in request.POST:
            form = ItemCartForm(request.POST)
            if form.is_valid():
                nutrient = form.cleaned_data["nutrient"]
                nutrient_val = form.cleaned_data["nutrient_val"]
                nutrient_unit = form.cleaned_data["nutrient_unit"]
                nutrient_ref_val = form.cleaned_data["nutrient_ref_val"]
                nutrient_ref_unit = form.cleaned_data["nutrient_ref_unit"]
                if "nutrient_cart" in request.session:
                    request.session["nutrient_cart"] += [[nutrient.pk, nutrient_val, nutrient_unit.pk, nutrient_ref_val, nutrient_ref_unit.pk]]
                else:
                    request.session["nutrient_cart"] = [[nutrient.pk, nutrient_val, nutrient_unit.pk, nutrient_ref_val, nutrient_ref_unit.pk]]
        if len(delete_key) > 0:
            form = ItemCartForm(request.POST)
            delete_idx = int(delete_key[0].split("-")[1])
            request.session["nutrient_cart"].pop(delete_idx)
            request.session.modified = True
        if "save" in request.POST:
            form = ItemCartForm(request.POST, instance=item)
            if form.is_valid():
                with transaction.atomic():
                    form.save()
                    cart = request.session.get("nutrient_cart", [])
                    item.item_nutrients.clear()
                    if len(cart) > 0:
                        for tup in cart:
                            itemnut, created = ItemNutrient.objects.get_or_create(
                                itemnut_name=Nutrient.objects.get(pk=tup[0]),
                                itemnut_val=tup[1],
                                itemnut_unit=Unit.objects.get(pk=tup[2]),
                                itemnut_ref_val=tup[3],
                                itemnut_ref_unit=Unit.objects.get(pk=tup[4])
                            )
                            item.item_nutrients.add(itemnut)
                # reset cart
                request.session["nutrient_cart"] = []
                return redirect("track:item_show")
    else:
        # in case of a get request, build cart from entry
        form = ItemCartForm(instance=item,
                             initial={
            "nutrient_unit": Unit.get_default_unit(),
            "nutrient_ref_val": 100,
            "nutrient_ref_unit": item.item_unit
            })
        cart = []
        for nt in item.item_nutrients.all():
            cart.append([
                nt.itemnut_name.pk,
                float(nt.itemnut_val),
                nt.itemnut_unit.pk,
                float(nt.itemnut_ref_val),
                nt.itemnut_ref_unit.pk
            ])
        request.session["nutrient_cart"] = cart
    
    cart = request.session.get("nutrient_cart", [])
    cart_list = []
    for tup in cart:
        cart_list.append((
            Nutrient.objects.get(pk=tup[0]),
            tup[1],
            Unit.objects.get(pk=tup[2]),
            tup[3],
            Unit.objects.get(pk=tup[4])
        ))
    context = {
        "cart_list": cart_list,
        "form": form,
        "item": item
    }
    
    return render(request, "track/item_update.html", context)