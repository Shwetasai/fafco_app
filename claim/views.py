from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from .models import Claim,ClaimDocument
from .serializers import ClaimSerializer, ClaimDocumentSerializer

class ClaimListCreateAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        claims = Claim.objects.filter(dealer=request.user)
        serializer = ClaimSerializer(claims, many=True)
        return Response(serializer.data)

    def post(self, request, *args, **kwargs):
        serializer = ClaimSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(dealer=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ClaimRetrieveUpdateAPIView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request, pk, *args, **kwargs):
        serializer = ClaimSerializer(get_object_or_404(Claim, pk=pk, dealer=self.request.user))
        return Response(serializer.data)

    def put(self, request, pk, *args, **kwargs):
        claim = get_object_or_404(Claim, pk=pk, dealer=self.request.user)
        serializer = ClaimSerializer(claim, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk, *args, **kwargs):
        get_object_or_404(Claim, pk=pk, dealer=self.request.user).delete()
        return Response({"message": "Claim deleted successfully."}, status=status.HTTP_204_NO_CONTENT)


class ClaimDocumentUploadAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, pk, *args, **kwargs):
        claim = get_object_or_404(Claim, pk=pk, dealer=request.user)
        serializer = ClaimDocumentSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(claim=claim)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def get(self, request, pk, doc_pk=None, *args, **kwargs):
        if doc_pk:
            document = get_object_or_404(ClaimDocument, pk=doc_pk, claim__pk=pk, claim__dealer=request.user)
            serializer = ClaimDocumentSerializer(document)
        else:
            documents = ClaimDocument.objects.filter(claim__pk=pk, claim__dealer=request.user)
            serializer = ClaimDocumentSerializer(documents, many=True)
        return Response(serializer.data)

    def put(self, request, pk, doc_pk, *args, **kwargs):
        document = get_object_or_404(ClaimDocument, pk=doc_pk, claim__pk=pk, claim__dealer=request.user)
        serializer = ClaimDocumentSerializer(document, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk, doc_pk, *args, **kwargs):
        document = get_object_or_404(ClaimDocument, pk=doc_pk, claim__pk=pk, claim__dealer=request.user)
        document.delete()
        return Response({"message": "Document deleted successfully."}, status=status.HTTP_204_NO_CONTENT)