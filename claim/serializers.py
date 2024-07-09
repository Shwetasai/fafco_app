from rest_framework import serializers
from .models import Claim, ClaimDocument



class ClaimSerializer(serializers.ModelSerializer):
    dealer = serializers.ReadOnlyField(source='dealer.email')

    class Meta:
        model = Claim
        fields = [
            'rm_id', 'dealer', 'date_entered', 'service_date', 'status', 'status_code',
            'date_finalized', 'csr_note', 'user_note', 'dealer_ref_number','claim_action','part_problem','date_installed','barcode',
            'active','claim_action'
        ]
        read_only_fields = ['rm_id', 'dealer']


class ClaimDocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = ClaimDocument
        fields = ['id', 'document', 'uploaded_at']
