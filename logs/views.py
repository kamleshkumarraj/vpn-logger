from django.shortcuts import render

# Create your views here.
from rest_framework.response import Response
from rest_framework import status

def api_response(success, message, data=None, status_code=status.HTTP_200_OK):
    return Response(
        {
            "success": success,
            "message": message,
            "data": data
        },
        status=status_code
    )
    
from rest_framework.views import APIView
from rest_framework import status
from .models import VPNSession
from .serializers import VPNSessionSerializer
from django.db import transaction

from django.db import transaction
from django.utils import timezone
from rest_framework.views import APIView
from rest_framework import status

class VPNSessionCreateView(APIView):

    def post(self, request):
        try:
            payload = request.data

            # Normalize payload (single OR bulk)
            if isinstance(payload, dict):
                payload = [payload]

            # -----------------------------
            # Step 0: Normalize payload
            # -----------------------------
            payload_map = {
                item["client_ip"]: item
                for item in payload
                if item.get("client_ip")
            }

            if not payload_map:
                return api_response(
                    success=False,
                    message="No valid client_ip found in payload",
                    data=[]
                )

            payload_ips = set(payload_map.keys())

            # -----------------------------
            # Step 1: Fetch DB sessions once
            # -----------------------------
            db_sessions = VPNSession.objects.filter(
                client_ip__in=payload_ips
            )

            db_map = {s.client_ip: s for s in db_sessions}
            db_ips = set(db_map.keys())

            # -----------------------------
            # Step 2: Deactivate missing ACTIVE sessions
            # (ACTIVE in DB but not in payload)
            # -----------------------------
            VPNSession.objects.filter(
                status="ACTIVE"
            ).exclude(
                client_ip__in=payload_ips
            ).update(
                status="DEACTIVE",
                disconnected_at=timezone.now()
            )

            # -----------------------------
            # Step 3: Update existing sessions
            # -----------------------------
            sessions_to_update = []

            for ip in payload_ips & db_ips:
                session = db_map[ip]
                payload_data = payload_map[ip]

                if session.status != "ACTIVE":
                    session.status = "ACTIVE"
                    session.connected_at = timezone.now()

                session.uptime = payload_data.get("uptime", session.uptime)
                session.last_seen = timezone.now()

                sessions_to_update.append(session)

            # -----------------------------
            # Step 4: Create new sessions
            # -----------------------------
            sessions_to_create = []

            for ip in payload_ips - db_ips:
                payload_data = payload_map[ip]

                sessions_to_create.append(
                    VPNSession(
                        client_ip=ip,
                        status="ACTIVE",
                        uptime=payload_data.get("uptime"),
                        connected_at=timezone.now(),
                        last_seen=timezone.now(),
                    )
                )

            # -----------------------------
            # Step 5: Atomic DB write
            # -----------------------------
            with transaction.atomic():
                if sessions_to_update:
                    VPNSession.objects.bulk_update(
                        sessions_to_update,
                        ["status", "uptime", "last_seen", "connected_at"]
                    )

                if sessions_to_create:
                    VPNSession.objects.bulk_create(sessions_to_create)

            return api_response(
                success=True,
                message="VPN sessions synchronized successfully",
                data={
                    "updated": len(sessions_to_update),
                    "created": len(sessions_to_create),
                    "active": len(payload_ips)
                }
            )

        except Exception as e:
            return api_response(
                success=False,
                message=str(e),
                data=None,
                status_code=status.HTTP_400_BAD_REQUEST
            )


class VPNSessionUpdateView(APIView):

    def put(self, request, pk):
        try:
            session = VPNSession.objects.get(pk=pk)
            serializer = VPNSessionSerializer(session, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()

            return api_response(
                success=True,
                message="VPN session updated successfully",
                data=serializer.data
            )

        except VPNSession.DoesNotExist:
            return api_response(
                success=False,
                message="VPN session not found",
                data=None,
                status_code=status.HTTP_404_NOT_FOUND
            )

        except Exception as e:
            return api_response(
                success=False,
                message=str(e),
                data=None,
                status_code=status.HTTP_400_BAD_REQUEST
            )


class VPNSessionDeleteView(APIView):

    def delete(self, request, pk):
        try:
            session = VPNSession.objects.get(pk=pk)
            session.delete()

            return api_response(
                success=True,
                message="VPN session deleted successfully",
                data=None
            )

        except VPNSession.DoesNotExist:
            return api_response(
                success=False,
                message="VPN session not found",
                data=None,
                status_code=status.HTTP_404_NOT_FOUND
            )

        except Exception as e:
            return api_response(
                success=False,
                message=str(e),
                data=None,
                status_code=status.HTTP_400_BAD_REQUEST
            )

from django.shortcuts import render

def vpn_dashboard(request):
    # Example data (replace with DB or API later)
    vpn_sessions = VPNSession.objects.all()
    
    context = {
        "sessions": vpn_sessions
    }
    return render(request, "logs/vpn_dashboard.html", context)
