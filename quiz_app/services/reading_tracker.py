from quiz_app.models import ReadingProgress, DocumentPage

class ReadingTracker:
    """
    Service for auto-tracking reading progress and constructing
    strictly bounded document text slices based on confirmed boundaries.
    """

    @staticmethod
    def update_progress(student, document, page_number, duration_seconds=5):
        """
        Updates student's reading progress for a given document.
        Ensures highest_page only increments forward when student navigates further.
        """
        progress, created = ReadingProgress.objects.get_or_create(
            student=student,
            document=document,
            defaults={'highest_page': page_number, 'time_spent': duration_seconds}
        )

        if not created:
            if page_number > progress.highest_page:
                progress.highest_page = page_number
            progress.time_spent += duration_seconds
            progress.save()

        return progress

    @staticmethod
    def get_allowed_content(document, confirmed_page, confirmed_paragraph=1, confirmed_line=1):
        """
        Extracts content ONLY up to the student's confirmed boundary.

        STRICT BOUNDARY RULES:
        1. Pages < confirmed_page: FULL page text is included.
        2. Page == confirmed_page: Text is cut off at confirmed_paragraph / confirmed_line.
        3. Pages > confirmed_page: FORBIDDEN / Completely excluded.
        """
        pages = DocumentPage.objects.filter(
            document=document,
            page_number__lte=confirmed_page
        ).order_by('page_number')

        allowed_text_chunks = []
        included_pages = []

        for page in pages:
            included_pages.append(page.page_number)
            if page.page_number < confirmed_page:
                # Include entire page
                text_block = f"--- PAGE {page.page_number} ---\n{page.extracted_text}"
                if page.has_image and page.image_description:
                    text_block += f"\n[VISUAL DIAGRAM / IMAGE: {page.image_description}]"
                allowed_text_chunks.append({
                    "page_number": page.page_number,
                    "text": text_block,
                    "has_image": page.has_image,
                    "image_description": page.image_description,
                    "is_full_page": True
                })
            elif page.page_number == confirmed_page:
                # Include page content trimmed to paragraph & line boundary
                trimmed_text = ReadingTracker._trim_page_content(
                    page, confirmed_paragraph, confirmed_line
                )
                text_block = f"--- PAGE {page.page_number} (Up to Paragraph {confirmed_paragraph}, Line {confirmed_line}) ---\n{trimmed_text}"
                if page.has_image and page.image_description:
                    text_block += f"\n[VISUAL DIAGRAM / IMAGE: {page.image_description}]"
                allowed_text_chunks.append({
                    "page_number": page.page_number,
                    "text": text_block,
                    "has_image": page.has_image,
                    "image_description": page.image_description,
                    "is_full_page": False
                })

        full_allowed_prompt_text = "\n\n".join([chunk["text"] for chunk in allowed_text_chunks])

        return {
            "allowed_chunks": allowed_text_chunks,
            "full_allowed_text": full_allowed_prompt_text,
            "included_pages": included_pages,
            "confirmed_boundary": {
                "page": confirmed_page,
                "paragraph": confirmed_paragraph,
                "line": confirmed_line
            }
        }

    @staticmethod
    def _trim_page_content(page, target_paragraph, target_line):
        """
        Trims a DocumentPage text up to the specified paragraph and line number.
        """
        paragraphs_data = page.paragraphs_data or []
        if not paragraphs_data:
            # Fallback text splitting if structured paragraphs missing
            paragraphs = [p.strip() for p in page.extracted_text.split('\n\n') if p.strip()]
            paragraphs_data = [
                {
                    "paragraph_number": i + 1,
                    "text": p,
                    "lines": [l.strip() for l in p.split('.') if l.strip()]
                }
                for i, p in enumerate(paragraphs)
            ]

        trimmed_paragraphs = []
        for p in paragraphs_data:
            p_num = p.get('paragraph_number', 1)
            if p_num < target_paragraph:
                trimmed_paragraphs.append(p.get('text', ''))
            elif p_num == target_paragraph:
                lines = p.get('lines', [])
                if lines and target_line <= len(lines):
                    selected_lines = lines[:target_line]
                    trimmed_paragraphs.append(". ".join(selected_lines) + ".")
                else:
                    trimmed_paragraphs.append(p.get('text', ''))
                break
            else:
                break

        return "\n\n".join(trimmed_paragraphs) if trimmed_paragraphs else page.extracted_text
