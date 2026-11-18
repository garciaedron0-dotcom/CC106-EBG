from django.contrib import messages
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_http_methods

from .forms import StudentForm
from .models import student


def student_registration(request):
    form = StudentForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Student registered successfully.")
        return redirect("registration_success")

    return render(request, "registration/student_registration.html", {"form": form})


def registration_success(request):
    return render(request, "registration/success.html")


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


def student_detail(request, pk):
    student_record = get_object_or_404(student, pk=pk)
    return render(
        request,
        "registration/student_detail.html",
        {"student": student_record},
    )


def student_create(request):
    form = StudentForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Student created successfully.")
        return redirect("student_list")

    return render(request, "registration/student_form.html", {"form": form})


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
