import json

from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404


# Create your views here.

# Contest
from django.views.decorators.http import require_http_methods
from rest_framework import status
from rest_framework.decorators import permission_classes
from rest_framework.generics import CreateAPIView, UpdateAPIView, ListAPIView, RetrieveAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from gateway.models import Contest, Subscribe, Command, Solution
from django.db.models import Q

# Distribution


# Test form
from django.shortcuts import render
from django.http import *

from .enums.user_contest_type import UserContestType
from .forms import TestForm, SendSolutionValidationForm
# from .bot.start import start_bot

import asyncio

from .permissions import ContestIsOwnedByMe, CommandIsOwnedByMe, SolutionIsOwnedByMe, IsSolutionIsCorrect, \
    IsNoHaveCommand, IsRequestInRegTime
from .serializers import ContestAdminSerializer, ContestParticipantSerializer, ContestCreateSerializer, \
    ContestUpdateSerializer, SubscribeSerializer, CommandListSerializer, CommandUpdateSerializer, \
    CommandCreateSerializer, SolutionListSerializer
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
        return Subscribe.objects.filter(id = self.request.user.subscribe.id)


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


class CreateCommandAPIView(CreateAPIView):
    serializer_class = CommandCreateSerializer
    permission_classes = [IsAuthenticated, IsNoHaveCommand, IsRequestInRegTime]


class UpdateCommandAPIView(UpdateAPIView):
    serializer_class = CommandUpdateSerializer
    permission_classes = [IsAuthenticated, CommandIsOwnedByMe]
    queryset = Command.objects.all()


class ListCommandAPIView(ListAPIView):
    serializer_class = CommandListSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self, *args, **kwargs):
        tags = list(self.request.GET.get('tags', ""))
        contest_id = self.request.GET.get('contest_id', "")
        task_id = self.request.GET.get('task_id', "")

        queryset = Command.objects.all()

        if tags:
            queryset = queryset.filter(tags__name__in=tags)
        if contest_id:
            queryset = queryset.filter(contest_id=contest_id)
        if task_id:
            queryset = queryset.filter(task_id=task_id)

        return queryset


class GetCommandAPIView(RetrieveAPIView):
    serializer_class = CommandCreateSerializer
    permission_classes = [IsAuthenticated, CommandIsOwnedByMe]
    queryset = Command.objects.all()


class SendSolutionAPIView(APIView):

    permission_classes = (IsAuthenticated, IsSolutionIsCorrect)

    def post(self, request):
        form = SendSolutionValidationForm(request.data)
        if form.is_valid():
            solution_url = form.cleaned_data['solution_url']
            command_id = form.cleaned_data['command_id']

            command = Command.objects.filter(id = command_id).first()
            sol, created = Solution.objects.get_or_create(
                command_id=command_id,
                url=solution_url,
                task_id=command.task.id,
                status="CRE"
            )

            # Вам нужно будет добавить здесь вашу логику обработки данных формы
            return Response(SolutionListSerializer(sol).data, status=status.HTTP_200_OK)
        else:
            errors = form.errors.as_json()
            return Response({'success': False, 'errors': errors}, status=status.HTTP_400_BAD_REQUEST)


class ListSolutionAPIView(ListAPIView):
    serializer_class = SolutionListSerializer
    permission_classes = [IsAuthenticated, SolutionIsOwnedByMe]

    def get_queryset(self, *args, **kwargs):
        reviewed = self.request.GET.get('reviewed', "None")
        queryset = Solution.objects.all()

        if reviewed != "None":
            if reviewed == True:
                queryset = queryset.filter(command__review_to_command__reviewer_id=self.request.user.id)
            elif reviewed == False:
                queryset = queryset.filter(~Q(command__review_to_command__reviewer_id=self.request.user.id))

        return queryset