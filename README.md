# 🎖️ A.U.R.A : Audio Understanding and Reconnaissance Automation

A comprehensive military tactical operations system featuring:

- **Real-time battlefield reporting** with MQTT communication
- **AI-powered analysis** using Google Gemini for tactical insights
- **Interactive dashboard** with military hierarchy visualization
- **Automated report generation** (CASEVAC, EOINCREP, FRAGO, SITREP)
- **Smart suggestions** and notifications for commanders
- **Speech-to-text** soldier assistant for hands-free reporting

## 📁 Project Structure

```
aalto_defence_project/
├── backend/                          # Backend application
│   ├── backend.py                   # FastAPI server
│   └── requirements.txt             # Python dependencies
├── database/                         # Database files
│   ├── schema.sql                   # Database schema
│   ├── setup.py                     # Initialization script
│   ├── military_hierarchy.db        # SQLite database
│   └── migrations/                  # SQL migration scripts
│       ├── add_frago_table.sql
│       └── add_suggestions_table.sql
├── mil_dashboard/                    # Next.js dashboard frontend
│   ├── src/app/                     # App pages
│   ├── src/components/              # React components
│   └── src/lib/                     # Utilities
├── soldier_assistant/                # Raspberry Pi voice assistant
│   └── RASPBERRY_PI_DEPLOYMENT.md
├── Decoding_and_storing_LLM/        # LLM data encoding utilities
├── scripts/                          # Utility scripts
│   ├── populate_reports.py
│   ├── send_test_report.py
│   └── clear_reports.py
├── tests/                            # Test files
│   ├── test_backend.py
│   ├── test_ai_suggestions.py
│   ├── test_casevac_*.py
│   └── test_soldier_integration.py
├── docs/                             # Documentation
│   ├── API_DOCUMENTATION.md
│   ├── SCHEMA_DOCUMENTATION.md
│   └── AI_PROMPTS_AND_CONCEPT.md   # AI prompts & project concept
├── tools/                            # Additional utilities
└── .venv/                            # Python virtual environment
```

## 🚀 Quick Start

### Prerequisites

- Python 3.8+ with virtual environment
- Node.js 18+ and npm
- SQLite3

### 1. **Setup Backend**

```bash
# Activate virtual environment
.venv\Scripts\activate

# Start backend server (from project root)
python backend/backend.py
```

The backend will run on `https://military-hierarchy-backend.onrender.com/`

### 2. **Setup Frontend**

```bash
# Navigate to dashboard
cd mil_dashboard

# Install dependencies (first time only)
npm install --legacy-peer-deps

# Start frontend
npm run dev
```

The dashboard will run on `http://localhost:3000` (or 3001 if 3000 is in use)

### 3. **Access the System**

- **Backend API**: https://military-hierarchy-backend.onrender.com/
- **API Docs**: https://military-hierarchy-backend.onrender.com/docs
- **Dashboard**: http://localhost:3000

## 📋 Features

### Report Types

- **CASEVAC**: Casualty evacuation requests with AI-assisted field completion
- **EOINCREP**: Enemy observation and intelligence reports
- **FRAGO**: Fragmentary orders for tactical changes
- **SITREP**: Situation reports

### AI Capabilities

- **Smart Suggestions**: AI analyzes recent reports to suggest field values
- **Chat Analysis**: Ask questions about reports and get tactical insights
- **Auto-fill**: Intelligent completion of report forms based on context

### Real-time Communication

- **MQTT Integration**: Real-time report delivery from field units
- **Live Updates**: Dashboard updates automatically as new reports arrive
- **Notifications**: Smart alerts for critical situations

## 🛠️ Development

### Backend (FastAPI)

- **File**: `backend.py`
- **Port**: 8000
- **Tech**: FastAPI, SQLite, MQTT, Google Gemini AI

### Frontend (Next.js)

- **Directory**: `mil_dashboard/`
- **Port**: 3000
- **Tech**: Next.js 15, React 19, TailwindCSS, shadcn/ui

### Database

- **Type**: SQLite
- **File**: `military_hierarchy.db`
- **Schema**: See `database_schema.sql`

## 📚 Documentation

- **API Documentation**: `docs/API_DOCUMENTATION.md`
- **Database Schema**: `docs/SCHEMA_DOCUMENTATION.md`
- **Project Structure**: `PROJECT_STRUCTURE.md`
- **Raspberry Pi Setup**: `soldier_assistant/RASPBERRY_PI_DEPLOYMENT.md`

## 🧪 Testing

```bash
# Run backend tests
python tests/test_backend.py

# Test soldier integration
python test_soldier_integration.py
```

## 📝 License

This project is for educational purposes.

---

**Built for Aalto University Defence Project**
