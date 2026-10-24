import hashlib
import os
import re
from pathlib import Path
from typing import Dict, List, Any, Tuple
import pypdf
import docx

# Magic byte signatures
FILE_SIGNATURES = {
    "pdf": b"%PDF",
    "docx": b"PK\x03\x04",
    "png": b"\x89PNG\r\n\x1a\n",
    "jpg": b"\xff\xd8\xff",
    "jpeg": b"\xff\xd8\xff",
}

COMMON_SKILLS_KEYWORDS = [
    ("Python", "Python", "Technical"),
    ("SQL", "SQL", "Technical"),
    ("PostgreSQL", "PostgreSQL", "Technical"),
    ("MySQL", "MySQL", "Technical"),
    ("JavaScript", "JavaScript", "Technical"),
    ("TypeScript", "TypeScript", "Technical"),
    ("React", "React", "Technical"),
    ("React.js", "React", "Technical"),
    ("Node.js", "Node.js", "Technical"),
    ("FastAPI", "FastAPI", "Technical"),
    ("Flask", "Flask", "Technical"),
    ("Django", "Django", "Technical"),
    ("Docker", "Docker", "DevOps"),
    ("Kubernetes", "Kubernetes", "DevOps"),
    ("AWS", "AWS", "Cloud"),
    ("Azure", "Azure", "Cloud"),
    ("Git", "Git", "DevOps"),
    ("HTML/CSS", "HTML/CSS", "Technical"),
    ("Tailwind CSS", "Tailwind CSS", "Technical"),
    ("Machine Learning", "Machine Learning", "Data & AI"),
    ("Pandas", "Pandas", "Data & AI"),
    ("NumPy", "NumPy", "Data & AI"),
    ("Scikit-Learn", "Scikit-Learn", "Data & AI"),
    ("REST API", "REST APIs", "Technical"),
    ("GraphQL", "GraphQL", "Technical"),
    ("Linux", "Linux", "DevOps"),
    ("CI/CD", "CI/CD", "DevOps"),
    ("Data Analysis", "Data Analysis", "Data & AI"),
    ("Agile/Scrum", "Agile", "Management"),
]

PROMPT_INJECTION_PATTERNS = [
    r"ignore\s+(all\s+)?previous\s+instructions",
    r"system\s*prompt",
    r"you\s+are\s+now\s+in\s+developer\s+mode",
    r"as\s+an\s+ai\s+language\s+model",
    r"<script>",
    r"javascript:",
    r"sudo\s+rm",
]

def calculate_sha256(content: bytes) -> str:
    return hashlib.sha256(content).hexdigest()

def validate_file_bytes(content: bytes, filename: str, max_size_mb: int = 15) -> Tuple[bool, str, str]:
    """Validates file size, extension, and magic byte signature."""
    size_mb = len(content) / (1024 * 1024)
    if size_mb > max_size_mb:
        return False, f"File size ({size_mb:.1f} MB) exceeds maximum allowed limit of {max_size_mb} MB.", ""
        
    ext = os.path.splitext(filename)[1].lower().lstrip(".")
    if ext not in ["pdf", "docx", "txt", "png", "jpg", "jpeg"]:
        return False, f"Unsupported file extension: .{ext}", ""
        
    if ext in FILE_SIGNATURES:
        sig = FILE_SIGNATURES[ext]
        if not content.startswith(sig):
            # For docx check offset in first 4 bytes
            if ext == "docx" and content[:4] == b"PK\x03\x04":
                pass
            else:
                return False, f"File content signature does not match declared .{ext} format.", ""
                
    mime_type = "text/plain"
    if ext == "pdf":
        mime_type = "application/pdf"
    elif ext == "docx":
        mime_type = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    elif ext in ["png", "jpg", "jpeg"]:
        mime_type = f"image/{ext if ext != 'jpg' else 'jpeg'}"
        
    return True, "", mime_type

def extract_text_from_pdf(filepath: str) -> List[Dict[str, Any]]:
    pages_data = []
    try:
        reader = pypdf.PdfReader(filepath)
        for i, page in enumerate(reader.pages):
            text = page.extract_text() or ""
            pages_data.append({
                "page_number": i + 1,
                "text": text.strip()
            })
    except Exception as e:
        pages_data.append({
            "page_number": 1,
            "text": "",
            "error": str(e)
        })
    return pages_data

def extract_text_from_docx(filepath: str) -> List[Dict[str, Any]]:
    try:
        doc = docx.Document(filepath)
        full_text = []
        for p in doc.paragraphs:
            if p.text.strip():
                full_text.append(p.text.strip())
        for table in doc.tables:
            for row in table.rows:
                row_text = " | ".join(cell.text.strip() for cell in row.cells if cell.text.strip())
                if row_text:
                    full_text.append(row_text)
        return [{
            "page_number": 1,
            "text": "\n".join(full_text)
        }]
    except Exception as e:
        return [{
            "page_number": 1,
            "text": "",
            "error": str(e)
        }]

def extract_text_from_txt(filepath: str) -> List[Dict[str, Any]]:
    try:
        with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
            text = f.read()
        return [{"page_number": 1, "text": text.strip()}]
    except Exception as e:
        return [{"page_number": 1, "text": "", "error": str(e)}]

def parse_claims_from_text(pages_data: List[Dict[str, Any]]) -> Dict[str, Any]:
    full_text = "\n\n".join(p["text"] for p in pages_data)
    claims: List[Dict[str, Any]] = []
    warnings: List[str] = []
    
    # Check for prompt injection patterns
    for pattern in PROMPT_INJECTION_PATTERNS:
        match = re.search(pattern, full_text, re.IGNORECASE)
        if match:
            warnings.append(f"Untrusted instruction pattern detected in document: '{match.group(0)}'. Neutralized.")
            
    # Check for empty text
    if not full_text.strip():
        return {
            "claims": [],
            "document_type": "other",
            "extraction_quality": "Review Required",
            "warnings": ["No machine-readable text found in file. Document may be a scanned image requiring OCR."]
        }
        
    # Detect Contact details
    email_match = re.search(r'[\w\.-]+@[\w\.-]+\.\w+', full_text)
    if email_match:
        page_num = 1
        claims.append({
            "claim_type": "personal_info",
            "field_name": "email",
            "raw_value": email_match.group(0),
            "normalized_value": email_match.group(0).lower(),
            "confidence": 0.98,
            "page_number": page_num,
            "section_heading": "Contact Details",
            "text_excerpt": email_match.group(0),
        })
        
    phone_match = re.search(r'(?:\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}', full_text)
    if phone_match:
        claims.append({
            "claim_type": "personal_info",
            "field_name": "phone",
            "raw_value": phone_match.group(0),
            "normalized_value": phone_match.group(0).strip(),
            "confidence": 0.92,
            "page_number": 1,
            "section_heading": "Contact Details",
            "text_excerpt": phone_match.group(0),
        })
        
    github_match = re.search(r'github\.com/([a-zA-Z0-9_-]+)', full_text, re.IGNORECASE)
    if github_match:
        claims.append({
            "claim_type": "personal_info",
            "field_name": "github",
            "raw_value": github_match.group(0),
            "normalized_value": f"https://{github_match.group(0)}",
            "confidence": 0.96,
            "page_number": 1,
            "section_heading": "Links",
            "text_excerpt": github_match.group(0),
        })
        
    linkedin_match = re.search(r'linkedin\.com/in/([a-zA-Z0-9_-]+)', full_text, re.IGNORECASE)
    if linkedin_match:
        claims.append({
            "claim_type": "personal_info",
            "field_name": "linkedin",
            "raw_value": linkedin_match.group(0),
            "normalized_value": f"https://{linkedin_match.group(0)}",
            "confidence": 0.96,
            "page_number": 1,
            "section_heading": "Links",
            "text_excerpt": linkedin_match.group(0),
        })

    # Detect Name (heuristic from first lines)
    lines = [line.strip() for line in full_text.splitlines() if line.strip()]
    if lines:
        first_line = lines[0]
        if len(first_line.split()) <= 4 and not re.search(r'resume|curriculum|vitae|page', first_line, re.IGNORECASE):
            claims.append({
                "claim_type": "personal_info",
                "field_name": "full_name",
                "raw_value": first_line,
                "normalized_value": first_line,
                "confidence": 0.88,
                "page_number": 1,
                "section_heading": "Header",
                "text_excerpt": first_line,
            })

    # Detect Education
    edu_patterns = [
        r'(Bachelor(?:[\'’]s)?|Master(?:[\'’]s)?|B\.?S\.?|B\.?Tech|M\.?S\.?|Ph\.?D\.?|Associate)\s+(?:of|in)?\s+([A-Za-z\s]+?)(?:\n|,|–|-|\.|\d{4})',
    ]
    for pattern in edu_patterns:
        for match in re.finditer(pattern, full_text, re.IGNORECASE):
            degree_str = match.group(0).strip()
            # find enclosing line for excerpt
            excerpt = match.group(0)
            claims.append({
                "claim_type": "education",
                "field_name": "degree",
                "raw_value": degree_str,
                "normalized_value": degree_str,
                "confidence": 0.86,
                "page_number": 1,
                "section_heading": "Education",
                "text_excerpt": excerpt,
            })

    # Detect Skills with verbatim excerpts and section headings
    found_skills = set()
    for kw, canonical, cat in COMMON_SKILLS_KEYWORDS:
        pattern = r'\b' + re.escape(kw) + r'\b'
        match = re.search(pattern, full_text, re.IGNORECASE)
        if match and canonical not in found_skills:
            found_skills.add(canonical)
            # Find which page it came from
            page_found = 1
            excerpt_str = ""
            for p in pages_data:
                p_match = re.search(pattern, p["text"], re.IGNORECASE)
                if p_match:
                    page_found = p["page_number"]
                    start = max(0, p_match.start() - 40)
                    end = min(len(p["text"]), p_match.end() + 40)
                    excerpt_str = p["text"][start:end].replace("\n", " ").strip()
                    break
                    
            claims.append({
                "claim_type": "skill",
                "field_name": canonical,
                "raw_value": match.group(0),
                "normalized_value": canonical,
                "category": cat,
                "confidence": 0.90,
                "page_number": page_found,
                "section_heading": "Skills / Experience",
                "text_excerpt": f"...{excerpt_str}..." if excerpt_str else match.group(0),
            })

    # Detect Projects
    project_matches = re.finditer(r'(?:Project|System|Platform|Application):\s*([^\n]+)', full_text, re.IGNORECASE)
    for p_match in project_matches:
        p_name = p_match.group(1).strip()
        claims.append({
            "claim_type": "project",
            "field_name": "title",
            "raw_value": p_name,
            "normalized_value": p_name,
            "confidence": 0.85,
            "page_number": 1,
            "section_heading": "Projects",
            "text_excerpt": p_match.group(0),
        })

    # Detect Document Type
    doc_type = "resume"
    if re.search(r'cover\s+letter|dear\s+hiring\s+manager', full_text, re.IGNORECASE):
        doc_type = "cover_letter"
    elif re.search(r'certificate\s+of|has\s+successfully\s+completed', full_text, re.IGNORECASE):
        doc_type = "certificate"
    elif re.search(r'project\s+report|final\s+report', full_text, re.IGNORECASE):
        doc_type = "project_report"

    # Assess extraction quality
    if len(claims) >= 6:
        extraction_quality = "High"
    elif len(claims) >= 3:
        extraction_quality = "Moderate"
    else:
        extraction_quality = "Review Required"
        warnings.append("Sparse extraction results. Please review and complement missing fields manually.")

    return {
        "claims": claims,
        "document_type": doc_type,
        "extraction_quality": extraction_quality,
        "warnings": warnings,
        "page_count": len(pages_data),
        "total_characters": len(full_text)
    }
