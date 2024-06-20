from django.test import TestCase, Client
from django.urls import reverse
from django.conf import settings
from datetime import datetime


class EditProjectTaskTestCase(TestCase):
    def setUp(self):
        self.project = Project.objects.create(name="Test Project")
        self.task = Task.objects.create(
            title="Test Task",
            description="Test Description",
            start=datetime(2023, 1, 1),
            end=datetime(2023, 12, 31),
            status="Pending",
            project=self.project
        )

        self.client = Client()

        self.url = reverse('edit_project_task', args=[self.project.id, self.task.id])

    def test_edit_project_task(self):
        new_data = {
            "title": "Updated Task",
            "description": "Updated Description",
            "start": "2024-01-01",
            "end": "2024-12-31",
            "statuses": "Completed"
        }

    response = self.client.post(self.url, new_data)

    self.task.refresh_from_db()

    self.assertEqual(self.task.title, new_data["title"])
    self.assertEqual(self.task.description, new_data["description"])
    self.assertEqual(self.task.start, datetime.strptime(new_data["start"], '%Y-%m-%d'))
    self.assertEqual(self.task.end, datetime.strptime(new_data["end"], '%Y-%m-%d'))
    self.assertEqual(self.task.status, new_data["statuses"])

    self.assertEqual(response.status_code, 302)

    expected_redirect_url = reverse('man_project_info', kwargs={"id": self.project.id})
    self.assertRedirects(response, expected_redirect_url)

class PrintReportTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create(first_name="John", last_name="Doe")
        self.project = Project.objects.create(name="Test Project")
        self.task = Task.objects.create(
            title="Test Task",
            description="Test Description",
            start=datetime(2023, 1, 1),
            end=datetime(2023, 12, 31),
            status="Pending",
            project=self.project
        )
        self.task_report = TaskReport.objects.create(
            report="Test Report",
            report_employee=self.user,
            report_task=self.task
        )

        self.client = Client()

        self.url = reverse('print_report', args=[self.project.id, self.task.id, self.task_report.id])

    def tearDown(self):
        reports_dir = os.path.join(settings.BASE_DIR, "reports")
        for filename in os.listdir(reports_dir):
            file_path = os.path.join(reports_dir, filename)
            if os.path.isfile(file_path):
                os.unlink(file_path)

def test_print_report(self):
    response = self.client.get(self.url)

    self.assertEqual(response.status_code, 302)

    expected_redirect_url = reverse('man_task_info', kwargs={"proj_id": self.project.id, "task_id": self.task.id})
    self.assertRedirects(response, expected_redirect_url)

    reports_dir = os.path.join(settings.BASE_DIR, "reports")
    self.assertTrue(os.path.exists(reports_dir))

    files = os.listdir(reports_dir)
    self.assertEqual(len(files), 1)

    with open(os.path.join(reports_dir, files[0]), 'r') as f:
        content = f.read()
        expected_content = f"{self.user.first_name} {self.user.last_name}\n{self.task.title}\n{self.task_report.report}"
        self.assertEqual(content, expected_content)

class GetTaskInfoTestCase(TestCase):
    def setUp(self):
        self.project = Project.objects.create(name="Test Project")
        self.task = Task.objects.create(
            title="Test Task",
            description="Test Description",
            start=datetime(2023, 1, 1),
            end=datetime(2023, 12, 31),
            status="Pending",
            project=self.project
        )
        self.employee = Employee.objects.create(first_name="John", last_name="Doe")

        self.client = Client()

        self.url = reverse('get_task_info', args=[self.project.id, self.task.id])

    def test_get_task_info_post(self):
        data = {
            "employees": "Doe John",
            "start": "2023-01-01",
            "end": "2023-12-31"
        }
        response = self.client.post(self.url, data)
        task_employee = TaskEmployee.objects.filter(task_title=self.task, task_employee=self.employee).first()
        self.assertIsNotNone(task_employee)
        self.assertEqual(task_employee.start, datetime.strptime(data["start"], '%Y-%m-%d'))
        self.assertEqual(task_employee.end, datetime.strptime(data["end"], '%Y-%m-%d'))

        self.assertEqual(response.status_code, 200)

    def test_get_task_info_get(self):
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)

        context = response.context
        self.assertIn("task_info", context)
        self.assertIn("employees", context)
        self.assertIn("employees_list", context)
        self.assertIn("task_id", context)
        self.assertIn("proj_id", context)

        task_info = context["task_info"]
        self.assertEqual(len(task_info), 1)
        self.assertEqual(task_info[0][0], self.task.title)
        self.assertEqual(task_info[0][1], self.task.description)
        self.assertEqual(task_info[0][2], self.task.end.strftime('%d-%m-%Y'))
        self.assertEqual(task_info[0][3], "Pending")  # Assuming STA-TUS_DICT["Pending"] returns "Pending"

        employees_list = context["employees_list"]
        self.assertEqual(list(employees_list), [self.employee])
