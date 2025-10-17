from django.shortcuts import render
from django.db.models import Count, Avg, Sum, Q, F, Case, When, DecimalField
from django.db.models.functions import TruncMonth, TruncWeek
from django.utils import timezone
from datetime import datetime, timedelta

from customCalsses.CustomBaseModelViewSet import CustomBaseModelViewSet
from .models import JobDetailsModel
from .serializers import JobDetailsModelSerializer
from helpers.PaginationClass import CustomPageNumberPagination
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.response import Response
from .filters import JobDetailsModelFilterSet
from rest_framework.permissions import IsAuthenticated
from rest_framework import filters
from rest_framework.decorators import action
from rest_framework.viewsets import ViewSet

from rest_framework.views import APIView
from rest_framework import status
from auditlog.models import LogEntry
from django.contrib.contenttypes.models import ContentType
import json
from .utils import generate_audit_message
from rest_framework.exceptions import PermissionDenied


class JobDetailsModelViewSet(CustomBaseModelViewSet):
    queryset = JobDetailsModel.objects.all()
    serializer_class = JobDetailsModelSerializer
    pagination_class = CustomPageNumberPagination
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter, filters.SearchFilter]
    filterset_class = JobDetailsModelFilterSet
    permission_classes = [IsAuthenticated] 
    ordering_fields = '__all__'
    search_fields = ['job_no', 'model', 'job_details', 'note', 'feedback']

    def get_queryset(self):
        """
        Override to automatically filter by shop parameter from frontend
        """
        queryset = super().get_queryset()
        
        # Get shop ID from the 'shop' parameter (your frontend standard)
        shop_id = self.request.query_params.get('shop')
        if shop_id:
            queryset = queryset.filter(shop_id=shop_id)
        
        return queryset

    def perform_destroy(self, instance):
        """
        Override delete to check if user is the shop owner
        """
        # Check if the user is the owner of the shop
        if instance.shop.owner != self.request.user:
            raise PermissionDenied("Only the shop owner can delete jobs.")
        
        # If owner, proceed with deletion
        super().perform_destroy(instance)

    # ANALYTICS ENDPOINTS
    @action(detail=False, methods=['get'], url_path='analytics/performance')
    def performance_analytics(self, request):
        """
        GET /jobs/analytics/performance/
        Get performance metrics with optional filters
        """
        # Get shop ID from 'shop' parameter (consistent with frontend)
        shop_id = request.query_params.get('shop')
        date_from = request.query_params.get('date_from')
        date_to = request.query_params.get('date_to')
        
        # Build queryset with shop filter
        queryset = JobDetailsModel.objects.all()
        if shop_id:
            queryset = queryset.filter(shop_id=shop_id)
        
        if date_from and date_to:
            try:
                date_range = [
                    datetime.strptime(date_from, '%Y-%m-%d').date(),
                    datetime.strptime(date_to, '%Y-%m-%d').date()
                ]
                queryset = queryset.filter(created_at__date__range=date_range)
            except ValueError:
                return Response({
                    'error': 'Invalid date format. Use YYYY-MM-DD'
                }, status=status.HTTP_400_BAD_REQUEST)
        
        # Calculate performance metrics
        total_jobs = queryset.count()
        completed_jobs = queryset.filter(status__in=['completed', 'delivered']).count()
        
        # First time fix rate
        completed_with_status = queryset.filter(status__in=['completed', 'delivered'])
        first_time_fixes = completed_with_status.filter(first_time_fix=True).count()
        first_time_fix_rate = (first_time_fixes / completed_with_status.count() * 100) if completed_with_status.count() > 0 else 0
        
        # Average completion time
        completion_time_jobs = queryset.filter(
            completed_at__isnull=False,
            started_at__isnull=False,
            status__in=['completed', 'delivered']
        )
        
        avg_completion_days = 0
        if completion_time_jobs.exists():
            total_days = sum([
                (job.completed_at.date() - job.started_at.date()).days 
                for job in completion_time_jobs
            ])
            avg_completion_days = total_days / completion_time_jobs.count()
        
        # Efficiency metrics
        efficiency_jobs = queryset.filter(
            estimated_hours__isnull=False,
            actual_hours__isnull=False,
            actual_hours__gt=0
        )
        
        avg_efficiency = 0
        if efficiency_jobs.exists():
            efficiencies = [
                (job.estimated_hours / job.actual_hours * 100) 
                for job in efficiency_jobs
            ]
            avg_efficiency = sum(efficiencies) / len(efficiencies)
        
        # Overdue jobs
        overdue_jobs = queryset.filter(
            delivery__lt=timezone.now().date(),
            status__in=['assigned', 'in_progress']
        ).count()
        
        return Response({
            'total_jobs': total_jobs,
            'completed_jobs': completed_jobs,
            'completion_rate': (completed_jobs / total_jobs * 100) if total_jobs > 0 else 0,
            'first_time_fix_rate': round(first_time_fix_rate, 2),
            'average_completion_days': round(avg_completion_days, 1),
            'average_efficiency_percentage': round(avg_efficiency, 2),
            'overdue_jobs': overdue_jobs,
            'efficiency_jobs_tracked': efficiency_jobs.count(),
            'filters_applied': {
                'shop': shop_id,  # Changed from shop_id to shop
                'date_from': date_from,
                'date_to': date_to
            }
        })

    @action(detail=False, methods=['get'], url_path='analytics/financial')
    def financial_analytics(self, request):
        """
        GET /jobs/analytics/financial/
        Get financial metrics with optional filters
        """
        # Get shop ID from 'shop' parameter (consistent with frontend)
        shop_id = request.query_params.get('shop')
        date_from = request.query_params.get('date_from')
        date_to = request.query_params.get('date_to')
        
        # Build queryset with shop filter
        queryset = JobDetailsModel.objects.exclude(final_bill__isnull=True)
        if shop_id:
            queryset = queryset.filter(shop_id=shop_id)
        
        if date_from and date_to:
            try:
                date_range = [
                    datetime.strptime(date_from, '%Y-%m-%d').date(),
                    datetime.strptime(date_to, '%Y-%m-%d').date()
                ]
                queryset = queryset.filter(created_at__date__range=date_range)
            except ValueError:
                return Response({
                    'error': 'Invalid date format. Use YYYY-MM-DD'
                }, status=status.HTTP_400_BAD_REQUEST)
        
        # Calculate financial metrics using aggregation
        financial_data = queryset.aggregate(
            total_revenue=Sum('final_bill'),
            total_parts_cost=Sum('parts_cost'),
            total_labor_cost=Sum('labor_cost'),
            total_discount=Sum('discount_amount'),
            total_tax=Sum('tax_amount'),
            average_bill=Avg('final_bill'),
            job_count=Count('id')
        )
        
        # Calculate derived metrics
        total_revenue = financial_data['total_revenue'] or 0
        total_parts_cost = financial_data['total_parts_cost'] or 0
        total_labor_cost = financial_data['total_labor_cost'] or 0
        total_costs = total_parts_cost + total_labor_cost
        total_profit = total_revenue - total_costs
        profit_margin = (total_profit / total_revenue * 100) if total_revenue > 0 else 0
        
        return Response({
            'total_revenue': float(total_revenue),
            'total_costs': float(total_costs),
            'parts_cost': float(total_parts_cost),
            'labor_cost': float(total_labor_cost),
            'total_profit': float(total_profit),
            'profit_margin_percentage': round(profit_margin, 2),
            'average_bill_value': float(financial_data['average_bill'] or 0),
            'total_discounts': float(financial_data['total_discount'] or 0),
            'total_tax': float(financial_data['total_tax'] or 0),
            'jobs_analyzed': financial_data['job_count'],
            'filters_applied': {
                'shop': shop_id,  # Changed from shop_id to shop
                'date_from': date_from,
                'date_to': date_to
            }
        })

    @action(detail=False, methods=['get'], url_path='analytics/technician-performance')
    def technician_performance(self, request):
        """
        GET /jobs/analytics/technician-performance/
        Get technician performance metrics
        """
        # Get shop ID from 'shop' parameter (consistent with frontend)
        shop_id = request.query_params.get('shop')
        date_from = request.query_params.get('date_from')
        date_to = request.query_params.get('date_to')
        
        # Build queryset with shop filter
        queryset = JobDetailsModel.objects.exclude(technician__isnull=True)
        if shop_id:
            queryset = queryset.filter(shop_id=shop_id)
        
        if date_from and date_to:
            try:
                date_range = [
                    datetime.strptime(date_from, '%Y-%m-%d').date(),
                    datetime.strptime(date_to, '%Y-%m-%d').date()
                ]
                queryset = queryset.filter(created_at__date__range=date_range)
            except ValueError:
                return Response({
                    'error': 'Invalid date format. Use YYYY-MM-DD'
                }, status=status.HTTP_400_BAD_REQUEST)
        
        # Calculate technician performance metrics
        performance_data = queryset.values(
            'technician__id',
            'technician__first_name',  # Adjust field names based on your Employee model
            'technician__last_name'
        ).annotate(
            total_jobs=Count('id'),
            completed_jobs=Count('id', filter=Q(status__in=['completed', 'delivered'])),
            total_revenue=Sum('final_bill'),
            total_hours=Sum('actual_hours'),
            first_time_fixes=Count('id', filter=Q(first_time_fix=True)),
            rework_jobs=Count('id', filter=Q(rework_required=True)),
            avg_efficiency=Avg(
                Case(
                    When(
                        estimated_hours__isnull=False, 
                        actual_hours__isnull=False, 
                        actual_hours__gt=0,
                        then=F('estimated_hours') / F('actual_hours') * 100
                    ),
                    default=None,
                    output_field=DecimalField()
                )
            )
        ).annotate(
            completion_rate=Case(
                When(total_jobs__gt=0, then=F('completed_jobs') * 100.0 / F('total_jobs')),
                default=0,
                output_field=DecimalField()
            ),
            first_time_fix_rate=Case(
                When(total_jobs__gt=0, then=F('first_time_fixes') * 100.0 / F('total_jobs')),
                default=0,
                output_field=DecimalField()
            ),
            revenue_per_hour=Case(
                When(total_hours__gt=0, then=F('total_revenue') / F('total_hours')),
                default=0,
                output_field=DecimalField()
            )
        ).order_by('-total_revenue')
        
        # Format the response
        technicians = []
        for tech in performance_data:
            technician_name = f"{tech['technician__first_name']} {tech['technician__last_name']}"
            technicians.append({
                'technician_id': tech['technician__id'],
                'technician_name': technician_name,
                'total_jobs': tech['total_jobs'],
                'completed_jobs': tech['completed_jobs'],
                'completion_rate': float(tech['completion_rate'] or 0),
                'first_time_fix_rate': float(tech['first_time_fix_rate'] or 0),
                'total_revenue': float(tech['total_revenue'] or 0),
                'total_hours': float(tech['total_hours'] or 0),
                'revenue_per_hour': float(tech['revenue_per_hour'] or 0),
                'average_efficiency': float(tech['avg_efficiency'] or 0),
                'rework_jobs': tech['rework_jobs']
            })
        
        return Response({
            'technicians': technicians,
            'total_technicians': len(technicians),
            'filters_applied': {
                'shop': shop_id,  # Changed from shop_id to shop
                'date_from': date_from,
                'date_to': date_to
            }
        })

    @action(detail=False, methods=['get'], url_path='analytics/monthly-trends')
    def monthly_trends(self, request):
        """
        GET /jobs/analytics/monthly-trends/
        Get monthly financial and performance trends
        """
        # Get shop ID from 'shop' parameter (consistent with frontend)
        shop_id = request.query_params.get('shop')
        months = int(request.query_params.get('months', 12))  # Default 12 months
        
        end_date = timezone.now().date()
        start_date = end_date - timedelta(days=months * 30)
        
        # Build queryset with shop filter
        queryset = JobDetailsModel.objects.filter(
            created_at__date__range=[start_date, end_date]
        )
        if shop_id:
            queryset = queryset.filter(shop_id=shop_id)
        
        # Monthly trends with financial data
        monthly_data = queryset.exclude(final_bill__isnull=True).annotate(
            month=TruncMonth('created_at')
        ).values('month').annotate(
            revenue=Sum('final_bill'),
            parts_cost=Sum('parts_cost'),
            labor_cost=Sum('labor_cost'),
            job_count=Count('id'),
            completed_jobs=Count('id', filter=Q(status__in=['completed', 'delivered'])),
            avg_bill=Avg('final_bill')
        ).annotate(
            total_cost=F('parts_cost') + F('labor_cost'),
            profit=F('revenue') - F('total_cost'),
            profit_margin=Case(
                When(revenue__gt=0, then=F('profit') / F('revenue') * 100),
                default=0,
                output_field=DecimalField()
            ),
            completion_rate=Case(
                When(job_count__gt=0, then=F('completed_jobs') * 100.0 / F('job_count')),
                default=0,
                output_field=DecimalField()
            )
        ).order_by('month')
        
        # Format response
        trends = []
        for data in monthly_data:
            trends.append({
                'month': data['month'].strftime('%Y-%m'),
                'revenue': float(data['revenue'] or 0),
                'total_cost': float(data['total_cost'] or 0),
                'profit': float(data['profit'] or 0),
                'profit_margin': float(data['profit_margin'] or 0),
                'job_count': data['job_count'],
                'completed_jobs': data['completed_jobs'],
                'completion_rate': float(data['completion_rate'] or 0),
                'average_bill': float(data['avg_bill'] or 0)
            })
        
        return Response({
            'monthly_trends': trends,
            'period_months': months,
            'filters_applied': {
                'shop': shop_id  # Changed from shop_id to shop
            }
        })

    @action(detail=False, methods=['get'], url_path='analytics/dashboard')
    def dashboard_summary(self, request):
        """
        GET /jobs/analytics/dashboard/
        Get summary metrics for dashboard
        """
        # Get shop ID from 'shop' parameter (consistent with frontend)
        shop_id = request.query_params.get('shop')
        
        # Build queryset with shop filter
        queryset = JobDetailsModel.objects.all()
        if shop_id:
            queryset = queryset.filter(shop_id=shop_id)
        
        # Current month data
        current_month_start = timezone.now().replace(day=1).date()
        current_month_jobs = queryset.filter(created_at__date__gte=current_month_start)
        
        # Quick metrics
        total_jobs = queryset.count()
        completed_jobs = queryset.filter(status__in=['completed', 'delivered']).count()
        overdue_jobs = queryset.filter(
            delivery__lt=timezone.now().date(),
            status__in=['assigned', 'in_progress']
        ).count()
        
        # Financial summary (jobs with bills)
        billed_jobs = queryset.exclude(final_bill__isnull=True)
        monthly_revenue = current_month_jobs.exclude(final_bill__isnull=True).aggregate(
            revenue=Sum('final_bill'),
            profit=Sum('final_bill') - Sum('parts_cost') - Sum('labor_cost')
        )
        
        return Response({
            'summary': {
                'total_jobs': total_jobs,
                'completed_jobs': completed_jobs,
                'completion_rate': (completed_jobs / total_jobs * 100) if total_jobs > 0 else 0,
                'overdue_jobs': overdue_jobs,
                'current_month_jobs': current_month_jobs.count(),
                'current_month_revenue': float(monthly_revenue['revenue'] or 0),
                'current_month_profit': float(monthly_revenue['profit'] or 0)
            },
            'filters_applied': {
                'shop': shop_id  # Changed from shop_id to shop
            }
        })


class JobAuditLogView(APIView):
    def get(self, request, job_id):
        """
        Get all audit logs for a specific job with human-readable messages
        """
        try:
            job = JobDetailsModel.objects.get(id=job_id)
            content_type = ContentType.objects.get_for_model(JobDetailsModel)
            
            # Get all log entries for this job
            log_entries = LogEntry.objects.filter(
                content_type=content_type,
                object_id=job_id
            ).order_by('-timestamp')
            
            logs = []
            for entry in log_entries:
                # FIX: Handle both dict and string formats
                if isinstance(entry.changes, str):
                    changes = json.loads(entry.changes)
                elif isinstance(entry.changes, dict):
                    changes = entry.changes
                else:
                    changes = {}
                
                log_data = {
                    'id': entry.id,
                    'timestamp': entry.timestamp,
                    'user': entry.actor.username if entry.actor else 'System',
                    'action': entry.get_action_display(),
                    'message': generate_audit_message(entry, JobDetailsModel),
                    'changes': changes  # Already a dict, no need to parse
                }
                logs.append(log_data)
            
            return Response({
                'job_id': job_id,
                'job_number': job.job_no,
                'audit_logs': logs
            }, status=status.HTTP_200_OK)
            
        except JobDetailsModel.DoesNotExist:
            return Response({
                'error': 'Job not found'
            }, status=status.HTTP_404_NOT_FOUND)
