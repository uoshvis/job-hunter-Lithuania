from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import list_route, detail_route
from django.contrib import messages

from positions.serializers import PositionsSerializer
from positions.models import Positions
from .tasks import scrape_ads


class PositionsViewSet(viewsets.ViewSet):

    def retrieve(self, request, pk=None):
        """
        Returns the given position by id
        """
        queryset = Positions.objects.filter(id=pk).first()
        if queryset:
            serializer = PositionsSerializer(queryset)
            data = serializer.data
            return Response(data)
        else:
            return Response(status=status.HTTP_404_NOT_FOUND)

    def list(self, request):
        """
        Returns a list of all existing positions
        """
        queryset = Positions.objects.all()
        serializer = PositionsSerializer(queryset, many=True)
        data = serializer.data
        return Response(data)

    def destroy(self, request, pk=None):
        """
        Delete given position by id
        """
        queryset = Positions.objects.filter(id=pk).first()
        if queryset:
            queryset.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        else:
            return Response(status=status.HTTP_404_NOT_FOUND)

    @list_route()
    def search(self, request):
        """
        Initialize scraper using parameters ?city=City&keyword=keyword
        starts Celery Worker Process
        """
        if request.query_params:
            city = request.query_params.get('city', '')
            keyword = request.query_params.get('keyword', '')
            scrape_ads.delay(city=city, keyword=keyword)
            messages.success(self.request, 'We are searching')
            return Response({'message': 'Searching'})
        else:
            return Response(
                {'message': 'Nothing to search'},
                status=status.HTTP_204_NO_CONTENT
            )

    @detail_route(methods=['PUT'])
    def comment(self, request, pk=None):
        """
        Add your comment
        """
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

    @list_route()
    def filter(self, request):
        """
        Filter positions by given ids ?ids=id1,id2
        """
        if request.query_params:
            ids = request.query_params.get('ids', None)
            if ids:
                ids = ids.split(',')
                queryset = Positions.objects(id__in=ids)
                if queryset:
                    serializer = PositionsSerializer(queryset, many=True)
                    data = serializer.data
                    return Response(data)
        else:
            return Response(status=status.HTTP_404_NOT_FOUND)
