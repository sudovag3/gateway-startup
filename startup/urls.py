from django.contrib import admin
from django.urls import path, include
from gateway import views
from gateway.views import contest_detail, CreateContestAPIView, UpdateContestAPIView, ListContestAPIView, \
    ListSubscribeAPIView, ListMySubscribeAPIView, buy_rate, CreateCommandAPIView, UpdateCommandAPIView, \
    ListCommandAPIView, GetCommandAPIView, SendSolutionAPIView, SetContestAdminAPIView, SetParticipantAPIView, \
    CreateReviewAPIView

urlpatterns = [
    path('admin/', admin.site.urls),

    #Contest
    path('contest/detail/', contest_detail),
    path('contest/create/', CreateContestAPIView.as_view()),
    path('contest/update/<int:pk>/', UpdateContestAPIView.as_view()),
    path('contest/list/', ListContestAPIView.as_view()),
    path('contest/set_admin/', SetContestAdminAPIView.as_view()),
    path('contest/set_participant/', SetParticipantAPIView.as_view()),

    #Rate
    path('rate/all/', ListSubscribeAPIView.as_view()),
    path('rate/my/', ListMySubscribeAPIView.as_view()),
    path('rate/buy/<int:sub_id>', buy_rate),

    path('command/create/', CreateCommandAPIView.as_view()),
    path('command/update/<int:pk>/', UpdateCommandAPIView.as_view()),
    path('command/list/', ListCommandAPIView.as_view()),
    path('command/get/<int:pk>', GetCommandAPIView.as_view()),

    path('solution/send', SendSolutionAPIView.as_view()),

    path('review/send/', CreateReviewAPIView.as_view())

    # path('distribution/telegram/', views.index),
]
