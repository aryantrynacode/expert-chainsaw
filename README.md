An AI-powered assistant for bug bounty hunters.  
The app scans multiple URLs, generates AI triaged findings, helps researchers verify them manually, and builds professional vulnerability reports with an AI chatbot.

---

## 🔐 1. Login / Signup Page
**Purpose:** Provide authentication for users to manage their scans, reports, and dashboard.

**Features:**
- Email/Password signup or login (JWT/Firebase Auth).
- Session management (stay logged in).
- Guest mode (optional, but without saving history).
- Forgot password & reset flow.

---

# 4. AI Chatbot Page

**Purpose:** Help researchers structure and finalize a professional vulnerability report.

**Features:**

- Chat interface to refine:

  - Report title & description

  - Impact and severity justification

  - Steps to reproduce (from AI + user input)

  - Mitigation advice

- Uses scan JSON + PoC + researcher input as context.

- Outputs a polished, export-ready report draft.

---

## 🌍 2. Report Submission Page
**Purpose:** Let researchers input multiple URLs to be scanned by the backend.

**Features:**
- Input field for **one or multiple URLs** (comma or newline separated).
- Optional **file upload** (snippet/HTML for static analysis).
- “Run Scan” button triggers backend passive scan.
- Scan results returned as a **structured JSON file** for each URL:
  ```json
  {
    "title": "Potential XSS in profile bio",
    "description": "Unescaped user input reflected in HTML response.",
    "location": "/profile?bio=",
    "severity": "High",
    "ai_confidence": 0.83
  }
- Results stored in DB and linked to the user.

---

##  3. Manual Verification Page

**Purpose:** Allow researcher to test and confirm vulnerabilities themselves.

**Features:**

- Shows AI-generated scan results.

- Researcher can mark each result as:

    - Pending → not yet checked.

    - Verified → confirmed by researcher.

    - False Positive → AI misclassified.

- Upload Proof of Concept (PoC):

- Text/code snippet

- Screenshot (image file)

- Notes field for extra researcher observations.

---

## Dashboard Page


**Purpose:** Central place for users to track all their scans and reports.

**Features:**

- profile picture

- username : during authorization 


- Table/list view of all submitted URLs.

   **For each URL/report:**

        Title

        Severity

        AI confidence

        Current status (Pending / Verified / Drafted / Exported)

        Filters: by severity, status, or date.

    **Quick access buttons:**

- View all scans 

- View all reports (with download option)

- Open AI chatbot


