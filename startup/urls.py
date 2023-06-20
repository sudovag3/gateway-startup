from django.contrib import admin
from django.urls import path, include
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework import permissions

from gateway import views
from gateway.views import home, home_creator, home_participant, contest_create, contest_front_detail

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
    path('admin/', admin.site.urls),
    path('api/v1/', include('gateway.urls', namespace='api')),
    path('accounts/', include('allauth.urls')),

    #Front
    path('', home),

    #Добавляем новый рут и прокидываем наш созданный view
    path('contest/detail/<contest_id>', contest_front_detail, name='contest-detail'),

    path('creator/', home_creator, name='home-creator'),
    path('creator/contest/create', contest_create, name='contest-create'),

    path('participant/', home_participant, name='home-participant'),


    #Docs
    path('docs/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui')
    # path('distribution/telegram/', views.index),
]
