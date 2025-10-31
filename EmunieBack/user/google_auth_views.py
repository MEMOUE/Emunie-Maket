from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework.authtoken.models import Token
from google.oauth2 import id_token
from google.auth.transport import requests
from django.conf import settings
from django.contrib.auth import get_user_model
from django.db import transaction
import secrets

User = get_user_model()


class GoogleAuthView(APIView):
    """
    Vue pour l'authentification/inscription via Google OAuth
    """
    permission_classes = [AllowAny]

    def post(self, request):
        """
        Authentifie ou crée un utilisateur avec le token Google

        Body params:
        - token: Google ID token (obligatoire)
        """
        token = request.data.get('token')

        if not token:
            return Response(
                {'detail': 'Token Google requis'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            # Vérifier le token Google
            idinfo = id_token.verify_oauth2_token(
                token,
                requests.Request(),
                settings.GOOGLE_CLIENT_ID
            )

            # Vérifier que le token provient bien de Google
            if idinfo['iss'] not in ['accounts.google.com', 'https://accounts.google.com']:
                raise ValueError('Wrong issuer.')

            # Extraire les informations de l'utilisateur
            google_user_id = idinfo['sub']
            email = idinfo.get('email')
            email_verified = idinfo.get('email_verified', False)
            first_name = idinfo.get('given_name', '')
            last_name = idinfo.get('family_name', '')
            picture = idinfo.get('picture', '')

            if not email:
                return Response(
                    {'detail': 'Email non fourni par Google'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Chercher ou créer l'utilisateur
            with transaction.atomic():
                user = None
                created = False

                # 1. Chercher par google_id
                try:
                    user = User.objects.get(google_id=google_user_id)
                except User.DoesNotExist:
                    # 2. Chercher par email
                    try:
                        user = User.objects.get(email=email)
                        # Lier le compte Google
                        user.google_id = google_user_id
                        if email_verified:
                            user.email_verified = True
                        user.save()
                    except User.DoesNotExist:
                        # 3. Créer un nouveau compte
                        username = self._generate_username(email, first_name, last_name)

                        user = User.objects.create_user(
                            username=username,
                            email=email,
                            first_name=first_name,
                            last_name=last_name,
                            google_id=google_user_id,
                            email_verified=email_verified,
                            password=None  # Pas de mot de passe pour OAuth
                        )

                        # Définir un mot de passe inutilisable
                        user.set_unusable_password()
                        user.save()
                        created = True

            # Vérifier si le compte est actif
            if not user.is_active:
                return Response(
                    {'detail': 'Ce compte est désactivé'},
                    status=status.HTTP_403_FORBIDDEN
                )

            # Créer ou récupérer le token d'authentification
            token, _ = Token.objects.get_or_create(user=user)

            # Préparer les données utilisateur
            from .serializers import UserProfileSerializer
            user_serializer = UserProfileSerializer(user)

            return Response({
                'token': token.key,
                'user': user_serializer.data,
                'created': created,
                'message': 'Compte créé avec succès' if created else 'Connexion réussie'
            }, status=status.HTTP_200_OK)

        except ValueError as e:
            # Token invalide
            return Response(
                {'detail': f'Token Google invalide: {str(e)}'},
                status=status.HTTP_401_UNAUTHORIZED
            )
        except Exception as e:
            # Erreur serveur
            return Response(
                {'detail': f'Erreur lors de l\'authentification Google: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def _generate_username(self, email, first_name, last_name):
        """
        Génère un nom d'utilisateur unique basé sur l'email
        """
        # Utiliser la partie avant @ de l'email
        base_username = email.split('@')[0]

        # Nettoyer le username (enlever caractères spéciaux)
        base_username = ''.join(c for c in base_username if c.isalnum() or c in ['_', '-'])

        # Limiter la longueur
        base_username = base_username[:50]

        # Vérifier l'unicité
        username = base_username
        counter = 1

        while User.objects.filter(username=username).exists():
            # Ajouter un suffixe numérique
            random_suffix = secrets.token_hex(3)  # 6 caractères hexadécimaux
            username = f"{base_username}_{random_suffix}"
            counter += 1

            if counter > 100:  # Protection contre boucle infinie
                username = f"{base_username}_{secrets.token_hex(4)}"
                break

        return username


class GoogleAuthCallbackView(APIView):
    """
    Vue de callback pour OAuth (optionnelle, pour flux serveur)
    """
    permission_classes = [AllowAny]

    def get(self, request):
        """
        Gère le callback OAuth de Google
        """
        code = request.GET.get('code')

        if not code:
            return Response(
                {'detail': 'Code d\'autorisation manquant'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # TODO: Échanger le code contre un token d'accès
        # Cette méthode est pour le flux serveur OAuth

        return Response({
            'message': 'Callback OAuth reçu'
        })