from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import list_route, detail_route

from positions.serializers import PositionsSerializer
from positions.models import Positions
from main import search_positions


class PositionsViewSet(viewsets.ViewSet):
    """
    Returs positions from db-
    or searches for new positions
    """
    def retrieve(self, request, pk=None):
        queryset = Positions.objects.filter(id=pk).first()
        if queryset:
            serializer = PositionsSerializer(queryset)
            data = serializer.data
            return Response(data)
        else:
            return Response(status=status.HTTP_404_NOT_FOUND)

    def list(self, request):
        queryset = Positions.objects.all()
        serializer = PositionsSerializer(queryset, many=True)
        data = serializer.data
        return Response(data)

    def destroy(self, request, pk=None):
        queryset = Positions.objects.filter(id=pk).first()
        if queryset:
            queryset.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        else:
            return Response(status=status.HTTP_404_NOT_FOUND)

    @list_route(methods=['GET'])
    def search(self, request):
        if request.query_params:
            city = request.query_params.get('city', '')
            keyword = request.query_params.get('keyword', '')
            search_positions(city=city, keyword=keyword)
        queryset = Positions.objects.all()
        serializer = PositionsSerializer(queryset, many=True)
        data = serializer.data

        return Response(data)

    @detail_route(methods=['PUT'])
    def comment(self, request, pk=None):
        queryset = Positions.objects.filter(id=pk).first()
        if queryset:
            comment = request.data.get('comment', None)
            setattr(queryset, 'comment', comment)
            queryset.save()
            serializer = PositionsSerializer(queryset)
            data = serializer.data
            return Response(data)
        else:
            return Response(status=status.HTTP_404_NOT_FOUND)
