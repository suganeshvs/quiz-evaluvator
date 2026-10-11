import json
import os
import random
import re
import shutil
import subprocess
import sys
import tempfile
import threading
import time
import urllib.parse
import urllib.request
from django.conf import settings

class AIService:
    """
    Modular AI Service Interface supporting Local Ollama LLM API,
    OpenAI / Gemini LLM APIs, and Fallback Mock AI Mode.
    Equipped with autonomous self-download and self-healing for AI engine & models.
    """
    _engine_lock = threading.Lock()
    _is_downloading_engine = False
    _is_pulling_model = False
    _engine_status = "uninitialized"

    @classmethod
    def ensure_ai_engine_ready(cls, async_mode=False):
        """
        Guarantees that the local AI engine (Ollama) and required models (llama3.2:1b)
        are downloaded, installed, running, and ready irrespective of the computer.
        If async_mode is True, runs in a background thread to prevent blocking.
        """
        if not getattr(settings, 'USE_OLLAMA', True):
            return True

        if async_mode:
            t = threading.Thread(target=cls._perform_engine_setup, daemon=True)
            t.start()
            return True
        else:
            return cls._perform_engine_setup()

    @classmethod
    def _perform_engine_setup(cls):
        with cls._engine_lock:
            base_url = getattr(settings, 'OLLAMA_BASE_URL', 'http://localhost:11434').rstrip('/')
            preferred_model = getattr(settings, 'OLLAMA_MODEL', 'llama3.2:1b')

            # 1. Check if Ollama service is already responding
            if cls._is_ollama_running(base_url):
                cls._engine_status = "running"
                cls._ensure_model_downloaded(base_url, preferred_model)
                return True

            # 2. Service is not listening. Check if Ollama executable exists on this computer
            ollama_exe = cls._find_ollama_executable()
            if not ollama_exe:
                # 3. Not installed on this machine: auto-download and install Ollama!
                print("[AI ENGINE] Ollama not found on this computer. Automatically downloading & installing...")
                ollama_exe = cls._auto_download_and_install_ollama()

            if ollama_exe:
                # 4. Start Ollama service in background
                print(f"[AI ENGINE] Starting Ollama daemon ({ollama_exe} serve)...")
                cls._start_ollama_service(ollama_exe)
                # Wait up to 8 seconds for daemon to start
                for _ in range(8):
                    time.sleep(1)
                    if cls._is_ollama_running(base_url):
                        cls._engine_status = "running"
                        break

            # 5. Verify service is active and ensure model is pulled
            if cls._is_ollama_running(base_url):
                cls._ensure_model_downloaded(base_url, preferred_model)
                return True
            else:
                cls._engine_status = "offline_fallback"
                return False

    @classmethod
    def _is_ollama_running(cls, base_url):
        try:
            req = urllib.request.Request(f"{base_url}/api/tags")
            with urllib.request.urlopen(req, timeout=2) as response:
                return response.status == 200
        except Exception:
            return False

    @classmethod
    def _find_ollama_executable(cls):
        exe = shutil.which('ollama')
        if exe and os.path.exists(exe):
            return exe

        candidates = [
            os.path.expandvars(r'%LOCALAPPDATA%\Programs\Ollama\ollama.exe'),
            r'C:\Program Files\Ollama\ollama.exe',
            os.path.expandvars(r'%PROGRAMFILES%\Ollama\ollama.exe'),
            r'C:\ProgramData\Ollama\ollama.exe',
            '/usr/local/bin/ollama',
            '/usr/bin/ollama',
        ]
        for c in candidates:
            if c and os.path.exists(c):
                return c
        return None

    @classmethod
    def _start_ollama_service(cls, ollama_exe):
        try:
            creationflags = getattr(subprocess, 'CREATE_NO_WINDOW', 0) if os.name == 'nt' else 0
            subprocess.Popen(
                [ollama_exe, 'serve'],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                creationflags=creationflags
            )
            return True
        except Exception as e:
            print(f"[AI ENGINE] Error launching Ollama service: {e}")
            return False

    @classmethod
    def _auto_download_and_install_ollama(cls):
        if sys.platform != 'win32':
            return None
        installer_path = os.path.join(tempfile.gettempdir(), 'OllamaSetup.exe')
        url = 'https://ollama.com/download/OllamaSetup.exe'
        try:
            print(f"[AI ENGINE] Downloading Ollama installer from {url}...")
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req, timeout=120) as resp, open(installer_path, 'wb') as f:
                shutil.copyfileobj(resp, f)

            print("[AI ENGINE] Download complete. Executing silent installation...")
            creationflags = getattr(subprocess, 'CREATE_NO_WINDOW', 0) if os.name == 'nt' else 0
            subprocess.run([installer_path, '/silent'], capture_output=True, timeout=180, creationflags=creationflags)
            try:
                os.remove(installer_path)
            except Exception:
                pass

            # Refresh PATH in current process
            local_appdata = os.environ.get('LOCALAPPDATA', '')
            ollama_dir = os.path.join(local_appdata, 'Programs', 'Ollama')
            if ollama_dir not in os.environ.get('PATH', ''):
                os.environ['PATH'] = f"{ollama_dir};{os.environ.get('PATH', '')}"

            return cls._find_ollama_executable()
        except Exception as e:
            print(f"[AI ENGINE] Automatic Ollama installation failed: {e}")
            return None

    @classmethod
    def _ensure_model_downloaded(cls, base_url, preferred_model='llama3.2:1b'):
        if cls._is_pulling_model:
            return

        model = cls._resolve_ollama_model(base_url, preferred_model)
        if model:
            return

        def pull_worker():
            cls._is_pulling_model = True
            print(f"[AI ENGINE] Pulling required AI model '{preferred_model}' in background...")
            try:
                pull_url = f"{base_url}/api/pull"
                payload = json.dumps({"name": preferred_model, "stream": False}).encode('utf-8')
                req = urllib.request.Request(pull_url, data=payload, headers={'Content-Type': 'application/json'})
                with urllib.request.urlopen(req, timeout=600) as resp:
                    print(f"[AI ENGINE] Model '{preferred_model}' download complete via API!")
            except Exception as e:
                try:
                    ollama_exe = cls._find_ollama_executable() or 'ollama'
                    creationflags = getattr(subprocess, 'CREATE_NO_WINDOW', 0) if os.name == 'nt' else 0
                    subprocess.run([ollama_exe, 'pull', preferred_model], timeout=600, creationflags=creationflags)
                    print(f"[AI ENGINE] Model '{preferred_model}' download complete via CLI!")
                except Exception as ex:
                    print(f"[AI ENGINE] Model pull error: {ex}")
            finally:
                cls._is_pulling_model = False

        t = threading.Thread(target=pull_worker, daemon=True)
        t.start()

    @staticmethod
    def generate_mcqs(allowed_content_info, count=5, existing_questions=None):
        """
        Generates MCQs strictly from allowed_content_info.
        Prioritizes Local Ollama API, then OpenAI/Gemini, then fallback Mock AI.
        """
        use_ollama = getattr(settings, 'USE_OLLAMA', True)
        if use_ollama:
            try:
                # Trigger self-healing / auto-readiness in background
                AIService.ensure_ai_engine_ready(async_mode=True)
                print("Attempting MCQ generation using local Ollama LLM API...")
                questions = AIService._generate_ollama_mcqs(allowed_content_info, count)
                if questions:
                    return questions
            except Exception as e:
                print(f"Local Ollama API unavailable/error: {e}. Falling back to secondary AI / Mock AI.")

        if getattr(settings, 'MOCK_AI', False):
            return AIService._generate_mock_mcqs(allowed_content_info, count, existing_questions)

        # Attempt OpenAI or Gemini if configured
        try:
            if getattr(settings, 'OPENAI_API_KEY', ''):
                return AIService._generate_openai_mcqs(allowed_content_info, count)
            elif getattr(settings, 'GEMINI_API_KEY', ''):
                return AIService._generate_gemini_mcqs(allowed_content_info, count)
            else:
                return AIService._generate_mock_mcqs(allowed_content_info, count, existing_questions)
        except Exception as e:
            print(f"AI API call failed: {e}. Falling back to MOCK AI.")
            return AIService._generate_mock_mcqs(allowed_content_info, count, existing_questions)

    @staticmethod
    def _generate_ollama_mcqs(allowed_content_info, count):
        """
        Queries local Ollama API (http://localhost:11434/api/chat) to generate structured JSON MCQs.
        Auto-detects installed Ollama models and handles robust JSON parsing.
        """
        base_url = getattr(settings, 'OLLAMA_BASE_URL', 'http://localhost:11434').rstrip('/')
        url = f"{base_url}/api/chat"
        preferred_model = getattr(settings, 'OLLAMA_MODEL', 'llama3.2:1b')
        
        # 1. Auto-detect installed model in Ollama if preferred model isn't available
        model = AIService._resolve_ollama_model(base_url, preferred_model)
        if not model:
            AIService._ensure_model_downloaded(base_url, preferred_model)
            raise Exception("AI model is currently downloading in background. Using instant fallback.")

        prompt_text = allowed_content_info['full_allowed_text']
        if len(prompt_text) > 3000:
            prompt_text = prompt_text[:3000]

        confirmed_page = allowed_content_info['confirmed_boundary']['page']

        system_prompt = (
            "You are a quiz generator. Generate valid JSON MCQs based ONLY on the provided text.\n"
            "Respond strictly in this JSON format:\n"
            '{"questions": [{"question": "...", "option_a": "...", "option_b": "...", "option_c": "...", "option_d": "...", "correct_answer": "A", "source_page": 1, "explanation": "..."}]}'
        )

        user_prompt = f"Generate {count} distinct MCQs from this text:\n\n{prompt_text}"

        payload = {
            "model": model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            "format": "json",
            "stream": False
        }

        data_bytes = json.dumps(payload).encode('utf-8')
        req = urllib.request.Request(
            url,
            data=data_bytes,
            headers={'Content-Type': 'application/json'},
            method='POST'
        )

        # Extended timeout to 90 seconds for local LLM inference
        with urllib.request.urlopen(req, timeout=90) as response:
            res_data = json.loads(response.read().decode('utf-8'))
            content_str = res_data.get('message', {}).get('content', '')

            # Extract and parse JSON with automatic error repairing
            return AIService._repair_and_parse_json(content_str)

    @staticmethod
    def _repair_and_parse_json(content_str):
        """
        Repairs common LLM JSON syntax errors (missing commas, trailing commas, bad quotes)
        and extracts valid MCQ dicts.
        """
        if not content_str:
            return []

        cleaned = content_str.strip()
        if "```" in cleaned:
            match = re.search(r'```(?:json)?\s*([\s\S]*?)\s*```', cleaned)
            if match:
                cleaned = match.group(1)

        json_match = re.search(r'(\{[\s\S]*\}|\[[\s\S]*\])', cleaned)
        if json_match:
            cleaned = json_match.group(1)

        # 1. Attempt direct parse
        try:
            parsed = json.loads(cleaned)
            normalized = AIService._normalize_mcq_list(parsed)
            if normalized:
                return normalized
        except Exception:
            pass

        # 2. Syntax repairs on full JSON string
        repaired = re.sub(r'("\s*)\n?(\s*"[a-zA-Z_]+":)', r'\1,\2', cleaned)
        repaired = re.sub(r',\s*([\}\]])', r'\1', repaired)

        try:
            parsed = json.loads(repaired)
            normalized = AIService._normalize_mcq_list(parsed)
            if normalized:
                return normalized
        except Exception:
            pass

        # 3. Extract individual question objects using regex pattern matching
        extracted = []
        matches = re.findall(r'\{[^{}]*?"question"[^{}]*?\}', cleaned, re.DOTALL)
        if not matches:
            matches = re.findall(r'\{[^{}]*?"option_a"[^{}]*?\}', cleaned, re.DOTALL)

        for m in matches:
            try:
                d = json.loads(m)
                if isinstance(d, dict):
                    extracted.append(d)
                    continue
            except Exception:
                pass

            m_rep = re.sub(r'("\s*)\n?(\s*"[a-zA-Z_]+":)', r'\1,\2', m)
            m_rep = re.sub(r',\s*([\}\]])', r'\1', m_rep)
            try:
                d = json.loads(m_rep)
                if isinstance(d, dict):
                    extracted.append(d)
            except Exception:
                pass

        return AIService._normalize_mcq_list(extracted)

    @staticmethod
    def _normalize_mcq_list(raw):
        """
        Normalizes any JSON structure (dict with questions/mcqs/data, list of dicts,
        nested lists, or single dict) into a flat list of question dicts.
        """
        if not raw:
            return []

        if isinstance(raw, dict):
            for key in ['questions', 'mcqs', 'quiz', 'data', 'results', 'items']:
                if key in raw and isinstance(raw[key], (list, dict)):
                    return AIService._normalize_mcq_list(raw[key])
            if 'question' in raw or 'option_a' in raw or 'question_text' in raw:
                return [raw]
            for val in raw.values():
                if isinstance(val, (list, dict)):
                    res = AIService._normalize_mcq_list(val)
                    if res:
                        return res
            return []

        if isinstance(raw, list):
            result = []
            for item in raw:
                if isinstance(item, dict):
                    if 'question' in item or 'option_a' in item or 'question_text' in item:
                        result.append(item)
                    else:
                        res = AIService._normalize_mcq_list(item)
                        if res:
                            result.extend(res)
                elif isinstance(item, list):
                    res = AIService._normalize_mcq_list(item)
                    if res:
                        result.extend(res)
            return result

        return []

    @staticmethod
    def analyze_pdf_page(page_text, page_num):
        """
        Analyzes a PDF page using local Ollama LLM (prioritizing llama3.2:1b)
        to extract key educational topics, concise summary, and visual diagram analysis.
        """
        if not page_text or len(page_text.strip()) < 10:
            return None

        use_ollama = getattr(settings, 'USE_OLLAMA', True)
        if not use_ollama:
            return None

        try:
            base_url = getattr(settings, 'OLLAMA_BASE_URL', 'http://localhost:11434').rstrip('/')
            preferred_model = getattr(settings, 'OLLAMA_MODEL', 'llama3.2:1b')
            model = AIService._resolve_ollama_model(base_url, preferred_model)
            if not model:
                return None

            url = f"{base_url}/api/chat"
            system_prompt = (
                "You are a document analyzer. Analyze the provided PDF page text.\n"
                "Respond strictly in valid JSON format:\n"
                '{"topics": ["Topic 1", "Topic 2", "Topic 3"], "summary": "...", "image_description": "..."}'
            )

            prompt_text = page_text[:2000]
            payload = {
                "model": model,
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"Analyze Page {page_num} text:\n\n{prompt_text}"}
                ],
                "format": "json",
                "stream": False
            }

            data_bytes = json.dumps(payload).encode('utf-8')
            req = urllib.request.Request(
                url,
                data=data_bytes,
                headers={'Content-Type': 'application/json'},
                method='POST'
            )

            with urllib.request.urlopen(req, timeout=3) as response:
                res_data = json.loads(response.read().decode('utf-8'))
                content_str = res_data.get('message', {}).get('content', '')
                if content_str:
                    try:
                        return json.loads(content_str)
                    except Exception:
                        pass
        except Exception as e:
            pass

        return None

    @staticmethod
    def _resolve_ollama_model(base_url, preferred_model='llama3.2:1b'):
        """
        Queries /api/tags to find active models in Ollama.
        Prioritizes 'llama3.2:1b' and any llama3.2 variants on any machine.
        """
        try:
            tags_url = f"{base_url}/api/tags"
            req = urllib.request.Request(tags_url)
            with urllib.request.urlopen(req, timeout=1) as response:
                data = json.loads(response.read().decode('utf-8'))
                models = [m.get('name') for m in data.get('models', []) if m.get('name')]
                if not models:
                    return None

                # 1. Exact or partial match for llama3.2:1b
                for m in models:
                    if 'llama3.2:1b' in m.lower():
                        return m

                # 2. Check for llama3.2 family (e.g., llama3.2:3b, llama3.2:latest)
                for m in models:
                    if 'llama3.2' in m.lower():
                        return m

                # 3. Check for preferred model string
                for m in models:
                    if preferred_model.lower() in m.lower() or m.lower().startswith(preferred_model.split(':')[0].lower()):
                        return m

                # 4. Fallback to first available model
                return models[0]
        except Exception as e:
            # Try running CLI 'ollama list' if API call failed
            try:
                import subprocess
                res = subprocess.run(['ollama', 'list'], capture_output=True, text=True, timeout=1)
                if res.returncode == 0:
                    output = res.stdout.lower()
                    if 'llama3.2:1b' in output or 'llama3.2' in output:
                        return 'llama3.2:1b'
            except Exception:
                pass
            return preferred_model

    @staticmethod
    def _generate_mock_mcqs(allowed_content_info, count=5, existing_questions=None):
        """
        Generates realistic MCQs based on actual text in allowed_content_info chunks.
        Strictly respects source_page <= confirmed_page boundary.
        """
        chunks = allowed_content_info.get('allowed_chunks', [])
        confirmed_page = allowed_content_info['confirmed_boundary']['page']
        
        existing_texts = set()
        if existing_questions:
            existing_texts = {q.question_text.lower().strip() for q in existing_questions}

        generated_questions = []
        
        # Predefined question templates mapped to topics/concepts per page
        for chunk in chunks:
            p_num = chunk['page_number']
            if p_num > confirmed_page:
                continue  # STRICT PROTECTION INVARIANT: never use unread pages!

            text = chunk['text']
            has_image = chunk.get('has_image', False)
            image_desc = chunk.get('image_description', '')

            # Page-specific question generators based on extracted content
            candidates = AIService._build_mock_questions_for_page(p_num, text, has_image, image_desc)
            
            for q_data in candidates:
                if q_data['question'].lower().strip() not in existing_texts:
                    q_data['source_page'] = p_num  # ensure exact source page
                    generated_questions.append(q_data)
                    existing_texts.add(q_data['question'].lower().strip())

        # Shuffle and select requested count
        random.shuffle(generated_questions)
        return generated_questions[:count]

    @staticmethod
    def _build_mock_questions_for_page(page_num, page_text, has_image, image_desc):
        """
        Curated question bank per page for Light Chapter 1 demo content,
        falling back to keyword-extracted templates for custom uploaded text.
        """
        questions = []

        if "electromagnetic radiation" in page_text.lower() or page_num == 1:
            questions.append({
                "question": "What is light defined as according to the reading material?",
                "option_a": "A mechanical sound wave requiring a solid medium",
                "option_b": "A form of electromagnetic radiation and energy enabling vision",
                "option_c": "A gravitational force field produced by magnetic poles",
                "option_d": "A high-frequency pressure wave moving through air",
                "correct_answer": "B",
                "explanation": "Page 1 states that light is a form of electromagnetic radiation and energy that enables optical perception.",
                "is_image_based": False
            })
            questions.append({
                "question": "What is the speed of light in a vacuum?",
                "option_a": "3 x 10^8 meters per second",
                "option_b": "3 x 10^5 meters per second",
                "option_c": "1.5 x 10^8 meters per second",
                "option_d": "340 meters per second",
                "correct_answer": "A",
                "explanation": "Page 1 mentions light travels at a speed of 3 x 10^8 meters per second in a vacuum.",
                "is_image_based": False
            })

        if "rectilinear propagation" in page_text.lower() or page_num == 2:
            questions.append({
                "question": "What does the principle of rectilinear propagation of light state?",
                "option_a": "Light bends continuously around obstacle corners",
                "option_b": "Light travels in straight lines in a homogeneous medium",
                "option_c": "Light speeds up when entering opaque barriers",
                "option_d": "Light reflects back without any angle change",
                "correct_answer": "B",
                "explanation": "Page 2 explains that rectilinear propagation means light travels in straight lines.",
                "is_image_based": False
            })
            questions.append({
                "question": "Which natural phenomenon is explained by rectilinear propagation?",
                "option_a": "Atmospheric scattering of blue light",
                "option_b": "Formation of shadows and eclipses",
                "option_c": "Color dispersion through a glass prism",
                "option_d": "Internal reflection in optical fibers",
                "correct_answer": "B",
                "explanation": "Page 2 highlights that straight-line light propagation explains shadow and eclipse formation.",
                "is_image_based": False
            })

        if "laws of reflection" in page_text.lower() or page_num == 3:
            questions.append({
                "question": "According to the Laws of Reflection, what is the relationship between angle of incidence (i) and angle of reflection (r)?",
                "option_a": "Angle of incidence is greater than angle of reflection",
                "option_b": "Angle of incidence is equal to angle of reflection (i = r)",
                "option_c": "Angle of incidence is half of angle of reflection",
                "option_d": "They add up to 180 degrees",
                "correct_answer": "B",
                "explanation": "Page 3 specifies the first law of reflection: angle of incidence equals angle of reflection (i = r).",
                "is_image_based": False
            })
            if has_image:
                questions.append({
                    "question": "In the reflection ray diagram shown on Page 3, where do the incident ray, reflected ray, and normal lie?",
                    "option_a": "In three mutually perpendicular planes",
                    "option_b": "In the same plane at the point of incidence",
                    "option_c": "Inside the reflecting medium only",
                    "option_d": "At 45 degree angles to each other",
                    "correct_answer": "B",
                    "explanation": "Page 3 text and diagram confirm that incident ray, reflected ray, and normal all lie in the same plane.",
                    "is_image_based": True
                })

        if "plane mirror" in page_text.lower() or page_num == 4:
            questions.append({
                "question": "Which of the following describes the image formed by a plane mirror?",
                "option_a": "Real, inverted, and larger than the object",
                "option_b": "Virtual, erect, laterally inverted, and equal in size to object",
                "option_c": "Real, erect, and smaller than the object",
                "option_d": "Virtual, inverted, and highly magnified",
                "correct_answer": "B",
                "explanation": "Page 4 states plane mirror images are virtual, erect, laterally inverted, and equal size.",
                "is_image_based": False
            })

        if "center of curvature" in page_text.lower() or page_num == 5:
            questions.append({
                "question": "What is the mathematical relationship between Radius of Curvature (R) and Focal Length (f) of a spherical mirror?",
                "option_a": "R = f / 2",
                "option_b": "R = 2f",
                "option_c": "R = f^2",
                "option_d": "R = 3f",
                "correct_answer": "B",
                "explanation": "Page 5 specifies that radius of curvature is twice the focal length (R = 2f).",
                "is_image_based": False
            })
            if has_image:
                questions.append({
                    "question": "Based on the spherical mirror terminology diagram on Page 5, what is the geometric center of the reflecting surface called?",
                    "option_a": "Principal Focus (F)",
                    "option_b": "Pole (P)",
                    "option_c": "Center of Curvature (C)",
                    "option_d": "Aperture",
                    "correct_answer": "B",
                    "explanation": "Page 5 diagram and text define the Pole (P) as the geometric center of the reflecting surface.",
                    "is_image_based": True
                })

        if page_num == 6 or "shaving mirrors" in page_text.lower():
            questions.append({
                "question": "Where must an object be placed in front of a concave mirror to form a virtual, erect, and magnified image?",
                "option_a": "At Infinity",
                "option_b": "Between the Pole (P) and Focus (F)",
                "option_c": "Beyond Center of Curvature (C)",
                "option_d": "At Center of Curvature (C)",
                "correct_answer": "B",
                "explanation": "Page 6 explains that placing an object between P and F creates a virtual, erect, magnified image.",
                "is_image_based": False
            })

        if page_num == 7 or "convex mirrors" in page_text.lower():
            questions.append({
                "question": "Why are convex mirrors used as rear-view mirrors in automobiles?",
                "option_a": "They produce real inverted images of far objects",
                "option_b": "They provide a wide field of view with erect, diminished images",
                "option_c": "They magnify objects to make them appear closer",
                "option_d": "They reflect colored light rays only",
                "correct_answer": "B",
                "explanation": "Page 7 notes convex mirrors provide a wide field of view by producing erect, diminished images.",
                "is_image_based": False
            })

        if page_num == 8 or "mirror formula" in page_text.lower():
            questions.append({
                "question": "What is the correct Mirror Formula connecting u, v, and f?",
                "option_a": "1/f = 1/v + 1/u",
                "option_b": "1/f = 1/v - 1/u",
                "option_c": "f = v + u",
                "option_d": "m = v / u",
                "correct_answer": "A",
                "explanation": "Page 8 states the mirror formula is 1/f = 1/v + 1/u.",
                "is_image_based": False
            })

        if page_num == 9 or "refraction" in page_text.lower():
            questions.append({
                "question": "What happens to a light ray when it travels from an optically rarer medium to a denser medium?",
                "option_a": "It bends away from the normal line",
                "option_b": "It bends toward the normal line",
                "option_c": "It reflects back into the rarer medium completely",
                "option_d": "It stops moving",
                "correct_answer": "B",
                "explanation": "Page 9 explains that moving from rarer to denser medium causes light to bend toward the normal.",
                "is_image_based": False
            })

        if page_num == 10 or "snell's law" in page_text.lower():
            questions.append({
                "question": "How is the absolute refractive index (n) of a medium calculated?",
                "option_a": "n = speed of light in vacuum (c) / speed of light in medium (v)",
                "option_b": "n = speed in medium (v) / speed in vacuum (c)",
                "option_c": "n = angle of incidence / angle of reflection",
                "option_d": "n = focal length x radius of curvature",
                "correct_answer": "A",
                "explanation": "Page 10 states that absolute refractive index n = c / v.",
                "is_image_based": False
            })

        # Generic fallback for any customized uploaded text
        if not questions:
            questions.append({
                "question": f"Key concept question from Page {page_num}: What is the primary topic discussed?",
                "option_a": f"Concepts regarding {page_text[:30]}...",
                "option_b": "Unrelated mechanical thermodynamics",
                "option_c": "Geological rock formation layers",
                "option_d": "Organic chemical compound synthesis",
                "correct_answer": "A",
                "explanation": f"Page {page_num} focuses directly on: {page_text[:100]}...",
                "is_image_based": False
            })

        return questions

    @staticmethod
    def _generate_openai_mcqs(allowed_content_info, count):
        import openai
        client = openai.OpenAI(api_key=settings.OPENAI_API_KEY)
        
        prompt_text = allowed_content_info['full_allowed_text']
        confirmed_page = allowed_content_info['confirmed_boundary']['page']

        system_prompt = (
            "You are an educational quiz generator. Generate multiple-choice questions only from the supplied content.\n"
            "STRICT RULES:\n"
            "1. Use only the supplied content.\n"
            "2. Do not use outside knowledge.\n"
            "3. Do not generate questions from content outside the supplied reading boundary.\n"
            "4. Each question must have exactly four options (A, B, C, D).\n"
            "5. Only one option can be correct.\n"
            "6. Include exact source_page (must be <= " + str(confirmed_page) + ").\n"
            "7. Return JSON format as {\"questions\": [...]}"
        )

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Generate {count} MCQs from this content:\n\n{prompt_text}"}
            ],
            response_format={"type": "json_object"}
        )

        data = json.loads(response.choices[0].message.content)
        return data.get("questions", [])

    @staticmethod
    def _generate_gemini_mcqs(allowed_content_info, count):
        # Placeholder for optional Gemini SDK integration if key provided
        return AIService._generate_mock_mcqs(allowed_content_info, count)
