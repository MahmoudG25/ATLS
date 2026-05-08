from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from services.upload_service import upload_file


class UploadFileView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        file_obj = request.FILES.get("file")
        if not file_obj:
            return Response(
                {"detail": "No file was uploaded."}, status=status.HTTP_400_BAD_REQUEST
            )
        secure_url = upload_file(file_obj)
        return Response({"file_url": secure_url}, status=status.HTTP_201_CREATED)
