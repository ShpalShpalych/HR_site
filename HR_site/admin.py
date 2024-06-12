from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin

from .forms import (CustomUserCreationForm, CustomUserChangeForm, CustomManagerCreationForm, CustomManagerChangeForm,
                    CustomEmployeeCreationForm, CustomEmployeeChangeForm)
from .models import (CustomUser, Manager, Employee, Task, Project, ProjectManager,
                     TaskEmployee, ProjectTask, TaskReport, Department, Doc)


class CustomUserAdmin(UserAdmin):
    add_form = CustomUserCreationForm
    form = CustomUserChangeForm
    model = CustomUser
    list_display = ['first_name', 'last_name']

    fieldsets = (
        ('Personal', {"fields": ('first_name', 'last_name')}),
        ('Info', {"fields": ('username', 'email')}),
    )


admin.site.register(CustomUser, CustomUserAdmin)


class CustomManagerAdmin(UserAdmin):
    add_form = CustomManagerCreationForm
    form = CustomManagerChangeForm
    model = Manager
    list_display = ['first_name', 'last_name', 'department_title']

    fieldsets = (
        ('Personal', {"fields": ('first_name', 'last_name')}),
        ('Info', {"fields": ('username', 'email', 'role')}),
        ('Department', {"fields": ('department_title', )}),
    )


admin.site.register(Manager, CustomManagerAdmin)


class CustomEmployeeAdmin(UserAdmin):
    add_form = CustomEmployeeCreationForm
    form = CustomEmployeeChangeForm
    model = Employee
    list_display = ['first_name', 'last_name', 'department_title']

    fieldsets = (
        ('Personal', {"fields": ('first_name', 'last_name')}),
        ('Info', {"fields": ('username', 'email', 'role')}),
        ('Department', {"fields": ('department_title',)}),
    )


admin.site.register(Employee, CustomEmployeeAdmin)


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ['title', 'description', 'start', 'end']


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ['title', 'description', 'start', 'end']


@admin.register(ProjectManager)
class ProjectManagerAdmin(admin.ModelAdmin):
    list_display = ['project_title', 'project_manager']


@admin.register(TaskEmployee)
class TaskEmployeeAdmin(admin.ModelAdmin):
    list_display = ['task_title', 'task_employee']


@admin.register(ProjectTask)
class ProjectTaskAdmin(admin.ModelAdmin):
    list_display = ['project_title', 'task_title']


@admin.register(TaskReport)
class TaskReportAdmin(admin.ModelAdmin):
    pass


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    pass


@admin.register(Doc)
class DocAdmin(admin.ModelAdmin):
    pass
