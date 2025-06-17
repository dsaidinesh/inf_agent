# 🎯 Campaign Trigger API Guide

## Overview

The Campaign Trigger API allows you to automatically fetch creator data from your Supabase database and trigger AI phone calls based on just a **campaign ID**. This is perfect for automating your influencer outreach workflow.

## Quick Start

### 1. Setup Sample Data (First Time Only)
```bash
python setup_sample_data.py
```
This creates sample campaigns and creators in your Supabase database.

### 2. Start the Server
```bash
python main.py
```

### 3. Test the Endpoints
```bash
python test_campaign_trigger.py
```

## API Endpoints

### 📋 List Available Campaigns
```http
GET /api/campaign-trigger/campaigns?status=active&limit=20
```

**Response:**
```json
{
  "campaigns": [
    {
      "id": "tech_campaign_001",
      "product_name": "TechPro Wireless Earbuds",
      "brand_name": "AudioMax Technologies",
      "product_niche": "tech",
      "total_budget": 15000.0,
      "status": "active",
      "sponsor_email": "sponsor@audiomax-tech.com",
      "trigger_url": "/api/campaign-trigger/trigger/tech_campaign_001"
    }
  ]
}
```

### 🔍 Discover Creators for Campaign
```http
GET /api/campaign-trigger/discover/{campaign_id}?max_results=10&min_followers=100000&max_rate=10000
```

**Example:**
```bash
curl "http://localhost:8000/api/campaign-trigger/discover/tech_campaign_001?max_results=5"
```

**Response:**
```json
{
  "campaign_id": "tech_campaign_001",
  "campaign_name": "AudioMax Technologies - TechPro Wireless Earbuds",
  "total_budget": 15000.0,
  "product_niche": "tech",
  "creators_found": 2,
  "creators": [
    {
      "id": "creator_tech_001",
      "name": "TechReviewer_Sarah",
      "email": "sarah.tech@example.com",
      "phone": "+1-555-TECH-001",
      "platform": "YouTube",
      "niche": "tech",
      "followers": 850000,
      "engagement_rate": 4.8,
      "typical_rate": 5500,
      "match_score": 0.85
    }
  ],
  "next_step": "Use POST /api/campaign-trigger/trigger/tech_campaign_001 to start calls"
}
```

### 🎯 **MAIN ENDPOINT: Trigger AI Calls**
```http
POST /api/campaign-trigger/trigger/{campaign_id}?max_creators=5&call_priority=high_match&force_refresh=false
```

**Example:**
```bash
curl -X POST "http://localhost:8000/api/campaign-trigger/trigger/tech_campaign_001?max_creators=3"
```

**Response:**
```json
{
  "message": "🎯 Campaign calls initiated successfully",
  "task_id": "abc123-def456-ghi789",
  "campaign_id": "tech_campaign_001",
  "creators_found": 2,
  "calls_initiated": 2,
  "estimated_duration_minutes": 6,
  "monitor_url": "/api/campaign-trigger/monitor/abc123-def456-ghi789",
  "creator_details": [
    {
      "id": "creator_tech_001",
      "name": "TechReviewer_Sarah",
      "phone": "+1-555-TECH-001",
      "typical_rate": 5500,
      "match_score": 0.85
    }
  ],
  "next_steps": [
    "AI agents will call each creator automatically",
    "Negotiations will be conducted by AI",
    "Results will be sent to sponsor for approval",
    "Monitor progress using the monitor_url"
  ]
}
```

### 📊 Monitor Campaign Progress
```http
GET /api/campaign-trigger/monitor/{task_id}
```

**Example:**
```bash
curl "http://localhost:8000/api/campaign-trigger/monitor/abc123-def456-ghi789"
```

**Response:**
```json
{
  "task_id": "abc123-def456-ghi789",
  "campaign_id": "tech_campaign_001",
  "status": "negotiations",
  "progress_percentage": 60.0,
  "total_calls": 2,
  "completed_calls": 1,
  "successful_negotiations": 1,
  "call_status": [
    {
      "creator_id": "creator_tech_001",
      "creator_name": "TechReviewer_Sarah",
      "phone_number": "+1-555-TECH-001",
      "call_status": "completed",
      "call_id": "conv_12345",
      "final_rate": 5200,
      "call_duration": 280
    }
  ],
  "estimated_completion": "2024-12-14 15:30:00"
}
```

## Complete Workflow Example

### Python Code Example
```python
import requests
import time

base_url = "http://localhost:8000"

# 1. List available campaigns
response = requests.get(f"{base_url}/api/campaign-trigger/campaigns")
campaigns = response.json()["campaigns"]
print(f"Found {len(campaigns)} campaigns")

# 2. Pick a campaign
campaign_id = campaigns[0]["id"]
print(f"Using campaign: {campaign_id}")

# 3. Preview creators (optional)
response = requests.get(f"{base_url}/api/campaign-trigger/discover/{campaign_id}")
creators = response.json()["creators"]
print(f"Found {len(creators)} matching creators")

# 4. Trigger AI calls
response = requests.post(f"{base_url}/api/campaign-trigger/trigger/{campaign_id}?max_creators=3")
task_data = response.json()
task_id = task_data["task_id"]
print(f"Triggered calls! Task ID: {task_id}")

# 5. Monitor progress
while True:
    response = requests.get(f"{base_url}/api/campaign-trigger/monitor/{task_id}")
    data = response.json()
    
    print(f"Status: {data['status']} | Progress: {data['progress_percentage']:.1f}%")
    
    if data["status"] in ["completed", "failed"]:
        print(f"Campaign finished! Successful negotiations: {data['successful_negotiations']}")
        break
    
    time.sleep(10)  # Wait 10 seconds before checking again
```

### cURL Commands
```bash
# 1. List campaigns
curl "http://localhost:8000/api/campaign-trigger/campaigns"

# 2. Discover creators
curl "http://localhost:8000/api/campaign-trigger/discover/tech_campaign_001"

# 3. Trigger calls
curl -X POST "http://localhost:8000/api/campaign-trigger/trigger/tech_campaign_001?max_creators=3"

# 4. Monitor progress (use task_id from step 3)
curl "http://localhost:8000/api/campaign-trigger/monitor/YOUR_TASK_ID"
```

## Parameters Explained

### Trigger Endpoint Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `max_creators` | int | 5 | Maximum number of creators to call (1-10) |
| `call_priority` | string | "high_match" | Priority: "high_match", "recent_activity", or "all" |
| `force_refresh` | bool | false | Force new calls even if recent ones exist |

### Discovery Endpoint Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `max_results` | int | 10 | Maximum creators to return (1-50) |
| `min_followers` | int | 1000 | Minimum follower count |
| `max_rate` | float | None | Maximum rate per creator |

## What Happens When You Trigger?

1. **🔍 Campaign Fetch**: System retrieves campaign data from Supabase
2. **👤 Creator Discovery**: Finds matching creators based on campaign niche and requirements
3. **🎯 AI Agent Activation**: Enhanced orchestrator starts calling creators
4. **📞 Phone Calls**: ElevenLabs AI makes actual phone calls to creators
5. **💰 Negotiation**: AI conducts pricing and terms negotiation
6. **📊 Analytics**: Results sent to sponsor for approval
7. **📝 Contract Generation**: Contracts generated for approved deals
8. **📧 Email Notifications**: All parties notified of outcomes

## Sample Campaign IDs

After running `setup_sample_data.py`, you'll have these campaigns:

- **`11111111-2222-3333-4444-555555555555`** - TechPro Wireless Earbuds (Budget: $15,000)
- **`22222222-3333-4444-5555-666666666666`** - FitPro Protein Powder (Budget: $12,000)  
- **`33333333-4444-5555-6666-777777777777`** - GlowUp Skincare Set (Budget: $18,000)

## Database Integration

The system automatically:
- ✅ Fetches campaign data from `campaigns` table
- ✅ Queries matching creators from `creators` table
- ✅ Logs all emails to `email_logs` table
- ✅ Stores sponsor decisions in `sponsor_decisions` table
- ✅ Tracks call results and analytics

## Error Handling

The API includes comprehensive error handling:

- **404**: Campaign or creators not found
- **422**: Invalid parameters
- **500**: Server errors with detailed logs

## Monitoring & Analytics

- Real-time progress tracking
- Individual call status monitoring
- Success rate analytics
- Sponsor approval workflow
- Email delivery tracking

## Next Steps

1. **Setup**: Run `setup_sample_data.py` to populate database
2. **Test**: Use `test_campaign_trigger.py` to verify functionality
3. **Integrate**: Use the API endpoints in your application
4. **Monitor**: Track campaigns using the monitoring endpoints
5. **Scale**: Add more campaigns and creators to your database

## Learning Notes

This system demonstrates several important programming concepts:

- **RESTful API Design**: Clean, intuitive endpoints
- **Database Integration**: Supabase queries and data modeling
- **Background Processing**: Async task execution
- **Error Handling**: Comprehensive exception management
- **Monitoring**: Real-time status tracking
- **Data Validation**: Pydantic models for type safety

The code is designed to be educational, with clear separation of concerns and extensive logging to help you understand each step of the process. 