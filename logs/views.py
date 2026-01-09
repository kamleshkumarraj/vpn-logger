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

from django.db import transaction
from django.utils import timezone
from rest_framework.views import APIView
from rest_framework import status

class VPNSessionCreateView(APIView):

    def post(self, request):
        try:
            payload = request.data

            # -----------------------------
            # Normalize payload
            # -----------------------------
            if payload is None:
                payload = []

            if isinstance(payload, dict):
                payload = [payload]

            # -----------------------------
            # CASE 1: Empty payload → deactivate ALL
            # -----------------------------
            if len(payload) == 0:
                updated = VPNSession.objects.filter(
                    status="Connected"
                ).update(
                    status="Disconnected"
                )

                return api_response(
                    success=True,
                    message="All VPN sessions Disconnected (empty payload)",
                    data={"Disconnected": updated}
                )

            # -----------------------------
            # Step 0: Normalize payload map
            # -----------------------------
            payload_map = {
                item["client_ip"]: item
                for item in payload
                if item.get("client_ip")
            }

            payload_ips = set(payload_map.keys())

            if not payload_ips:
                return api_response(
                    success=False,
                    message="Payload does not contain valid client_ip values",
                    data=[]
                )

            # -----------------------------
            # Step 1: Fetch DB sessions once
            # -----------------------------
            db_sessions = VPNSession.objects.filter(
                client_ip__in=payload_ips
            )

            db_map = {s.client_ip: s for s in db_sessions}
            db_ips = set(db_map.keys())

            # -----------------------------
            # Step 2: Deactivate missing Connected sessions
            # -----------------------------
            VPNSession.objects.filter(
                status="Connected"
            ).exclude(
                client_ip__in=payload_ips
            ).update(
                status="Disconnected"
            )

            # -----------------------------
            # Step 3: Update existing sessions
            # -----------------------------
            sessions_to_update = []

            for ip in payload_ips & db_ips:
                session = db_map[ip]
                data = payload_map[ip]

                session.status = "Connected"
                session.vpn_id = data.get("vpn_id", session.vpn_id)
                session.name = data.get("name", session.name)
                session.uptime = data.get("uptime", session.uptime)
                session.proposal = data.get("proposal", session.proposal)
                session.bytes_in = data.get("bytes_in", session.bytes_in)
                session.bytes_out = data.get("bytes_out", session.bytes_out)

                sessions_to_update.append(session)

            # -----------------------------
            # Step 4: Create new sessions
            # -----------------------------
            sessions_to_create = []

            for ip in payload_ips - db_ips:
                data = payload_map[ip]

                sessions_to_create.append(
                    VPNSession(
                        client_ip=ip,
                        vpn_id=data.get("vpn_id"),
                        name=data.get("name"),
                        status="Connected",
                        uptime=data.get("uptime"),
                        proposal=data.get("proposal"),
                        bytes_in=data.get("bytes_in", 0),
                        bytes_out=data.get("bytes_out", 0),
                    )
                )

            # -----------------------------
            # Step 5: Atomic write
            # -----------------------------
            with transaction.atomic():
                if sessions_to_update:
                    VPNSession.objects.bulk_update(
                        sessions_to_update,
                        [
                            "status",
                            "vpn_id",
                            "name",
                            "uptime",
                            "proposal",
                            "bytes_in",
                            "bytes_out",
                        ]
                    )

                if sessions_to_create:
                    VPNSession.objects.bulk_create(
                        sessions_to_create,
                        ignore_conflicts=True  # safety for race conditions
                    )

            return api_response(
                success=True,
                message="VPN sessions synchronized successfully",
                data={
                    "received": len(payload),
                    "updated": len(sessions_to_update),
                    "created": len(sessions_to_create),
                    "Connected": len(payload_ips),
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
    status = request.GET.get("status") 
    vpn_sessions = VPNSession.objects.filter(status=status)
    
    context = {
        "sessions": vpn_sessions
    }
    return render(request, "logs/vpn_dashboard.html", context)
