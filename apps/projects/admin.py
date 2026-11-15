from django.contrib import admin
from apps.projects.models import DeveloperOrganization, DeveloperMember, Project, ProjectMedia

@admin.register(DeveloperOrganization)
class DeveloperOrganizationAdmin(admin.ModelAdmin):
    list_display = ('company_name', 'established_year', 'verification_status', 'website')
    list_filter = ('verification_status',)
    search_fields = ('company_name', 'description')
    prepopulated_fields = {'slug': ('company_name',)}

@admin.register(DeveloperMember)
class DeveloperMemberAdmin(admin.ModelAdmin):
    list_display = ('organization', 'user', 'role_title')
    search_fields = ('organization__company_name', 'user__username', 'role_title')

@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ('name', 'developer', 'city', 'locality', 'rera_id', 'created_at')
    list_filter = ('city', 'developer')
    search_fields = ('name', 'rera_id', 'developer__company_name')
    prepopulated_fields = {'slug': ('name',)}

@admin.register(ProjectMedia)
class ProjectMediaAdmin(admin.ModelAdmin):
    list_display = ('project', 'media_type', 'file')
    list_filter = ('media_type',)
