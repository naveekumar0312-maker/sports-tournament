from django.db import models
from django.utils import timezone

class District(models.Model):
    name = models.CharField(max_length=150)
    lgd_code = models.PositiveIntegerField(unique=True, null=True, blank=True)
    state_name = models.CharField(max_length=100, default='Tamil Nadu')
    code = models.CharField(max_length=10, blank=True, null=True)
    region = models.CharField(max_length=50, blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        if self.lgd_code:
            return f"{self.name} (LGD: {self.lgd_code})"
        return self.name

class Taluk(models.Model):
    district = models.ForeignKey(District, on_delete=models.CASCADE, related_name='taluks')
    name = models.CharField(max_length=150)
    lgd_code = models.PositiveIntegerField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return f"{self.name} ({self.district.name})"

# Alias for SubDistrict
SubDistrict = Taluk

class Village(models.Model):
    taluk = models.ForeignKey(Taluk, on_delete=models.CASCADE, related_name='villages')
    name = models.CharField(max_length=150)
    lgd_code = models.PositiveIntegerField(null=True, blank=True)
    pin_code = models.CharField(max_length=20, blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)


    class Meta:
        ordering = ['name']

    def __str__(self):
        return f"{self.name} ({self.taluk.name})"

class LocalArea(models.Model):
    name = models.CharField(max_length=100)
    taluk = models.ForeignKey(Taluk, on_delete=models.CASCADE, related_name='local_areas')
    pincode = models.CharField(max_length=10, blank=True, null=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return f"{self.name}, {self.taluk.name}"


