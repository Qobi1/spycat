from rest_framework import serializers
from django.db import transaction
from .models import Cat, Mission, Target
from .validators import validate_breed_exists


class CatSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cat
        fields = [
            "id",
            "name",
            "years_experience",
            "breed",
            "salary",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ("id", "created_at", "updated_at")

    def validate_breed(self, value):
        validate_breed_exists(value)
        return value


class TargetSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(required=False)

    class Meta:
        model = Target
        fields = ["id", "name", "country", "notes", "complete", "created_at", "updated_at"]
        read_only_fields = ("created_at", "updated_at")


class MissionSerializer(serializers.ModelSerializer):
    cat = serializers.PrimaryKeyRelatedField(
        queryset=Cat.objects.all(), required=False, allow_null=True
    )
    targets = TargetSerializer(many=True)

    class Meta:
        model = Mission
        fields = ["id", "cat", "completed", "targets", "created_at"]
        read_only_fields = ("id", "created_at")

    def validate_targets(self, targets):
        """
        Ensure a mission has between 1 and 3 targets.
        """
        if not isinstance(targets, list):
            raise serializers.ValidationError("Targets must be a list.")
        if not (1 <= len(targets) <= 3):
            raise serializers.ValidationError("A mission must have 1–3 targets.")
        return targets

    def validate_cat(self, cat):
        """
        Ensure cat (if provided) isn't already assigned to another mission.
        """
        if cat and hasattr(cat, "mission"):
            raise serializers.ValidationError("This cat already has a mission assigned.")
        return cat

    @transaction.atomic
    def create(self, validated_data):
        targets_data = validated_data.pop("targets")
        mission = Mission.objects.create(**validated_data)

        for target_data in targets_data:
            Target.objects.create(mission=mission, **target_data)

        self._update_mission_completion(mission)
        return mission

    @transaction.atomic
    def update(self, instance, validated_data):
        targets_data = validated_data.pop("targets", None)
        new_cat = validated_data.pop("cat", None)
        completed_flag = validated_data.pop("completed", None)

        if new_cat:
            self._assign_cat(instance, new_cat)

        if targets_data is not None:
            self._update_targets(instance, targets_data)

        if completed_flag is not None:
            self._mark_mission_completed(instance, completed_flag)

        self._update_mission_completion(instance)
        instance.refresh_from_db()
        return instance

    def _assign_cat(self, mission, cat):
        """
        Assign a cat to mission if it's free.
        """
        if hasattr(cat, "mission") and cat.mission_id != mission.id:
            raise serializers.ValidationError({"cat": "This cat is already on another mission."})
        mission.cat = cat
        mission.save()

    def _update_targets(self, mission, targets_data):
        """
        Update, create, or delete mission targets.
        """
        existing_targets = {t.id: t for t in mission.targets.all()}
        sent_ids = [t.get("id") for t in targets_data if t.get("id")]

        # Delete targets not included in update
        for t_id in set(existing_targets.keys()) - set(sent_ids):
            existing_targets[t_id].delete()

        # Add/update targets
        for target_data in targets_data:
            t_id = target_data.get("id")

            # Update existing
            if t_id and t_id in existing_targets:
                target = existing_targets[t_id]
                self._update_single_target(mission, target, target_data)
            else:
                if mission.targets.count() >= 3:
                    raise serializers.ValidationError("Cannot have more than 3 targets.")
                Target.objects.create(mission=mission, **target_data)

    def _update_single_target(self, mission, target, data):
        if mission.completed or target.complete:
            if "notes" in data and data["notes"] != target.notes:
                raise serializers.ValidationError(
                    {"notes": "Cannot update notes for a completed target or mission."}
                )

        for field, value in data.items():
            if field != "id":
                setattr(target, field, value)
        target.save()

    def _mark_mission_completed(self, mission, flag):
        if flag and mission.targets.filter(complete=False).exists():
            raise serializers.ValidationError(
                {"completed": "Cannot complete mission while some targets are incomplete."}
            )
        mission.completed = bool(flag)
        mission.save()

    def _update_mission_completion(self, mission):
        if mission.targets.exists() and not mission.targets.filter(complete=False).exists():
            if not mission.completed:
                mission.completed = True
                mission.save()
