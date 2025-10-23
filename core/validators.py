import requests
from django.conf import settings
from rest_framework import serializers

THECATAPI_BASE = "https://api.thecatapi.com/v1/breeds"

def validate_breed_exists(breed_name: str):
    """
    Validate that the breed exists in TheCatAPI.
    Raises serializers.ValidationError on failure.
    """
    # simple request: get list of breeds and check name match
    headers = {}

    try:
        resp = requests.get(THECATAPI_BASE, headers=headers, timeout=5)
        resp.raise_for_status()
        breeds = resp.json()
    except Exception as e:
        # If TheCatAPI is unreachable — choose: fail validation or accept? We'll fail with informative message
        raise serializers.ValidationError(f"Could not validate breed via TheCatAPI: {e}")

    name_lower = breed_name.strip().lower()
    for b in breeds:
        # The API has "name" e.g. "Abyssinian"
        if b.get("name", "").strip().lower() == name_lower:
            return True

    raise serializers.ValidationError(f"Breed '{breed_name}' not recognized by TheCatAPI.")
