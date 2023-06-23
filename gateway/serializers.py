from rest_framework import serializers

from gateway.models import Contest, Subscribe, Command, Solution, Tag, User, Review, Award, Task, Invite


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = '__all__'


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'


class CommandSerializer(serializers.ModelSerializer):
    # tags = TagSerializer(read_only=True, many=True)
    # admin = UserSerializer(many=True)
    # participant = UserSerializer(many=True)
    participants = serializers.StringRelatedField(many=True)
    admin = serializers.StringRelatedField()

    class Meta:
        model = Command
        fields = '__all__'





class ContestAdminSerializer(serializers.ModelSerializer):
    tags = TagSerializer(read_only=True, many=True)
    contest_admins = UserSerializer(read_only=True, many=True)

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
        read_only_fields = ['status', 'owner']


class ContestUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Contest
        fields = '__all__'
        read_only_fields = ['status', 'owner']


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
                  'participant_cap',
                  'command_min',
                  'command_max',
                  'region',
                  'tags'
                  ]


class CommandCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Command
        fields = [
            'command_name',
            'open_to_invite',
            'contest',
            'admin'
        ]

class CommandUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Command
        fields = [
            'command_name',
            'task',
            'open_to_invite'
        ]


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


class ReviewCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = '__all__'


class TaskSerializer(serializers.ModelSerializer):

    class Meta:
        model = Task
        fields = '__all__'


class AwardGetSerializer(serializers.ModelSerializer):
    task = TaskSerializer(read_only=True)
    command = CommandSerializer(read_only=True)

    class Meta:
        model = Award
        fields = '__all__'


class AwardSerializer(serializers.ModelSerializer):

    class Meta:
        model = Award
        fields = '__all__'


class TaskGetSerializer(serializers.ModelSerializer):
    contest = ContestParticipantSerializer(read_only=True)
    tags = TagSerializer(read_only=True, many=True)

    class Meta:
        model = Task
        fields = '__all__'





class InviteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Invite
        fields = '__all__'