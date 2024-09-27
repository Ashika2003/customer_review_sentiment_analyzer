from rest_framework import serializers

class ReviewFileSerializer(serializers.Serializer):
    file = serializers.FileField()
    
    def validate_file(self, value):
        if not value.name.endswith(('.csv', '.xlsx')):
            raise serializers.ValidationError("Invalid file format. Only .csv and .xlsx files are accepted.")
        return value
