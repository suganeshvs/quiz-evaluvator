from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
import json

from quiz_app.models import User, ClassRoom, Enrollment, Document, DocumentPage, ReadingProgress, QuizAttempt, QuizQuestion
from quiz_app.forms import ClassRoomForm, DocumentUploadForm
from quiz_app.services.document_analyzer import DocumentAnalyzer
from quiz_app.services.reading_tracker import ReadingTracker
from quiz_app.services.quiz_generator import QuizGenerator


def login_view(request):
    """
    Login view for both Teachers and Students.
    """
    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == 'POST':
        u_name = request.POST.get('username')
        p_word = request.POST.get('password')
        user = authenticate(request, username=u_name, password=p_word)
        if user is not None:
            login(request, user)
            return redirect('dashboard')
        else:
            messages.error(request, "Invalid username or password.")

    return render(request, 'auth/login.html')


def logout_view(request):
    logout(request)
    return redirect('login')


@login_required
def dashboard_view(request):
    """
    Main dashboard router directing Teacher vs Student.
    """
    if request.user.is_teacher:
        return redirect('teacher_dashboard')
    else:
        return redirect('student_dashboard')


# ==========================================
# TEACHER VIEWS
# ==========================================

@login_required
def teacher_dashboard(request):
    if not request.user.is_teacher:
        return redirect('student_dashboard')

    classes = ClassRoom.objects.filter(teacher=request.user)
    documents = Document.objects.filter(classroom__teacher=request.user)
    recent_attempts = QuizAttempt.objects.filter(document__classroom__teacher=request.user)[:5]
    total_students = Enrollment.objects.filter(classroom__teacher=request.user).values('student').distinct().count()

    context = {
        'classes': classes,
        'documents': documents,
        'recent_attempts': recent_attempts,
        'total_students': total_students,
    }
    return render(request, 'teacher/dashboard.html', context)


@login_required
def create_class(request):
    if not request.user.is_teacher:
        return redirect('student_dashboard')

    if request.method == 'POST':
        form = ClassRoomForm(request.POST)
        if form.is_valid():
            classroom = form.save(commit=False)
            classroom.teacher = request.user
            classroom.save()
            messages.success(request, f"Class {classroom.name} ({classroom.code}) created successfully!")
            return redirect('teacher_dashboard')
    else:
        form = ClassRoomForm()

    return render(request, 'teacher/create_class.html', {'form': form})


@login_required
def upload_document(request, class_id=None):
    if not request.user.is_teacher:
        return redirect('student_dashboard')

    classroom = get_object_or_404(ClassRoom, id=class_id, teacher=request.user) if class_id else None
    classes = ClassRoom.objects.filter(teacher=request.user)

    if request.method == 'POST':
        form = DocumentUploadForm(request.POST, request.FILES)
        selected_class_id = request.POST.get('classroom_id')
        target_class = get_object_or_404(ClassRoom, id=selected_class_id, teacher=request.user)

        if form.is_valid():
            doc = form.save(commit=False)
            doc.classroom = target_class
            doc.save()

            # Process document text & images using analyzer service
            DocumentAnalyzer.process_document(doc)

            messages.success(request, f"Document '{doc.title}' uploaded and AI analysis completed!")
            return redirect('teacher_document_list')
    else:
        form = DocumentUploadForm()

    return render(request, 'teacher/upload_document.html', {
        'form': form,
        'classroom': classroom,
        'classes': classes
    })


@login_required
def teacher_document_list(request):
    if not request.user.is_teacher:
        return redirect('student_dashboard')

    documents = Document.objects.filter(classroom__teacher=request.user).order_by('-upload_date')
    return render(request, 'teacher/document_list.html', {'documents': documents})


@login_required
def teacher_student_list(request):
    if not request.user.is_teacher:
        return redirect('student_dashboard')

    enrollments = Enrollment.objects.filter(classroom__teacher=request.user).select_related('student', 'classroom')
    return render(request, 'teacher/student_list.html', {'enrollments': enrollments})


@login_required
def class_detail(request, class_id):
    if not request.user.is_teacher:
        return redirect('student_dashboard')

    classroom = get_object_or_404(ClassRoom, id=class_id, teacher=request.user)
    documents = classroom.documents.all().order_by('-upload_date')
    enrollments = classroom.enrollments.select_related('student').order_by('enrolled_at')

    # Fetch all completed student quiz attempts for this specific class
    quiz_attempts = QuizAttempt.objects.filter(
        document__classroom=classroom,
        status='COMPLETED'
    ).select_related('student', 'document').order_by('-completed_at')

    context = {
        'classroom': classroom,
        'documents': documents,
        'enrollments': enrollments,
        'quiz_attempts': quiz_attempts,
    }
    return render(request, 'teacher/class_detail.html', context)


@login_required
def delete_class(request, class_id):
    if not request.user.is_teacher:
        return redirect('student_dashboard')

    classroom = get_object_or_404(ClassRoom, id=class_id, teacher=request.user)
    
    if request.method == 'POST':
        class_name = classroom.name
        classroom.delete()
        messages.success(request, f"Class '{class_name}' deleted successfully.")
        return redirect('teacher_dashboard')

    return render(request, 'teacher/delete_confirm.html', {
        'object_type': 'Class',
        'object_name': f"{classroom.name} ({classroom.code})",
        'cancel_url': 'teacher_dashboard'
    })


@login_required
def delete_document(request, doc_id):
    if not request.user.is_teacher:
        return redirect('student_dashboard')

    doc = get_object_or_404(Document, id=doc_id, classroom__teacher=request.user)
    class_id = doc.classroom.id

    if request.method == 'POST':
        doc_title = doc.title
        doc.delete()
        messages.success(request, f"Document '{doc_title}' deleted successfully.")
        return redirect('class_detail', class_id=class_id)

    return render(request, 'teacher/delete_confirm.html', {
        'object_type': 'Document',
        'object_name': doc.title,
        'cancel_url': 'teacher_document_list'
    })


@login_required
def enroll_student(request, class_id):
    if not request.user.is_teacher:
        return redirect('student_dashboard')

    classroom = get_object_or_404(ClassRoom, id=class_id, teacher=request.user)

    if request.method == 'POST':
        email = request.POST.get('student_email', '').strip().lower()
        if not email:
            messages.error(request, "Please provide a valid student email address.")
            return redirect('class_detail', class_id=class_id)

        # Find existing student or create new student account with this email
        student_user = User.objects.filter(email__iexact=email).first()
        if not student_user:
            student_user = User.objects.filter(username__iexact=email).first()

        if not student_user:
            uname = email.split('@')[0]
            # Ensure unique username
            base_uname = uname
            count = 1
            while User.objects.filter(username=uname).exists():
                uname = f"{base_uname}{count}"
                count += 1

            student_user = User.objects.create_user(
                username=uname,
                email=email,
                password='password123',
                role='STUDENT'
            )
            messages.info(request, f"Created new student account for {email} (Username: {uname}, Default Password: password123).")

        # Enroll student in classroom
        enrollment, created = Enrollment.objects.get_or_create(student=student_user, classroom=classroom)
        if created:
            messages.success(request, f"Student '{student_user.username}' ({email}) enrolled in {classroom.name} successfully!")
        else:
            messages.warning(request, f"Student '{student_user.username}' ({email}) is already enrolled in {classroom.name}.")

    return redirect('class_detail', class_id=class_id)


@login_required
def teacher_reports(request):
    if not request.user.is_teacher:
        return redirect('student_dashboard')

    attempts = QuizAttempt.objects.filter(
        document__classroom__teacher=request.user,
        status='COMPLETED'
    ).select_related('student', 'document').order_by('-completed_at')

    return render(request, 'teacher/teacher_reports.html', {'attempts': attempts})


# ==========================================
# STUDENT VIEWS
# ==========================================

@login_required
def student_dashboard(request):
    if not request.user.is_student:
        return redirect('teacher_dashboard')

    enrollments = Enrollment.objects.filter(student=request.user).select_related('classroom')
    my_class_ids = enrollments.values_list('classroom_id', flat=True)
    documents = Document.objects.filter(classroom_id__in=my_class_ids).order_by('-upload_date')

    # Get reading progress per document
    progress_map = {}
    for p in ReadingProgress.objects.filter(student=request.user):
        progress_map[p.document_id] = p

    recent_attempts = QuizAttempt.objects.filter(student=request.user).select_related('document')[:5]

    context = {
        'enrollments': enrollments,
        'documents': documents,
        'progress_map': progress_map,
        'recent_attempts': recent_attempts,
    }
    return render(request, 'student/dashboard.html', context)


@login_required
def document_viewer(request, doc_id):
    """
    Student document reader displaying pages, tracking progress,
    and featuring the top-right [ QUICK QUIZ ] button.
    STRICT ENROLLMENT CHECK: Student can ONLY view documents of enrolled classes!
    """
    doc = get_object_or_404(Document, id=doc_id)

    if request.user.is_student:
        is_enrolled = Enrollment.objects.filter(student=request.user, classroom=doc.classroom).exists()
        if not is_enrolled:
            messages.error(request, f"Access Denied: You are not enrolled in class '{doc.classroom.name}'.")
            return redirect('student_dashboard')

    pages = doc.pages.all().order_by('page_number')

    # Ensure document has pages (fallback if needed)
    if not pages.exists():
        DocumentAnalyzer.process_document(doc)
        pages = doc.pages.all().order_by('page_number')

    # Get or create reading progress
    progress, _ = ReadingProgress.objects.get_or_create(
        student=request.user,
        document=doc,
        defaults={'highest_page': 1}
    )

    page_num = request.GET.get('page', progress.highest_page)
    try:
        page_num = int(page_num)
        page_num = max(1, min(page_num, doc.total_pages or 1))
    except ValueError:
        page_num = 1

    # Auto-update highest page reached
    if page_num > progress.highest_page:
        progress.highest_page = page_num
        progress.save()

    current_page = pages.filter(page_number=page_num).first()

    context = {
        'document': doc,
        'pages': pages,
        'current_page': current_page,
        'current_page_num': page_num,
        'progress': progress,
        'total_pages': doc.total_pages or len(pages),
    }
    return render(request, 'documents/viewer.html', context)


@login_required
def update_reading_progress(request, doc_id):
    """
    AJAX endpoint called periodically by document reader to log page view & time.
    """
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            page_num = int(data.get('page_number', 1))
            duration = int(data.get('duration', 5))
            doc = get_object_or_404(Document, id=doc_id)

            progress = ReadingTracker.update_progress(
                student=request.user,
                document=doc,
                page_number=page_num,
                duration_seconds=duration
            )

            return JsonResponse({
                'status': 'success',
                'highest_page': progress.highest_page,
                'percentage': progress.percentage
            })
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
    return JsonResponse({'status': 'error'}, status=405)


@login_required
def confirm_progress(request, doc_id):
    """
    Reading Progress Confirmation view shown when student clicks QUICK QUIZ.
    Prompts student to verify or adjust Page / Paragraph / Line boundary.
    """
    doc = get_object_or_404(Document, id=doc_id)
    progress = ReadingProgress.objects.filter(student=request.user, document=doc).first()
    detected_page = progress.highest_page if progress else 1

    if request.method == 'POST':
        confirmed_page = int(request.POST.get('confirmed_page', detected_page))
        granularity = request.POST.get('granularity', 'page')
        confirmed_paragraph = 1
        confirmed_line = 1

        if granularity == 'paragraph':
            confirmed_paragraph = int(request.POST.get('paragraph_num', 1))
        elif granularity == 'line':
            confirmed_paragraph = int(request.POST.get('paragraph_num', 1))
            confirmed_line = int(request.POST.get('line_num', 1))

        # Create new QuizAttempt with confirmed boundary
        attempt = QuizAttempt.objects.create(
            student=request.user,
            document=doc,
            confirmed_page=confirmed_page,
            confirmed_paragraph=confirmed_paragraph,
            confirmed_line=confirmed_line,
            status='IN_PROGRESS'
        )

        # Generate initial batch of questions
        QuizGenerator.generate_next_questions(attempt, batch_size=3)

        return redirect('take_quiz', attempt_id=attempt.id)

    context = {
        'document': doc,
        'detected_page': detected_page,
        'total_pages': doc.total_pages,
    }
    return render(request, 'documents/confirm_progress.html', context)


@login_required
def take_quiz(request, attempt_id):
    """
    Interactive Quiz Interface.
    Displays questions dynamically, allowing endless questions or END QUIZ.
    """
    attempt = get_object_or_404(QuizAttempt, id=attempt_id, student=request.user)

    if attempt.status == 'COMPLETED':
        return redirect('quiz_result', attempt_id=attempt.id)

    questions = attempt.questions.all().order_by('id')

    # Index of current question
    q_index = request.GET.get('q', len(questions))
    try:
        q_index = int(q_index)
    except ValueError:
        q_index = 1

    # Generate more questions dynamically if student reached the end of current list
    if q_index > len(questions):
        new_q = QuizGenerator.generate_next_questions(attempt, batch_size=2)
        questions = attempt.questions.all().order_by('id')

    current_q = questions[q_index - 1] if (0 < q_index <= len(questions)) else questions.last()

    context = {
        'attempt': attempt,
        'questions': questions,
        'current_q': current_q,
        'current_q_index': q_index,
        'total_generated': len(questions),
    }
    return render(request, 'quiz/take_quiz.html', context)


@login_required
def submit_answer(request, question_id):
    """
    AJAX Endpoint to save student answer for a specific question.
    """
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            selected_option = data.get('answer', '').strip().upper()
            question = get_object_or_404(QuizQuestion, id=question_id, quiz_attempt__student=request.user)

            question.student_answer = selected_option
            question.save()

            # Update attempt progress count
            question.quiz_attempt.calculate_results()

            return JsonResponse({
                'status': 'success',
                'is_correct': question.is_correct(),
                'correct_answer': question.correct_answer,
                'explanation': question.explanation,
                'source_page': question.source_page
            })
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
    return JsonResponse({'status': 'error'}, status=405)


@login_required
def fetch_more_questions(request, attempt_id):
    """
    AJAX Endpoint to fetch/generate additional questions for unlimited quiz.
    """
    attempt = get_object_or_404(QuizAttempt, id=attempt_id, student=request.user)
    new_qs = QuizGenerator.generate_next_questions(attempt, batch_size=3)
    return JsonResponse({'status': 'success', 'count': len(new_qs)})


@login_required
def end_quiz(request, attempt_id):
    """
    Calculates final score ONLY from attempted questions and marks attempt COMPLETED.
    """
    attempt = get_object_or_404(QuizAttempt, id=attempt_id, student=request.user)
    attempt.completed_at = timezone.now()
    attempt.status = 'COMPLETED'
    attempt.calculate_results()  # Strictly excludes unattempted questions!

    return redirect('quiz_result', attempt_id=attempt.id)


@login_required
def quiz_result(request, attempt_id):
    """
    Detailed Quiz Result breakdown screen.
    """
    attempt = get_object_or_404(QuizAttempt, id=attempt_id, student=request.user)
    questions = attempt.questions.filter(student_answer__isnull=False)

    context = {
        'attempt': attempt,
        'questions': questions,
    }
    return render(request, 'quiz/quiz_result.html', context)


@login_required
def quiz_history(request):
    """
    Student view for past quiz attempts.
    """
    attempts = QuizAttempt.objects.filter(
        student=request.user,
        status='COMPLETED'
    ).select_related('document').order_by('-completed_at')

    return render(request, 'student/quiz_history.html', {'attempts': attempts})
