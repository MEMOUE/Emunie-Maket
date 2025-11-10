# EmunieBack/user/password_reset_views.py

from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from .models import PasswordResetToken
from .serializers import (
    PasswordResetRequestSerializer,
    PasswordResetConfirmSerializer,
    PasswordResetVerifyTokenSerializer
)

User = get_user_model()


@api_view(['POST'])
@permission_classes([AllowAny])
def request_password_reset(request):
    """
    Demander un lien de réinitialisation de mot de passe

    POST /api/user/password/reset/request/
    Body: { "email": "user@example.com" }
    """
    serializer = PasswordResetRequestSerializer(data=request.data)

    if not serializer.is_valid():
        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )

    email = serializer.validated_data['email']

    try:
        user = User.objects.get(email=email, is_active=True)

        # Générer un token de réinitialisation
        reset_token = PasswordResetToken.generate_token(user, expiry_hours=24)

        # Construire l'URL de réinitialisation
        frontend_url = getattr(settings, 'FRONTEND_URL', 'http://localhost:4200')
        reset_url = f"{frontend_url}/reset-password?token={reset_token.token}"

        # Préparer l'email
        subject = "Réinitialisation de votre mot de passe - Emunie Market"
        message = f"""
Bonjour {user.first_name or user.username},

Vous avez demandé la réinitialisation de votre mot de passe sur Emunie Market.

Cliquez sur le lien ci-dessous pour réinitialiser votre mot de passe :
{reset_url}

Ce lien est valide pendant 24 heures.

Si vous n'avez pas demandé cette réinitialisation, ignorez simplement cet email.

Cordialement,
L'équipe Emunie Market
"""

        html_message = f"""
<!DOCTYPE html>
<html>
<head>
    <style>
        body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
        .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
        .header {{ background: linear-gradient(135deg, #f97316 0%, #fb923c 100%); color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0; }}
        .content {{ background: #f9fafb; padding: 30px; border-radius: 0 0 10px 10px; }}
        .button {{ display: inline-block; background: #f97316; color: white; padding: 15px 30px; text-decoration: none; border-radius: 8px; font-weight: bold; margin: 20px 0; }}
        .button:hover {{ background: #ea580c; }}
        .footer {{ text-align: center; margin-top: 20px; color: #6b7280; font-size: 14px; }}
        .warning {{ background: #fef3c7; border-left: 4px solid #f59e0b; padding: 15px; margin: 20px 0; border-radius: 4px; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🔐 Réinitialisation de mot de passe</h1>
        </div>
        <div class="content">
            <p>Bonjour <strong>{user.first_name or user.username}</strong>,</p>

            <p>Vous avez demandé la réinitialisation de votre mot de passe sur <strong>Emunie Market</strong>.</p>

            <p style="text-align: center;">
                <a href="{reset_url}" class="button">Réinitialiser mon mot de passe</a>
            </p>

            <p>Ou copiez ce lien dans votre navigateur :</p>
            <p style="background: white; padding: 10px; border-radius: 4px; word-break: break-all;">
                {reset_url}
            </p>

            <div class="warning">
                <strong>⏱️ Important :</strong> Ce lien est valide pendant <strong>24 heures</strong>.
            </div>

            <p>Si vous n'avez pas demandé cette réinitialisation, ignorez simplement cet email. Votre mot de passe restera inchangé.</p>

            <div class="footer">
                <p>Cordialement,<br>L'équipe <strong>Emunie Market</strong></p>
                <p style="font-size: 12px; color: #9ca3af;">Cet email a été envoyé automatiquement, merci de ne pas y répondre.</p>
            </div>
        </div>
    </div>
</body>
</html>
"""

        # Envoyer l'email
        try:
            send_mail(
                subject=subject,
                message=message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[email],
                html_message=html_message,
                fail_silently=False,
            )
        except Exception as e:
            print(f"Error sending email: {e}")
            # En développement, afficher le lien dans la console
            print(f"\n{'=' * 80}")
            print(f"PASSWORD RESET LINK (Development Mode):")
            print(f"{reset_url}")
            print(f"{'=' * 80}\n")

    except User.DoesNotExist:
        # Ne pas révéler que l'utilisateur n'existe pas
        pass

    # Toujours retourner un message de succès
    return Response({
        'message': 'Si un compte existe avec cet email, un lien de réinitialisation a été envoyé.',
        'detail': 'Veuillez vérifier votre boîte de réception (et vos spams).'
    }, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([AllowAny])
def verify_reset_token(request):
    """
    Vérifier la validité d'un token de réinitialisation

    POST /api/user/password/reset/verify/
    Body: { "token": "token_string" }
    """
    serializer = PasswordResetVerifyTokenSerializer(data=request.data)

    if not serializer.is_valid():
        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )

    token_string = serializer.validated_data['token']

    try:
        token = PasswordResetToken.objects.get(token=token_string)

        if not token.is_valid:
            if token.is_used:
                return Response({
                    'valid': False,
                    'error': 'Ce lien a déjà été utilisé.'
                }, status=status.HTTP_400_BAD_REQUEST)
            elif token.is_expired:
                return Response({
                    'valid': False,
                    'error': 'Ce lien a expiré. Veuillez demander un nouveau lien.'
                }, status=status.HTTP_400_BAD_REQUEST)

        return Response({
            'valid': True,
            'email': token.user.email,
            'username': token.user.username
        }, status=status.HTTP_200_OK)

    except PasswordResetToken.DoesNotExist:
        return Response({
            'valid': False,
            'error': 'Lien de réinitialisation invalide.'
        }, status=status.HTTP_404_NOT_FOUND)


@api_view(['POST'])
@permission_classes([AllowAny])
def confirm_password_reset(request):
    """
    Confirmer la réinitialisation avec un nouveau mot de passe

    POST /api/user/password/reset/confirm/
    Body: {
        "token": "token_string",
        "new_password": "new_password",
        "new_password_confirm": "new_password"
    }
    """
    serializer = PasswordResetConfirmSerializer(data=request.data)

    if not serializer.is_valid():
        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )

    token_string = serializer.validated_data['token']
    new_password = serializer.validated_data['new_password']

    try:
        token = PasswordResetToken.objects.get(token=token_string)

        # Vérifier la validité du token
        if not token.is_valid:
            if token.is_used:
                return Response({
                    'error': 'Ce lien a déjà été utilisé.'
                }, status=status.HTTP_400_BAD_REQUEST)
            elif token.is_expired:
                return Response({
                    'error': 'Ce lien a expiré. Veuillez demander un nouveau lien.'
                }, status=status.HTTP_400_BAD_REQUEST)

        # Réinitialiser le mot de passe
        user = token.user
        user.set_password(new_password)
        user.save()

        # Marquer le token comme utilisé
        token.is_used = True
        token.save()

        # Envoyer un email de confirmation (optionnel)
        try:
            subject = "Votre mot de passe a été réinitialisé - Emunie Market"
            message = f"""
Bonjour {user.first_name or user.username},

Votre mot de passe a été réinitialisé avec succès sur Emunie Market.

Si vous n'êtes pas à l'origine de ce changement, contactez immédiatement notre support.

Cordialement,
L'équipe Emunie Market
"""

            send_mail(
                subject=subject,
                message=message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[user.email],
                fail_silently=True,
            )
        except Exception as e:
            print(f"Error sending confirmation email: {e}")

        return Response({
            'message': 'Votre mot de passe a été réinitialisé avec succès.',
            'detail': 'Vous pouvez maintenant vous connecter avec votre nouveau mot de passe.'
        }, status=status.HTTP_200_OK)

    except PasswordResetToken.DoesNotExist:
        return Response({
            'error': 'Lien de réinitialisation invalide.'
        }, status=status.HTTP_404_NOT_FOUND)