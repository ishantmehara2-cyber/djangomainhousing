from django.contrib import admin
from apps.moderation.models import AuditLog, PropertyVerification, Report

@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ('action', 'entity', 'entity_id', 'user', 'ip_address', 'created_at')
    list_filter = ('action', 'entity', 'created_at')
    search_fields = ('action', 'entity', 'user__username', 'ip_address')

@admin.register(PropertyVerification)
class PropertyVerificationAdmin(admin.ModelAdmin):
    list_display = ('property', 'verifier_user', 'verified_at')
    search_fields = ('property__title', 'verifier_user__username')

@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    list_display = ('id', 'property', 'reporter_user', 'reason_category', 'status', 'resolved_by_user', 'created_at')
    list_filter = ('status', 'reason_category', 'created_at')
    search_fields = ('property__title', 'reporter_user__username', 'reason', 'investigation_notes')
