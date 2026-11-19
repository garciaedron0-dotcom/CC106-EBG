
from django.contrib import messages
from django.contrib.auth.views import LoginView
from django.contrib.auth.decorators import user_passes_test
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.decorators.http import require_http_methods

from .forms import StudentForm
from .models import student


# Check if user is an authenticated staff member
def staff_check(user):
    return user.is_authenticated and user.is_staff


class StaffLoginView(LoginView):
    template_name = "login.html"

    def get_success_url(self):
        if self.request.user.is_staff:
            return reverse("staff_dashboard")
        return reverse("login")


# Staff Dashboard
@user_passes_test(staff_check, login_url='login')
def staff_dashboard(request):
    total_students = student.objects.count()
    male_students = student.objects.filter(gender__in=("M", "Male")).count()
    female_students = student.objects.filter(gender__in=("F", "Female")).count()

    if total_students:
        male_percent = round((male_students / total_students) * 100, 1)
        female_percent = round((female_students / total_students) * 100, 1)
    else:
        male_percent = 0
        female_percent = 0

    query = request.GET.get("q", "").strip()
    students = student.objects.all().order_by("last_name", "first_name", "student_id")
    if query:
        students = students.filter(
            Q(student_id__icontains=query)
            | Q(first_name__icontains=query)
            | Q(last_name__icontains=query)
        )

    return render(
        request,
        'registration/dashboard.html',
        {
            "total_students": total_students,
            "male_students": male_students,
            "female_students": female_students,
            "male_percent": male_percent,
            "female_percent": female_percent,
            "students": students,
            "query": query,
        },
    )


# Public Student Registration
def student_registration(request):
    form = StudentForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Student registered successfully.")
        return redirect("registration_success")

    return render(request, "registration/student_registration.html", {"form": form})


def registration_success(request):
    return render(request, "registration/success.html")


# Staff-only Student Directory
@user_passes_test(staff_check, login_url='login')
def student_list(request):
    query = request.GET.get("q", "").strip()
    students = student.objects.all().order_by("last_name", "first_name", "student_id")
    if query:
        students = students.filter(
            Q(student_id__icontains=query)
            | Q(first_name__icontains=query)
            | Q(last_name__icontains=query)
        )

    return render(
        request,
        "registration/student_list.html",
        {"students": students, "query": query},
    )


# Staff-only Student Details
@user_passes_test(staff_check, login_url='login')
def student_detail(request, pk):
    student_record = get_object_or_404(student, pk=pk)
    return render(
        request,
        "registration/student_detail.html",
        {"student": student_record},
    )


# Staff-only Student Creation
@user_passes_test(staff_check, login_url='login')
def student_create(request):
    form = StudentForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Student created successfully.")
        return redirect("student_list")

    return render(request, "registration/student_form.html", {"form": form})


# Staff-only Student Update
@user_passes_test(staff_check, login_url='login')
def student_update(request, pk):
    student_record = get_object_or_404(student, pk=pk)
    form = StudentForm(request.POST or None, instance=student_record)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Student updated successfully.")
        return redirect("student_detail", pk=student_record.pk)

    return render(
        request,
        "registration/student_form.html",
        {"form": form, "student": student_record},
    )


# Staff-only Student Deletion
@user_passes_test(staff_check, login_url='login')
@require_http_methods(["GET", "POST"])
def student_delete(request, pk):
    student_record = get_object_or_404(student, pk=pk)
    if request.method == "POST":
        student_record.delete()
        messages.success(request, "Student deleted successfully.")
        return redirect("student_list")

    return render(
        request,
        "registration/student_confirm_delete.html",
        {"student": student_record},
    )
