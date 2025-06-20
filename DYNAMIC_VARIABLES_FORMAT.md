# 🎯 New Dynamic Variables Format for Eleven Labs Integration

## Overview

The Eleven Labs integration has been updated to use a new, more structured format for dynamic variables. This format provides better organization and more comprehensive data to the AI agent during phone calls.

## New Format Structure

The system now sends **4 key variables** to Eleven Labs:

### 1. 🏷️ `InfluencerProfile` (Structured String)
Contains **ALL** comprehensive influencer data in a structured string format with 27+ fields:

```
name: Abhiram | channel: olivia_rodriguez519 | email: abhiram@example.com | phone: +91 9876543210 | platform: Instagram | niche: Fitness | about: Certified personal trainer sharing workout routines and healthy lifestyle tips | specialties: workout_routines, nutrition_tips, fitness_gear_reviews | collaboration_style: Professional and authentic approach | followers: 436K | followers_numeric: 436000 | audience_type: Fitness Enthusiasts | engagement: 4.5% | engagement_numeric: 4.5 | avg_views: 27K | avg_views_numeric: 27000 | demographics: age_18_24: 35; age_25_34: 45; age_35_44: 15; male: 60; female: 40 | performance: brand_safety_score: 9.2; collaboration_rating: 4.8; avg_posting_frequency: 5 posts/week | location: Los Angeles, USA | languages: English, Spanish | collaboration_rate: 5167 | rate_history: 2023: 4800; 2024: 5167 | availability: good | last_campaign: 2024-11-15 | recent_campaigns: Nike (2024-10-15); Protein World (2024-09-20) | creator_tier: macro_influencer | estimated_cpm: $191.37
```

**Complete field breakdown:**
- **Basic Info**: name, channel, email, phone_number
- **Platform & Content**: platform, niche, about, specialties, preferred_collaboration_style  
- **Audience & Performance**: followers (formatted + numeric), audienceType, engagement (formatted + numeric), avgViews (formatted + numeric)
- **Demographics & Insights**: audience_demographics, performance_metrics
- **Location & Languages**: location, languages
- **Business Details**: collaboration_rate, rate_history, availability, last_campaign_date, recent_campaigns
- **Calculated Metrics**: creator_tier, estimated_cpm

### 2. 📋 `campaignBrief` (String)
Detailed campaign information formatted for easy reading:

```
Brand: FitTech Solutions
Product: SmartFit Pro Tracker
Description: Advanced fitness tracking device with AI-powered workout recommendations
Target Audience: Fitness enthusiasts aged 20-35
Campaign Goal: Product launch and brand awareness
Niche: fitness
Content Type: Video review, social media posts
Timeline: 7-14 days
Usage Rights: Organic posts with 6-month brand rights
```

### 3. 💰 `PriceRange` (String)
Budget and pricing information:

```
Initial Offer: $4,500 | Max Budget: $6,000 | Negotiable based on deliverables and timeline
```

### 4. 👤 `influencerName` (String)
Simple name reference for the agent:

```
Abhiram
```

## API Call Format

When making calls to Eleven Labs, the variables are sent in this structure:

```json
{
  "agent_id": "your_agent_id_here",
  "agent_phone_number_id": "your_phone_number_id_here",
  "to_number": "+1234567890",
  "conversation_initiation_client_data": {
    "dynamic_variables": {
      "InfluencerProfile": {
        "name": "Abhiram",
        "channel": "olivia_rodriguez519",
        "niche": "Fitness",
        "about": "Certified personal trainer...",
        "followers": "436K",
        "audienceType": "Fitness Enthusiasts",
        "engagement": "4.5%",
        "avgViews": "27K",
        "location": "Los Angeles, USA",
        "languages": ["English"],
        "collaboration_rate": 5167
      },
      "campaignBrief": "Brand: FitTech Solutions\nProduct: SmartFit Pro Tracker...",
      "PriceRange": "Initial Offer: $4,500 | Max Budget: $6,000 | Negotiable...",
      "influencerName": "Abhiram"
    }
  }
}
```

## Key Improvements

### ✅ Better Organization
- All influencer data is grouped in one JSON object
- Campaign information is clearly structured
- Pricing is presented in a readable format

### ✅ More Comprehensive Data
- Includes audience type, engagement rate, average views
- Location and language information
- Collaboration history and preferences

### ✅ Agent-Friendly Format
- Easy for AI agent to parse and reference
- Clear separation of different data types
- Consistent naming conventions

## Implementation Details

### Files Modified
- `services/enhanced_voice.py` - Updated `_generate_dynamic_variables()` method
- Both `_prepare_dynamic_variables()` and `_generate_dynamic_variables()` now use the same format

### Backward Compatibility
- The system automatically converts existing creator profile data to the new format
- No changes needed to existing campaign or creator data structures
- All existing API endpoints continue to work

## Testing

The new format has been tested and verified with:
- ✅ Sample influencer data matching your requirements
- ✅ Comprehensive campaign information
- ✅ Realistic pricing strategies
- ✅ All 4 required variables are properly generated

## Usage in Your Eleven Labs Agent

Configure your Eleven Labs agent to expect these 4 variables:

1. **InfluencerProfile** - Access influencer details like `{{InfluencerProfile.name}}`, `{{InfluencerProfile.followers}}`, etc.
2. **campaignBrief** - Reference complete campaign details with `{{campaignBrief}}`
3. **PriceRange** - Use pricing information with `{{PriceRange}}`
4. **influencerName** - Quick name reference with `{{influencerName}}`

This structured approach will give your AI agent maximum context for successful influencer negotiations! 