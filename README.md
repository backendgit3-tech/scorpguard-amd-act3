<div align="center">
  <h1>🦂 SCORPGUARD</h1>
  <p><strong>The Agent Runtime Guardian</strong></p>
  <p>Production-grade resilience for AI agents. Built for the AMD Developer Hackathon: ACT III.</p>
  
  [![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi)](https://fastapi.tiangolo.com/)
  [![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
  [![PostgreSQL](https://img.shields.io/badge/PostgreSQL-316192?style=for-the-badge&logo=postgresql&logoColor=white)](https://postgresql.org)
  [![Redis](https://img.shields.io/badge/Redis-DC382D?style=for-the-badge&logo=redis&logoColor=white)](https://redis.io)
  [![AMD](https://img.shields.io/badge/AMD_MI300X-ED1C24?style=for-the-badge&logo=amd&logoColor=white)](https://amd.com)
</div>

---

## 🚨 The Problem: Why 86% of Enterprise AI Agents Fail

AI agents are being deployed into production at an unprecedented rate, but most of them fail. Not because of bad models, but because of **broken runtime infrastructure**:
- **State Amnesia:** Container restarts erase agent memory and context.
- **Hallucination Cascades:** A silent error in Step 3 compounds into a catastrophic failure by Step 12.
- **Cost Blindness:** Runaway token usage silently breaches business budgets.

## 💡 The Solution: SCORPGUARD

**SCORPGUARD** is an intelligent middleware layer that wraps around any AI agent to ensure safe, reliable, and cost-effective execution. It doesn't just monitor agents; it **heals** them.

### Core Features
- 🛡️ **Event-Sourced State Persistence:** Checkpoints agent state to PostgreSQL, ensuring memory survives container kills and restarts.
- 🧠 **Dual-Layer Anomaly Detection:**
  - *Layer 1 (Rule-Based):* <10ms detection of fatal crashes, loops, and out-of-order steps.
  - *Layer 2 (Semantic AI):* LLM-based deep verification to catch logical hallucinations and silent errors.
- 🔄 **Auto-Rollback Engine:** Instantly rewinds agent state to the last safe checkpoint upon detecting an anomaly.
- 💰 **Real-Time Cost Monitor:** Tracks token usage and USD cost per agent action.

## 🏗️ Architecture & Tech Stack

SCORPGUARD is built for enterprise scale with a focus on high availability.

- **Inference:** Designed for **AMD Instinct MI300X** using **ROCm** and **vLLM** (Qwen2.5).
- **High Availability Fallback:** Groq API integration for uninterrupted, ultra-fast LLM inference when GPU nodes are scaling.
- **Backend:** FastAPI, SQLAlchemy (Async), PostgreSQL (Event Store), Redis (Cache/Broker), Celery (Background Tasks).
- **Frontend:** A real-time, dark-theme command center for live monitoring and anomaly simulation.

## 🎬 The "Kill & Recover" Demo

SCORPGUARD features an interactive frontend dashboard to prove its capabilities:
1. **Rule Anomaly Simulation:** Injects a fatal runtime error. Watch as Layer 1 instantly catches it and rolls back the state.
2. **Semantic Anomaly Simulation:** The agent silently hallucinates (e.g., claims a user's $500 balance is $5000). Watch Layer 2's LLM catch the logical inconsistency and heal the state.

## 🚀 Quick Start (Local Development)

**1. Clone the repository**
```bash
git clone https://github.com/backendgit3-tech/scorpguard-amd-act3.git
cd scorpguard-amd-act3

2. Set up environment variables
Copy .env.example to .env and fill in your keys:

```env
DATABASE_URL=postgresql+asyncpg://user:pass@localhost:5432/scorpguard
REDIS_URL=redis://localhost:6379/0
GROQ_API_KEY=your_api_key_here
```

3. Start the databases (Docker)

```bash
docker compose up -d
```

4. Install dependencies & Run

```bash
python -m venv venv
source venv/bin/activate  # On Windows: .\venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8080
```

5. Access the Dashboard
Open http://localhost:8080 in your browser.

---

<div align="center">
  <p>Built with ❤️ by <strong>Team Scorpion</strong></p>
  <p>Intelligent Systems. Secured.</p>
</div
