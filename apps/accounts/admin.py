from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from apps.accounts.models import (
    User,
    PartnerDocument,
    DocumentsPendingLead,
    DocumentsPendingLeadNote,
    DocumentsPendingLeadStatusHistory
)

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'phone', 'role', 'status', 'is_staff')
    list_filter = ('role', 'status', 'is_staff', 'is_active')
    search_fields = ('username', 'email', 'phone')
    fieldsets = UserAdmin.fieldsets + (
        ('Additional Info', {'fields': ('phone', 'role', 'status', 'email_verified', 'phone_verified', 'avatar', 'agency_name', 'bio')}),
    )

@admin.register(PartnerDocument)
class PartnerDocumentAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'document_type', 'verification_status', 'uploaded_at')
    list_filter = ('verification_status', 'document_type')
    search_fields = ('user__email', 'user__username', 'original_filename')

@admin.register(DocumentsPendingLead)
class DocumentsPendingLeadAdmin(admin.ModelAdmin):
    list_display = ('lead_id', 'full_name', 'mobile_number', 'email_address', 'agency_name', 'city_name', 'email_verified', 'status', 'created_at')
    list_filter = ('status', 'email_verified', 'created_at')
    search_fields = ('lead_id', 'full_name', 'email_address', 'mobile_number', 'city_name', 'agency_name')
    ordering = ('-created_at',)

@admin.register(DocumentsPendingLeadNote)
class DocumentsPendingLeadNoteAdmin(admin.ModelAdmin):
    list_display = ('id', 'lead', 'author', 'created_at')
    search_fields = ('lead__lead_id', 'lead__full_name', 'note_text')

@admin.register(DocumentsPendingLeadStatusHistory)
class DocumentsPendingLeadStatusHistoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'lead', 'old_status', 'new_status', 'updated_by', 'created_at')
    search_fields = ('lead__lead_id', 'lead__full_name')
