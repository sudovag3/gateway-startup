from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404


# Create your views here.

# Contest
from gateway.models import Contest

# Distribution


# Test form
from django.shortcuts import render
from django.http import *
from .forms import TestForm
from .bot.start import start_bot

import asyncio


def index(request):
    if request.method == "POST":
        token = request.POST.get("token")
        output = "<h1><Бот с этим токеном: {0}</h1>" \
                 "<h2>Успешно создан!</h2>".format(token)
        asyncio.run(start_bot(token))

        return HttpResponse(output)
    else:
        userform = TestForm()
        return render(request, "../templates/index.html", {'form': userform})













# @login_required
# def contest_detail(request, id):
#     contest_qs = get_object_or_404(Contest, id=id)
#     type = type_of_user_contest(request.user, contest_qs)
#     if contest_owner_required(request.user, product_qs.category.bot.slug):
#         context = {
#             'product': product_qs
#         }
#         return render(request, "shop/products/product_detail.html", context)
#     else:
#         return HttpResponseNotFound("Sorry, вам не сюда)")
