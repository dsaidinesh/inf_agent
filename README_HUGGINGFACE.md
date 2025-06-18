# InfluencerFlow AI Platform 🚀

## AI-Powered Influencer Marketing Automation

This is a comprehensive FastAPI-based platform that automates influencer marketing campaigns using AI agents, real-time voice calls, and smart contract generation.

---

## 🎯 **Live Demo Features**

- **🤖 AI Campaign Orchestration**: Automated influencer discovery and outreach
- **📞 Voice-Enabled Negotiations**: Real-time AI phone calls to influencers  
- **📊 Real-Time Streaming**: Live campaign progress monitoring
- **📝 Smart Contract Generation**: Automated contract creation and management
- **💰 Dynamic Pricing**: AI-powered rate negotiations

---

## 🔧 **Quick Start**

### **Live Endpoints:**

#### **🏠 Main Dashboard**
```
GET /
```

#### **📊 Real-Time Campaign Streaming**
```
GET /api/campaign-trigger/trigger/{campaign_id}/stream
```

#### **🎯 Campaign Management**
```
POST /api/campaign-trigger/trigger/{campaign_id}
GET /api/campaign-trigger/monitor/{task_id}
GET /api/campaign-trigger/discover/{campaign_id}
```

#### **📞 Voice & Webhook Integration**
```
POST /api/webhook/elevenlabs
GET /api/monitor/conversations
```

---

## 🎮 **Demo Usage**

### **1. Test Campaign Streaming**
```bash
curl "https://your-space-url/api/campaign-trigger/trigger/11111111-2222-3333-4444-555555555555/stream"
```

### **2. View Available Campaigns** 
```bash
curl "https://your-space-url/api/campaign-trigger/campaigns"
```

### **3. Health Check**
```bash
curl "https://your-space-url/health"
```

---

## 🛠 **Architecture**

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Campaign      │    │   AI Agent      │    │   Voice Service │
│   Trigger API   │───▶│   Orchestrator  │───▶│   (ElevenLabs)  │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Real-time     │    │   Contract      │    │   Email         │
│   Streaming     │    │   Generation    │    │   Notifications │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

---

## 📋 **Core Components**

- **`agents/`**: AI orchestration and campaign management
- **`api/`**: FastAPI routes for triggers, monitoring, webhooks
- **`services/`**: Voice, email, database, and analytics services
- **`models/`**: Data models and campaign structures
- **`frontend_example/`**: Demo HTML interfaces

---

## 🔑 **Environment Configuration**

For full functionality, set these environment variables:

```bash
# Required for AI
GROQ_API_KEY=your_groq_api_key

# Optional for real voice calls
ELEVENLABS_API_KEY=your_elevenlabs_key
ELEVENLABS_AGENT_ID=your_agent_id

# Optional for email notifications  
SENDGRID_API_KEY=your_sendgrid_key

# Optional for database
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_key
```

---

## 🚀 **Demo Mode**

The platform runs in demo mode by default with:
- ✅ Mock voice calls (no ElevenLabs required)
- ✅ Simulated negotiations with realistic outcomes
- ✅ Full streaming and monitoring capabilities  
- ✅ Contract generation and email workflows

---

## 📱 **Frontend Demos**

Access these interactive demos:
- **Campaign Trigger Demo**: `/frontend_example/campaign_trigger_streaming_demo.html`
- **Streaming Logs Demo**: `/frontend_example/streaming_logs_demo.html` 
- **Monitor Dashboard**: `/frontend_example/monitor.html`

---

## 📊 **API Documentation**

Visit `/docs` for complete interactive API documentation with:
- 🔄 Real-time streaming endpoints
- 🎯 Campaign management
- 📞 Voice integration webhooks
- 📊 Analytics and monitoring

---

## 🏗 **Tech Stack**

- **Backend**: FastAPI, Python 3.11+
- **AI/ML**: Groq, OpenAI, Sentence Transformers
- **Voice**: ElevenLabs API integration
- **Database**: Supabase, PostgreSQL
- **Real-time**: Server-Sent Events (SSE)
- **Email**: SendGrid integration
- **Frontend**: HTML5, JavaScript, EventSource

---

## 🛡 **Security & Privacy**

- Environment-based configuration
- Optional API key requirements
- Secure webhook handling
- Privacy-focused demo mode

---

## 🤝 **Contributing**

This is an open-source project. Feel free to:
- Report issues
- Suggest features  
- Submit pull requests
- Fork for your own use

---

## 📄 **License**

MIT License - Feel free to use this for your projects!

---

**🎉 Built for Hugging Face Spaces - Ready to deploy!** 