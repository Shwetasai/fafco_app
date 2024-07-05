from rest_framework import serializers
from .models import Part,Partcsv

class PartSerializer(serializers.ModelSerializer):
    class Meta:
        model = Part
        fields = '__all__'
    
    def validate(self, data):
        if 'barcode' in data and 'part_number' in data:
            if data['barcode'][:6] != data['part_number']:
                raise serializers.ValidationError("The first 6 characters of the barcode must match the part number.")
        return data

class PartcsvSerializer(serializers.ModelSerializer):
    class Meta:
        model = Partcsv
        fields = '__all__'