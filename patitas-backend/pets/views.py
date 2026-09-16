import math

from rest_framework import permissions, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import Animal
from .serializers import AnimalSerializer


def distancia_metros(lat1, lon1, lat2, lon2):
    """Fórmula de Haversine: distancia en metros entre dos coordenadas."""
    R = 6378137.0
    d_lat = math.radians(lat2 - lat1)
    d_lon = math.radians(lon2 - lon1)
    a = (
        math.sin(d_lat / 2) ** 2
        + math.cos(math.radians(lat1))
        * math.cos(math.radians(lat2))
        * math.sin(d_lon / 2) ** 2
    )
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))


class IsOwnerOrReadOnly(permissions.BasePermission):
    """Solo quien registró el animal puede editarlo o borrarlo."""

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.registrado_por_id == request.user.id


class AnimalViewSet(viewsets.ModelViewSet):
    """
    GET    /api/animales/              -> lista pública
    POST   /api/animales/              -> crear (requiere login, multipart para la foto)
    GET    /api/animales/<id>/         -> detalle
    PATCH  /api/animales/<id>/         -> editar (solo dueño)
    DELETE /api/animales/<id>/         -> borrar (solo dueño)
    GET    /api/animales/cercanos/?lat=&lng=&radio=1000
    GET    /api/animales/mis-animales/ -> los del usuario autenticado
    """

    queryset = Animal.objects.all()
    serializer_class = AnimalSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly]

    def get_queryset(self):
        qs = Animal.objects.all()
        especie = self.request.query_params.get("especie")
        if especie:
            qs = qs.filter(especie=especie)
        estado = self.request.query_params.get("estado_salud")
        if estado:
            qs = qs.filter(estado_salud=estado)
        return qs

    @action(detail=False, methods=["get"], url_path="cercanos")
    def cercanos(self, request):
        try:
            lat = float(request.query_params.get("lat"))
            lng = float(request.query_params.get("lng"))
        except (TypeError, ValueError):
            return Response(
                {"detail": "Debes enviar los parámetros lat y lng."}, status=400
            )

        radio = float(request.query_params.get("radio", 1000))
        cercanos = [
            a
            for a in self.get_queryset()
            if distancia_metros(lat, lng, a.latitud, a.longitud) <= radio
        ]
        serializer = self.get_serializer(cercanos, many=True)
        return Response(serializer.data)

    @action(
        detail=False,
        methods=["get"],
        url_path="mis-animales",
        permission_classes=[permissions.IsAuthenticated],
    )
    def mis_animales(self, request):
        qs = Animal.objects.filter(registrado_por=request.user)
        return Response(self.get_serializer(qs, many=True).data)
