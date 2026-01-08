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

class VPNSessionCreateView(APIView):

    def post(self, request):
        """
        Accepts:
        - Single object
        - Array of objects (bulk)
        """
        try:
            payload = request.data
            is_bulk = isinstance(payload, list)

            if not is_bulk:
                payload = [payload]

            client_ips = [item.get("client_ip") for item in payload if item.get("client_ip")]

            # Filter existing IPs
            existing_ips = set(
                VPNSession.objects.filter(client_ip__in=client_ips)
                .values_list("client_ip", flat=True)
            )

            # Keep only new records
            new_records = [
                item for item in payload
                if item.get("client_ip") not in existing_ips
            ]

            if not new_records:
                return api_response(
                    success=False,
                    message="All client IPs already exist",
                    data=[]
                )

            serializer = VPNSessionSerializer(data=new_records, many=True)
            serializer.is_valid(raise_exception=True)

            with transaction.atomic():
                serializer.save()

            return api_response(
                success=True,
                message="VPN sessions created successfully",
                data=serializer.data
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
    vpn_sessions = [
        {
            "vpn_id": "126",
            "name": "vpn-l2tp",
            "status": "ESTABLISHED",
            "uptime": "14 seconds ago",
            "client_ip": "54.234.239.63",
            "proposal": "AES_CBC_128/HMAC_SHA2_256_128/PRF_HMAC_SHA2_256/ECP_256",
            "bytes_in": 0,
            "bytes_out": 0,
        }
    ]

    context = {
        "sessions": vpn_sessions
    }
    return render(request, "logs/vpn_dashboard.html", context)
