from django.contrib import admin

from reporting.models import TaskGroup, TaskReport


class TaskGroupAdmin(admin.ModelAdmin):
    list_display = ['task', 'created_by', 'created_at', 'document']
    raw_id_fields = ['created_by', 'document']


class TaskReportAdmin(admin.ModelAdmin):
    list_display = ['label', 'method', 'workflow_state', 'user', 'document', 'cpu_cost', 'gpu_cost']
    list_filter = ('method', 'workflow_state')
    raw_id_fields = ('document', 'document_part', 'user', 'ocr_model')


admin.site.register(TaskGroup, TaskGroupAdmin)
admin.site.register(TaskReport, TaskReportAdmin)
