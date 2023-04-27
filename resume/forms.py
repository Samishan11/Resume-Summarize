from django import forms
from crispy_forms.bootstrap import FormActions
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit


class ResumeUploadForm(forms.Form):
    resume = forms.FileField(label="")

    def clean_resume(self):
        resume = self.cleaned_data["resume"]
        file_size = resume.size
        if file_size > 5242880:
            raise forms.ValidationError("The file is too large (max. 5 megabytes)")
        return resume

    def __init__(self, *args, **kwargs):
        super(ResumeUploadForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = "post"
        self.helper.layout = Layout(
            "resume", FormActions(Submit("submit", "Upload", css_class="btn-primary"))
        )
