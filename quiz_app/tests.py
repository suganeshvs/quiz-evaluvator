from django.test import TestCase, Client
from django.urls import reverse
from quiz_app.models import User, ClassRoom, Enrollment, Document, DocumentPage, ReadingProgress, QuizAttempt, QuizQuestion
from quiz_app.services.document_analyzer import DocumentAnalyzer
from quiz_app.services.reading_tracker import ReadingTracker
from quiz_app.services.quiz_generator import QuizGenerator

class AIQuizAnalyzerTestCase(TestCase):
    def setUp(self):
        # Create Teacher and Student
        self.teacher = User.objects.create_user(
            username='test_teacher', password='password123', role='TEACHER'
        )
        self.student = User.objects.create_user(
            username='test_student', password='password123', role='STUDENT'
        )

        # Create Class
        self.classroom = ClassRoom.objects.create(
            name='10A', code='SCI10A', subject='Science', teacher=self.teacher
        )
        Enrollment.objects.create(student=self.student, classroom=self.classroom)

        # Create 20-Page Document
        self.document = Document.objects.create(
            classroom=self.classroom,
            title='Light_Chapter_1.pdf',
            file_type='PDF',
            total_pages=20
        )
        DocumentAnalyzer.process_document(self.document)

        self.client = Client()

    def test_user_login(self):
        login_success = self.client.login(username='test_teacher', password='password123')
        self.assertTrue(login_success)

    def test_teacher_class_creation(self):
        self.client.login(username='test_teacher', password='password123')
        response = self.client.post(reverse('create_class'), {
            'name': '10B',
            'subject': 'Physics',
            'code': 'PHY10B'
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(ClassRoom.objects.filter(code='PHY10B').exists())

    def test_reading_progress_tracking(self):
        progress = ReadingTracker.update_progress(
            student=self.student,
            document=self.document,
            page_number=5,
            duration_seconds=30
        )
        self.assertEqual(progress.highest_page, 5)
        self.assertEqual(progress.percentage, 25.0)

    def test_content_boundary_enforcement(self):
        """
        STRICT TEST: If confirmed_page = 5, NO question may have source_page > 5!
        """
        attempt = QuizAttempt.objects.create(
            student=self.student,
            document=self.document,
            confirmed_page=5,
            confirmed_paragraph=2,
            confirmed_line=3
        )

        # Generate questions
        questions = QuizGenerator.generate_next_questions(attempt, batch_size=10)
        self.assertTrue(len(questions) > 0)

        for q in attempt.questions.all():
            self.assertLessEqual(
                q.source_page, 5,
                f"FORBIDDEN CONTENT VIOLATION: Question source page {q.source_page} exceeds confirmed boundary 5!"
            )

    def test_score_calculation_strict_rule(self):
        """
        STRICT TEST: 18 attempted, 14 correct => score = 14/18, percentage = 77.78%
        """
        attempt = QuizAttempt.objects.create(
            student=self.student,
            document=self.document,
            confirmed_page=5
        )

        # Simulate 18 answered questions (14 correct, 4 wrong)
        for i in range(18):
            is_correct = (i < 14)
            correct_ans = 'A'
            student_ans = 'A' if is_correct else 'B'

            QuizQuestion.objects.create(
                quiz_attempt=attempt,
                question_text=f"Question {i+1}",
                option_a="Option A",
                option_b="Option B",
                option_c="Option C",
                option_d="Option D",
                correct_answer=correct_ans,
                student_answer=student_ans,
                source_page=3,
                explanation="Sample explanation"
            )

        attempt.calculate_results()

        self.assertEqual(attempt.questions_attempted, 18)
        self.assertEqual(attempt.correct_answers, 14)
        self.assertEqual(attempt.wrong_answers, 4)
        self.assertEqual(attempt.score, "14/18")
        self.assertEqual(attempt.percentage, 77.78)

    def test_quiz_history_logging(self):
        attempt = QuizAttempt.objects.create(
            student=self.student,
            document=self.document,
            confirmed_page=5,
            status='COMPLETED',
            questions_attempted=18,
            correct_answers=14,
            wrong_answers=4,
            score='14/18',
            percentage=77.78
        )
        self.client.login(username='test_student', password='password123')
        response = self.client.get(reverse('quiz_history'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "14/18")
        self.assertContains(response, "77.78%")

    def test_teacher_class_detail_and_deletion(self):
        self.client.login(username='test_teacher', password='password123')
        # View class detail
        res_detail = self.client.get(reverse('class_detail', kwargs={'class_id': self.classroom.id}))
        self.assertEqual(res_detail.status_code, 200)
        self.assertContains(res_detail, self.classroom.name)

        # Delete class
        res_del = self.client.post(reverse('delete_class', kwargs={'class_id': self.classroom.id}))
        self.assertEqual(res_del.status_code, 302)
        self.assertFalse(ClassRoom.objects.filter(id=self.classroom.id).exists())

    def test_teacher_document_deletion(self):
        self.client.login(username='test_teacher', password='password123')
        doc_id = self.document.id
        res_del = self.client.post(reverse('delete_document', kwargs={'doc_id': doc_id}))
        self.assertEqual(res_del.status_code, 302)
        self.assertFalse(Document.objects.filter(id=doc_id).exists())

    def test_student_enrollment_and_access_control(self):
        # 1. Create a second student who is NOT enrolled
        unassigned_student = User.objects.create_user(
            username='stranger_student', email='stranger@classroom.edu', password='password123', role='STUDENT'
        )

        # 2. Stranger tries to access document viewer -> Must be DENIED
        self.client.login(username='stranger_student', password='password123')
        res_denied = self.client.get(reverse('document_viewer', kwargs={'doc_id': self.document.id}), follow=True)
        self.assertContains(res_denied, "Access Denied")

        # 3. Teacher enrolls stranger using email
        self.client.login(username='test_teacher', password='password123')
        res_enroll = self.client.post(reverse('enroll_student', kwargs={'class_id': self.classroom.id}), {
            'student_email': 'stranger@classroom.edu'
        }, follow=True)
        self.assertEqual(res_enroll.status_code, 200)
        self.assertTrue(Enrollment.objects.filter(student=unassigned_student, classroom=self.classroom).exists())

        # 4. Now stranger can access document viewer -> Must be ALLOWED
        self.client.login(username='stranger_student', password='password123')
        res_allowed = self.client.get(reverse('document_viewer', kwargs={'doc_id': self.document.id}))
        self.assertEqual(res_allowed.status_code, 200)
