from django.contrib import admin
from .models import ChatMessage, IncidentReport  # Import the model class
from django.utils.html import format_html

class IncidentReportAdmin(admin.ModelAdmin):
    list_display = ('id', 'issue_type', 'date_time', 'location', 'description', 'witness', 'evidence_display', 'created_anonymously')
    list_filter = ('created_anonymously',)
    search_fields = ('issue_type', 'location', 'description', 'witness',)
    def has_view_permission(self, request, obj=None):
        if obj and obj.created_anonymously:
            return False
        return True

    def evidence_display(self, obj):
        if obj.evidence:
            if obj.evidence.url.endswith(".jpg") or obj.evidence.url.endswith(".jpeg") or obj.evidence.url.endswith(".png"):
                return format_html('<img src="{}" style="max-width: 100px; max-height: 100px;" />', obj.evidence.url)
            elif obj.evidence.url.endswith(".mp4") or obj.evidence.url.endswith(".webm") or obj.evidence.url.endswith(".ogg"):
                return format_html('<video width="100" height="100" controls><source src="{}" type="video/mp4">Your browser does not support the video tag.</video>', obj.evidence.url)
            else:
                return format_html('<a href="{}">Download Evidence</a>', obj.evidence.url)
        return "No evidence"

    evidence_display.short_description = 'Evidence'

admin.site.register(IncidentReport, IncidentReportAdmin)

class ChatMessageAdmin(admin.ModelAdmin):
    list_display = ['sender', 'receiver', 'message', 'timestamp']  # Customize displayed fields
    search_fields = ['sender__username', 'receiver__username', 'message']  # Add search functionality
    list_filter = ['timestamp']  # Add filters

admin.site.register(ChatMessage)