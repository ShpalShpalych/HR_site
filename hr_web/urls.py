"""
URL configuration for hr_web project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path

from hr_site.views import LoginUser, home, logout_user

from hr_site.views import EmployeeSiteUser, ManagerSiteUser

esu = EmployeeSiteUser()
msu = ManagerSiteUser()

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', home, name='home'),
    path('login/', LoginUser.as_view(), name="login"),
    path('logout/', logout_user, name="logout"),

    path('employee_projects/', esu.get_tasks_list_page, name="empl_tasks"),
    path('employee_projects/task/<int:id>/', esu.get_task_info, name="empl_task_info"),
    path('employee_projects/task/<int:id>/make_report/', esu.make_report_page, name="empl_task_make_report_page"),
    path('employee_projects/task/<int:id>/make_report/make_report', esu.make_report, name="empl_task_make_report"),



    path('manager_projects/', msu.get_projects_list, name="man_projects"),

    path('manager_projects/<int:id>/delete', msu.delete_project, name="man_projects_delete"),

    path('manager_projects/<int:id>/edit/', msu.edit_project_page, name="man_projects_edit_page"),
    path('manager_projects/<int:id>/edit/edit', msu.edit_project, name="man_projects_edit"),

    path('manager_projects/add_project/', msu.add_project_page, name="man_project_add_page"),
    path('manager_projects/add_project/add_project', msu.add_project, name="man_project_add"),

    path('manager_projects/search', msu.search_project, name="man_search_project"),

    path('manager_projects/<int:id>/', msu.get_project_info, name="man_project_info"),
    path('manager_projects/<int:id>/doc/<int:doc_id>', msu.get_doc, name="man_doc"),

    path('manager_projects/<int:proj_id>/add_task/', msu.add_task_page, name="man_project_task_add_page"),
    path('manager_projects/<int:proj_id>/add_task/add_task', msu.add_task, name="man_project_task_add"),

    path('manager_projects/<int:proj_id>/edit/<int:task_id>/',
         msu.edit_project_task_page,
         name="man_project_task_edit_page"),
    path('manager_projects/<int:proj_id>/edit/<int:task_id>/edit', msu.edit_project_task, name="man_project_task_edit"),

    path('manager_projects/<int:proj_id>/delete/<int:task_id>', msu.delete_task, name="man_task_delete"),

    path('manager_projects/<int:proj_id>/task/<int:task_id>/', msu.get_task_info, name="man_task_info"),

    path('manager_projects/<int:proj_id>/task/<int:task_id>/read_report/<int:empl_id>/',
         msu.get_task_employee_reports,
         name="man_task_report_info"),
    path('manager_projects/<int:proj_id>/task/<int:task_id>/read_report/<int:empl_id>/print/<int:report_id>',
         msu.print_report,
         name="print_report"),

    path('manager_projects/<int:proj_id>/task/<int:task_id>/delete/<int:task_empl_id>', msu.delete_empl, name="man_task_delete_empl"),

    path('manager_projects/<int:proj_id>/search', msu.search_task, name="man_project_task_search"),

    path('manager_projects/statistics', msu.get_statistics, name="statistics"),
]
