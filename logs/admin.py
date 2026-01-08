from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import VPNSession


@admin.register(VPNSession)
class VPNSessionAdmin(admin.ModelAdmin):
    # Columns shown in list view
    list_display = (
        "vpn_id",
        "name",
        "client_ip",
        "status",
        "bytes_in",
        "bytes_out",
        "created_at",
    )

    # Filters on right sidebar
    list_filter = (
        "status",
        "name",
        "created_at",
    )

    # Search box
    search_fields = (
        "client_ip",
        "vpn_id",
        "name",
        "proposal",
    )

    # Default ordering
    ordering = ("-created_at",)

    # Read-only fields (audit safety)
    readonly_fields = (
        "created_at",
        "updated_at",
    )

    # Pagination (important for VPN logs)
    list_per_page = 50

    # Group fields in detail view
    fieldsets = (
        ("VPN Information", {
            "fields": (
                "vpn_id",
                "name",
                "status",
                "uptime",
            )
        }),
        ("Connection Details", {
            "fields": (
                "client_ip",
                "proposal",
                "bytes_in",
                "bytes_out",
            )
        }),
        ("Timestamps", {
            "fields": (
                "created_at",
                "updated_at",
            )
        }),
    )
