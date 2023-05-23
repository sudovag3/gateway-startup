from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404


# Create your views here.

# Contest
from django.views.decorators.http import require_http_methods
from rest_framework.generics import CreateAPIView, UpdateAPIView, ListAPIView
from rest_framework.permissions import IsAuthenticated

from gateway.models import Contest, Subscribe

# Distribution


# Test form
from django.shortcuts import render
from django.http import *

from .enums.user_contest_type import UserContestType
from .forms import TestForm
# from .bot.start import start_bot

import asyncio

from .permissions import ContestIsOwnedByMe
from .serializers import ContestAdminSerializer, ContestParticipantSerializer, ContestCreateSerializer, \
    ContestUpdateSerializer, SubscribeSerializer
from .utils import type_of_user_contest


# def index(request):
#     if request.method == "POST":
#         token = request.POST.get("token")
#         output = "<h1><Бот с этим токеном: {0}</h1>" \
#                  "<h2>Успешно создан!</h2>".format(token)
#         asyncio.run(start_bot(token))
#
#         return HttpResponse(output)
#     else:
#         userform = TestForm()
#         return render(request, "../templates/index.html", {'form': userform})


@require_http_methods(["GET"])
@login_required
def contest_detail(request):
    id = request.GET.get("id", "")
    contest_qs = get_object_or_404(Contest, id=id)
    type = type_of_user_contest(request.user, id)

    if type == UserContestType.admin:
        serializer = ContestAdminSerializer(contest_qs)
    else:
        serializer = ContestParticipantSerializer(contest_qs)

    return JsonResponse(serializer.data, safe=False)


@require_http_methods(["GET"])
@login_required
def contest_detail(request):
    id = request.GET.get("id", "")
    contest_qs = get_object_or_404(Contest, id=id)
    type = type_of_user_contest(request.user, id)

    if type == UserContestType.admin:
        serializer = ContestAdminSerializer(contest_qs)
    else:
        serializer = ContestParticipantSerializer(contest_qs)

    return JsonResponse(serializer.data, safe=False)


class CreateContestAPIView(CreateAPIView):
    serializer_class = ContestCreateSerializer
    permission_classes = [IsAuthenticated]


class UpdateContestAPIView(UpdateAPIView):
    serializer_class = ContestUpdateSerializer
    permission_classes = [IsAuthenticated, ContestIsOwnedByMe]
    queryset = Contest.objects.all()


class ListSubscribeAPIView(ListAPIView):
    serializer_class = SubscribeSerializer
    permission_classes = [IsAuthenticated]
    queryset = Subscribe.objects.all()


class ListMySubscribeAPIView(ListAPIView):
    serializer_class = SubscribeSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Subscribe.objects.filter(id = self.request.user.subscribes.id)


def buy_rate(request, sub_id):
    return HttpResponse("")


class ListContestAPIView(ListAPIView):
    serializer_class = ContestParticipantSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self, *args, **kwargs):
        tags = list(self.request.GET.get('tags', ""))
        status = self.request.GET.get('status', "")

        queryset = Contest.objects.all()

        if tags:
            queryset = queryset.filter(tags__name__in=tags)
        if status:
            queryset = queryset.filter(status=status)

        return queryset


    # def get_queryset(self, *args, **kwargs):
    #
    #     contest_id = kwargs.get('contest_id')
    #     print(contest_id + "!!!")
    #     contest = get_object_or_404(Contest, id=contest_id)
    #     return contest









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
