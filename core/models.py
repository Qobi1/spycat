from django.db import models
from django.core.validators import MinValueValidator

class Cat(models.Model):
    name = models.CharField(max_length=120)
    years_experience = models.PositiveIntegerField(default=0)
    breed = models.CharField(max_length=200)
    salary = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} ({self.breed})"


class Mission(models.Model):
    cat = models.OneToOneField('Cat', null=True, blank=True, on_delete=models.SET_NULL, related_name='mission')
    created_at = models.DateTimeField(auto_now_add=True)
    completed = models.BooleanField(default=False)

    def __str__(self):
        return f"Mission #{self.pk} - {'completed' if self.completed else 'active'}"


class Target(models.Model):
    mission = models.ForeignKey(Mission, on_delete=models.CASCADE, related_name='targets')
    name = models.CharField(max_length=200)
    country = models.CharField(max_length=120)
    notes = models.TextField(blank=True)
    complete = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        # ensure each target unique per mission by name maybe
        unique_together = ('mission', 'name')

    def __str__(self):
        return f"{self.name} ({'done' if self.complete else 'pending'})"
