from django.db import models
from django.conf import settings

STATUS_CHOICES = [
    (0, 'Pending'),
    (1, 'In Progress'),
    (2, 'Completed'),
]

STATUS_CODE_CHOICES = [
    (100, 'Initial Review'),
    (200, 'Under Review'),
    (300, 'Approved'),
    (400, 'Rejected'),
]


'''CLAIM_ACTION = [
    (1, 'Repair'),
    (2, 'replace'),
]'''

PART_PROBLEM = [
        (1, 'Freeze Damage'),
        (2, 'Dimple Leak - Rev Only'),
        (3, 'Header Leak'),
        (4, 'Panel Leak'),
        (5, 'Panel Split'),
        (6, 'Panel too long'),
        (7, 'Panel too short'),
        (8, 'VRV Fail'),
    ]

class Claim(models.Model):
    rm_id = models.AutoField(primary_key=True)
    dealer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    date_entered = models.DateField()
    service_date = models.DateField()
    status = models.SmallIntegerField(choices=STATUS_CHOICES, default=0)
    status_code = models.SmallIntegerField(choices=STATUS_CODE_CHOICES)
    date_finalized = models.DateField(null=True, blank=True)
    csr_note = models.TextField(null=True, blank=True)
    user_note = models.TextField(null=True, blank=True)
    dealer_ref_number = models.CharField(max_length=100, null=True, blank=True)
    #claim_action = models.PositiveSmallIntegerField(choices=CLAIM_ACTION, blank=True, null=True)
    part_problem = models.PositiveSmallIntegerField(choices=PART_PROBLEM,blank=True,null=True)
    def __str__(self):
        return f"Claim - {self.rm_id}"


class ClaimDocument(models.Model):
    claim = models.ForeignKey(Claim, related_name='documents', on_delete=models.CASCADE)
    document = models.FileField(upload_to='claim_documents/')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Document for Claim {self.claim.rm_id}"
