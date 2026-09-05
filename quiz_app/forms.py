from django import forms
from quiz_app.models import ClassRoom, Document

class ClassRoomForm(forms.ModelForm):
    class Meta:
        model = ClassRoom
        fields = ['name', 'code', 'subject']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. 10A'}),
            'code': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. SCI10A'}),
            'subject': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Science'}),
        }

class DocumentUploadForm(forms.ModelForm):
    class Meta:
        model = Document
        fields = ['title', 'file', 'file_type']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Light_Chapter_1.pdf'}),
            'file': forms.FileInput(attrs={'class': 'form-control'}),
            'file_type': forms.Select(attrs={'class': 'form-select'}),
        }

    def clean_file(self):
        file = self.cleaned_data.get('file')
        if file:
            ext = file.name.split('.')[-1].lower()
            if ext not in ['pdf', 'ppt', 'pptx']:
                raise forms.ValidationError("Unsupported file format. Please upload PDF, PPT, or PPTX.")
            if file.size > 25 * 1024 * 1024:  # 25 MB limit
                raise forms.ValidationError("File size exceeds 25 MB limit.")
        return file
