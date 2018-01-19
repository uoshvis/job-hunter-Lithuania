from positions.serializers import PositionsSerializer
from positions.models import Positions
from utils.main import search_positions

from rest_framework.generics import RetrieveUpdateDestroyAPIView, ListAPIView


class PositionsEditView(RetrieveUpdateDestroyAPIView):
    queryset = Positions.objects.all()
    serializer_class = PositionsSerializer
    lookup_field = 'id'


class PositionsListView(ListAPIView):
    serializer_class = PositionsSerializer
    # queryset is evaluated only once  - use get_queryset instead

    def get_queryset(self):
        return Positions.objects.all()


class PositionsSearchView(ListAPIView):
    serializer_class = PositionsSerializer

    def get_queryset(self):
        if self.request.query_params:
            city = self.request.query_params.get('city', '')
            keyword = self.request.query_params.get('keyword', '')
            ids = search_positions(city=city, keyword=keyword)
        return Positions.objects.filter(ad_id__in=ids)


# TODO how about statuses??
