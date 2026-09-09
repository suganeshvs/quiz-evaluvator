import os
import shutil

def prepare_netlify_landing():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    deploy_dir = os.path.join(base_dir, "deploy_landing")
    
    if os.path.exists(deploy_dir):
        shutil.rmtree(deploy_dir)
    
    os.makedirs(deploy_dir, exist_ok=True)
    os.makedirs(os.path.join(deploy_dir, "static", "css"), exist_ok=True)
    os.makedirs(os.path.join(deploy_dir, "static", "images"), exist_ok=True)

    # 1. Copy CSS & Images
    shutil.copy(os.path.join(base_dir, "static", "css", "classroom.css"), os.path.join(deploy_dir, "static", "css", "classroom.css"))
    if os.path.exists(os.path.join(base_dir, "static", "images", "logo.png")):
        shutil.copy(os.path.join(base_dir, "static", "images", "logo.png"), os.path.join(deploy_dir, "static", "images", "logo.png"))
    if os.path.exists(os.path.join(base_dir, "logo.ico")):
        shutil.copy(os.path.join(base_dir, "logo.ico"), os.path.join(deploy_dir, "logo.ico"))

    # 2. Copy Setup Files
    zip_path = os.path.join(base_dir, "AI_Quiz_Analyzer_Setup.zip")
    if os.path.exists(zip_path):
        shutil.copy(zip_path, os.path.join(deploy_dir, "AI_Quiz_Analyzer_Setup.zip"))
    
    bat_path = os.path.join(base_dir, "AI_Quiz_Analyzer_Installer.bat")
    if os.path.exists(bat_path):
        shutil.copy(bat_path, os.path.join(deploy_dir, "AI_Quiz_Analyzer_Installer.bat"))

    # 3. Create standalone static index.html for Netlify
    html_content = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AI Quiz Analyzer | Google Classroom Educational Application</title>
    <!-- Google Fonts: Inter -->
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">
    <!-- Bootstrap 5 CSS & Icons -->
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css" rel="stylesheet">
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.3/font/bootstrap-icons.min.css">
    <!-- Google Classroom Stylesheet -->
    <link rel="stylesheet" href="static/css/classroom.css">
    <link rel="icon" type="image/x-icon" href="logo.ico">
</head>
<body class="bg-light">

    <!-- Header -->
    <header class="gc-header">
        <div class="d-flex align-items-center gap-3">
            <a class="gc-brand" href="#">
                <div class="gc-chalkboard-logo">
                    <svg width="22" height="20" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                        <path d="M12 11C13.6569 11 15 9.65685 15 8C15 6.34315 13.6569 5 12 5C10.3431 5 9 6.34315 9 8C9 9.65685 10.3431 11 12 11Z" fill="white"/>
                        <path d="M6 18C6 15.3333 8.66667 14 12 14C15.3333 14 18 15.3333 18 18V19H6V18Z" fill="white"/>
                        <circle cx="5" cy="11" r="2" fill="white" opacity="0.8"/>
                        <circle cx="19" cy="11" r="2" fill="white" opacity="0.8"/>
                        <rect x="15" y="17.5" width="5" height="1" fill="white"/>
                    </svg>
                </div>
                <span class="gc-brand-title">AI Quiz Analyzer</span>
            </a>
        </div>
        <div>
            <a href="AI_Quiz_Analyzer_Installer.bat" class="btn-gc-primary download-link">
                <i class="bi bi-download"></i> Download One-Click Setup (.bat)
            </a>
        </div>
    </header>

    <main class="container py-4">
        <!-- Hero Section -->
        <div class="gc-card p-4 p-md-5 mb-4 text-center bg-white border">
            <div class="gc-chalkboard-logo mx-auto mb-3" style="width: 72px; height: 60px; border-width: 4px;">
                <svg width="40" height="34" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                    <path d="M12 11C13.6569 11 15 9.65685 15 8C15 6.34315 13.6569 5 12 5C10.3431 5 9 6.34315 9 8C9 9.65685 10.3431 11 12 11Z" fill="white"/>
                    <path d="M6 18C6 15.3333 8.66667 14 12 14C15.3333 14 18 15.3333 18 18V19H6V18Z" fill="white"/>
                    <circle cx="5" cy="11" r="2" fill="white" opacity="0.8"/>
                    <circle cx="19" cy="11" r="2" fill="white" opacity="0.8"/>
                    <rect x="15" y="17.5" width="5" height="1" fill="white"/>
                </svg>
            </div>

            <span class="badge bg-success-subtle text-success border border-success-subtle px-3 py-1.5 rounded mb-3 font-weight-medium" style="background: var(--gc-primary-light); color: var(--gc-primary-dark);">
                <i class="bi bi-mortarboard-fill me-1"></i> Official Google Classroom Inspired Desktop Application
            </span>

            <h1 class="display-5 fw-bold text-dark mb-3" style="letter-spacing: -0.5px;">
                AI Quiz Analyzer & Evaluator
            </h1>

            <p class="fs-5 text-secondary mx-auto mb-4" style="max-width: 720px; line-height: 1.6;">
                Learn smarter. Practice better. Upload course documents (PDF/PPT), track student reading boundaries down to exact pages & paragraphs, and generate targeted AI self-assessment quizes.
            </p>

            <div class="d-flex flex-wrap justify-content-center align-items-center gap-3">
                <a href="AI_Quiz_Analyzer_Installer.bat" class="btn-gc-primary font-weight-semibold fs-6 py-2 px-4 shadow-sm download-link" style="height: 48px;">
                    <i class="bi bi-download fs-5"></i> Download One-Click Application Setup (.bat)
                </a>
                <a href="AI_Quiz_Analyzer_Setup.zip" class="btn-gc-secondary font-weight-semibold fs-6 py-2 px-4" style="height: 48px;">
                    <i class="bi bi-file-earmark-zip fs-5"></i> Download Setup ZIP (.zip)
                </a>
            </div>
            <div class="form-text mt-3 text-secondary small">Automatically pops up Windows prompt: <em>"Do you want to install and run AI Quiz Analyzer now?"</em> [Yes] / [No], creates Desktop shortcut with green chalkboard logo, and launches application!</div>
        </div>

        <!-- Features Grid -->
        <div class="row g-4 mb-4">
            <div class="col-md-6 col-lg-3">
                <div class="gc-card p-4 h-100">
                    <div class="gc-resource-icon mb-3" style="background: var(--gc-primary-light); color: var(--gc-primary);">
                        <i class="bi bi-palette"></i>
                    </div>
                    <h5 class="fw-bold text-dark mb-2">Google Classroom UI</h5>
                    <p class="text-secondary small mb-0">Designed around Google Classroom green (#1E8E3E), Material Design components, student rosters, and color class cards.</p>
                </div>
            </div>

            <div class="col-md-6 col-lg-3">
                <div class="gc-card p-4 h-100">
                    <div class="gc-resource-icon mb-3" style="background: var(--gc-blue-light); color: var(--gc-blue);">
                        <i class="bi bi-book-half"></i>
                    </div>
                    <h5 class="fw-bold text-dark mb-2">PDF & PPT Reader</h5>
                    <p class="text-secondary small mb-0">Integrated Mozilla PDF.js document reader with automatic text extraction, page zoom, and real-time coverage tracking.</p>
                </div>
            </div>

            <div class="col-md-6 col-lg-3">
                <div class="gc-card p-4 h-100">
                    <div class="gc-resource-icon mb-3" style="background: var(--gc-yellow-light); color: var(--gc-yellow);">
                        <i class="bi bi-lightning-charge-fill"></i>
                    </div>
                    <h5 class="fw-bold text-dark mb-2">Targeted AI Quizzes</h5>
                    <p class="text-secondary small mb-0">Confirms student reading boundary before generating dynamic multiple-choice questions strictly from read pages.</p>
                </div>
            </div>

            <div class="col-md-6 col-lg-3">
                <div class="gc-card p-4 h-100">
                    <div class="gc-resource-icon mb-3" style="background: var(--gc-red-light); color: var(--gc-red);">
                        <i class="bi bi-bar-chart-line"></i>
                    </div>
                    <h5 class="fw-bold text-dark mb-2">Teacher Analytics</h5>
                    <p class="text-secondary small mb-0">Teacher dashboard featuring classroom rosters, student score analytics, and one-click quiz attempt clearing.</p>
                </div>
            </div>
        </div>

        <!-- Installation Guide -->
        <div class="gc-card p-4 p-md-5 mb-4">
            <div class="d-flex align-items-center gap-3 mb-4">
                <div class="gc-chalkboard-logo" style="width: 48px; height: 40px; border-width: 3px;">
                    <svg width="28" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                        <path d="M12 11C13.6569 11 15 9.65685 15 8C15 6.34315 13.6569 5 12 5C10.3431 5 9 6.34315 9 8C9 9.65685 10.3431 11 12 11Z" fill="white"/>
                        <path d="M6 18C6 15.3333 8.66667 14 12 14C15.3333 14 18 15.3333 18 18V19H6V18Z" fill="white"/>
                    </svg>
                </div>
                <div>
                    <h4 class="fw-bold text-dark mb-1">Local Windows Installation Guide</h4>
                    <p class="text-secondary small mb-0">Run AI Quiz Analyzer natively as a Windows application with desktop shortcut icon.</p>
                </div>
            </div>

            <div class="row g-4">
                <div class="col-md-4">
                    <div class="p-3 bg-light rounded border h-100">
                        <span class="badge bg-primary rounded-circle mb-2 fw-bold" style="width: 28px; height: 28px; display: inline-flex; align-items: center; justify-content: center;">1</span>
                        <h6 class="fw-bold text-dark mb-1">Download One-Click Setup</h6>
                        <p class="small text-secondary mb-0">Click the green download button to get <code>AI_Quiz_Analyzer_Installer.bat</code>.</p>
                    </div>
                </div>
                <div class="col-md-4">
                    <div class="p-3 bg-light rounded border h-100">
                        <span class="badge bg-primary rounded-circle mb-2 fw-bold" style="width: 28px; height: 28px; display: inline-flex; align-items: center; justify-content: center;">2</span>
                        <h6 class="fw-bold text-dark mb-1">Click [Yes] on Pop-up</h6>
                        <p class="small text-secondary mb-0">Open file and click <strong>[Yes]</strong> on the Windows popup dialog box: <em>"Do you want to install and run AI Quiz Analyzer now?"</em></p>
                    </div>
                </div>
                <div class="col-md-4">
                    <div class="p-3 bg-light rounded border h-100">
                        <span class="badge bg-primary rounded-circle mb-2 fw-bold" style="width: 28px; height: 28px; display: inline-flex; align-items: center; justify-content: center;">3</span>
                        <h6 class="fw-bold text-dark mb-1">Application Launches!</h6>
                        <p class="small text-secondary mb-0">The installer extracts files, configures local AI, creates an <strong>AI Quiz Analyzer</strong> desktop shortcut with the logo icon, and opens the app!</p>
                    </div>
                </div>
            </div>

            <div class="text-center mt-4 border-top pt-4">
                <a href="AI_Quiz_Analyzer_Installer.bat" class="btn-gc-primary px-4 py-2 font-weight-medium download-link">
                    <i class="bi bi-download me-1"></i> Download AI Quiz Analyzer Setup Installer
                </a>
            </div>
        </div>
    </main>

    <footer class="text-center py-4 bg-white border-top text-secondary small">
        &copy; 2026 AI Quiz Analyzer | Google Classroom Inspired Application
    </footer>
</body>
</html>
"""

    with open(os.path.join(deploy_dir, "index.html"), "w", encoding="utf-8") as f:
        f.write(html_content)

    print(f"Netlify landing folder created successfully at:\n  {deploy_dir}")

if __name__ == "__main__":
    prepare_netlify_landing()
