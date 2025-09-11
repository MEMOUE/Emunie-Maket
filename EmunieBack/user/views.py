from rest_framework import generics, status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.views import APIView
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from django.db.models import Q
from .models import UserRating, Conversation, Message
from .serializers import (
    UserRegistrationSerializer, UserProfileSerializer, UserListSerializer,
    UserRatingSerializer, ConversationSerializer, MessageSerializer,
    PasswordChangeSerializer, EmailVerificationSerializer, PhoneVerificationSerializer
)

User = get_user_model()

class UserRegistrationView(generics.CreateAPIView):
    """Inscription des utilisateurs"""
    serializer_class = UserRegistrationSerializer
    permission_classes = [permissions.AllowAny]
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        
        # Ici vous pouvez ajouter l'envoi d'email de vérification
        # send_verification_email.delay(user.id)
        
        return Response({
            'message': 'Compte créé avec succès. Vérifiez votre email.',
            'user_id': user.id
        }, status=status.HTTP_201_CREATED)

class UserProfileView(generics.RetrieveUpdateAPIView):
    """Profil utilisateur (vue et modification)"""
    serializer_class = UserProfileSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_object(self):
        return self.request.user

class UserDetailView(generics.RetrieveAPIView):
    """Détails publics d'un utilisateur"""
    queryset = User.objects.filter(is_active=True)
    serializer_class = UserListSerializer
    permission_classes = [permissions.AllowAny]

class UserListView(generics.ListAPIView):
    """Liste des utilisateurs"""
    queryset = User.objects.filter(is_active=True)
    serializer_class = UserListSerializer
    permission_classes = [permissions.AllowAny]
    filterset_fields = ['location']
    search_fields = ['username', 'first_name', 'last_name']
    ordering_fields = ['created_at', 'total_ads', 'average_rating']
    ordering = ['-created_at']

class UserRatingListCreateView(generics.ListCreateAPIView):
    """Liste et création des évaluations utilisateur"""
    serializer_class = UserRatingSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        user_id = self.kwargs.get('user_id')
        return UserRating.objects.filter(rated_user_id=user_id)
    
    def perform_create(self, serializer):
        user_id = self.kwargs.get('user_id')
        serializer.save(rater=self.request.user, rated_user_id=user_id)

class ConversationListView(generics.ListAPIView):
    """Liste des conversations de l'utilisateur"""
    serializer_class = ConversationSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return Conversation.objects.filter(
            participants=self.request.user
        ).order_by('-updated_at')

class ConversationDetailView(generics.RetrieveAPIView):
    """Détail d'une conversation"""
    serializer_class = ConversationSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return Conversation.objects.filter(participants=self.request.user)

class MessageListCreateView(generics.ListCreateAPIView):
    """Messages d'une conversation"""
    serializer_class = MessageSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        conversation_id = self.kwargs.get('conversation_id')
        conversation = get_object_or_404(
            Conversation.objects.filter(participants=self.request.user),
            id=conversation_id
        )
        return Message.objects.filter(conversation=conversation)
    
    def perform_create(self, serializer):
        conversation_id = self.kwargs.get('conversation_id')
        conversation = get_object_or_404(
            Conversation.objects.filter(participants=self.request.user),
            id=conversation_id
        )
        serializer.save(sender=self.request.user, conversation=conversation)

class StartConversationView(APIView):
    """Démarrer une conversation avec un utilisateur"""
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        recipient_id = request.data.get('recipient_id')
        if not recipient_id:
            return Response({'error': 'recipient_id requis'}, status=status.HTTP_400_BAD_REQUEST)
        
        recipient = get_object_or_404(User, id=recipient_id)
        
        # Vérifier si une conversation existe déjà
        conversation = Conversation.objects.filter(
            participants=request.user
        ).filter(participants=recipient).first()
        
        if not conversation:
            conversation = Conversation.objects.create()
            conversation.participants.add(request.user, recipient)
        
        serializer = ConversationSerializer(conversation, context={'request': request})
        return Response(serializer.data)

class PasswordChangeView(APIView):
    """Changer le mot de passe"""
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        serializer = PasswordChangeSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            user = request.user
            user.set_password(serializer.validated_data['new_password'])
            user.save()
            return Response({'message': 'Mot de passe changé avec succès'})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def send_email_verification(request):
    """Envoyer un email de vérification"""
    # Ici vous implémenterez l'envoi d'email
    # send_verification_email.delay(request.user.id)
    return Response({'message': 'Email de vérification envoyé'})

@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def verify_email(request):
    """Vérifier l'email avec le token"""
    token = request.data.get('token')
    if not token:
        return Response({'error': 'Token requis'}, status=status.HTTP_400_BAD_REQUEST)
    
    # Ici vous implémenterez la vérification du token
    # Logique de vérification...
    
    return Response({'message': 'Email vérifié avec succès'})

@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def send_phone_verification(request):
    """Envoyer un code de vérification SMS"""
    phone_number = request.data.get('phone_number')
    if not phone_number:
        return Response({'error': 'Numéro de téléphone requis'}, status=status.HTTP_400_BAD_REQUEST)
    
    # Ici vous implémenterez l'envoi de SMS
    # send_sms_verification.delay(request.user.id, phone_number)
    
    return Response({'message': 'Code de vérification envoyé'})

@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def verify_phone(request):
    """Vérifier le téléphone avec le code"""
    serializer = PhoneVerificationSerializer(data=request.data)
    if serializer.is_valid():
        code = serializer.validated_data['code']
        # Ici vous implémenterez la vérification du code
        # Logique de vérification...
        
        request.user.phone_verified = True
        request.user.save()
        return Response({'message': 'Téléphone vérifié avec succès'})
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def user_stats(request):
    """Statistiques de l'utilisateur"""
    user = request.user
    stats = {
        'total_ads': user.total_ads,
        'active_ads': user.ads.filter(status='active').count(),
        'total_views': user.total_views,
        'total_favorites': user.ads.aggregate(
            total=models.Sum('favorites_count')
        )['total'] or 0,
        'average_rating': user.average_rating,
        'total_ratings': user.received_ratings.count(),
        'unread_messages': Message.objects.filter(
            conversation__participants=user,
            is_read=False
        ).exclude(sender=user).count(),
    }
    return Response(stats)