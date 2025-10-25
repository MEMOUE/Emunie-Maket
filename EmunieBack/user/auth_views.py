from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.contrib.auth import authenticate, login, logout
from django.db.models import Q
from .serializers import UserProfileSerializer
from .models import CustomUser

class LoginView(APIView):
    """
    Vue de connexion permettant l'authentification avec username OU email
    """
    permission_classes = [AllowAny]

    def post(self, request):
        username_or_email = request.data.get('username')
        password = request.data.get('password')

        # Validation des champs requis
        if not username_or_email or not password:
            return Response(
                {'detail': 'Identifiant et mot de passe requis'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Chercher l'utilisateur par username OU email
        try:
            # Recherche avec Q objects pour username ou email
            user_obj = CustomUser.objects.get(
                Q(username=username_or_email) | Q(email=username_or_email)
            )
            # Authentifier avec le username trouvé
            # Django authenticate nécessite le username exact
            user = authenticate(username=user_obj.username, password=password)
        except CustomUser.DoesNotExist:
            # Utilisateur non trouvé
            user = None
        except CustomUser.MultipleObjectsReturned:
            # Si plusieurs utilisateurs trouvés (ne devrait pas arriver avec unique=True)
            return Response(
                {'detail': 'Erreur de configuration du compte'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        # Vérifier si l'authentification a réussi
        if user is None:
            return Response(
                {'detail': 'Email/nom d\'utilisateur ou mot de passe incorrect'},
                status=status.HTTP_401_UNAUTHORIZED
            )

        # Vérifier si le compte est actif
        if not user.is_active:
            return Response(
                {'detail': 'Ce compte est désactivé'},
                status=status.HTTP_403_FORBIDDEN
            )

        # Créer ou récupérer le token
        token, created = Token.objects.get_or_create(user=user)

        # Connecter l'utilisateur dans la session
        login(request, user)

        # Sérialiser les données utilisateur
        user_serializer = UserProfileSerializer(user)

        return Response({
            'token': token.key,
            'user': user_serializer.data
        }, status=status.HTTP_200_OK)


class LogoutView(APIView):
    """
    Vue de déconnexion
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            # Supprimer le token d'authentification
            request.user.auth_token.delete()
        except Exception as e:
            # Si le token n'existe pas, continuer quand même
            pass

        # Déconnecter l'utilisateur de la session
        logout(request)

        return Response(
            {'detail': 'Déconnexion réussie'},
            status=status.HTTP_200_OK
        )