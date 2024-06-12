from django.contrib.auth.models import AbstractUser
from django.db import models


ROLE_CHOICES = (
    ('MANAGER', 'manager'),
    ('EMPLOYEE', 'employee'),
    ('DEFAULT', 'default')
)

STATUS = (
    ("ON APPROVAL", "на согласовании"),
    ("IN PROGRESS", "в процессе"),
    ("DONE", "завершен")
)

STATUS_DICT = dict(STATUS)


class CustomUser(AbstractUser):
    role = models.CharField(
        max_length=10,
        choices=ROLE_CHOICES,
        default='DEFAULT'
    )

    def __str__(self):
        return self.first_name + self.last_name


class Department(models.Model):
    title = models.CharField(max_length=30)

    def __str__(self):
        return self.title


class Doc(models.Model):
    title = models.CharField(max_length=50)

    def __str__(self):
        return self.title

class Manager(CustomUser):
    role = models.CharField(
        max_length=10,
        choices=ROLE_CHOICES,
        default='MANAGER',
        name='manager_role'
    )
    department_title = models.ForeignKey(Department, on_delete=models.CASCADE, null=True)

    class Meta:
        verbose_name = 'Manager'
        verbose_name_plural = 'Managers'


class Employee(CustomUser):
    role = models.CharField(
        max_length=10,
        choices=ROLE_CHOICES,
        default='EMPLOYEE',
        name='employee_role'
    )
    department_title = models.ForeignKey(Department, on_delete=models.CASCADE, null=True)

    class Meta:
        verbose_name = 'Employee'
        verbose_name_plural = 'Employees'


class Task(models.Model):
    title = models.CharField(max_length=30)
    description = models.TextField(max_length=1000)
    start = models.DateField()
    end = models.DateField()

    status = models.CharField(
        max_length=15,
        choices=STATUS,
        default='ON APPROVAL',
    )

    def __str__(self):
        return self.title


class Project(models.Model):
    title = models.CharField(max_length=30)
    description = models.TextField(max_length=1000)
    start = models.DateField()
    end = models.DateField()

    doc_title = models.ForeignKey(Doc, on_delete=models.CASCADE, null=True)

    status = models.CharField(
        max_length=15,
        choices=STATUS,
        default='ON APPROVAL',
    )

    def __str__(self):
        return self.title


class ProjectManager(models.Model):
    project_title = models.ForeignKey(Project, on_delete=models.CASCADE)
    project_manager = models.ForeignKey(Manager, on_delete=models.CASCADE)

    start = models.DateField(default="2024-05-10", null=True)
    end = models.DateField(default="2024-05-20", null=True)


class TaskEmployee(models.Model):
    task_title = models.ForeignKey(Task, on_delete=models.CASCADE)
    task_employee = models.ForeignKey(Employee, on_delete=models.CASCADE)

    start = models.DateField(default="2024-05-10", null=True)
    end = models.DateField(default="2024-05-20", null=True)


class ProjectTask(models.Model):
    project_title = models.ForeignKey(Project, on_delete=models.CASCADE)
    task_title = models.ForeignKey(Task, on_delete=models.CASCADE)


class TaskReport(models.Model):
    report_task = models.ForeignKey(Task, on_delete=models.CASCADE)
    report_employee = models.ForeignKey(Employee, on_delete=models.CASCADE, null=True)
    report = models.TextField(max_length=1000)
    end = models.DateField(default="2024-05-20", null=True)

