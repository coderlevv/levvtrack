from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from ..models import Nutrient
from ..forms import NutrientForm


@login_required
def nutrient_show(request):
    nutrient_list = Nutrient.objects.all()
    context = { 'nutrient_list': nutrient_list }
    return render(request, "track/nutrient_show.html", context)


@login_required
def nutrient_create(request):
    if request.method == "POST":
        form = NutrientForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("track:nutrient_show")
    form = NutrientForm()
    context = { 'form': form }
    return render(request, "track/nutrient_create.html", context)


@login_required
def nutrient_update(request, nutrient_id):
    nutrient = get_object_or_404(Nutrient, pk=nutrient_id)
    if request.method == "POST":
        form = NutrientForm(request.POST, instance=nutrient)
        if form.is_valid():
            form.save()
            return redirect("track:nutrient_show")
    else:
        form = NutrientForm(instance=nutrient)
    context = { 'form': form, 'nutrient': nutrient }
    return render(request, "track/nutrient_update.html", context)


@login_required
def nutrient_delete(request, nutrient_id):
    nutrient = get_object_or_404(Nutrient, pk=nutrient_id)
    context = { "nutrient": nutrient }
    if request.method == "POST":
        nutrient.delete()
        return redirect("track:nutrient_show")
    return render(request, "track/nutrient_delete.html", context)
