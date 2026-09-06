from decimal import Decimal

from rest_framework import serializers

from customCalsses.CustomBaseModelSerializer import CustomBaseModelSerializer
from .models import PaymentRecordDetailsModel, CustomerBalanceModel, PaymentAllocationModel


class PaymentAllocationModelSerializer(serializers.ModelSerializer):
    job_no = serializers.CharField(source='job.job_no', read_only=True)

    class Meta:
        model = PaymentAllocationModel
        fields = ['id', 'job', 'job_no', 'amount', 'created_at']
        read_only_fields = ['id', 'created_at']


class PaymentRecordDetailsModelSerializer(CustomBaseModelSerializer):
    job_allocations = PaymentAllocationModelSerializer(many=True, required=False)

    class Meta:
        model = PaymentRecordDetailsModel
        fields = "__all__"

    def validate(self, attrs):
        allocations = attrs.get('job_allocations') or []
        amount = attrs.get('amount')

        total_allocated = sum((alloc['amount'] for alloc in allocations), Decimal('0.00'))
        if amount is not None and total_allocated > amount:
            raise serializers.ValidationError({
                'job_allocations': f"Allocated amount (₹{total_allocated}) cannot exceed the payment amount (₹{amount})"
            })

        for alloc in allocations:
            job = alloc['job']
            remaining = job.amount_remaining
            if remaining is not None and alloc['amount'] > remaining:
                raise serializers.ValidationError({
                    'job_allocations': f"₹{alloc['amount']} for job {job.job_no} exceeds its remaining balance of ₹{remaining}"
                })

        return attrs

    def create(self, validated_data):
        allocations_data = validated_data.pop('job_allocations', [])
        payment = super().create(validated_data)
        for alloc in allocations_data:
            PaymentAllocationModel.objects.create(
                payment=payment,
                shop=payment.shop,
                **alloc
            )
        return payment


class CustomerBalanceModelSerializer(CustomBaseModelSerializer):
    class Meta:
        model = CustomerBalanceModel
        fields = "__all__"
