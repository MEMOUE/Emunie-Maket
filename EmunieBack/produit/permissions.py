from rest_framework import permissions

class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Permission personnalisée pour permettre aux propriétaires d'un objet de le modifier.
    Les permissions de lecture sont autorisées pour toutes les requêtes,
    mais les permissions d'écriture ne sont accordées qu'au propriétaire de l'objet.
    """
    
    def has_object_permission(self, request, view, obj):
        # Permissions de lecture pour toutes les requêtes
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # Permissions d'écriture uniquement pour le propriétaire
        return obj.user == request.user

class IsAdOwner(permissions.BasePermission):
    """
    Permission pour vérifier que l'utilisateur est le propriétaire de l'annonce.
    """
    
    def has_object_permission(self, request, view, obj):
        # Vérifier si l'objet a un attribut 'ad' (pour les images, vidéos, etc.)
        if hasattr(obj, 'ad'):
            return obj.ad.user == request.user
        # Sinon, vérifier directement l'attribut 'user'
        elif hasattr(obj, 'user'):
            return obj.user == request.user
        return False