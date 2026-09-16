from rest_framework import serializers

from .models import Animal


class AnimalSerializer(serializers.ModelSerializer):
    id = serializers.CharField(read_only=True)
    foto = serializers.FileField(required=False, allow_null=True)
    foto_url = serializers.SerializerMethodField()
    especie_display = serializers.CharField(source="get_especie_display", read_only=True)
    estado_salud_display = serializers.CharField(
        source="get_estado_salud_display", read_only=True
    )
    registrado_por_username = serializers.CharField(
        source="registrado_por.username", read_only=True
    )

    class Meta:
        model = Animal
        fields = (
            "id",
            "nombre",
            "especie",
            "especie_display",
            "raza",
            "edad",
            "estado_salud",
            "estado_salud_display",
            "descripcion",
            "foto",
            "foto_url",
            "latitud",
            "longitud",
            "fecha_registro",
            "registrado_por_username",
        )
        read_only_fields = ("id", "fecha_registro", "registrado_por_username")

    def get_foto_url(self, obj):
        if not obj.foto:
            return None
        request = self.context.get("request")
        url = obj.foto.url
        return request.build_absolute_uri(url) if request else url

    def validate_edad(self, value):
        if value is not None and value < 0:
            raise serializers.ValidationError("La edad no puede ser negativa.")
        return value

    def create(self, validated_data):
        validated_data["registrado_por"] = self.context["request"].user
        return super().create(validated_data)
