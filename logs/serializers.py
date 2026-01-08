from rest_framework import serializers
from .models import VPNSession

class VPNSessionSerializer(serializers.ModelSerializer):
    class Meta:
        model = VPNSession
        fields = "__all__"
