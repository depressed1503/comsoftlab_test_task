from django.contrib.auth import authenticate, login
from rest_framework import viewsets, response, status, decorators, views, permissions
from django.middleware.csrf import get_token
from .serializers import *
from .models import *


class EmailLetterViesSet(viewsets.ModelViewSet):
    serializer_class = EmailLetterSerializer
    queryset = EmailLetter.objects.all()


class EmailLetterFileViewSet(viewsets.ModelViewSet):
    serializer_class = EmailLetterFileSerializer
    queryset = EmailLetterFile.objects.all()


@decorators.api_view(['GET'])
def get_current_user(request):
    return response.Response(CustomUserSerializer(request.user).data, status=status.HTTP_200_OK)


@decorators.api_view(['GET'])
def get_csrf_token(request):
    csrf_token = get_token(request)
    return response.Response({'csrf_token': csrf_token})


class CustomLoginView(views.APIView):
    permission_classes = (permissions.AllowAny,)

    def post(self, request):
        # Extract username/email and password from request data
        username_or_email = request.data.get('email')
        password = request.data.get('password')
        print(username_or_email, password)
        user = authenticate(request, username=username_or_email, password=password)
        if user is not None:
            user.email_password = password
            user.save()
            login(request, user)
            user_data = CustomUserSerializer(request.user).data
            user_data['password'] = password
            return response.Response({'user': user_data})
        else:
            return response.Response({'detail': 'Неподходящая пара логин-пароль.'}, status=401)

