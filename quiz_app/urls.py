from django.urls import path
from quiz_app import views

urlpatterns = [
    # Auth
    path('', views.login_view, name='login'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/', views.dashboard_view, name='dashboard'),

    # Teacher URLs
    path('teacher/dashboard/', views.teacher_dashboard, name='teacher_dashboard'),
    path('teacher/class/create/', views.create_class, name='create_class'),
    path('teacher/class/<int:class_id>/', views.class_detail, name='class_detail'),
    path('teacher/class/<int:class_id>/enroll/', views.enroll_student, name='enroll_student'),
    path('teacher/class/<int:class_id>/delete/', views.delete_class, name='delete_class'),
    path('teacher/upload/', views.upload_document, name='upload_document'),
    path('teacher/upload/<int:class_id>/', views.upload_document, name='upload_document_class'),
    path('teacher/document/<int:doc_id>/delete/', views.delete_document, name='delete_document'),
    path('teacher/documents/', views.teacher_document_list, name='teacher_document_list'),
    path('teacher/students/', views.teacher_student_list, name='teacher_student_list'),
    path('teacher/reports/', views.teacher_reports, name='teacher_reports'),

    # Student URLs
    path('student/dashboard/', views.student_dashboard, name='student_dashboard'),
    path('student/quiz/history/', views.quiz_history, name='quiz_history'),

    # Document & Reading Reader
    path('document/<int:doc_id>/read/', views.document_viewer, name='document_viewer'),
    path('api/document/<int:doc_id>/ping/', views.update_reading_progress, name='update_reading_progress'),
    path('document/<int:doc_id>/confirm-progress/', views.confirm_progress, name='confirm_progress'),

    # Quick Quiz Engine URLs
    path('quiz/attempt/<int:attempt_id>/take/', views.take_quiz, name='take_quiz'),
    path('api/question/<int:question_id>/answer/', views.submit_answer, name='submit_answer'),
    path('api/quiz/<int:attempt_id>/more-questions/', views.fetch_more_questions, name='fetch_more_questions'),
    path('quiz/attempt/<int:attempt_id>/end/', views.end_quiz, name='end_quiz'),
    path('quiz/attempt/<int:attempt_id>/result/', views.quiz_result, name='quiz_result'),
]
