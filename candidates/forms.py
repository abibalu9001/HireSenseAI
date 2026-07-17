from django import forms


class ResumeUploadForm(forms.Form):
    resume_file = forms.FileField(
        widget=forms.FileInput(attrs={
            'class': 'form-control',
            'accept': '.pdf,.docx,.doc',
            'id': 'resumeFile',
        }),
        help_text='Accepted formats: PDF, DOCX (max 50MB)'
    )
    job = forms.IntegerField(widget=forms.HiddenInput(), required=False)
