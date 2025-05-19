import subprocess
import os
import re
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse
from .models import CodeUpload, CodeAnalysis
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from django.contrib.auth.decorators import login_required
from django.core.mail import EmailMessage
from io import BytesIO
from django.shortcuts import render
from django.http import HttpResponse
import subprocess
import tempfile
import os
from django.http import JsonResponse

# Function to highlight output text based on warning/note
def highlight_output(output):
    output = re.sub(r'warning: (.*)', r'<span style="color:orange;"><b>⚠️ Warning:</b> \1</span>', output)
    output = re.sub(r'note: (.*)', r'<span style="color:blue;">ℹ️ Note: \1</span>', output)
    return output

# Function to detect severity based on the output
def detect_severity(output):
    if "Dereference of null pointer" in output:
        return "Critical"
    elif "Memory leak" in output:
        return "Critical"
    elif "Uninitialized variable" in output:
        return "Warning"
    else:
        return "Info"

# Function to suggest fixes based on the output
def suggest_fix(output):
    if "Dereference of null pointer" in output:
        return "Check if the pointer is NULL before dereferencing."
    elif "Memory leak" in output:
        return "Ensure all allocated memory is freed after usage."
    elif "Uninitialized variable" in output:
        return "Initialize variables before using them."
    else:
        return "No automatic suggestion available."

# Function to calculate the code quality score based on the output
def calculate_score(output):
    warning_count = output.count('warning:')
    note_count = output.count('note:')
    score = 100 - (warning_count * 10) - (note_count * 2)
    return max(score, 0)

# View to handle code upload and analysis
@login_required
def upload_code(request):
    if request.method == 'POST':
        if 'file' not in request.FILES:
            return render(request, 'codeanalyzer/upload.html', {'error': 'No file uploaded. Please choose a file.'})

        uploaded_file = request.FILES['file']
        code_file = CodeUpload(file=uploaded_file)
        code_file.save()

        file_path = code_file.file.path

        clang_tidy_path = 'C:\\Program Files\\LLVM\\bin\\clang-tidy.exe'

        process = subprocess.run(
            [clang_tidy_path, file_path, '--', '-std=c11'],
            capture_output=True,
            text=True
        )
        output = process.stdout + process.stderr

        highlighted_output = highlight_output(output)
        severity = detect_severity(output)
        suggestion = suggest_fix(output)
        score = calculate_score(output)

        # Save analysis results to the database (attach the user here!)
        CodeAnalysis.objects.create(
            user=request.user,  # <--- Added user assignment
            filename=uploaded_file.name,
            analysis_output=output,
            severity=severity,
            suggestion=suggestion,
            code_quality_score=score
        )

        return render(request, 'codeanalyzer/result.html', {
            'output': highlighted_output,
            'severity': severity,
            'suggestion': suggestion,
            'score': score,
            'filename': uploaded_file.name,
        })

    return render(request, 'codeanalyzer/upload.html')

# View to display the history of previous code analyses
@login_required
def analysis_history(request):
    analyses = CodeAnalysis.objects.filter(user=request.user).order_by('-analyzed_at')  # <--- Filter only by current user

    labels = [f'"{analysis.filename}"' for analysis in analyses]
    scores = [analysis.code_quality_score for analysis in analyses]

    bug_types = {"Critical": 0, "Warning": 0, "Info": 0}
    for analysis in analyses:
        bug_types[analysis.severity] = bug_types.get(analysis.severity, 0) + 1

    return render(request, 'codeanalyzer/history.html', {
        'analyses': analyses,
        'labels': labels,
        'scores': scores,
        'bug_types': bug_types
    })

# View to export the code analysis as a PDF
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, FrameBreak
from reportlab.platypus.flowables import PageBreak
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_CENTER
from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle

@login_required
def export_pdf(request, analysis_id):
    analysis = get_object_or_404(CodeAnalysis, id=analysis_id, user=request.user)

    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter,
                            rightMargin=72, leftMargin=72,
                            topMargin=72, bottomMargin=72)

    styles = getSampleStyleSheet()
    style_normal = styles['Normal']
    style_heading = styles['Heading1']
    style_bold = ParagraphStyle(name='Bold', parent=style_normal, fontName='Helvetica-Bold')

    # Custom centered title style
    style_title = ParagraphStyle(
        'title',
        parent=styles['Heading1'],
        fontSize=18,
        alignment=TA_CENTER,
        spaceAfter=20
    )

    elements = []

    # Title
    elements.append(Paragraph("Code Analysis Report", style_title))

    # Basic info
    elements.append(Paragraph(f"<b>Filename:</b> {analysis.filename}", style_normal))
    elements.append(Paragraph(f"<b>Severity:</b> {analysis.severity}", style_normal))
    elements.append(Paragraph(f"<b>Score:</b> {analysis.code_quality_score} / 100", style_normal))
    elements.append(Paragraph(f"<b>Suggestion:</b> {analysis.suggestion}", style_normal))
    elements.append(Spacer(1, 12))

    # Analysis Output header
    elements.append(Paragraph("<b>Detailed Analysis Output:</b>", style_bold))
    elements.append(Spacer(1, 6))

    # Prepare the output text with simple HTML escaping & line breaks
    output_text = analysis.analysis_output.replace('\n', '<br/>')
    # Use a monospace font style for code output
    style_code = ParagraphStyle(
        'code',
        parent=style_normal,
        fontName='Courier',
        fontSize=9,
        leading=12,
        backColor=colors.whitesmoke,
        borderPadding=5,
        borderColor=colors.lightgrey,
        borderWidth=0.5,
        borderRadius=2,
        spaceBefore=6,
        spaceAfter=6
    )
    elements.append(Paragraph(output_text, style_code))

    doc.build(elements)

    pdf = buffer.getvalue()
    buffer.close()

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="report_{analysis.filename}.pdf"'
    response.write(pdf)

    return response

# 🌟 New View: Show IDE Page
def ide_view(request):
    return render(request, 'ide.html')


# Full path to clang-tidy executable (update this to the correct path on your machine)
clang_tidy_path = 'C:\\Program Files\\LLVM\\bin\\clang-tidy.exe'

# 🌟 New View: Handle IDE Code Analysis
import subprocess
import tempfile
import os
from django.http import JsonResponse

@login_required
def analyze_code_online(request):
    if request.method == 'POST':
        code = request.POST.get('code')
        if not code.strip():
            return JsonResponse({'error': 'No code submitted.'}, status=400)

        # Save the code to a temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix='.c') as temp_file:
            temp_file.write(code.encode('utf-8'))
            temp_file_path = temp_file.name

        clang_tidy_path = 'C:\\Program Files\\LLVM\\bin\\clang-tidy.exe'

        # Run clang-tidy on the temporary file
        process = subprocess.run(
            [clang_tidy_path, temp_file_path, '--', '-std=c11'],
            capture_output=True,
            text=True
        )

        output = process.stdout + process.stderr

        # Process the output and generate the necessary analysis details
        highlighted_output = highlight_output(output)
        severity = detect_severity(output)
        suggestion = suggest_fix(output)
        score = calculate_score(output)

        # Return the analysis results as JSON
        result = {
            'filename': os.path.basename(temp_file_path),
            'severity': severity,
            'score': score,
            'suggestion': suggestion,
            'output': highlighted_output
        }

        # Clean up the temporary file after analysis
        os.remove(temp_file_path)

        return JsonResponse(result)

    return JsonResponse({'error': 'Invalid request method.'}, status=400)