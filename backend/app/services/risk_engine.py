import re
from datetime import datetime, timezone
from typing import Dict, List, Any
from urllib.parse import urlparse

# Technology initial release years
TECH_TIMELINE = {
    "react": 2013,
    "flutter": 2017,
    "fastapi": 2018,
    "kubernetes": 2014,
    "next.js": 2016,
    "nextjs": 2016,
    "rust": 2015,
    "swift": 2014,
    "vue": 2014,
    "vue.js": 2014,
    "svelte": 2016,
    "tailwind": 2017,
    "docker": 2013,
    "golang": 2012,
}

PAYMENT_PATTERNS = [
    (r"pay\s+(?:a\s+)?(?:processing|application|registration|training|equipment|security)\s+fee", "Upfront payment or processing fee required", "critical"),
    (r"(?:security\s+deposit|processing\s+fee|application\s+fee|registration\s+fee)", "Upfront recruitment fee or security deposit requested", "critical"),
    (r"(?:send|wire|deposit|transfer|pay)\s+\$?\d+.*?(?:before|to\s+secure|for\s+materials|fee|deposit|wire)", "Mandatory upfront financial deposit requested", "critical"),
    (r"(?:gift\s*card|crypto|bitcoin|usdt|western\s*union|moneygram)", "Payment requested via non-standard or irreversible methods", "critical"),
    (r"(?:purchase|buy)\s+your\s+own\s+equipment\s+from\s+our\s+vendor", "Mandated purchase from specific third-party vendor", "high"),
]

COMMUNICATION_PATTERNS = [
    (r"(?:contact|message|interview|reach\s+out)\s+(?:only|strictly|via)\s+(?:telegram|whatsapp|signal)", "Exclusively relies on messaging apps for hiring", "high"),
    (r"telegram\s*:\s*@[\w_]+", "Recruiter provides Telegram handle as sole communication", "medium"),
    (r"whatsapp\s*(?:us|me)?\s*at\s*[\+\d\s\(\)-]+", "Direct recruitment via WhatsApp without corporate channel", "medium"),
    (r"no\s+interview\s+(?:needed|required)|immediate\s+hire\s+guaranteed", "Guaranteed hire without interview or qualification review", "critical"),
]

UNREALISTIC_COMPENSATION_PATTERNS = [
    (r"(?:earn|\$)\s*(?:1[0-9]{2}|[2-9][0-9]{2})\s*/\s*hr.*(?:entry\s*level|data\s*entry|no\s*experience)", "Implausibly high wage for entry-level tasks", "high"),
    (r"earn\s+\$?\d{4,}\s+per\s+week\s+working\s+\d+\s+hours", "Outsized compensation promised for minimal work", "high"),
]

FREE_EMAIL_DOMAINS = ["gmail.com", "yahoo.com", "hotmail.com", "outlook.com", "proton.me", "protonmail.com", "aol.com"]

def analyze_job_listing(
    title: str,
    employer: str,
    description: str,
    employer_domain: str = "",
    contact_email: str = "",
    contact_phone: str = "",
    contact_messaging: str = "",
    salary_text: str = "",
    application_url: str = ""
) -> Dict[str, Any]:
    current_year = datetime.now(timezone.utc).year
    text_corpus = f"{title}\n{employer}\n{description}\n{contact_messaging}\n{salary_text}"
    
    signals: List[Dict[str, Any]] = []
    positive_signals: List[Dict[str, Any]] = []
    unknown_signals: List[Dict[str, Any]] = []
    
    # 1. Evaluate Payment Signals
    for pattern, rule_title, severity in PAYMENT_PATTERNS:
        match = re.search(pattern, text_corpus, re.IGNORECASE)
        if match:
            signals.append({
                "signal_category": "payment_request",
                "severity": severity,
                "title": rule_title,
                "description": "Legitimate employers never demand application, onboarding, or training fees before employment.",
                "evidence_excerpt": match.group(0),
                "certainty": "confirmed",
                "recommended_action": "Do NOT send any funds, gift cards, or payments under any circumstances."
            })

    # 2. Evaluate Communication Channels
    for pattern, rule_title, severity in COMMUNICATION_PATTERNS:
        match = re.search(pattern, text_corpus, re.IGNORECASE)
        if match:
            signals.append({
                "signal_category": "communication_pattern",
                "severity": severity,
                "title": rule_title,
                "description": "Recruiters demanding communication exclusively via informal messaging apps often evade institutional oversight.",
                "evidence_excerpt": match.group(0),
                "certainty": "confirmed",
                "recommended_action": "Request formal email correspondence from an official enterprise domain before continuing."
            })
            
    if contact_messaging and ("telegram" in contact_messaging.lower() or "whatsapp" in contact_messaging.lower()):
        if not any(s["title"].startswith("Exclusively relies") for s in signals):
            signals.append({
                "signal_category": "communication_pattern",
                "severity": "medium",
                "title": "Recruitment directed to messaging platform",
                "description": "Contact info lists direct messaging channel as primary contact.",
                "evidence_excerpt": contact_messaging,
                "certainty": "confirmed",
                "recommended_action": "Verify recruiter identity on LinkedIn and request verification email."
            })

    # 3. Domain & Employer Consistency
    if contact_email:
        email_domain = contact_email.split("@")[-1].lower() if "@" in contact_email else ""
        if email_domain in FREE_EMAIL_DOMAINS and len(employer) > 2:
            # If the employer is not a tiny family shop
            signals.append({
                "signal_category": "domain_mismatch",
                "severity": "high",
                "title": f"Public email domain (@{email_domain}) used for corporate entity",
                "description": f"The listing claims to represent '{employer}', but uses a free public email provider (@{email_domain}) rather than an authenticated organization domain.",
                "evidence_excerpt": contact_email,
                "certainty": "confirmed",
                "recommended_action": "Check the employer's official website career portal to verify the posting."
            })
            
    if employer_domain:
        clean_domain = employer_domain.lower().replace("http://", "").replace("https://", "").split("/")[0]
        # Check suspicious TLDs often used in impostor sites
        if re.search(r'\.(xyz|top|work|click|site|live|buzz|link)$', clean_domain):
            signals.append({
                "signal_category": "domain_mismatch",
                "severity": "medium",
                "title": f"Uncommon high-risk top-level domain ({clean_domain})",
                "description": "The employer domain uses a high-churn, inexpensive TLD frequently associated with temporary spoof sites.",
                "evidence_excerpt": employer_domain,
                "certainty": "potential",
                "recommended_action": "Perform a WHOIS query and verify organization registry details."
            })
            
    if application_url:
        parsed_app = urlparse(application_url)
        app_domain = parsed_app.netloc.lower()
        if employer_domain and app_domain:
            clean_emp = employer_domain.lower().replace("www.", "").split("/")[0]
            clean_app = app_domain.replace("www.", "")
            if clean_emp not in clean_app and clean_app not in clean_emp and not re.search(r'(greenhouse|lever|workday|ashbyhq|smartrecruiters|bamboohr)', clean_app):
                signals.append({
                    "signal_category": "domain_mismatch",
                    "severity": "medium",
                    "title": "Application URL points to different domain than employer",
                    "description": f"The application link domain '{clean_app}' does not match stated employer '{clean_emp}' or standard ATS platforms.",
                    "evidence_excerpt": application_url,
                    "certainty": "potential",
                    "recommended_action": "Ensure the application form does not request sensitive financial credentials or passwords."
                })

    # 4. Implausible Technology Experience Requirements
    for tech, release_year in TECH_TIMELINE.items():
        max_possible_years = current_year - release_year
        exp_pattern = rf'(?:(\d{{1,2}})\+?\s*(?:years?|yrs?)(?:\s+of)?(?:\s+experience)?\s+(?:in|with)?\s*{re.escape(tech)}|{re.escape(tech)}\s+(?:for\s+)?(\d{{1,2}})\+?\s*(?:years?|yrs?))'
        exp_match = re.search(exp_pattern, text_corpus, re.IGNORECASE)
        if exp_match:
            claimed_years = int(exp_match.group(1) or exp_match.group(2))
            if claimed_years > max_possible_years:
                signals.append({
                    "signal_category": "implausible_experience",
                    "severity": "high",
                    "title": f"Anachronistic requirement: {claimed_years} years in {tech.capitalize()}",
                    "description": f"{tech.capitalize()} was released in {release_year} (maximum possible elapsed time is ~{max_possible_years} years). Demanding {claimed_years} years suggests a fabricated or uncalibrated listing.",
                    "evidence_excerpt": exp_match.group(0),
                    "certainty": "confirmed",
                    "recommended_action": "Treat this posting with caution as requirements show signs of boilerplate generation or lack of technical vetting."
                })

    # 5. Unrealistic Compensation & Urgency
    for pattern, rule_title, severity in UNREALISTIC_COMPENSATION_PATTERNS:
        match = re.search(pattern, text_corpus, re.IGNORECASE)
        if match:
            signals.append({
                "signal_category": "listing_content",
                "severity": severity,
                "title": rule_title,
                "description": "Exaggerated promises of high compensation for zero-skill entry-level tasks are hallmark indicators of recruitment scams.",
                "evidence_excerpt": match.group(0),
                "certainty": "confirmed",
                "recommended_action": "Compare against National Career Service and bureau of labor statistics wage distributions."
            })

    # 6. Check for Positive Signals
    if employer_domain and not re.search(r'\.(xyz|top|click|site)$', employer_domain.lower()):
        positive_signals.append({
            "title": "Established Organization Domain",
            "evidence": employer_domain,
            "description": "Employer provides a professional institutional web domain."
        })
    if contact_email and not any(contact_email.lower().endswith(f) for f in FREE_EMAIL_DOMAINS):
        positive_signals.append({
            "title": "Corporate Email Address",
            "evidence": contact_email,
            "description": "Contact address corresponds to an authenticated corporate host."
        })
    if re.search(r'(interview|technical\s+round|code\s+review|portfolio\s+presentation)', description, re.IGNORECASE):
        positive_signals.append({
            "title": "Structured Evaluation Process",
            "evidence": "Standard recruitment stages described",
            "description": "Outlines legitimate technical and behavioral hiring stages."
        })
    if len(description) > 300 and re.search(r'(responsibilities|requirements|qualifications)', description, re.IGNORECASE):
        positive_signals.append({
            "title": "Detailed Job Scope",
            "evidence": "Clearly enumerated duties and qualifications",
            "description": "The posting articulates clear roles, expectations, and prerequisites."
        })

    # 7. Check for Unknown / Inconclusive Information
    if not contact_email and not contact_phone and not contact_messaging:
        unknown_signals.append("No direct recruiter contact information supplied; reliant entirely on third-party portal.")
    if not employer_domain:
        unknown_signals.append("Employer website domain is omitted. Independent business registration could not be verified automatically.")
    if not salary_text and not re.search(r'\$|\d+,\d{3}', description):
        unknown_signals.append("Salary and compensation range are undisclosed.")

    # 8. Score Calculation & Risk Tiers
    # Base calculation with weights
    weights = {
        "critical": 35.0,
        "high": 20.0,
        "medium": 10.0,
        "low": 5.0
    }
    raw_risk = sum(weights.get(s["severity"], 10.0) for s in signals)
    
    # Mitigation from positive signals (up to -20)
    mitigation = min(20.0, len(positive_signals) * 5.0)
    final_score = max(5.0, min(95.0, raw_risk - mitigation if raw_risk > 0 else 8.0))
    if any(s["severity"] == "critical" for s in signals):
        final_score = max(final_score, 65.0)
    
    if final_score >= 60.0 or any(s["severity"] == "critical" for s in signals):
        risk_tier = "Elevated risk indicators"
        summary = "Multiple high-severity risk indicators were identified in this listing. Exercise caution and do not provide funds or sensitive credentials."
    elif final_score >= 30.0 or len(signals) >= 1:
        risk_tier = "Needs verification"
        summary = "The listing contains signals or ambiguities that warrant independent verification before you submit an application."
    else:
        risk_tier = "Lower observed risk"
        summary = "No anomalous risk indicators were observed. Standard professional recruitment patterns and corporate indicators detected."

    return {
        "risk_score": round(final_score, 1),
        "risk_tier": risk_tier,
        "summary": summary,
        "signals": signals,
        "positive_signals": positive_signals,
        "unknown_signals": unknown_signals,
        "method": "Multi-Signal Rule Baseline with Calibrated Weights"
    }
