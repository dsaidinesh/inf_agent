# 📝 Outreach Logging System Guide

## 🎯 Overview

Your InfluencerFlow AI platform now automatically logs all influencer discovery and outreach activities to the **Supabase database**! Every time the agent discovers influencers, it creates detailed records in the `outreach_logs` table with campaign ID, influencer ID, and conversation ID.

## ✅ What's Been Added

### 🔧 New Components

#### 📝 OutreachLoggerService (`services/outreach_logger.py`)
- **Automatic logging** when influencers are discovered
- **Campaign tracking** with campaign IDs
- **Influencer tracking** with creator IDs  
- **Conversation tracking** with unique conversation IDs
- **Status updates** for ongoing outreach activities
- **Rich metadata** including similarity scores, estimated rates, and creator details

#### 🔗 Integration Points
- **Enhanced Orchestrator** - Logs discovery in `_run_discovery_phase`
- **Streaming Orchestrator** - Logs discovery with real-time updates
- **Regular Orchestrator** - Logs discovery in `_run_discovery_phase`
- **Discovery Agent** - Logs discovery in `find_matches` method

## 🗄️ Database Schema

### outreach_logs Table Structure

The system uses your existing `outreach_logs` table with these key fields:

```sql
-- Core Identifiers
id (UUID) - Unique log entry ID
campaign_id (UUID) - Links to campaigns table
creator_id (UUID) - Links to creators table  
conversation_id (TEXT) - Unique conversation identifier

-- Activity Details
channel (TEXT) - "discovery", "voice", "email", etc.
message_type (TEXT) - "influencer_discovery", "call_attempt", etc.
status (TEXT) - "discovered", "contacted", "responded", etc.
content (JSONB) - Rich metadata and details
timestamp (TIMESTAMPTZ) - When the activity occurred
```

### Content Structure

The `content` field contains rich JSON data:

```json
{
  "discovery_method": "ai_matching",
  "similarity_score": 0.85,
  "estimated_rate": 3000,
  "match_reasons": ["Good niche alignment", "Budget compatible"],
  "creator_details": {
    "name": "TechReviewer_Sarah",
    "email": "sarah.tech@example.com",
    "platform": "YouTube",
    "followers": 500000,
    "niche": "tech",
    "engagement_rate": 4.2
  }
}
```

## 🚀 How It Works

### 1. Automatic Discovery Logging

When influencers are discovered, the system automatically:

```python
# In orchestrator discovery phase
discovered = await self.discovery_agent.discover_influencers(
    product_niche=state.campaign_data.product_niche,
    total_budget=state.campaign_data.total_budget
)

# 📝 NEW: Automatic logging
await outreach_logger.log_influencer_discovery(
    campaign_id=state.campaign_id,
    discovered_influencers=discovered
)
```

### 2. Conversation ID Generation

Each discovery creates unique conversation IDs:
```
Format: conv_{campaign_id}_{creator_id}_{timestamp}
Example: conv_CAMP123_CREATOR456_1703123456
```

### 3. Rich Metadata Capture

For each discovered influencer, the system logs:
- **Discovery details**: Method, similarity score, match reasons
- **Creator profile**: Name, email, platform, followers, niche
- **Campaign context**: Estimated rate, budget compatibility
- **Timing**: Exact timestamp of discovery

## 🔧 Usage Examples

### Basic Query - Get Campaign Outreach Logs

```python
from services.outreach_logger import outreach_logger

# Get all outreach activities for a campaign
logs = await outreach_logger.get_outreach_logs_for_campaign("your-campaign-id")

for log in logs:
    creator_name = log['content']['creator_details']['name']
    status = log['status']
    print(f"{creator_name}: {status}")
```

### Manual Outreach Logging

```python
# Log a specific outreach attempt
await outreach_logger.log_outreach_attempt(
    campaign_id="your-campaign-id",
    creator_id="creator-id", 
    channel="voice",
    message_type="call_attempt",
    status="initiated",
    additional_data={
        "phone_number": "+91 7013543557",
        "attempt_number": 1,
        "notes": "First contact attempt"
    }
)
```

### Update Outreach Status

```python
# Update the status of an ongoing outreach
await outreach_logger.update_outreach_status(
    conversation_id="conv_CAMP123_CREATOR456_1703123456",
    new_status="contacted",
    additional_data={
        "response_received": True,
        "next_action": "send_follow_up"
    }
)
```

## 📊 Analytics & Monitoring

### Campaign Outreach Analytics

```python
# Get comprehensive campaign analytics
logs = await outreach_logger.get_outreach_logs_for_campaign(campaign_id)

# Count by status
status_counts = {}
for log in logs:
    status = log['status']
    status_counts[status] = status_counts.get(status, 0) + 1

print(f"Discovered: {status_counts.get('discovered', 0)}")
print(f"Contacted: {status_counts.get('contacted', 0)}")
print(f"Responded: {status_counts.get('responded', 0)}")
```

### Influencer Discovery Rates

```sql
-- SQL query for discovery analytics
SELECT 
    c.product_name,
    c.product_niche,
    COUNT(*) as influencers_discovered,
    AVG((ol.content->>'similarity_score')::float) as avg_similarity,
    AVG((ol.content->>'estimated_rate')::float) as avg_estimated_rate
FROM outreach_logs ol
JOIN campaigns c ON ol.campaign_id = c.id
WHERE ol.message_type = 'influencer_discovery'
GROUP BY c.product_name, c.product_niche
ORDER BY influencers_discovered DESC;
```

### Real-time Monitoring Dashboard

```python
# Monitor recent outreach activities
recent_logs = await supabase_db.supabase.table("outreach_logs") \
    .select("*") \
    .order("timestamp", desc=True) \
    .limit(10) \
    .execute()

for log in recent_logs.data:
    creator_name = log['content']['creator_details']['name']
    campaign_id = log['campaign_id']
    timestamp = log['timestamp']
    print(f"{timestamp}: {creator_name} - Campaign {campaign_id}")
```

## 🧪 Testing Your Setup

### 1. Run the Test Script

```bash
# Test the outreach logging functionality
python test_outreach_logging.py
```

Expected output:
```
🧪 Testing Outreach Logging Functionality
✅ Outreach logger service initialized with Supabase connection
✅ Successfully logged influencer discovery
✅ Found 2 outreach logs for test campaign
🎉 All outreach logging tests PASSED!
```

### 2. Test with Real Campaign

```bash
# Test with a real campaign trigger
python test_campaign_trigger.py
```

This will:
1. Discover influencers for a test campaign
2. Automatically log discoveries to outreach_logs
3. Show the logged data in your Supabase dashboard

### 3. Verify in Supabase Dashboard

1. Go to your Supabase dashboard
2. Navigate to Table Editor > outreach_logs
3. Filter by recent timestamps
4. Verify you see discovery logs with rich content

## 🔍 Troubleshooting

### Common Issues

#### 1. No Logs Appearing
```
⚠️ Supabase not available - outreach logging disabled
```
**Solution**: Check Supabase connection in `config/settings.py`

#### 2. Empty Content Field
```json
{"content": {}}
```
**Solution**: Ensure CreatorMatch objects have all required fields

#### 3. Missing Conversation IDs
```
conversation_id: null
```
**Solution**: Check conversation ID generation logic in `log_influencer_discovery`

### Debug Mode

Enable detailed logging:
```python
import logging
logging.basicConfig(level=logging.DEBUG)

# Run discovery with debug logging
discovered = await discovery_agent.find_matches(campaign_data)
```

### Manual Database Check

```sql
-- Check recent outreach logs
SELECT 
    ol.id,
    ol.campaign_id,
    ol.creator_id,
    ol.conversation_id,
    ol.status,
    ol.message_type,
    ol.content->>'creator_details'->>'name' as creator_name,
    ol.timestamp
FROM outreach_logs ol
WHERE ol.timestamp > NOW() - INTERVAL '1 hour'
ORDER BY ol.timestamp DESC;
```

## 🚀 Advanced Features

### 1. Custom Event Logging

```python
# Log custom outreach events
await outreach_logger.log_outreach_attempt(
    campaign_id=campaign_id,
    creator_id=creator_id,
    channel="custom",
    message_type="linkedin_message",
    status="sent",
    additional_data={
        "platform": "LinkedIn",
        "message_template": "initial_outreach_v2",
        "personalization_score": 0.85
    }
)
```

### 2. Bulk Status Updates

```python
# Update multiple outreach statuses
conversation_ids = ["conv_1", "conv_2", "conv_3"]

for conv_id in conversation_ids:
    await outreach_logger.update_outreach_status(
        conversation_id=conv_id,
        new_status="follow_up_needed",
        additional_data={"batch_update": True}
    )
```

### 3. Campaign Performance Tracking

```python
# Track campaign progression
campaign_logs = await outreach_logger.get_outreach_logs_for_campaign(campaign_id)

stages = {
    "discovered": 0,
    "contacted": 0, 
    "responded": 0,
    "negotiating": 0,
    "contracted": 0
}

for log in campaign_logs:
    status = log['status']
    if status in stages:
        stages[status] += 1

# Calculate funnel metrics
discovery_to_contact = stages['contacted'] / stages['discovered'] * 100
contact_to_response = stages['responded'] / stages['contacted'] * 100
print(f"Discovery → Contact: {discovery_to_contact:.1f}%")
print(f"Contact → Response: {contact_to_response:.1f}%")
```

## 📈 Benefits

### For Campaign Management
- **Complete audit trail** of all outreach activities
- **Performance tracking** across campaigns and influencers
- **Data-driven optimization** of outreach strategies

### For Analytics
- **Rich metadata** for similarity scores and match reasons
- **Time-series analysis** of discovery patterns
- **Conversion funnel** from discovery to contract

### For Compliance
- **Full documentation** of all influencer interactions
- **Timestamp tracking** for regulatory requirements
- **Status tracking** for follow-up obligations

## 🎯 Next Steps

1. **Monitor your dashboard** to see outreach logs appearing automatically
2. **Build custom analytics** using the rich metadata
3. **Set up alerts** for important status changes
4. **Integrate with other tools** using the conversation IDs
5. **Scale your outreach** with confidence in complete tracking

Your influencer AI agent now provides **complete visibility** into every step of the outreach process! 🚀 