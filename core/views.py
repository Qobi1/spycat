from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from django.db import transaction
from .models import Cat, Mission, Target
from .serializers import CatSerializer, MissionSerializer, TargetSerializer

# Cats
class CatListCreateAPIView(APIView):
    def get(self, request):
        cats = Cat.objects.all().order_by('-id')
        serializer = CatSerializer(cats, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = CatSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CatDetailAPIView(APIView):
    def get_object(self, pk):
        return get_object_or_404(Cat, pk=pk)

    def get(self, request, pk):
        cat = self.get_object(pk)
        return Response(CatSerializer(cat).data)

    def patch(self, request, pk):
        cat = self.get_object(pk)
        serializer = CatSerializer(cat, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        cat = self.get_object(pk)
        cat.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


# Missions
class MissionListCreateAPIView(APIView):
    def get(self, request):
        missions = Mission.objects.prefetch_related('targets').order_by('-id')
        serializer = MissionSerializer(missions, many=True)
        return Response(serializer.data)

    @transaction.atomic
    def post(self, request):
        serializer = MissionSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class MissionDetailAPIView(APIView):
    def get_object(self, pk):
        return get_object_or_404(Mission.objects.prefetch_related('targets'), pk=pk)

    def get(self, request, pk):
        mission = self.get_object(pk)
        return Response(MissionSerializer(mission).data)

    @transaction.atomic
    def patch(self, request, pk):
        mission = self.get_object(pk)
        serializer = MissionSerializer(mission, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        mission = self.get_object(pk)
        if mission.cat:
            return Response(
                {"detail": "Cannot delete mission assigned to a cat."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        mission.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


# Custom Actions
class MissionAssignCatAPIView(APIView):

    @transaction.atomic
    def post(self, request, pk):
        mission = get_object_or_404(Mission, pk=pk)
        if mission.cat:
            return Response({"detail": "Mission already has a cat."}, status=400)

        cat_id = request.data.get("cat_id")
        if not cat_id:
            return Response({"cat_id": "This field is required."}, status=400)

        cat = get_object_or_404(Cat, pk=cat_id)
        if hasattr(cat, "mission"):
            return Response({"detail": "Cat already assigned to another mission."}, status=400)

        mission.cat = cat
        mission.save()
        return Response(MissionSerializer(mission).data)


class TargetNotesAPIView(APIView):
    @transaction.atomic
    def post(self, request, mission_id, target_id):
        mission = get_object_or_404(Mission, pk=mission_id)
        target = get_object_or_404(Target, pk=target_id, mission=mission)

        if mission.completed or target.complete:
            return Response(
                {"detail": "Notes cannot be updated for completed targets or missions."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        notes = request.data.get("notes")
        if notes is None:
            return Response({"notes": "This field is required."}, status=status.HTTP_400_BAD_REQUEST)

        target.notes = notes
        target.save()
        return Response(TargetSerializer(target).data)
