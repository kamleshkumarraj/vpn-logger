from django.db import models

class VPNSession(models.Model):
    # REQUIRED fields
    vpn_id = models.CharField(max_length=50)
    client_ip = models.GenericIPAddressField(unique=True)

    # OPTIONAL fields
    name = models.CharField(max_length=100, null=True, blank=True)
    status = models.CharField(max_length=50, default="Active")
    uptime = models.CharField(max_length=100, null=True, blank=True)
    proposal = models.CharField(max_length=255, null=True, blank=True)
    bytes_in = models.BigIntegerField(null=True, blank=True, default=0)
    bytes_out = models.BigIntegerField(null=True, blank=True, default=0)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.client_ip} - {self.status}"

