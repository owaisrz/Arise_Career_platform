from typing import List, Dict, Any
from backend.app.services.risk_engine import analyze_job_listing

# Labeled evaluation benchmark cases (42 cases)
# true_label: "suspicious" (elevated/needs verification) vs "legitimate" (lower observed risk)
EVALUATION_DATASET: List[Dict[str, Any]] = [
    # 1-15: Critical & High Suspicious Scenarios
    {
        "id": "SCAM-01",
        "title": "Data Entry Remote Assistant",
        "employer": "Apex Global Solutions",
        "description": "Earn $180/hr data entry work from home. Please pay a processing fee of $75 to receive your starter security kit and laptop software.",
        "employer_domain": "apex-jobportal.xyz",
        "contact_email": "apexjobs@gmail.com",
        "salary_text": "$180/hr",
        "true_label": "suspicious",
        "category": "payment_request"
    },
    {
        "id": "SCAM-02",
        "title": "Immediate Virtual Assistant",
        "employer": "Swift Logistics Express",
        "description": "Immediate hire guaranteed! No interview needed. Contact strictly via Telegram @swift_hiring_manager to finalize placement.",
        "employer_domain": "swiftlogistics.top",
        "contact_email": "swiftrecruiter@outlook.com",
        "contact_messaging": "Telegram: @swift_hiring_manager",
        "salary_text": "$4,000/week",
        "true_label": "suspicious",
        "category": "communication_pattern"
    },
    {
        "id": "SCAM-03",
        "title": "Senior Frontend Developer",
        "employer": "TechInnovate Cloud",
        "description": "Looking for a seasoned developer with 14 years of experience in React and Next.js. Must know Redux and CSS.",
        "employer_domain": "techinnovate.com",
        "contact_email": "hr@techinnovate.com",
        "salary_text": "$120,000",
        "true_label": "suspicious",
        "category": "implausible_experience"
    },
    {
        "id": "SCAM-04",
        "title": "Customer Support Representative",
        "employer": "Global Tech Services",
        "description": "Deposit $150 before starting work to secure company training manuals. Refundable with first check.",
        "employer_domain": "globaltech.site",
        "contact_email": "support@globaltech.site",
        "true_label": "suspicious",
        "category": "payment_request"
    },
    {
        "id": "SCAM-05",
        "title": "Cryptocurrency Payment Specialist",
        "employer": "Decentralized Ventures LLC",
        "description": "Receive payments and transfer USDT crypto to our suppliers. Retain 10% commission. Must have personal bank account.",
        "employer_domain": "decentralventures.buzz",
        "contact_email": "payroll@decentralventures.buzz",
        "true_label": "suspicious",
        "category": "payment_request"
    },
    {
        "id": "SCAM-06",
        "title": "Mobile App Engineer",
        "employer": "NextWave Studio",
        "description": "Must have 11 years of experience in Flutter mobile development and Dart.",
        "employer_domain": "nextwavestudio.io",
        "contact_email": "hiring@nextwavestudio.io",
        "true_label": "suspicious",
        "category": "implausible_experience"
    },
    {
        "id": "SCAM-07",
        "title": "Packaging Inspector",
        "employer": "Home Delivery Hub",
        "description": "Receive parcels at your residential address, inspect contents, and purchase shipping labels using gift cards provided.",
        "employer_domain": "homedelivery.click",
        "contact_email": "hr@homedelivery.click",
        "true_label": "suspicious",
        "category": "payment_request"
    },
    {
        "id": "SCAM-08",
        "title": "Executive Assistant to CEO",
        "employer": "Starlight Capital",
        "description": "WhatsApp us at +1-800-555-0199 immediately. You will be sent an advance cashier check to purchase home office electronics.",
        "employer_domain": "starlight-holding.top",
        "contact_email": "starlightrecruitment@yahoo.com",
        "contact_messaging": "WhatsApp: +1-800-555-0199",
        "true_label": "suspicious",
        "category": "communication_pattern"
    },
    {
        "id": "SCAM-09",
        "title": "Python API Developer",
        "employer": "RapidCode Systems",
        "description": "Requires 10 years of experience in FastAPI and asynchronous python microservices.",
        "employer_domain": "rapidcode.tech",
        "contact_email": "dev-hiring@rapidcode.tech",
        "true_label": "suspicious",
        "category": "implausible_experience"
    },
    {
        "id": "SCAM-10",
        "title": "Online Typing & Transcriptionist",
        "employer": "Universal Media Group",
        "description": "Earn $250/hr data entry. Pay a registration fee of $50 to obtain the audio files and document templates.",
        "employer_domain": "universalmedia.xyz",
        "contact_email": "jobs@universalmedia.xyz",
        "true_label": "suspicious",
        "category": "payment_request"
    },
    {
        "id": "SCAM-11",
        "title": "Cloud Infrastructure Engineer",
        "employer": "CloudScale Works",
        "description": "Demanding 15+ years of experience in Kubernetes and container orchestration in production.",
        "employer_domain": "cloudscale.org",
        "contact_email": "infra@cloudscale.org",
        "true_label": "suspicious",
        "category": "implausible_experience"
    },
    {
        "id": "SCAM-12",
        "title": "HR Onboarding Coordinator",
        "employer": "Pinnacle Enterprise",
        "description": "Must pay application fee of $45 for criminal background verification prior to any interview.",
        "employer_domain": "pinnacle.site",
        "contact_email": "onboarding@pinnacle.site",
        "true_label": "suspicious",
        "category": "payment_request"
    },
    {
        "id": "SCAM-13",
        "title": "Remote Social Media Moderator",
        "employer": "ViralReach Inc",
        "description": "Contact only via Telegram @viral_reach_admin. No phone or video interview required. Immediate hire.",
        "employer_domain": "viralreach.live",
        "contact_email": "viraladmin@gmail.com",
        "contact_messaging": "Telegram: @viral_reach_admin",
        "true_label": "suspicious",
        "category": "communication_pattern"
    },
    {
        "id": "SCAM-14",
        "title": "Medical Biller & Typist",
        "employer": "CareFirst Health Staffing",
        "description": "Purchase your own equipment from our vendor at carefirst-billing-vendor.site prior to start date.",
        "employer_domain": "carefirsthealth.top",
        "contact_email": "carefirst@outlook.com",
        "true_label": "suspicious",
        "category": "payment_request"
    },
    {
        "id": "SCAM-15",
        "title": "Junior Web Designer",
        "employer": "PixelCraft Studios",
        "description": "Earn $140/hr with no experience required! High volume data entry and icon clipping.",
        "employer_domain": "pixelcraft.xyz",
        "contact_email": "pixelcraft@protonmail.com",
        "true_label": "suspicious",
        "category": "listing_content"
    },

    # 16-25: Ambiguous & Borderline Cases (Needs Verification)
    {
        "id": "AMBIG-01",
        "title": "Contract Content Writer",
        "employer": "EarlyStage Digital Agency",
        "description": "Freelance blog post writing. Send clips and resume to agency recruiter. Paid per article upon approval.",
        "employer_domain": "earlystage.io",
        "contact_email": "recruiting@gmail.com",
        "true_label": "suspicious",
        "category": "domain_mismatch"
    },
    {
        "id": "AMBIG-02",
        "title": "Product Growth Intern",
        "employer": "Fintech Stealth Labs",
        "description": "Pre-seed stealth startup seeking growth intern. Equity and modest stipend. Reach out on WhatsApp or email.",
        "employer_domain": "fintechlabs.co",
        "contact_email": "founders@fintechlabs.co",
        "contact_messaging": "WhatsApp: +1-555-0123",
        "true_label": "suspicious",
        "category": "communication_pattern"
    },
    {
        "id": "AMBIG-03",
        "title": "Junior Python Scraper",
        "employer": "DataScrape Hub",
        "description": "Build web scrapers in Python. Application URL goes to an external airtable form.",
        "employer_domain": "datascrape.xyz",
        "contact_email": "team@datascrape.xyz",
        "application_url": "https://airtable.com/app123/form",
        "true_label": "suspicious",
        "category": "domain_mismatch"
    },
    {
        "id": "AMBIG-04",
        "title": "Remote Community Manager",
        "employer": "Indie Game Guild",
        "description": "Moderate discord server and twitch chats. Telegram used for team announcements.",
        "employer_domain": "indiegameguild.gg",
        "contact_email": "info@indiegameguild.gg",
        "contact_messaging": "Telegram: @indieguild",
        "true_label": "suspicious",
        "category": "communication_pattern"
    },
    {
        "id": "AMBIG-05",
        "title": "Entry Level QA Tester",
        "employer": "BetaSoft QA",
        "description": "Manual testing of web applications. No compensation listed. Application via google form.",
        "employer_domain": "",
        "contact_email": "betasoftqa@gmail.com",
        "true_label": "suspicious",
        "category": "domain_mismatch"
    },

    # 26-42: Legitimate Verified Job Listings
    {
        "id": "LEGIT-01",
        "title": "Junior Full Stack Engineer",
        "employer": "Meridian Health Technologies",
        "description": "We are seeking a Junior Full Stack Engineer with proficiency in Python, React, and PostgreSQL. Responsibilities include building responsive UI components, integrating RESTful APIs, and writing automated unit tests. The hiring process includes a recruiter phone screen, technical coding interview, and team architecture discussion. Competitive salary between $75,000 - $90,000.",
        "employer_domain": "meridianhealth.com",
        "contact_email": "careers@meridianhealth.com",
        "salary_text": "$75,000 - $90,000",
        "true_label": "legitimate",
        "category": "verified_tech"
    },
    {
        "id": "LEGIT-02",
        "title": "Associate Data Analyst",
        "employer": "Beacon Financial Analytics",
        "description": "Join our analytics team to create executive business intelligence dashboards using SQL, Python, and Tableau. Qualifications: Bachelor's in CS, Mathematics, or equivalent practical experience. 1-2 years experience with relational databases and data visualization. Structured 3-round interview process.",
        "employer_domain": "beaconfinancial.org",
        "contact_email": "talent@beaconfinancial.org",
        "salary_text": "$70,000 - $82,000",
        "true_label": "legitimate",
        "category": "verified_data"
    },
    {
        "id": "LEGIT-03",
        "title": "Frontend React Developer",
        "employer": "Loomis Commerce Systems",
        "description": "Develop high-performance e-commerce storefronts using React, TypeScript, and Tailwind CSS. Requirements: 2-4 years frontend experience, familiarity with Webpack/Vite, component lifecycle, and state management. Two rounds of technical evaluation followed by manager conversation.",
        "employer_domain": "loomiscommerce.com",
        "contact_email": "jobs@loomiscommerce.com",
        "salary_text": "$85,000 - $105,000",
        "true_label": "legitimate",
        "category": "verified_tech"
    },
    {
        "id": "LEGIT-04",
        "title": "DevOps & Cloud Engineer",
        "employer": "Astra Cloud Platforms",
        "description": "Manage containerized deployments using Docker and Kubernetes on AWS. Responsibilities include maintaining CI/CD pipelines, monitoring server uptime, and writing Terraform scripts. 3-5 years cloud experience required.",
        "employer_domain": "astracloud.io",
        "contact_email": "recruiting@astracloud.io",
        "salary_text": "$115,000 - $135,000",
        "true_label": "legitimate",
        "category": "verified_devops"
    },
    {
        "id": "LEGIT-05",
        "title": "Backend Python Engineer",
        "employer": "Veritas Cyber Defense",
        "description": "Build high-throughput threat detection APIs using FastAPI, async SQLAlchemy, and Redis. Responsibilities: designing secure microservices, API documentation, and code reviews. 2-3 years backend experience.",
        "employer_domain": "veritascyber.com",
        "contact_email": "careers@veritascyber.com",
        "salary_text": "$95,000 - $115,000",
        "true_label": "legitimate",
        "category": "verified_backend"
    },
    {
        "id": "LEGIT-06",
        "title": "Machine Learning Associate",
        "employer": "Cognitive BioScience",
        "description": "Apply scikit-learn and pandas to analyze biological sequence datasets. Prepare data cleaning pipelines, feature engineering, and model validation reports. Structured technical assessment and research talk.",
        "employer_domain": "cognitivebio.edu",
        "contact_email": "research-jobs@cognitivebio.edu",
        "salary_text": "$80,000 - $95,000",
        "true_label": "legitimate",
        "category": "verified_ml"
    },
    {
        "id": "LEGIT-07",
        "title": "Mobile Software Engineer (iOS)",
        "employer": "Evergreen Mobile Apps",
        "description": "Design and maintain consumer iOS apps in Swift and SwiftUI. Collaborate with UI designers and product managers. 2-4 years native iOS development experience required.",
        "employer_domain": "evergreenapps.co",
        "contact_email": "talent@evergreenapps.co",
        "salary_text": "$90,000 - $110,000",
        "true_label": "legitimate",
        "category": "verified_mobile"
    },
    {
        "id": "LEGIT-08",
        "title": "QA Automation Engineer",
        "employer": "Precision Software Lab",
        "description": "Implement end-to-end test suites using Playwright, pytest, and GitHub Actions. Define test plans and reproduce bugs with engineering teams. 2+ years automated testing experience.",
        "employer_domain": "precisionlab.tech",
        "contact_email": "qa-hiring@precisionlab.tech",
        "salary_text": "$80,000 - $92,000",
        "true_label": "legitimate",
        "category": "verified_qa"
    },
    {
        "id": "LEGIT-09",
        "title": "Product Designer (UI/UX)",
        "employer": "Kestrel Interactive Design",
        "description": "Create intuitive wireframes, component design systems, and clickable prototypes in Figma. Conduct user research and accessibility compliance testing (WCAG 2.1 AA).",
        "employer_domain": "kestreldesign.studio",
        "contact_email": "design@kestreldesign.studio",
        "salary_text": "$85,000 - $100,000",
        "true_label": "legitimate",
        "category": "verified_design"
    },
    {
        "id": "LEGIT-10",
        "title": "Database Administrator",
        "employer": "National Logistics Network",
        "description": "Maintain high availability PostgreSQL clusters, optimize query performance, manage backups, and perform disaster recovery tests. 4+ years relational DBA experience.",
        "employer_domain": "nationallogistics.gov.in",
        "contact_email": "careers@nationallogistics.gov.in",
        "salary_text": "$85,000 - $105,000",
        "true_label": "legitimate",
        "category": "verified_database"
    },
    {
        "id": "LEGIT-11",
        "title": "Cybersecurity Analyst",
        "employer": "Sentinel Defense Systems",
        "description": "Monitor security alerts, conduct vulnerability scans, and assist with incident response workflows. Certifications such as CompTIA Security+ or CEH preferred.",
        "employer_domain": "sentineldefense.com",
        "contact_email": "soc-careers@sentineldefense.com",
        "salary_text": "$78,000 - $94,000",
        "true_label": "legitimate",
        "category": "verified_security"
    },
    {
        "id": "LEGIT-12",
        "title": "Technical Technical Writer",
        "employer": "OpenDev Platforms",
        "description": "Write developer documentation, API reference guides, and quickstart tutorials for open source libraries. Strong familiarity with Markdown and Git workflows.",
        "employer_domain": "opendev.org",
        "contact_email": "docs@opendev.org",
        "salary_text": "$70,000 - $85,000",
        "true_label": "legitimate",
        "category": "verified_docs"
    },
    {
        "id": "LEGIT-13",
        "title": "Junior Systems Administrator",
        "employer": "Summit Research Institute",
        "description": "Provision Linux workstations, manage user permissions via LDAP, and monitor server room environmental metrics. Great for early career IT graduates.",
        "employer_domain": "summitresearch.edu",
        "contact_email": "it-staffing@summitresearch.edu",
        "salary_text": "$55,000 - $68,000",
        "true_label": "legitimate",
        "category": "verified_it"
    },
    {
        "id": "LEGIT-14",
        "title": "Full Stack Web Developer",
        "employer": "Catalyst Social Tech",
        "description": "Build accessible public advocacy tools with React, Node.js, and MongoDB. Open to self-taught developers with strong GitHub portfolio projects.",
        "employer_domain": "catalystsocial.org",
        "contact_email": "hiring@catalystsocial.org",
        "salary_text": "$72,000 - $88,000",
        "true_label": "legitimate",
        "category": "verified_tech"
    },
    {
        "id": "LEGIT-15",
        "title": "Data Engineer",
        "employer": "Harbor Data Solutions",
        "description": "Design ETL pipelines using Apache Spark, Airflow, and PostgreSQL. Monitor batch processing jobs and ensure data quality metrics across warehouses.",
        "employer_domain": "harbordatasolutions.com",
        "contact_email": "careers@harbordatasolutions.com",
        "salary_text": "$100,000 - $120,000",
        "true_label": "legitimate",
        "category": "verified_data"
    },
    {
        "id": "LEGIT-16",
        "title": "Site Reliability Engineer",
        "employer": "Orbit Network Services",
        "description": "Ensure 99.99% uptime of microservice fleets. On-call rotation with incident post-mortems and chaos engineering experiments.",
        "employer_domain": "orbitnetwork.net",
        "contact_email": "sre-team@orbitnetwork.net",
        "salary_text": "$110,000 - $130,000",
        "true_label": "legitimate",
        "category": "verified_sre"
    },
    {
        "id": "LEGIT-17",
        "title": "Junior Business Analyst",
        "employer": "Global Insights Consulting",
        "description": "Gather user requirements, draft functional specification documents, and liaise between business stakeholders and engineering teams.",
        "employer_domain": "globalinsights.com",
        "contact_email": "recruiting@globalinsights.com",
        "salary_text": "$65,000 - $78,000",
        "true_label": "legitimate",
        "category": "verified_ba"
    },
    {
        "id": "LEGIT-18",
        "title": "Senior Backend Architect",
        "employer": "Vanguard Distributed Systems",
        "description": "Architect high availability systems in Go and PostgreSQL. 5+ years distributed systems experience. Structured code review and architectural interview rounds.",
        "employer_domain": "vanguardds.io",
        "contact_email": "careers@vanguardds.io",
        "salary_text": "$140,000 - $165,000",
        "true_label": "legitimate",
        "category": "verified_backend"
    },
    {
        "id": "LEGIT-19",
        "title": "Machine Learning Engineer (NLP)",
        "employer": "Lexicon AI Research",
        "description": "Train and evaluate domain-specific transformer models using PyTorch and HuggingFace. Conduct model evaluation, error analysis, and benchmarking.",
        "employer_domain": "lexiconai.org",
        "contact_email": "research@lexiconai.org",
        "salary_text": "$125,000 - $145,000",
        "true_label": "legitimate",
        "category": "verified_ml"
    },
    {
        "id": "LEGIT-20",
        "title": "Security Operations Specialist",
        "employer": "DefendGrid Cyber",
        "description": "Triage SIEM alerts, investigate suspicious login anomalies, and configure firewall policies. Industry standard certifications welcomed.",
        "employer_domain": "defendgrid.com",
        "contact_email": "talent@defendgrid.com",
        "salary_text": "$85,000 - $100,000",
        "true_label": "legitimate",
        "category": "verified_security"
    },
    {
        "id": "SCAM-16",
        "title": "Crypto Investment Assistant",
        "employer": "Global Currency Matrix",
        "description": "Earn $220/hr. Send cryptocurrency wire deposit to initiate contract training. Must purchase your own materials from our designated vendor.",
        "employer_domain": "matrix-currency.xyz",
        "contact_email": "matrixhr@gmail.com",
        "salary_text": "$220/hr",
        "true_label": "suspicious",
        "category": "payment_request"
    },
    {
        "id": "SCAM-17",
        "title": "Remote Administrative Clerk",
        "employer": "Prime Fast Delivery",
        "description": "Immediate placement! No interview required. Reach out on WhatsApp at +1-555-8899. You will be sent an advance check to buy supplies.",
        "employer_domain": "primefast.top",
        "contact_email": "primefast@outlook.com",
        "contact_messaging": "WhatsApp: +1-555-8899",
        "true_label": "suspicious",
        "category": "communication_pattern"
    }
]

def run_scam_model_evaluation() -> Dict[str, Any]:
    """Runs the scam detection multi-signal engine against all 42 labeled evaluation cases."""
    results = []
    tp = 0  # True Positive (suspicious classified as Elevated or Needs verification)
    fp = 0  # False Positive (legitimate classified as suspicious)
    tn = 0  # True Negative (legitimate classified as Lower observed risk)
    fn = 0  # False Negative (suspicious classified as Lower observed risk)
    
    category_breakdown: Dict[str, Dict[str, int]] = {}

    for item in EVALUATION_DATASET:
        analysis = analyze_job_listing(
            title=item["title"],
            employer=item["employer"],
            description=item["description"],
            employer_domain=item.get("employer_domain", ""),
            contact_email=item.get("contact_email", ""),
            contact_messaging=item.get("contact_messaging", ""),
            salary_text=item.get("salary_text", ""),
            application_url=item.get("application_url", "")
        )
        
        predicted_suspicious = analysis["risk_tier"] in ["Elevated risk indicators", "Needs verification"]
        actual_suspicious = item["true_label"] == "suspicious"
        
        cat = item.get("category", "general")
        if cat not in category_breakdown:
            category_breakdown[cat] = {"total": 0, "correct": 0}
        category_breakdown[cat]["total"] += 1
        
        if predicted_suspicious and actual_suspicious:
            tp += 1
            category_breakdown[cat]["correct"] += 1
        elif predicted_suspicious and not actual_suspicious:
            fp += 1
        elif not predicted_suspicious and not actual_suspicious:
            tn += 1
            category_breakdown[cat]["correct"] += 1
        else:
            fn += 1

        results.append({
            "id": item["id"],
            "title": item["title"],
            "employer": item["employer"],
            "true_label": item["true_label"],
            "predicted_tier": analysis["risk_tier"],
            "risk_score": analysis["risk_score"],
            "signal_count": len(analysis["signals"]),
            "signals": [s["title"] for s in analysis["signals"]],
            "correct": (predicted_suspicious == actual_suspicious)
        })

    precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
    recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
    fpr = fp / (fp + tn) if (fp + tn) > 0 else 0.0
    f1 = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0.0
    accuracy = (tp + tn) / len(EVALUATION_DATASET)

    return {
        "dataset_size": len(EVALUATION_DATASET),
        "suspicious_count": sum(1 for x in EVALUATION_DATASET if x["true_label"] == "suspicious"),
        "legitimate_count": sum(1 for x in EVALUATION_DATASET if x["true_label"] == "legitimate"),
        "metrics": {
            "accuracy": round(accuracy * 100, 2),
            "precision": round(precision * 100, 2),
            "recall": round(recall * 100, 2),
            "false_positive_rate": round(fpr * 100, 2),
            "f1_score": round(f1 * 100, 2)
        },
        "confusion_matrix": {
            "true_positives": tp,
            "false_positives": fp,
            "true_negatives": tn,
            "false_negatives": fn
        },
        "category_breakdown": category_breakdown,
        "sample_evaluations": results
    }
