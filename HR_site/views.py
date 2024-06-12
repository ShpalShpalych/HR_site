import os
from pathlib import Path

from django.contrib.auth import logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.views import LoginView
from django.db import connection
from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect
from django.urls import reverse_lazy, reverse

from datetime import datetime

from hr_site.models import (Project, Task, ProjectTask, Employee,
                            TaskEmployee, ProjectManager, Manager, TaskReport, Doc, STATUS, STATUS_DICT)

from hr_web.settings import BASE_DIR


# Create your views here.

class LoginUser(LoginView):
    form_class = AuthenticationForm
    template_name = os.path.join("registration", "login.html")

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        return dict(list(context.items()))

    def get_success_url(self):
        return reverse_lazy("home")


def logout_user(request):
    logout(request)
    return redirect('login')


def home(request):
    if request.user.is_authenticated:
        if request.user.is_superuser:
            return redirect('/admin')

        if request.user.role == 'MANAGER':
            return redirect('man_projects')
        elif request.user.role == 'EMPLOYEE':
            return redirect('empl_tasks')

    return render(request, 'home.html')


class EmployeeSiteUser:
    def get_tasks_list_page(self, request, *args, **kwargs):
        user_id = request.user.id
        query = f"""
        SELECT task.id, task.title, task.status, task.end
        FROM hr_site_employee as empl
        JOIN hr_site_taskemployee as task_emp
        ON empl.customuser_ptr_id = task_emp.task_employee_id
        JOIN hr_site_task as task
        ON task_emp.task_title_id = task.id
        WHERE empl.customuser_ptr_id = {user_id};"""

        with connection.cursor() as cursor:
            cursor.execute(query)
            request_info = list(cursor.fetchall())

        print(request_info)

        tasks = [
            (t_id, t_title, STATUS_DICT[t_status],
             ".".join(t_date.strftime('%d-%m-%Y').split(sep="-"))) for (t_id, t_title, t_status, t_date) in request_info]

        return render(request, 'empl_tasks_page.html', {"tasks": tasks})

    def get_task_info(self, request, id, *args, **kwargs):
        query = f"""
                SELECT task.id, task.title, task.description, task.status, task.start, task.end
                FROM hr_site_employee as empl
                JOIN hr_site_taskemployee as task_emp
                ON empl.customuser_ptr_id = task_emp.task_employee_id
                JOIN hr_site_task as task
                ON task_emp.task_title_id = task.id
                WHERE task.id = {id};"""

        with connection.cursor() as cursor:
            cursor.execute(query)
            request_info = list(cursor.fetchall())

        print(request_info)

        task_info = [
            (t_id, t_title, t_desc, STATUS_DICT[t_status],
             ".".join(t_start.strftime('%d-%m-%Y').split(sep="-")),
             ".".join(t_end.strftime('%d-%m-%Y').split(sep="-")))
            for (t_id, t_title, t_desc, t_status, t_start, t_end) in request_info][:1]

        return render(request, 'empl_task_info.html', {"task_info": task_info})

    def make_report_page(self, request, id, *args, **kwargs):
        return render(request, 'empl_make_report.html', {"id": id})

    def make_report(self, request, id, *args, **kwargs):
        report = request.POST.get('report')
        end = datetime.strptime(request.POST.get('end'), '%Y-%m-%d')

        task = Task.objects.get(id=id)

        user_id = request.user.id
        user = Employee.objects.get(customuser_ptr_id=user_id)

        task_report = TaskReport(report_task=task, report_employee=user, report=report, end=end)
        task_report.save()

        return HttpResponseRedirect(reverse('empl_task_info', kwargs={"id": id}))


class ManagerSiteUser:
    def get_projects_list(self, request, filtered_projects=None, *args, **kwargs):
        user_id = request.user.id
        query = f"""
                SELECT project.id, project.title, project.status, project.end
                FROM hr_site_manager as mans
                JOIN hr_site_projectmanager as pr_man
                ON mans.customuser_ptr_id = pr_man.project_manager_id
                JOIN hr_site_project as project
                ON project.id = pr_man.project_title_id
                WHERE mans.customuser_ptr_id = {user_id}
                ;
                """

        with connection.cursor() as cursor:
            cursor.execute(query)
            request_info = list(cursor.fetchall())

        if filtered_projects is None:
            filtered_projects = Project.objects.all().values_list('id', flat=True)

        projects = [
            (t_id,
             t_title, STATUS_DICT[t_status],
             ".".join(t_end.strftime('%d-%m-%Y').split(sep="-")))
            for (t_id, t_title, t_status, t_end) in request_info if t_id in filtered_projects]

        return render(request, 'man_projects_list.html', {"projects": projects})

    def add_project_page(self, request, *args, **kwargs):
        docs = Doc.objects.all()
        return render(request, 'man_add_project.html', {"docs": docs})

    def add_project(self, request, *args, **kwargs):
        current_manager = request.user.id

        title = request.POST.get('title')
        description = request.POST.get('description')

        doc_id = request.POST.get('docs')
        doc = Doc.objects.get(id=doc_id)

        start = datetime.strptime(request.POST.get('start'), '%Y-%m-%d')
        end = datetime.strptime(request.POST.get('end'), '%Y-%m-%d')

        project = Project(title=title, description=description, start=start, end=end, doc_title=doc)
        project.save()

        manager = Manager.objects.get(customuser_ptr_id=current_manager)
        pr_man = ProjectManager(project_title=project, project_manager=manager, start=start, end=end)
        pr_man.save()



        return HttpResponseRedirect(reverse('man_projects'))

    def get_project_info(self,  request, id, filtered_tasks=None, *args, **kwargs):
        query = f"""
                    SELECT task.id, task.title, task.status, task.end
                    FROM hr_site_project as project
                    JOIN hr_site_projecttask as pr_task
                    ON project.id = pr_task.project_title_id
                    JOIN hr_site_task as task
                    ON task.id = pr_task.task_title_id
                    WHERE project.id = {id};"""

        proj_info_query = f"""
                    SELECT project.title, project.description, project.end, project.status, project.doc_title_id
                    FROM hr_site_project as project
                    WHERE project.id = {id};"""

        with connection.cursor() as cursor:
            cursor.execute(query)
            request_info = list(cursor.fetchall())

            cursor.execute(proj_info_query)
            project_info_result = list(cursor.fetchall())

        project = [
            (p_title,
             p_description,
             ".".join(p_end.strftime('%d-%m-%Y').split(sep="-")),
             STATUS_DICT[p_status], p_doc)
            for (p_title, p_description, p_end, p_status, p_doc) in project_info_result]

        if filtered_tasks is None:
            filtered_tasks = Task.objects.all().values_list('id', flat=True)

        tasks = [
            (t_id,
             t_title, STATUS_DICT[t_status],
             ".".join(t_end.strftime('%d-%m-%Y').split(sep="-")))
            for (t_id, t_title, t_status, t_end) in request_info if t_id in filtered_tasks]

        return render(request, 'man_project_info.html', {"project": project,
                                                         "tasks": tasks,
                                                         "proj_id": id})

    def get_task_info(self, request, proj_id, task_id, *args, **kwargs):
        if request.method == "POST":
            employee = request.POST.get("employees")
            first_name, last_name = employee.split()
            empl = Employee.objects.get(last_name=last_name, first_name=first_name)

            start = datetime.strptime(request.POST.get('start'), '%Y-%m-%d')
            end = datetime.strptime(request.POST.get('end'), '%Y-%m-%d')

            task = Task.objects.get(id=task_id)
            task_empl = TaskEmployee(task_title=task, task_employee=empl, start=start, end=end)
            task_empl.save()

        query = f"""
                    SELECT task_emp.id, custom.first_name, custom.last_name, emp.customuser_ptr_id
                    FROM hr_site_task as task
                    JOIN hr_site_taskemployee as task_emp
                    ON task.id = task_emp.task_title_id
                    JOIN hr_site_employee as emp
                    ON emp.customuser_ptr_id = task_emp.task_employee_id
                    JOIN hr_site_customuser as custom
                    ON custom.id = emp.customuser_ptr_id
                    WHERE task.id = {task_id}
                    ;
                    """

        task_info_query = f"""
                    SELECT task.title, task.description, task.end, task.status
                    FROM hr_site_task as task
                    WHERE task.id = {task_id}
                    ;"""

        with connection.cursor() as cursor:
            cursor.execute(task_info_query)
            task_info_result = list(cursor.fetchall())

            cursor.execute(query)
            request_info = list(cursor.fetchall())

        task_info = [
            (t_title,
             t_description,
             ".".join(t_end.strftime('%d-%m-%Y').split(sep="-")),
             STATUS_DICT[t_status])
            for (t_title, t_description, t_end, t_status) in task_info_result]

        employees = [
            [task_empl_id,
             emp_first,
             emp_last,
             emp_id]
            for (task_empl_id, emp_first, emp_last, emp_id) in request_info]

        manager = Manager.objects.get(customuser_ptr_id=request.user.id)
        employees_list = Employee.objects.filter(department_title=manager.department_title)

        return render(request, 'man_task_info.html', {"task_info": task_info, "employees": employees,
                                                      "employees_list": employees_list, "task_id": task_id,
                                                      "proj_id": proj_id})

    def get_task_employee_reports(self, request, proj_id, task_id, empl_id, *args, **kwargs):
        task = Task.objects.get(id=task_id)
        employee = Employee.objects.get(customuser_ptr_id=empl_id)

        task_reps = TaskReport.objects.filter(report_task=task, report_employee=employee)

        if task_reps:
            task_report = [(task_rep.id,
                           task_rep.report,
                           ".".join(task_rep.end.strftime('%d-%m-%Y').split(sep="-"))) for task_rep in task_reps]
        else:
            task_report = []

        return render(request, 'man_task_report_info.html', {"task_report": task_report,
                                                             "task_id": task_id,
                                                             "proj_id": proj_id
                                                             })

    def add_task_page(self, request, proj_id, *args, **kwargs):
        project = Project.objects.get(id=proj_id)
        employees = Employee.objects.all()

        return render(request, 'man_add_tasks.html', {"project": project, "employees": employees, "proj_id": proj_id})

    def add_task(self, request, proj_id, *args, **kwargs):
        project = Project.objects.get(id=proj_id)
        title = request.POST.get('title')
        description = request.POST.get('description')

        start = datetime.strptime(request.POST.get('start'), '%Y-%m-%d')
        end = datetime.strptime(request.POST.get('end'), '%Y-%m-%d')

        task = Task(title=title, description=description, start=start, end=end)
        task.save()

        proj = Project.objects.get(title=project)
        proj_task = ProjectTask(project_title=proj, task_title=task)
        proj_task.save()

        return HttpResponseRedirect(reverse('man_project_info', kwargs={'id': proj.id}))

    def delete_empl(self, request, proj_id, task_id, task_empl_id, *args, **kwargs):
        task_empl = TaskEmployee.objects.get(id=task_empl_id)
        task_empl.delete()

        return HttpResponseRedirect(reverse('man_task_info', kwargs={'proj_id': proj_id, 'task_id': task_id}))

    def delete_project(self, request, id, *args, **kwargs):
        query = f"""
        SELECT task.id
        FROM hr_site_task as task
        JOIN hr_site_projecttask as pr_task 
        ON task.id = pr_task.task_title_id
        JOIN hr_site_project as project
        ON project.id = pr_task.project_title_id
        WHERE project.id = {id}
        ;
        """

        with connection.cursor() as cursor:
            cursor.execute(query)
            request_info = list(cursor.fetchall())

        for task_id in request_info:
            task = Task.objects.get(id=task_id[0])
            task.delete()

        project = Project.objects.get(id=id)
        project.delete()

        return HttpResponseRedirect(reverse('man_projects'))

    def delete_task(self, request, proj_id, task_id, *args, **kwargs):
        task = Task.objects.get(id=task_id)
        task.delete()

        return HttpResponseRedirect(reverse('man_project_info', kwargs={"id": proj_id}))

    def edit_project_page(self, request, id, *args, **kwargs):
        project = Project.objects.get(id=id)
        title, description, start, end, status = (
            project.title, project.description, project.start, project.end, project.status)
        start = datetime.strftime(start, '%Y-%m-%d')
        end = datetime.strftime(end, '%Y-%m-%d')

        return render(request, 'man_edit_project.html', {
            "title": title,
            "description": description,
            "start": start,
            "end": end,
            "statuses": STATUS,
            "id": id})

    def edit_project(self, request, id, *args, **kwargs):
        project = Project.objects.get(id=id)

        title = request.POST.get("title")
        description = request.POST.get("description")
        start = datetime.strptime(request.POST.get('start'), '%Y-%m-%d')
        end = datetime.strptime(request.POST.get('end'), '%Y-%m-%d')
        status = request.POST.get("statuses")

        project.title, project.description, project.start, project.end, project.status = title, description, start, end, status
        project.save()

        return HttpResponseRedirect(reverse('man_projects'))

    def edit_project_task_page(self, request, proj_id, task_id, *args, **kwargs):
        task = Task.objects.get(id=task_id)
        title, description, start, end, status = task.title, task.description, task.start, task.end, task.status
        start = datetime.strftime(start, '%Y-%m-%d')
        end = datetime.strftime(end, '%Y-%m-%d')

        return render(request, 'man_edit_project_task.html', {
            "title": title,
            "description": description,
            "start": start,
            "end": end,
            "statuses": STATUS,
            "proj_id": proj_id,
            "task_id": task_id})

    def edit_project_task(self, request, proj_id, task_id, *args, **kwargs):
        task = Task.objects.get(id=task_id)

        title = request.POST.get("title")
        description = request.POST.get("description")
        start = datetime.strptime(request.POST.get('start'), '%Y-%m-%d')
        end = datetime.strptime(request.POST.get('end'), '%Y-%m-%d')
        status = request.POST.get("statuses")

        task.title, task.description, task.start, task.end, task.status = title, description, start, end, status
        task.save()

        return HttpResponseRedirect(reverse('man_project_info', kwargs={"id": proj_id}))

    def print_report(self, request, proj_id, task_id, report_id, *args, **kwargs):
        task_report = TaskReport.objects.get(id=report_id)

        report = task_report.report
        user = task_report.report_employee

        user_name = user.first_name + " " + user.last_name
        task_name = task_report.report_task.title

        report = "\n".join([user_name, task_name, report])

        curr_time = datetime.now()
        curr_time = datetime.strftime(curr_time, '%d_%m_%Y_%H_%M_%S')

        filename = "_".join(["report", curr_time])
        filepath = os.path.join(BASE_DIR, "reports", filename)

        with open(filepath, 'w') as f:
            f.write(report)

        return HttpResponseRedirect(reverse('man_task_info', kwargs={"proj_id": proj_id, "task_id": task_id}))

    def search_project(self, request, *args, **kwargs):
        search_text = request.POST.get("search_text")

        projects = Project.objects.filter(title__contains=search_text).values_list('id', flat=True)

        if not projects:
            projects = []

        return self.get_projects_list(request, filtered_projects=projects)

    def search_task(self, request, proj_id, *args, **kwargs):
        search_text = request.POST.get("search_text")

        tasks = Task.objects.filter(title__contains=search_text).values_list('id', flat=True)

        if not tasks:
            tasks = []

        return self.get_project_info(request, proj_id, filtered_tasks=tasks)

    def get_statistics(self, request, *args, **kwargs):
        user_id = request.user.id
        manager = Manager.objects.get(customuser_ptr_id=user_id)
        dep = manager.department_title
        query = f"""
        SELECT task.status, COUNT(*)
        FROM hr_site_manager as manager
        JOIN hr_site_department as department
        ON manager.department_title_id = department.id
        JOIN hr_site_projectmanager as pr_man
        ON manager.customuser_ptr_id = pr_man.project_manager_id
        JOIN hr_site_projecttask as pr_task 
        ON pr_man.project_title_id = pr_task.project_title_id
        JOIN hr_site_task as task
        ON pr_task.task_title_id = task.id
        WHERE department.id = {dep.id}
        GROUP BY task.status"""

        with connection.cursor() as cursor:
            cursor.execute(query)
            task_efficiency_info = list(cursor.fetchall())

        tei = dict(task_efficiency_info)
        done = tei.get("DONE", 0)
        in_progress = tei.get("IN PROGRESS", 0)
        if done or in_progress:
            done_count = done / (done + in_progress) * 100
            done_count = f"{done_count: .2f}%"
        else:
            done_count = None

        return render(request, 'man_statistics.html', {"department": dep.title,
                                                       "in_progress": in_progress,
                                                       "done": done,
                                                       "done_count": done_count})

    def get_doc(self, request, doc_id, *args, **kwargs):
        doc = Doc.objects.get(id=doc_id)
        doc = doc.title
        title = doc.split(".")[0]

        path = os.path.join(BASE_DIR, "documents", doc)
        try:
            with open(path, 'r') as f:
                text = f.read()
        except FileNotFoundError:
            title = "Файл не найден"
            text = ""

        return render(request, 'man_doc.html', {"title": title, "text": text, "doc": doc})





