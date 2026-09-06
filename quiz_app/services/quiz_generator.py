from quiz_app.models import QuizAttempt, QuizQuestion
from quiz_app.services.reading_tracker import ReadingTracker
from quiz_app.services.ai_service import AIService

class QuizGenerator:
    """
    High-level Quiz Generator enforcing boundary rules, MCQ validation,
    and dynamic unlimited question generation.
    """

    @staticmethod
    def generate_next_questions(quiz_attempt, batch_size=3):
        """
        Generates additional valid MCQs for an active quiz attempt,
        strictly respecting the attempt's confirmed boundary.
        """
        document = quiz_attempt.document
        confirmed_page = quiz_attempt.confirmed_page
        confirmed_paragraph = quiz_attempt.confirmed_paragraph
        confirmed_line = quiz_attempt.confirmed_line

        # 1. Fetch allowed content up to boundary
        allowed_info = ReadingTracker.get_allowed_content(
            document=document,
            confirmed_page=confirmed_page,
            confirmed_paragraph=confirmed_paragraph,
            confirmed_line=confirmed_line
        )

        # 2. Fetch existing questions to avoid duplicates
        existing_questions = quiz_attempt.questions.all()

        # 3. Call AI Service
        raw_mcqs = AIService.generate_mcqs(
            allowed_content_info=allowed_info,
            count=batch_size + 2,  # generate slight surplus for filtering
            existing_questions=existing_questions
        )

        created_questions = []

        # 4. Strict Validation Filter
        for q in raw_mcqs:
            if not isinstance(q, dict):
                if isinstance(q, list) and q and isinstance(q[0], dict):
                    q = q[0]
                else:
                    continue

            source_page = q.get('source_page', confirmed_page)

            # STRICT BOUNDARY CHECK: No question from unread pages!
            if source_page > confirmed_page:
                print(f"REJECTED QUESTION: source_page ({source_page}) > confirmed_page ({confirmed_page})")
                continue

            # Option validation
            opt_a = q.get('option_a', '').strip()
            opt_b = q.get('option_b', '').strip()
            opt_c = q.get('option_c', '').strip()
            opt_d = q.get('option_d', '').strip()
            correct = q.get('correct_answer', 'A').strip().upper()

            if not (opt_a and opt_b and opt_c and opt_d):
                continue

            if correct not in ['A', 'B', 'C', 'D']:
                correct = 'A'

            # Save Question
            new_question = QuizQuestion.objects.create(
                quiz_attempt=quiz_attempt,
                question_text=q.get('question', ''),
                option_a=opt_a,
                option_b=opt_b,
                option_c=opt_c,
                option_d=opt_d,
                correct_answer=correct,
                source_page=source_page,
                explanation=q.get('explanation', 'Based on confirmed reading material.'),
                is_image_based=q.get('is_image_based', False)
            )
            created_questions.append(new_question)

            if len(created_questions) >= batch_size:
                break

        return created_questions
