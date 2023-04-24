from django import forms

class ResumeUploadForm(forms.Form):
    resume = forms.FileField(label='Select a file', help_text='max. 5 megabytes')

    def clean_resume(self):
        resume = self.cleaned_data['resume']
        file_size = resume.size
        if file_size > 5242880:
            raise forms.ValidationError("The file is too large (max. 5 megabytes)")
        return resume
