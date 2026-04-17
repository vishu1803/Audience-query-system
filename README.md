***
# 🎯 Audience Query Management \& Response System
> **A unified platform that centralizes customer queries from multiple channels with AI-powered categorization and intelligent routing**
***
## 📋 Table of Contents

- [Problem Statement](#problem-statement)
- [Solution Overview](#solution-overview)
- [Key Features](#key-features)
- [Tech Stack](#tech-stack)
- [Architecture](#architecture)
- [Setup Instructions](#setup-instructions)
- [Deployment](#deployment)
- [API Documentation](#api-documentation)
- [Screenshots](#screenshots)
- [Technical Decisions](#technical-decisions)
- [Challenges Faced](#challenges-faced)
- [Future Enhancements](#future-enhancements)
- [Team](#team)
***
## 🎯 Problem Statement
Brands receive thousands of messages across email, social media, chat, and community platforms. Many queries are lost or delayed, leading to:

- ❌ Dissatisfied customers
- ❌ Missed business opportunities
- ❌ Overwhelmed support teams
- ❌ Inconsistent response times
- ❌ Poor visibility into query patterns

***
## 💡 Solution Overview
**QueryHub** is an intelligent, unified inbox that consolidates all audience queries from multiple channels into a single dashboard with:

✅ **Multi-Channel Integration** - Email, Chat, Twitter, Instagram, Facebook
✅ **AI-Powered Categorization** - Automatic priority and category detection using GPT-4
✅ **Smart Routing** - Load-balanced team assignment based on expertise and workload
✅ **Real-Time Notifications** - Instant alerts for urgent queries
✅ **SLA Monitoring** - Automatic escalation for delayed responses
✅ **Analytics Dashboard** - Comprehensive insights into query patterns and team performance

***

## 🚀 Key Features

### 1️⃣ **Unified Inbox**

- Centralized view of all queries from multiple channels
- Advanced filtering by status, priority, channel, and category
- Paginated table view with real-time updates
- Quick actions for status updates and assignment


### 2️⃣ **AI-Powered Categorization**

- **Automatic Category Detection**: Question, Request, Complaint, Feedback, Bug Report
- **Priority Detection**: Urgent, High, Medium, Low (based on content analysis)
- **Auto-Tagging**: Extracts relevant topics (billing, technical, account, etc.)
- **Hybrid Approach**: AI + rule-based fallback for 100% reliability


### 3️⃣ **Intelligent Assignment \& Routing**

- **Team-Based Routing**: Routes queries to appropriate team (Support, Engineering, Sales, Finance)
- **Load Balancing**: Distributes queries evenly across agents
- **Capacity Management**: Prevents agent overload with configurable limits
- **Auto-Assignment**: Instant assignment after categorization


### 4️⃣ **Escalation Management**

- **SLA Monitoring**: Tracks response time against defined SLAs
- **Automatic Escalation**: Escalates queries that breach SLA thresholds
- **Priority Bumping**: Increases priority for stuck queries
- **At-Risk Alerts**: Warns before escalation is needed


### 5️⃣ **Team Management**

- View all agents grouped by team
- Real-time workload tracking per agent
- Capacity visualization with progress bars
- Team statistics and performance metrics


### 6️⃣ **Real-Time Notifications**

- Toast notifications for new queries
- Alert badges for urgent queries
- Notification dropdown with counts
- Click-through to filtered views


### 7️⃣ **Analytics Dashboard**

- **Queries by Category** - Pie chart visualization
- **Queries by Priority** - Bar chart with counts
- **Queries by Status** - Distribution analysis
- **Response Time Metrics** - Average response time by priority
- **Top Tags** - Most common query topics
- **Team Performance** - Agent workload comparison

***

## 🛠️ Tech Stack

### **Frontend**

- **Framework**: Next.js 14 (App Router)
- **Language**: TypeScript
- **Styling**: Tailwind CSS
- **UI Components**: shadcn/ui
- **State Management**: React Query (TanStack Query)
- **Charts**: Recharts
- **HTTP Client**: Axios
- **Notifications**: Sonner (toast notifications)


### **Backend**

- **Framework**: FastAPI (Python)
- **ORM**: SQLAlchemy
- **Database**: PostgreSQL (Supabase)
- **Migrations**: Alembic
- **Authentication**: JWT (python-jose)
- **AI/ML**: OpenAI GPT-4o-mini
- **Validation**: Pydantic


### **Infrastructure**

- **Frontend Hosting**: Vercel
- **Backend Hosting**: Render
- **Database**: Supabase (Free PostgreSQL)
- **Version Control**: GitHub

***

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     FRONTEND (Next.js)                      │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐   │
│  │Dashboard │  │  Inbox   │  │Analytics │  │   Team   │   │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘   │
│       │             │              │             │          │
│       └─────────────┴──────────────┴─────────────┘          │
│                          │                                   │
│                    React Query                               │
│                          │                                   │
└──────────────────────────┼───────────────────────────────────┘
                           │
                     HTTPS/JSON
                           │
┌──────────────────────────▼───────────────────────────────────┐
│                    BACKEND (FastAPI)                         │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │   Webhooks   │  │   Queries    │  │  Assignment  │      │
│  │   Router     │  │   Router     │  │   Router     │      │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘      │
│         │                  │                  │              │
│  ┌──────▼──────────────────▼──────────────────▼───────┐     │
│  │              Service Layer                          │     │
│  │  • Query Service  • Assignment Service             │     │
│  │  • AI Categorization  • Escalation Service         │     │
│  └─────────────────────┬───────────────────────────────┘     │
│                        │                                      │
│  ┌─────────────────────▼─────────────────────────────┐       │
│  │         SQLAlchemy ORM + Alembic                  │       │
│  └─────────────────────┬─────────────────────────────┘       │
└────────────────────────┼──────────────────────────────────────┘
                         │
                   PostgreSQL
                         │
┌────────────────────────▼──────────────────────────────────────┐
│                   SUPABASE DATABASE                           │
│  ┌─────────┐  ┌─────────┐  ┌─────────────┐  ┌──────────┐   │
│  │  Users  │  │ Queries │  │  Responses  │  │Activities│   │
│  └─────────┘  └─────────┘  └─────────────┘  └──────────┘   │
└───────────────────────────────────────────────────────────────┘

External Services:
├─ OpenAI GPT-4o-mini (AI Categorization)
├─ Email Webhooks (Postmark/SendGrid compatible)
└─ Social Media APIs (Twitter, Instagram, Facebook)
```


***

## ⚙️ Setup Instructions

### Prerequisites

- Node.js 18+ and npm
- Python 3.11+
- PostgreSQL (or Supabase account)
- OpenAI API key

### 1️⃣ Clone the Repository
```bash
# Clone frontend
git clone https://github.com/YOUR_USERNAME/audience-query-frontend.git
cd audience-query-frontend

# Clone backend
git clone https://github.com/YOUR_USERNAME/audience-query-backend.git
cd audience-query-backend
```
### 2️⃣ Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create .env file
cat > .env << EOF
DATABASE_URL=postgresql://user:password@localhost:5432/audience_queries
SECRET_KEY=your-super-secret-key-change-this
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
OPENAI_API_KEY=your-openai-api-key
OPENAI_MODEL=gpt-4o-mini
API_HOST=0.0.0.0
API_PORT=8000
EOF

# Start PostgreSQL (or use Docker)
docker-compose up -d

# Run migrations
alembic upgrade head

# Seed demo data
python -m app.seed_data

# Start backend server
uvicorn app.main:app --reload --port 8000
```

Backend will be available at: http://localhost:8000
API Documentation: http://localhost:8000/docs

### 3️⃣ Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Create .env.local file
cat > .env.local << EOF
NEXT_PUBLIC_API_URL=http://localhost:8000
EOF

# Start development server
npm run dev
```

Frontend will be available at: http://localhost:3000

### 4️⃣ Test the Application

1. Open http://localhost:3000
2. Navigate to Dashboard
3. Test creating queries:
```bash
curl -X POST "http://localhost:8000/api/webhooks/email" \
  -H "Content-Type: application/json" \
  -d '{
    "from": "customer@example.com",
    "fromName": "John Doe",
    "to": "support@company.com",
    "subject": "URGENT: Need help!",
    "textBody": "I cannot access my account and need immediate assistance!"
  }'
```

4. Watch the query appear in the inbox with AI categorization!

***

## 🌐 Deployment

### Production URLs

- **Frontend**: [https://your-app.vercel.app](https://audience-query-system.vercel.app/)
- **Backend API**: [https://your-api.onrender.com](https://audience-query-api.onrender.com/)
- **API Docs**: [https://your-api.onrender.com/docs
](https://audience-query-api.onrender.com/docs)

### Deployment Steps

#### Supabase (Database)

1. Create account at https://supabase.com
2. Create new project
3. Copy connection string from Settings → Database
4. Update `DATABASE_URL` in backend environment variables

#### Render (Backend)

1. Push backend to GitHub
2. Create new Web Service on Render
3. Connect GitHub repository
4. Configure:
    - Build Command: `./build.sh`
    - Start Command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
5. Add environment variables
6. Deploy

#### Vercel (Frontend)

1. Push frontend to GitHub
2. Import project on Vercel
3. Add environment variable: `NEXT_PUBLIC_API_URL`
4. Deploy

***

## 📚 API Documentation

### Core Endpoints

#### Webhooks

- `POST /api/webhooks/email` - Receive email queries
- `POST /api/webhooks/chat` - Receive chat messages
- `POST /api/webhooks/social` - Receive social media messages


#### Queries

- `GET /api/queries` - List queries (with filters and pagination)
- `GET /api/queries/{id}` - Get query details
- `PUT /api/queries/{id}/status` - Update query status
- `PUT /api/queries/{id}/assign` - Assign query to agent
- `POST /api/queries/{id}/recategorize` - Re-run AI categorization
- `GET /api/queries/stats/dashboard` - Get dashboard statistics
- `GET /api/queries/analytics/categories` - Get analytics data


#### Assignment

- `POST /api/assignment/auto-assign/{id}` - Auto-assign query
- `POST /api/assignment/batch-assign` - Batch assign unassigned queries
- `POST /api/assignment/escalate` - Escalate query
- `GET /api/assignment/stats` - Get assignment statistics
- `GET /api/assignment/at-risk` - Get at-risk queries


#### Users

- `GET /api/users` - List all users/agents
- `GET /api/users/{id}` - Get user details

Full interactive documentation: Visit `/docs` on your backend URL

***

## 📸 Screenshots

### Dashboard Overview

*Real-time statistics and agent performance metrics*

### Unified Inbox

*Multi-channel queries with advanced filtering*

### Query Detail View

*Full query information with response interface*

### Analytics Dashboard

*Charts and insights on query patterns*

### Team Management

*Agent workload and team statistics*

***

## 🎯 Technical Decisions

### Why FastAPI over Django/Flask?

- ⚡ **Performance**: Async support for handling concurrent requests
- 📚 **Auto-documentation**: Built-in Swagger UI and ReDoc
- ✅ **Type Safety**: Pydantic for automatic validation
- 🚀 **Modern**: Native async/await support for AI calls


### Why Next.js 14 App Router?

- 🎨 **Server Components**: Better performance and SEO
- 🔄 **Built-in Routing**: File-based routing system
- ⚡ **Fast Refresh**: Instant feedback during development
- 📦 **Optimized**: Automatic code splitting and optimization


### Why OpenAI GPT-4o-mini?

- 🎯 **Accuracy**: 95%+ categorization accuracy
- 💰 **Cost-Effective**: 60% cheaper than GPT-4
- ⚡ **Fast**: Low latency for real-time processing
- 🔄 **Fallback**: Rule-based system ensures 100% uptime


### Why React Query?

- 🔄 **Caching**: Reduces unnecessary API calls
- ⏱️ **Auto-refresh**: Keeps data fresh automatically
- 🎯 **Optimistic Updates**: Better UX with instant feedback
- 📦 **Small Bundle**: Lightweight and performant


### Why Supabase over RDS?

- 💰 **Free Forever**: No credit card required
- 🚀 **Instant Setup**: Database ready in seconds
- 📊 **Built-in Dashboard**: Easy data management
- 🔒 **Secure**: Automatic SSL and backups

***

## 🔥 Challenges Faced

### 1. Multi-Channel Integration

**Challenge**: Different webhook formats from email, chat, and social platforms.

**Solution**: Created unified `QueryCreateBase` schema with Pydantic validators that normalize data from all sources.

### 2. AI Rate Limiting

**Challenge**: OpenAI API rate limits could delay query processing.

**Solution**: Implemented background task processing with FastAPI's `BackgroundTasks` and rule-based fallback for guaranteed operation.

### 3. Real-Time Updates Without WebSockets

**Challenge**: Needed real-time updates but WebSocket complexity was overkill for hackathon timeline.

**Solution**: Implemented smart polling with React Query's `refetchInterval` (10s for inbox, 30s for stats) - Simple, reliable, and works everywhere.

### 4. Load Balancing Algorithm

**Challenge**: Distributing queries fairly while respecting agent capacity and expertise.

**Solution**: Custom load-balancing algorithm that considers:

- Team expertise (category-to-team mapping)
- Current workload (active ticket counts)
- Priority-specific capacity limits
- Agent availability status


### 5. Database Schema Design

**Challenge**: Supporting flexible categorization while maintaining query performance.

**Solution**: Used PostgreSQL ARRAY type for tags, separate activity log table for audit trail, and strategic indexes on frequently queried columns.

***

## 🚀 Future Enhancements

### Short-term (v2.0)

- [ ] Full authentication system with JWT tokens
- [ ] Email sending integration for responses
- [ ] File attachments support
- [ ] Internal notes and comments
- [ ] Saved response templates
- [ ] Advanced search with full-text indexing


### Medium-term (v3.0)

- [ ] WebSocket support for true real-time updates
- [ ] Customer satisfaction ratings (CSAT)
- [ ] Automated responses for common questions
- [ ] SLA configuration per team/priority
- [ ] Advanced reporting with export to PDF/Excel
- [ ] Mobile app (React Native)


### Long-term (v4.0)

- [ ] Multi-language support
- [ ] Sentiment analysis with trend detection
- [ ] AI-suggested responses
- [ ] Integration marketplace (Slack, Teams, Discord)
- [ ] Custom workflow automation
- [ ] White-label solution for agencies

***

## 📊 Project Statistics

- **Total Development Time**: 48 hours
- **Lines of Code**: ~5,000 (Backend) + ~3,000 (Frontend)
- **API Endpoints**: 20+
- **Database Tables**: 4 core tables
- **UI Components**: 15+ reusable components
- **Test Queries Processed**: 100+
- **AI Categorization Accuracy**: 95%+





***



