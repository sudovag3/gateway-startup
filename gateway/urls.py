from django.urls import path, include
from .views import *
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework import permissions

app_name = 'api'


schema_view = get_schema_view(
   openapi.Info(
      title="Your Project API",
      default_version='v1',
      description="API documentation for Your Project",
   ),
   public=True,
   permission_classes=(permissions.AllowAny,),
)


urlpatterns = [
    #Contest
    path('contest/detail/', contest_detail),
    path('contest/create/', CreateContestAPIView.as_view(), name='contest-create'),
    path('contest/update/<int:pk>/', UpdateContestAPIView.as_view(), name='contest-update'),
    path('contest/list/', ListContestAPIView.as_view()),
    path('contest/set_admin/', SetContestAdminAPIView.as_view()),
    path('contest/set_participant/', SetParticipantAPIView.as_view(), name='contest-set-participant'),

    #Rate
    path('rate/all/', ListSubscribeAPIView.as_view()),
    path('rate/my/', ListMySubscribeAPIView.as_view()),
    path('rate/buy/<int:sub_id>', buy_rate),

    #Command
    path('command/create/', CreateCommandAPIView.as_view()),
    path('command/update/<int:pk>/', UpdateCommandAPIView.as_view(), name='update-command'),
    path('command/list/', ListCommandAPIView.as_view()),
    path('command/get/<int:pk>', GetCommandAPIView.as_view()),
    path('command/delete/<int:pk>', DeleteCommandAPIView.as_view(), name='delete-command'),
    path('command/leave/', LeaveFromCommandView.as_view(), name='leave-from-command'),
    path('command/remove/', RemoveParticipantView.as_view(), name='remove-participant'),

    #Solution
    path('solution/send', SendSolutionAPIView.as_view()),

    #Review
    path('review/send/', CreateReviewAPIView.as_view()),

    #Award
    path('award/create/', AwardCreateView.as_view(), name='create_award'),
    path('award/<pk>/update/', AwardUpdateView.as_view(), name='update_award'),
    path('award/<pk>/delete/', AwardDeleteView.as_view(), name='delete_award'),
    path('award/list/', AwardListView.as_view(), name='list_award'),

    #Task
    path('task/create/', TaskCreateView.as_view(), name='create_task'),
    path('task/<pk>/update/', TaskUpdateView.as_view(), name='update_task'),
    path('task/<pk>/delete/', TaskDeleteView.as_view(), name='delete_task'),
    path('task/list/', TaskListView.as_view(), name='list_task'),

    #Invite
    path('invite/create/', CreateInviteView.as_view(), name='create_invite'),
    path('invite/send/', SendInviteView.as_view(), name='send_invite'),
    path('invite/list/', InviteListView.as_view(), name='list_invite'),
    path('application/list/', ApplicationListView.as_view(), name='list_application'),
    path('application/accept-decline/', AcceptDeclineApplicationView.as_view(),
         name='accept_decline_application'),
    path('invite/accept-decline/', AcceptDeclineInviteView.as_view(), name='accept_decline_invite'),


    #Docs
    path('docs/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui')


    # path('<slug>/order', app_order, name='bot-activate')
]