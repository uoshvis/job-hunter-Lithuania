from rest_framework_mongoengine import serializers
from positions.models import Positions


class PositionsSerializer(serializers.DocumentSerializer):
    class Meta:
        model = Positions
        fields = '__all__'
        read_only_fields = ('id', 'ad_id', 'position', 'place')

        # Another way:
        # extra_kwargs = {
        #     'id': {'read_only': True},
        # }
