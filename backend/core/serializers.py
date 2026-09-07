from rest_framework import serializers
from .models import Category, Transaction, Budget

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name']

    def validate_name(self, value):
        user = self.context['request'].user
        if Category.objects.filter(user=user, name=value).exists():
            raise serializers.ValidationError("Category with this name already exists.")
        return value

    def create(self, validated_data):
        user = self.context['request'].user
        return Category.objects.create(user=user, **validated_data)

class TransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = ['id', 'category', 'amount', 'type', 'date', 'description', 'is_anomaly', 'anomaly_reason', 'created_at']
        read_only_fields = ['is_anomaly', 'anomaly_reason', 'created_at']

    def validate_amount(self, value):
        if value <= 0:
            raise serializers.ValidationError("Amount must be greater than zero.")
        return value

    def validate_category(self, value):
        user = self.context['request'].user
        if value.user != user:
            raise serializers.ValidationError("Category must belong to the requesting user.")
        return value

class BudgetSerializer(serializers.ModelSerializer):
    class Meta:
        model = Budget
        fields = ['id', 'category', 'monthly_limit', 'month']

    def validate_category(self, value):
        user = self.context['request'].user
        if value.user != user:
            raise serializers.ValidationError("Category must belong to the requesting user.")
        return value

    def validate(self, attrs):
        user = self.context['request'].user
        category = attrs.get('category')
        month = attrs.get('month')
        if Budget.objects.filter(user=user, category=category, month=month).exists():
            raise serializers.ValidationError("A budget for this category and month already exists.")
        return attrs
