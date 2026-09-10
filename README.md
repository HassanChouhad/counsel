# CounselCore ⚖️

### *AWS AI Agents Hackathon — Professional Agents Track*

CounselCore is an advanced, autonomous legal research agent built using **Python**, **AWS Bedrock (Claude Engine)**, and the **Strands Agents SDK**. It is designed to act as a tireless, highly knowledgeable co-pilot for solo attorneys, paralegals, and legal teams, helping them cut down hours of manual research to minutes.

---

## 📖 Table of Contents
1. [Overview](#-overview)
2. [Key Features](#-key-features)
3. [Who It's For](#-who-its-for)
4. [How It Works](#-how-it-works)
5. [System Architecture](#-system-architecture)
6. [Prerequisites](#-prerequisites)
7. [Installation & Setup](#-installation--setup)
8. [Configuration (.env)](#-configuration-env)
9. [Running the Application](#-running-the-application)
10. [Legal databases and Mocking](#-legal-databases-and-mocking)
11. [License](#-license)

---

## 🌟 Overview
In modern law, drafting a preliminary legal strategy or brief is one of the most time-consuming and tedious phases of a case. Lawyers must sift through mountains of case files, search through proprietary statutory databases, and cross-reference hundreds of historical precedents.

**CounselCore** solves this bottleneck by orchestrating an autonomous legal reasoning pipeline. When a user inputs raw case notes or client facts, CounselCore automatically:
1. Identifies the core legal themes and relevant jurisdictions.
2. Formulates and executes optimal search queries to query local/national statutes and code libraries.
3. Queries precedents and landmark holdings.
4. Synthesizes the legal authority and factual matrix into a comprehensive, ready-to-refine **Preliminary Legal Strategy Brief** in Markdown.

---

## ✨ Key Features
* **Autonomous Agent Reasoning:** Leverages the Strands Agents SDK to let Claude 3 Sonnet determine what research tools to call and what queries to run.
* **AWS Bedrock Claude Engine:** Utilizing AWS Bedrock's enterprise-grade security and ultra-low latency inference to process sensitive legal client facts.
* **Intelligent Query Parser:** Employs semantic keyword and tag-matching logic to query precedents and statutory data dynamically.
* **Surgical Document Drafting:** A customizable template engine that generates professional, courtroom-ready markdown outlines.
* **No Out-of-Pocket Cost Demo:** Comes fully configured with high-quality mock database layers so judges can run and test the application immediately without expensive legal database API access keys.

---

## 👥 Who It's For
* **Solo Practitioners & Small Law Firms:** Levels the playing field against enterprise-class law firms with dedicated paralegal teams.
* **Corporate Legal Departments:** Accelerates response times to commercial contract disputes, privacy audits, and employment non-compete questions.
* **Pro-Bono Clinics:** Maximizes the volume of clients served by automating early research drafts.

---

## 🛠️ How It Works
CounselCore is engineered around a model-driven autonomous loop. The flow is as follows:

```
                  ┌─────────────────────────────────────┐
                  │          User Inputs Case Facts     │
                  └──────────────────┬──────────────────┘
                                     │
                                     ▼
                  ┌─────────────────────────────────────┐
                  │       CounselCore Agent Engine      │
                  │   (AWS Bedrock: Claude 3 Sonnet)     │
                  └──────────────────┬──────────────────┘
                                     │
           ┌─────────────────────────┼─────────────────────────┐
           │ (Autonomous Tool Call)  │ (Autonomous Tool Call)  │
           ▼                         ▼                         ▼
┌────────────────────┐    ┌────────────────────┐    ┌────────────────────┐
│ search_case_law()  │    │  lookup_statutes() │    │ draft_legal_brief()│
│                    │    │                    │    │                    │
│ Matches precedents │    │ Matches codes and  │    │ Formats & compiles │
│ & landmark cases   │    │ legislative titles │    │ final markdown     │
└──────────┬─────────┘    └──────────┬─────────┘    └──────────┬─────────┘
           │                         │                         │
           └─────────────────────────┼─────────────────────────┘
                                     │
                                     ▼
                  ┌─────────────────────────────────────┐
                  │    Prints Structured Legal Brief    │
                  │        (Attorney-Client Privileged) │
                  └─────────────────────────────────────┘
```

---

## 🏛️ System Architecture

CounselCore utilizes three specialized tools written and registered in the **Strands Agents SDK**:

1. **`search_case_law(query: str, jurisdiction: str)`**:
   Searches legal precedent holdings. Utilizes an intelligent tag and semantic-keyword lookup algorithm to match federal/state landmark decisions.
2. **`lookup_statutes(topic: str)`**:
   Returns statutory regulations (such as CA Business & Professions Code, Texas Non-compete Acts, US Copyright Act, and the California Consumer Privacy Act).
3. **`draft_legal_brief(case_facts: str, precedents: list, statutes: list)`**:
   An expert compiler that formats and stitches findings, client facts, and strategic recommendations into a unified legal strategy document.

---

## 📋 Prerequisites
Before running CounselCore, please ensure you have the following:
* **Python 3.10 or higher** installed.
* **AWS Account** with access granted to **Amazon Bedrock Foundation Models** (specifically `anthropic.claude-3-sonnet-20240229-v1:0` or any Claude model).
* AWS IAM Access Key and Secret Key with `bedrock:InvokeModel` permissions.

---

## ⚙️ Installation & Setup

### 1. Clone the Repository
```bash
git clone https://github.com/your-username/CounselCore.git
cd CounselCore
```

### 2. Create and Activate a Virtual Environment
```bash
# On macOS / Linux
python3 -m venv venv
source venv/bin/activate

# On Windows (Command Prompt)
python -m venv venv
venv\Scripts\activate.bat
```

### 3. Install Dependencies
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

---

## 🔑 Configuration (.env)

Rename `.env.example` to `.env` and enter your AWS configuration parameters:

```bash
cp .env.example .env
```

Open `.env` in your text editor and specify your AWS keys:
```ini
AWS_ACCESS_KEY_ID=your_actual_aws_access_key_id
AWS_SECRET_ACCESS_KEY=your_actual_aws_secret_access_key
AWS_DEFAULT_REGION=us-east-1

# Optional: You can change the model ID if you have access to a newer one,
# but 'anthropic.claude-3-sonnet-20240229-v1:0' is the standard out-of-the-box model.
AWS_BEDROCK_MODEL_ID=anthropic.claude-3-sonnet-20240229-v1:0
```

---

## 🚀 Running the Application

Launch the CounselCore interactive console application:
```bash
python app.py
```

### 📝 Example Case Facts to Try

You can test CounselCore's reasoning engine using one of these realistic disputes:

#### Scenario A: Non-compete & Customer Solicitation Dispute (Texas jurisdiction)
> A client named Summit Logistics hired an executive in Dallas, Texas. The executive signed a non-compete covenant restricting them from working for competitors within a 50-mile radius for 12 months. Upon resignation, they immediately joined Apex Logistics (a direct competitor 10 miles away) and began emailing our client lists. We want to know if we can seek an injunction in Texas.

#### Scenario B: Copyright & AI Generated Marketing Assets
> A graphic design studio based in New York discovered that a rival advertising firm, PixelCraft, has been scraping their copyrighted vector graphics, feeding them into a generative AI model, and producing commercial advertising materials that are virtually identical to our original sketches. PixelCraft claims it is fair use because it's AI-generated.

#### Scenario C: Medical Malpractice & Standard of Care Deviation
> In Massachusetts, a patient underwent gallbladder surgery at St. Jude Medical Center. The attending surgeon failed to complete the hospital's mandated pre-operative sanitation checklist. The patient contracted a severe post-operative infection, resulting in permanent liver damage. We need to evaluate if the hospital and surgeon can be held negligent.

---

## 📑 Legal Databases and Mocking

To ensure judges can run the hackathon demo without needing a paid subscription to Westlaw or LexisNexis (which cost thousands of dollars per month and require credential verification), CounselCore includes highly detailed mock databases in `tools.py` for:
* **Federal / 9th Circuit Decisions**
* **Texas Supreme Court & Court of Appeals Decisions**
* **New York Copyright & IP Infringement Cases**
* **Massachusetts Tort & Malpractice precedents**
* **California Privacy & Consumer Protection cases**

*If your search query doesn't match any specific tags, CounselCore is designed to fallback to general statutory guidelines and precedents to guarantee the agent always compiles a coherent and functional strategy brief.*

---

## 💾 Persistent Vector Database (ChromaDB)

CounselCore has been upgraded from static dictionaries to a local **ChromaDB vector database** implementing semantically indexed retrieval (RAG).

### 1. Ingest Core Landmark Data (Seed)
Run the seeder to populate the local database (`./chroma_db/`) with foundational state statutes and precedent summaries:
```bash
python seed_db.py
```

### 2. Ingest Real California Case Law (Harvard CAP Data)
We integrated support to download real court opinions directly from the **Harvard Caselaw Access Project**'s static server (`static.case.law`). 
Run the real data ingester, which downloads actual opinion documents, uses your AWS Bedrock model to autonomously extract facts, holdings, and principles, and indexes them into ChromaDB:
```bash
python ingest_real_cases.py
```

---

## 💻 Running the Web Frontend & API Server

In addition to the interactive command-line app, CounselCore includes a visually stunning, responsive **Vite.js + React (TypeScript)** web dashboard with a **Chat + Brief Split-View** UX.

### 1. Start the Python API Backend Server
Launch the FastAPI web server, which handles requests from the React client and coordinates with your Strands SDK Agent:
```bash
python api.py
```
*(Runs on [http://127.0.0.1:8000](http://127.0.0.1:8000))*

### 2. Run the Vite Web Client
Navigate to the `frontend/` directory, install packages, and start the development server:
```bash
cd frontend
npm run dev
```
*(Open your browser at [http://localhost:5173](http://localhost:5173))*

*Note: The frontend includes a **Simulated (Local Mock) Mode** that auto-detects if your FastAPI backend is offline and falls back to a realistic interactive demo, allowing judges to test and review the layout and transitions seamlessly even without AWS Bedrock access!*

---

## 📄 License
This project is licensed under the standard MIT License. See the [LICENSE](LICENSE) file for details.
