from rest_framework import serializers

from gateway.models import Contest, Subscribe, Command, Solution


class ContestAdminSerializer(serializers.ModelSerializer):
    class Meta:
        model = Contest
        fields = '__all__'


class SubscribeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subscribe
        fields = '__all__'


class ContestCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Contest
        fields = '__all__'


class ContestUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Contest
        fields = '__all__'


class ContestParticipantSerializer(serializers.ModelSerializer):
    class Meta:
        model = Contest
        fields = ['id',
                  'name',
                  'status',
                  'description',
                  'reg_start',
                  'reg_end',
                  'date_start',
                  'date_end',
                  'logo',
                  'command_min',
                  'command_max',
                  'region',
                  'tasks',
                  'tags'
                  ]


class CommandCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Command
        fields = '__all__'


class CommandUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Command
        fields = '__all__'


class CommandListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Command
        fields = ['id',
                  'command_name',
                  'open_to_invite',
                  'contest',
                  'admin',
                  'participants',
                  'tags'
                  ]


class SolutionListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Solution
        fields = '__all__'