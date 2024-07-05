from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError


CLAIM_ACTION = [
    (1, 'Repair'),
    (2, 'replace'),
]

class Part(models.Model):
    part_id = models.AutoField(primary_key=True)
    part_number = models.CharField(max_length=6)
    part_description = models.CharField(max_length=255)
    product_line = models.CharField(max_length=255)
    installing_dealer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='installed_parts')
    date_installed = models.DateField()
    barcode = models.CharField(max_length=15)
    active = models.BooleanField(default=True)
    claim_action = models.PositiveSmallIntegerField(choices=CLAIM_ACTION, blank=True, null=True)
    problem_code = models.PositiveSmallIntegerField(choices=[
        (1, 'Problem 1'),
        (2, 'Problem 2'),
    ], blank=True, null=True)

    def __str__(self):
        return f"Part - {self.part_number}"

    def clean(self):
        if self.barcode[:6] != self.part_number:
            raise ValidationError("The first 6 characters of the barcode must match the part number.")

class Partcsv(models.Model):
    part_number = models.CharField(max_length=50, unique=True)
    part_description = models.CharField(max_length=255)
    product_line = models.CharField(max_length=255)
    barcode = models.CharField(max_length=15,blank=True, null=True)
    active = models.BooleanField(default=True)

    def __str__(self) -> str:
        return self.part_number


