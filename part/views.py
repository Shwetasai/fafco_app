from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.exceptions import NotFound
from .models import Part,Partcsv
from .serializers import PartSerializer,PartcsvSerializer

class PartListCreateAPIView(APIView):
    def get(self, request):
        parts = Part.objects.all()
        serializer = PartSerializer(parts, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = PartSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class PartDetailAPIView(APIView):

    def get(self, request, part_id):
        part = self.get_object(part_id)
        serializer = PartSerializer(part)
        return Response(serializer.data)

    def put(self, request, part_id):
        part = self.get_object(part_id)
        serializer = PartSerializer(part, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, part_id):
        part = self.get_object(part_id)
        serializer = PartSerializer(part, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, part_id):
        part = self.get_object(part_id)
        part.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

class PartcsvListView(APIView):
    def get(self, request):
        parts = Partcsv.objects.all()
        serializer = PartcsvSerializer(parts, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
