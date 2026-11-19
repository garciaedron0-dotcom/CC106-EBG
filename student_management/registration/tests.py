from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from .forms import StudentForm
from .models import student


class StudentRegistrationTests(TestCase):
    def setUp(self):
        self.staff = get_user_model().objects.create_user(
            username="staff",
            password="TestPassword123!",
            is_staff=True,
        )
        self.client.force_login(self.staff)
        self.student = student.objects.create(
            student_id="TEST-001",
            first_name="Alex",
            last_name="Rivera",
            gender="Female",
            date_of_birth="2005-04-12",
            contact_number="09170000001",
        )

    def test_staff_login_redirects_to_welcome_dashboard_even_with_directory_next_url(self):
        self.client.logout()
        response = self.client.post(
            reverse("login"),
            {
                "username": "staff",
                "password": "TestPassword123!",
                "next": reverse("student_list"),
            },
        )
        self.assertRedirects(response, reverse("staff_dashboard"))

    def test_module_six_pages_and_registration_aliases_remain_available(self):
        for url in (
            reverse("landing"),
            reverse("home"),
            reverse("home_capitalized"),
            reverse("student_registration"),
            reverse("register"),
            reverse("registration_success"),
        ):
            with self.subTest(url=url):
                self.assertEqual(self.client.get(url).status_code, 200)

    def test_staff_dashboard_welcomes_staff_and_links_to_student_pages(self):
        response = self.client.get(reverse("staff_dashboard"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, f"Welcome, Staff {self.staff.username}!")
        self.assertContains(response, reverse("student_registration"))
        self.assertContains(response, reverse("student_list"))
        self.assertContains(response, reverse("logout"))

    def test_non_staff_cannot_open_dashboard_or_student_directory(self):
        non_staff = get_user_model().objects.create_user(
            username="student-user",
            password="TestPassword123!",
        )
        self.client.force_login(non_staff)

        for url in (reverse("staff_dashboard"), reverse("student_list")):
            with self.subTest(url=url):
                response = self.client.get(url)
                self.assertEqual(response.status_code, 302)
                self.assertIn(reverse("login"), response["Location"])

    def test_student_registration_remains_public(self):
        self.client.logout()
        response = self.client.get(reverse("student_registration"))
        self.assertEqual(response.status_code, 200)

    def test_home_pages_link_to_registration_and_directory(self):
        for url in (reverse("landing"), reverse("home")):
            with self.subTest(url=url):
                response = self.client.get(url)
                self.assertContains(response, reverse("student_registration"))
                self.assertContains(response, reverse("student_list"))

    def test_original_registration_post_still_creates_a_student(self):
        self.client.logout()
        response = self.client.post(
            reverse("student_registration"),
            {
                "student_id": "TEST-003",
                "first_name": "Taylor",
                "last_name": "Morgan",
                "gender": "Female",
                "date_of_birth": "2003-11-25",
                "contact_number": "09170000003",
            },
            follow=True,
        )
        self.assertRedirects(response, reverse("registration_success"))
        self.assertTrue(student.objects.filter(student_id="TEST-003").exists())
        self.assertContains(response, "Student registered successfully.")

    def test_directory_lists_students_and_has_clear_search_link(self):
        response = self.client.get(reverse("student_list"))
        self.assertContains(response, "TEST-001")
        self.assertContains(response, "Alex")
        self.assertContains(response, "Student Directory")
        self.assertContains(response, "/static/registration/style.css")

    def test_search_matches_student_id_first_name_and_last_name_case_insensitively(self):
        for query in ("test-001", "alex", "RIVERA"):
            with self.subTest(query=query):
                response = self.client.get(reverse("student_list"), {"q": query})
                self.assertContains(response, "TEST-001")
                self.assertEqual(len(response.context["students"]), 1)

    def test_clear_search_returns_to_unfiltered_directory(self):
        response = self.client.get(reverse("student_list"), {"q": "no-match"})
        self.assertContains(response, "Clear search")
        cleared_response = self.client.get(response.context["request"].path)
        self.assertContains(cleared_response, "TEST-001")

    def test_detail_shows_all_student_fields(self):
        response = self.client.get(reverse("student_detail", args=[self.student.pk]))
        for value in ("TEST-001", "Alex", "Rivera", "Female", "April 12, 2005", "09170000001"):
            with self.subTest(value=value):
                self.assertContains(response, value)

    def test_create_saves_valid_model_form_and_displays_success_message(self):
        response = self.client.post(
            reverse("student_create"),
            {
                "student_id": "TEST-002",
                "first_name": "Jamie",
                "last_name": "Santos",
                "gender": "Male",
                "date_of_birth": "2004-08-03",
                "contact_number": "09170000002",
            },
            follow=True,
        )
        self.assertRedirects(response, reverse("student_list"))
        self.assertTrue(student.objects.filter(student_id="TEST-002").exists())
        self.assertContains(response, "Student created successfully.")

    def test_create_rejects_invalid_and_duplicate_student_ids(self):
        response = self.client.post(
            reverse("student_create"),
            {
                "student_id": "TEST-001",
                "first_name": "Jamie",
                "last_name": "Santos",
                "gender": "Male",
                "date_of_birth": "not-a-date",
                "contact_number": "09170000002",
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertFalse(student.objects.filter(first_name="Jamie").exists())
        self.assertContains(response, "already exists")
        self.assertContains(response, "Enter a valid date")

    def test_update_saves_valid_changes_and_redirects_to_detail(self):
        response = self.client.post(
            reverse("student_update", args=[self.student.pk]),
            {
                "student_id": "TEST-001",
                "first_name": "Alexandra",
                "last_name": "Rivera",
                "gender": "Female",
                "date_of_birth": "2005-04-12",
                "contact_number": "09170000003",
            },
            follow=True,
        )
        self.assertRedirects(response, reverse("student_detail", args=[self.student.pk]))
        self.student.refresh_from_db()
        self.assertEqual(self.student.first_name, "Alexandra")
        self.assertContains(response, "Student updated successfully.")

    def test_delete_confirmation_get_does_not_delete_record(self):
        response = self.client.get(reverse("student_delete", args=[self.student.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "TEST-001")
        self.assertContains(response, reverse("student_detail", args=[self.student.pk]))
        self.assertTrue(student.objects.filter(pk=self.student.pk).exists())

    def test_delete_requires_csrf_and_post_confirms_deletion(self):
        from django.test import Client

        client = Client(enforce_csrf_checks=True)
        client.force_login(self.staff)
        confirmation_url = reverse("student_delete", args=[self.student.pk])
        response = client.get(confirmation_url)
        self.assertEqual(response.status_code, 200)
        csrf_token = client.cookies["csrftoken"].value
        self.assertEqual(client.post(confirmation_url).status_code, 403)

        response = client.post(
            confirmation_url,
            {"csrfmiddlewaretoken": csrf_token},
            follow=True,
        )
        self.assertRedirects(response, reverse("student_list"))
        self.assertFalse(student.objects.filter(pk=self.student.pk).exists())
        self.assertContains(response, "Student deleted successfully.")

    def test_form_uses_existing_fields_and_date_picker(self):
        form = StudentForm()
        self.assertEqual(
            tuple(form.fields),
            (
                "student_id",
                "first_name",
                "last_name",
                "gender",
                "date_of_birth",
                "contact_number",
            ),
        )
        self.assertEqual(form.fields["date_of_birth"].widget.input_type, "date")
