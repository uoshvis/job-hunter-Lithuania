from rest_framework_mongoengine import viewsets
from positions.serializers import PositionsSerializer
from positions.models import Positions


class PositionsViewSet(viewsets.ModelViewSet):
    '''
    Contains information about inputs/outputs of a single program
    that may be used in Universe workflows.
    '''
    lookup_field = 'id'
    serializer_class = PositionsSerializer

    def get_queryset(self):
        return Positions.objects.all()
