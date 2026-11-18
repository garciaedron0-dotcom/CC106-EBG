from django import forms

from .models import student


class StudentForm(forms.ModelForm):
    class Meta:
        model = student
        fields = (
            "student_id",
            "first_name",
            "last_name",
            "gender",
            "date_of_birth",
            "contact_number",
        )
        widgets = {
            "date_of_birth": forms.DateInput(
                attrs={"type": "date"},
                format="%Y-%m-%d",
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs["class"] = (
                "form-select" if isinstance(field.widget, forms.Select) else "form-control"
            )
