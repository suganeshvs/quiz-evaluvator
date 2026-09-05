from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    ROLE_CHOICES = (
        ('TEACHER', 'Teacher'),
        ('STUDENT', 'Student'),
    )
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='STUDENT')

    @property
    def is_teacher(self):
        return self.role == 'TEACHER'

    @property
    def is_student(self):
        return self.role == 'STUDENT'

    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"


class ClassRoom(models.Model):
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=20, unique=True)
    subject = models.CharField(max_length=100)
    teacher = models.ForeignKey(User, on_delete=models.CASCADE, related_name='classes_created')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} - {self.subject} ({self.code})"


class Enrollment(models.Model):
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='enrollments')
    classroom = models.ForeignKey(ClassRoom, on_delete=models.CASCADE, related_name='enrollments')
    enrolled_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('student', 'classroom')

    def __str__(self):
        return f"{self.student.username} in {self.classroom.name}"


class Document(models.Model):
    FILE_TYPE_CHOICES = (
        ('PDF', 'PDF Document'),
        ('PPT', 'PPT Presentation'),
        ('PPTX', 'PPTX Presentation'),
    )
    STATUS_CHOICES = (
        ('PENDING', 'Pending Processing'),
        ('PROCESSING', 'Processing'),
        ('COMPLETED', 'AI Analysis Completed'),
        ('FAILED', 'Processing Failed'),
    )

    classroom = models.ForeignKey(ClassRoom, on_delete=models.CASCADE, related_name='documents')
    title = models.CharField(max_length=255)
    file = models.FileField(upload_to='documents/', null=True, blank=True)
    file_type = models.CharField(max_length=10, choices=FILE_TYPE_CHOICES, default='PDF')
    total_pages = models.IntegerField(default=0)
    upload_date = models.DateTimeField(auto_now_add=True)
    processing_status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')

    def delete(self, *args, **kwargs):
        if self.file:
            try:
                self.file.delete(save=False)
            except Exception as e:
                print(f"Error deleting file {self.file}: {e}")
        super().delete(*args, **kwargs)

    def __str__(self):
        return f"{self.title} ({self.total_pages} Pages)"


class DocumentPage(models.Model):
    QUANTITY_CHOICES = (
        ('HIGH', 'High Content'),
        ('MEDIUM', 'Medium Content'),
        ('LOW', 'Low Content'),
    )

    document = models.ForeignKey(Document, on_delete=models.CASCADE, related_name='pages')
    page_number = models.IntegerField()
    extracted_text = models.TextField()
    content_quantity = models.CharField(max_length=10, choices=QUANTITY_CHOICES, default='HIGH')
    has_image = models.BooleanField(default=False)
    image_description = models.TextField(blank=True, default='')
    important_topics = models.JSONField(default=list, blank=True)
    paragraphs_data = models.JSONField(default=list, blank=True)

    class Meta:
        ordering = ['page_number']
        unique_together = ('document', 'page_number')

    def __str__(self):
        return f"{self.document.title} - Page {self.page_number}"


class ReadingProgress(models.Model):
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reading_progress')
    document = models.ForeignKey(Document, on_delete=models.CASCADE, related_name='student_progress')
    highest_page = models.IntegerField(default=1)
    paragraph_number = models.IntegerField(default=1)
    line_number = models.IntegerField(default=1)
    last_accessed = models.DateTimeField(auto_now=True)
    time_spent = models.IntegerField(default=0)  # in seconds

    class Meta:
        unique_together = ('student', 'document')

    @property
    def percentage(self):
        if self.document.total_pages > 0:
            pct = (self.highest_page / self.document.total_pages) * 100
            return round(pct, 1)
        return 0.0

    def __str__(self):
        return f"{self.student.username} - {self.document.title}: Page {self.highest_page}/{self.document.total_pages}"


class QuizAttempt(models.Model):
    STATUS_CHOICES = (
        ('IN_PROGRESS', 'In Progress'),
        ('COMPLETED', 'Completed'),
    )

    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='quiz_attempts')
    document = models.ForeignKey(Document, on_delete=models.CASCADE, related_name='quiz_attempts')
    confirmed_page = models.IntegerField()
    confirmed_paragraph = models.IntegerField(default=1)
    confirmed_line = models.IntegerField(default=1)
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    questions_attempted = models.IntegerField(default=0)
    correct_answers = models.IntegerField(default=0)
    wrong_answers = models.IntegerField(default=0)
    score = models.CharField(max_length=20, default='0/0')
    percentage = models.FloatField(default=0.0)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='IN_PROGRESS')

    class Meta:
        ordering = ['-started_at']

    def calculate_results(self):
        answered_q = self.questions.filter(student_answer__isnull=False)
        self.questions_attempted = answered_q.count()
        self.correct_answers = answered_q.filter(student_answer=models.F('correct_answer')).count()
        self.wrong_answers = self.questions_attempted - self.correct_answers
        self.score = f"{self.correct_answers}/{self.questions_attempted}"
        if self.questions_attempted > 0:
            self.percentage = round((self.correct_answers / self.questions_attempted) * 100, 2)
        else:
            self.percentage = 0.0
        self.save()

    def __str__(self):
        return f"Attempt by {self.student.username} on {self.document.title} - Score: {self.score} ({self.percentage}%)"


class QuizQuestion(models.Model):
    quiz_attempt = models.ForeignKey(QuizAttempt, on_delete=models.CASCADE, related_name='questions')
    question_text = models.TextField()
    option_a = models.TextField()
    option_b = models.TextField()
    option_c = models.TextField()
    option_d = models.TextField()
    correct_answer = models.CharField(max_length=1)  # A, B, C, D
    student_answer = models.CharField(max_length=1, null=True, blank=True)
    source_page = models.IntegerField()
    explanation = models.TextField()
    is_image_based = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def is_correct(self):
        return self.student_answer == self.correct_answer

    def __str__(self):
        return f"Q{self.id} (Page {self.source_page}): {self.question_text[:50]}..."
