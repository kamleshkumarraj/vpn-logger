from django.db import models

class VPNSession(models.Model):
    vpn_id = models.CharField(max_length=50)
    name = models.CharField(max_length=100)
    status = models.CharField(max_length=50)
    uptime = models.CharField(max_length=100)
    client_ip = models.GenericIPAddressField(unique=True)
    proposal = models.CharField(max_length=255)
    bytes_in = models.BigIntegerField(default=0)
    bytes_out = models.BigIntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.client_ip} - {self.status}"
