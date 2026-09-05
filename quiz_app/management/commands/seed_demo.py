from django.core.management.base import BaseCommand
from quiz_app.models import User, ClassRoom, Enrollment, Document, DocumentPage, ReadingProgress
from quiz_app.services.document_analyzer import DocumentAnalyzer

class Command(BaseCommand):
    help = "Seeds initial demo data for AI Quiz Analyzer in Google Classroom"

    def handle(self, *args, **options):
        self.stdout.write(self.style.NOTICE("Seeding demo environment..."))

        # 1. Create Teacher
        teacher, created = User.objects.get_or_create(
            username='teacher1',
            defaults={
                'email': 'teacher1@classroom.edu',
                'role': 'TEACHER',
                'first_name': 'Sarah',
                'last_name': 'Conner'
            }
        )
        teacher.set_password('password123')
        teacher.save()
        if created:
            self.stdout.write(self.style.SUCCESS("Created Teacher: teacher1 / password123"))

        # 2. Create Student
        student, created = User.objects.get_or_create(
            username='student1',
            defaults={
                'email': 'student1@classroom.edu',
                'role': 'STUDENT',
                'first_name': 'Alex',
                'last_name': 'Morgan'
            }
        )
        student.set_password('password123')
        student.save()
        if created:
            self.stdout.write(self.style.SUCCESS("Created Student: student1 / password123"))

        # 3. Create Class 10A
        classroom, created = ClassRoom.objects.get_or_create(
            code='SCI10A',
            defaults={
                'name': '10A',
                'subject': 'Science',
                'teacher': teacher
            }
        )
        if created:
            self.stdout.write(self.style.SUCCESS("Created Class 10A (Science) - Code: SCI10A"))

        # 4. Enroll Student
        Enrollment.objects.get_or_create(student=student, classroom=classroom)

        # 5. Create Document: Light_Chapter_1.pdf (20 pages)
        doc, created = Document.objects.get_or_create(
            classroom=classroom,
            title='Light_Chapter_1.pdf',
            defaults={
                'file_type': 'PDF',
                'total_pages': 20,
                'processing_status': 'PENDING'
            }
        )

        # Process document to extract 20 structured pages
        DocumentAnalyzer.process_document(doc)
        self.stdout.write(self.style.SUCCESS(f"Processed 20 pages for document '{doc.title}' with status: {doc.processing_status}"))

        # 6. Seed Student Progress (Reached Page 5)
        progress, _ = ReadingProgress.objects.get_or_create(
            student=student,
            document=doc,
            defaults={
                'highest_page': 5,
                'paragraph_number': 2,
                'line_number': 3,
                'time_spent': 180
            }
        )
        progress.highest_page = 5
        progress.save()

        self.stdout.write(self.style.SUCCESS("Demo seeding completed successfully!"))
        self.stdout.write(self.style.MIGRATE_HEADING("Login Credentials:"))
        self.stdout.write("  Teacher: username='teacher1', password='password123'")
        self.stdout.write("  Student: username='student1', password='password123'")
        self.stdout.write("  Class: 10A | Document: Light_Chapter_1.pdf (20 pages)")
        self.stdout.write("  Initial Reading Progress: Page 5 of 20")
