from rest_framework_mongoengine import serializers
from positions.models import Positions


class PositionsSerializer(serializers.DocumentSerializer):
    class Meta:
        model = Positions
        fields = '__all__'
