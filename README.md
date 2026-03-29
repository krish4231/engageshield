# 🛡️ EngageShield

**Intelligent Fake Engagement Detection System**

EngageShield is a full-stack, production-ready platform designed to detect bots, fake likes, artificial followers, and coordinated engagement networks on social media. 

Instead of relying on a single method, EngageShield acts as a "security team," running suspicious accounts through four different specialized detection engines simultaneously to calculate a highly accurate threat score.

![EngageShield Analysis Preview](./frontend/public/shield-icon.png)

---

## 📖 How It Works (Simple Explanation)

Imagine you are a security guard at a popular nightclub (a social media platform). You have four different specialists helping you spot people with fake IDs (fake engagements):

### 1. The ML (Machine Learning) Classifier 🤖
* **What it does:** Looks at the overall "vibe" and statistics of a user.
* **Example:** Normal users have varied interactions. A bot might like exactly 300 posts an hour, follow 5,000 people, but have 0 followers. The ML model spots these statistical red flags.

### 2. The Behavioral Analyzer ⏱️
* **What it does:** Looks at the *timing* of when a user acts.
* **Example:** Humans sleep. If an account is liking posts evenly every 4 minutes, 24 hours a day without stopping, the Behavioral Analyzer tags it as machine-like (a bot).

### 3. The Graph Engine (Network Analysis) 🕸️
* **What it does:** Looks at who is interacting with whom to find "gangs."
* **Example:** If 50 different accounts *only* ever like each other's posts within 5 seconds of them being uploaded, they are part of a coordinated "engagement pod." The Graph engine maps these relationships out to expose hidden networks.

### 4. The AI Insight Engine 🧠
* **What it does:** Translates all the complex data above into plain human English.
* **Example:** Instead of giving you a confusing spreadsheet of data, it tells you: "This target is highly suspicious because 80% of its interactions happen during sleep hours, and it only interacts with a cluster of 5 specific accounts."

**The Orchestrator:**
When you type in a username (like `target_0001`), EngageShield sends their data to all 4 engines at once. It aggregates the results, gives you a **Threat Score (0-100%)**, and decides if it needs to trigger an immediate **Real-time Alert**.

---

## 🚀 Key Features

* **Premium Dashboard:** A beautiful, dark-mode glassmorphism UI built with React, Vite, and ECharts.
* **Real-time Alerts:** Live WebSockets stream threat alerts to your dashboard the second suspicious activity happens.
* **Interactive Network Map:** Visually explore coordinated bot rings with physics-based nodes.
* **Advanced Data Pipeline:** Includes tools to securely ingest massive batches of social media data into a high-performance PostgreSQL (or SQLite) database.
* **Production Ready:** Fully containerized with Docker, Nginx, and GitHub Actions CI/CD pipelines.

---

## 🛠️ Tech Stack

* **Backend:** Python 3.12, FastAPI, Async SQLAlchemy, WebSockets
* **Data Science:** Scikit-Learn, XGBoost, NetworkX, Pandas
* **Frontend:** React 18, TypeScript, TailwindCSS/Vanilla CSS, ECharts, Recharts
* **Infrastructure:** PostgreSQL 16 (or SQLite for local dev), Redis 7, Docker Compose, Nginx

---

## 🏃‍♂️ How to Run the Project Locally

We've made it incredibly easy to start EngageShield. You can use our customized one-click startup script.

### Option 1: The Magic Startup Script (macOS/Linux)
Simply double-click the `start.command` file in your Finder, or run it via terminal:
```bash
./start.command
```
*This will auto-install dependencies, set up the database, start the backend API, start the React frontend, and automatically open your web browser.*

### Option 2: Run with Docker (Recommended for Production)
If you have Docker installed, you can spin up the full production architecture:
```bash
docker compose up --build -d
```
Then visit `http://localhost:5173` in your browser.

---

## 🧪 Testing with Mock Data

To see the dashboard come alive without needing to hook up real Twitter/Instagram APIs, we've included a data generator:

1. Stop the servers if they are running.
2. In your terminal, run the seeder script:
   ```bash
   cd backend
   source venv/bin/activate
   python seed_db.py
   ```
3. This creates **thousands of realistic mock engagements**, including hidden "bot" patterns and "coordinated pods."
4. Restart the servers using `./start.command`.
5. Go to the **Analysis Tab** and type in `target_0001` or `target_0004` to see if EngageShield catches the bots!

---

## 🔒 Security & Architecture

The system uses stateless JWT Authentication (`app/auth`), strict FastAPI dependency injection, and secure password hashing. The architecture heavily enforces separation of concerns:
* **`app/models/`** - Data definition
* **`app/detection/`** - Business logic & engines
* **`app/ingestion/`** - Data pipelines
* **`frontend/`** - Pure presentation layer 
