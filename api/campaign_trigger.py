# api/campaign_trigger.py
"""
🎯 Campaign Trigger API - Fetch creators from Supabase and trigger AI calls
This module provides endpoints that take a campaign ID, fetch associated creators 
from the database, and automatically trigger AI agent calls.
"""

import uuid
import logging
from datetime import datetime
from typing import List, Dict, Any, Optional
from fastapi import APIRouter, HTTPException, BackgroundTasks, Query
from fastapi.responses import JSONResponse, StreamingResponse
from pydantic import BaseModel
import json
import asyncio
from typing import AsyncGenerator

from services.supabase_database import SupabaseDatabaseService
from services.enhanced_voice import EnhancedVoiceService
from agents.enhanced_orchestrator import EnhancedCampaignOrchestrator
from models.campaign import CampaignData, Creator, Platform, Availability
from config.settings import settings

logger = logging.getLogger(__name__)

# Initialize router and services
campaign_trigger_router = APIRouter()
db_service = SupabaseDatabaseService()
voice_service = EnhancedVoiceService()
orchestrator = EnhancedCampaignOrchestrator()

# ================================
# REQUEST/RESPONSE MODELS
# ================================

class CampaignTriggerRequest(BaseModel):
    """Request to trigger calls for a campaign"""
    campaign_id: str
    force_refresh: bool = False  # If True, ignores recent calls and makes new ones
    max_creators: int = 5       # Maximum number of creators to call
    call_priority: str = "high_match"  # high_match, recent_activity, or all

class CampaignTriggerResponse(BaseModel):
    """Response from campaign trigger"""
    task_id: str
    campaign_id: str
    creators_found: int
    calls_initiated: int
    estimated_duration_minutes: int
    monitor_url: str
    creator_details: List[Dict[str, Any]]

class CreatorCallStatus(BaseModel):
    """Status of individual creator call"""
    creator_id: str
    creator_name: str
    phone_number: str
    call_status: str
    call_id: Optional[str] = None
    estimated_call_time: Optional[str] = None

# ================================
# MAIN TRIGGER ENDPOINTS
# ================================

@campaign_trigger_router.post("/trigger/{campaign_id}")
async def trigger_campaign_calls(
    campaign_id: str,
    background_tasks: BackgroundTasks,
    force_refresh: bool = Query(False, description="Force new calls even if recent ones exist"),
    max_creators: int = Query(5, description="Maximum creators to call", ge=1, le=10),
    call_priority: str = Query("high_match", description="Priority: high_match, recent_activity, or all")
):
    """
    🎯 MAIN ENDPOINT: Trigger AI calls for a campaign
    
    This endpoint:
    1. Fetches campaign data from Supabase by ID
    2. Finds associated creators for the campaign 
    3. Triggers AI phone calls to matching creators
    4. Returns tracking information for monitoring
    """
    try:
        task_id = str(uuid.uuid4())
        logger.info(f"🚀 Triggering campaign calls: {campaign_id}")
        
        # 1. Fetch campaign data from database
        campaign_data = await _fetch_campaign_data(campaign_id)
        if not campaign_data:
            raise HTTPException(
                status_code=404,
                detail=f"Campaign not found: {campaign_id}"
            )
        
        # 2. Find creators for this campaign
        creators = await _fetch_campaign_creators(
            campaign_id, 
            campaign_data,
            max_creators,
            call_priority,
            force_refresh
        )
        
        if not creators:
            # Handle gracefully when no creators are found
            logger.warning(f"⚠️ No creators found for campaign {campaign_id}")
            return JSONResponse(
                status_code=200,  # Use 200 instead of 404 to provide helpful information
                content={
                    "message": "⚠️ No eligible creators found for this campaign",
                    "campaign_id": campaign_id,
                    "campaign_name": f"{campaign_data.brand_name} - {campaign_data.product_name}",
                    "creators_found": 0,
                    "calls_initiated": 0,
                    "reason": "No creators match the campaign criteria",
                    "suggestions": [
                        "Try expanding the search criteria",
                        "Check if the product niche matches available creators",
                        "Consider increasing the max_creators parameter",
                        "Review the call_priority setting",
                        "Add more creators to the database for this niche"
                    ],
                    "debug_info": {
                        "product_niche": campaign_data.product_niche,
                        "search_parameters": {
                            "max_creators": max_creators,
                            "call_priority": call_priority,
                            "force_refresh": force_refresh
                        }
                    },
                    "next_steps": [
                        "Use GET /api/campaign-trigger/discover/{campaign_id} to see available creators",
                        "Add more creators with matching niches to the database",
                        "Modify campaign criteria if possible"
                    ]
                }
            )
        
        # 3. Start background task to make calls
        background_tasks.add_task(
            _execute_campaign_calls,
            task_id,
            campaign_data,
            creators,
            call_priority
        )
        
        # 4. Prepare response
        creator_details = [
            {
                "id": creator.id,
                "name": creator.name,
                "email": creator.email,
                "phone": creator.phone_number,
                "niche": creator.niche,
                "followers": creator.followers,
                "typical_rate": creator.typical_rate,
                "match_score": getattr(creator, 'match_score', 0.8)
            }
            for creator in creators
        ]
        
        response = CampaignTriggerResponse(
            task_id=task_id,
            campaign_id=campaign_id,
            creators_found=len(creators),
            calls_initiated=len(creators),
            estimated_duration_minutes=len(creators) * 3,  # ~3 min per call
            monitor_url=f"/api/campaign-trigger/monitor/{task_id}",
            creator_details=creator_details
        )
        
        logger.info(f"✅ Campaign calls triggered successfully: {task_id}")
        logger.info(f"📞 Calling {len(creators)} creators for campaign {campaign_id}")
        
        return JSONResponse(
            status_code=202,
            content={
                "message": "🎯 Campaign calls initiated successfully",
                "task_id": task_id,
                "campaign_id": campaign_id,
                "creators_found": len(creators),
                "calls_initiated": len(creators),
                "estimated_duration_minutes": len(creators) * 3,
                "monitor_url": f"/api/campaign-trigger/monitor/{task_id}",
                "creator_details": creator_details,
                "next_steps": [
                    "AI agents will call each creator automatically",
                    "Negotiations will be conducted by AI",
                    "Results will be sent to sponsor for approval",
                    "Monitor progress using the monitor_url"
                ]
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Campaign trigger failed: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to trigger campaign calls: {str(e)}"
        )

@campaign_trigger_router.get("/trigger/{campaign_id}/stream")
async def trigger_campaign_calls_with_streaming(
    campaign_id: str,
    force_refresh: bool = Query(False, description="Force new calls even if recent ones exist"),
    max_creators: int = Query(5, description="Maximum creators to call", ge=1, le=10),
    call_priority: str = Query("high_match", description="Priority: high_match, recent_activity, or all")
):
    """
    🎯 STREAMING VERSION: Trigger AI calls for a campaign with real-time updates
    
    This endpoint does the same as /trigger/{campaign_id} but streams real-time updates
    using Server-Sent Events (SSE) so you can watch the campaign progress live.
    
    Usage:
    - Browser: EventSource('http://localhost:8000/api/campaign-trigger/trigger/{campaign_id}/stream')
    - curl: curl http://localhost:8000/api/campaign-trigger/trigger/{campaign_id}/stream
    """
    logger.info(f"🎯 Triggering streaming campaign calls: {campaign_id}")
    
    return StreamingResponse(
        _stream_campaign_execution(campaign_id, force_refresh, max_creators, call_priority),
        media_type="text/plain",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Content-Type": "text/plain; charset=utf-8"
        }
    )

@campaign_trigger_router.get("/monitor/{task_id}")
async def monitor_campaign_calls(task_id: str):
    """
    📊 Monitor the progress of triggered campaign calls
    """
    try:
        # Check if task exists in active campaigns (from main.py)
        from main import active_campaigns
        
        logger.info(f"🔍 Checking for task: {task_id}")
        logger.info(f"📊 Active campaigns: {list(active_campaigns.keys())}")
        
        if task_id not in active_campaigns:
            raise HTTPException(
                status_code=404,
                detail=f"Task not found: {task_id}"
            )
        
        state = active_campaigns[task_id]
        logger.info(f"📊 Found state for task: {task_id}, stage: {getattr(state, 'current_stage', 'unknown')}")
        
        # Get current status
        call_status = []
        negotiations = getattr(state, 'negotiations', [])
        total_calls = len(negotiations)
        completed_calls = len([n for n in negotiations if getattr(n, 'status', '') == 'completed'])
        
        for negotiation in negotiations:
            call_status.append({
                "creator_id": getattr(negotiation, 'creator_id', 'unknown'),
                "creator_name": getattr(negotiation, 'creator_name', 'Unknown'),
                "phone_number": getattr(negotiation, 'phone_number', 'Unknown'),
                "call_status": getattr(negotiation, 'status', 'unknown'),
                "call_id": getattr(negotiation, 'conversation_id', None),
                "final_rate": getattr(negotiation, 'final_rate', 0),
                "call_duration": getattr(negotiation, 'call_duration_seconds', 0)
            })
        
        progress_percentage = (completed_calls / total_calls * 100) if total_calls > 0 else 0
        
        # Create response data
        response_data = {
            "task_id": task_id,
            "campaign_id": getattr(state, 'campaign_id', 'unknown'),
            "status": getattr(state, 'current_stage', 'unknown'),
            "progress_percentage": round(progress_percentage, 1),
            "total_calls": total_calls,
            "completed_calls": completed_calls,
            "successful_negotiations": getattr(state, 'successful_negotiations', 0),
            "call_status": call_status,
            "started_at": getattr(state, 'created_at', datetime.now()).isoformat(),
            "estimated_completion": _estimate_completion_time(state),
            "last_updated": datetime.now().isoformat(),
            "error_message": getattr(state, 'error_message', None)
        }
        
        logger.info(f"📊 Returning monitoring data for task: {task_id}")
        return response_data
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Monitor task failed: {str(e)}")
        import traceback
        logger.error(f"❌ Traceback: {traceback.format_exc()}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to monitor task: {str(e)}"
        )

# ================================
# CREATOR DISCOVERY ENDPOINTS
# ================================

@campaign_trigger_router.get("/discover/{campaign_id}")
async def discover_creators_for_campaign(
    campaign_id: str,
    max_results: int = Query(10, description="Maximum creators to return", ge=1, le=50),
    min_followers: int = Query(1000, description="Minimum follower count", ge=0),
    max_rate: float = Query(None, description="Maximum rate per creator")
):
    """
    🔍 Discover potential creators for a campaign without triggering calls
    Useful for previewing who would be contacted before actually making calls
    """
    try:
        logger.info(f"🔍 Discovering creators for campaign: {campaign_id}")
        
        # Fetch campaign data
        campaign_data = await _fetch_campaign_data(campaign_id)
        if not campaign_data:
            raise HTTPException(
                status_code=404,
                detail=f"Campaign not found: {campaign_id}"
            )
        
        # Get creators from database matching campaign criteria
        creators = await _discover_creators_for_campaign(
            campaign_data,
            max_results,
            min_followers,
            max_rate
        )
        
        # Format response
        creator_list = []
        for creator in creators:
            creator_info = {
                "id": creator.id,
                "name": creator.name,
                "email": creator.email,
                "phone": creator.phone_number,
                "platform": creator.platform,
                "niche": creator.niche,
                "followers": creator.followers,
                "engagement_rate": creator.engagement_rate,
                "typical_rate": creator.typical_rate,
                "availability": creator.availability,
                "location": creator.location,
                "match_score": getattr(creator, 'match_score', 0.0),
                "estimated_cost": getattr(creator, 'estimated_cost', creator.typical_rate)
            }
            creator_list.append(creator_info)
        
        return {
            "campaign_id": campaign_id,
            "campaign_name": f"{campaign_data.brand_name} - {campaign_data.product_name}",
            "total_budget": campaign_data.total_budget,
            "product_niche": campaign_data.product_niche,
            "creators_found": len(creators),
            "creators": creator_list,
            "discovery_criteria": {
                "max_results": max_results,
                "min_followers": min_followers,
                "max_rate": max_rate,
                "niche_focus": campaign_data.product_niche
            },
            "next_step": f"Use POST /api/campaign-trigger/trigger/{campaign_id} to start calls"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Creator discovery failed: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to discover creators: {str(e)}"
        )

@campaign_trigger_router.get("/campaigns")
async def list_available_campaigns(
    status: str = Query("active", description="Campaign status filter"),
    limit: int = Query(20, description="Number of campaigns to return", ge=1, le=100)
):
    """
    📋 List available campaigns that can be triggered
    """
    try:
        campaigns = await _fetch_available_campaigns(status, limit)
        
        campaign_list = []
        for campaign in campaigns:
            campaign_info = {
                "id": campaign["id"],
                "product_name": campaign["product_name"],
                "brand_name": campaign["brand_name"],
                "product_niche": campaign["product_niche"],
                "total_budget": campaign["total_budget"],
                "status": campaign.get("status", "unknown"),
                "created_at": campaign.get("created_at", ""),
                "sponsor_email": campaign.get("sponsor_email"),
                "trigger_url": f"/api/campaign-trigger/trigger/{campaign['id']}"
            }
            campaign_list.append(campaign_info)
        
        return {
            "campaigns": campaign_list,
            "total_found": len(campaigns),
            "status_filter": status,
            "usage": "Use trigger_url to start AI calls for any campaign"
        }
        
    except Exception as e:
        logger.error(f"❌ List campaigns failed: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to list campaigns: {str(e)}"
        )

# ================================
# HELPER FUNCTIONS
# ================================

async def _fetch_campaign_data(campaign_id: str) -> Optional[CampaignData]:
    """Fetch campaign data from Supabase"""
    try:
        if not db_service.supabase:
            logger.warning("⚠️ Supabase not available, using mock data")
            return _get_mock_campaign_data(campaign_id)
        
        result = db_service.supabase.table("campaigns").select("*").eq("id", campaign_id).execute()
        
        if not result.data:
            return None
        
        campaign_row = result.data[0]
        
        # Convert database row to CampaignData object
        campaign_data = CampaignData(
            id=campaign_row["id"],
            product_name=campaign_row["product_name"],
            brand_name=campaign_row["brand_name"],
            product_description=campaign_row["product_description"],
            target_audience=campaign_row["target_audience"],
            campaign_goal=campaign_row["campaign_goal"],
            product_niche=campaign_row["product_niche"],
            total_budget=campaign_row["total_budget"],
            sponsor_email=campaign_row.get("sponsor_email"),
            sponsor_name=campaign_row.get("sponsor_name"),
            sponsor_phone=campaign_row.get("sponsor_phone")
        )
        
        logger.info(f"✅ Fetched campaign data: {campaign_data.product_name}")
        return campaign_data
        
    except Exception as e:
        logger.error(f"❌ Error fetching campaign data: {str(e)}")
        return None

async def _fetch_campaign_creators(
    campaign_id: str,
    campaign_data: CampaignData,
    max_creators: int,
    call_priority: str,
    force_refresh: bool
) -> List[Creator]:
    """Fetch creators suitable for the campaign from database"""
    try:
        if not db_service.supabase:
            logger.warning("⚠️ Supabase not available, using mock creators")
            return await _get_mock_creators_for_campaign(campaign_data, max_creators)
        
        # Build query based on campaign requirements
        query = db_service.supabase.table("creators").select("*")
        
        # Filter by niche if specified (using flexible matching)
        if campaign_data.product_niche and campaign_data.product_niche.lower() != "general":
            # Try exact match first, then partial match
            campaign_niche_lower = campaign_data.product_niche.lower()
            
            # If campaign niche contains keywords, search for creators with those keywords
            if any(keyword in campaign_niche_lower for keyword in ['tech', 'technology', 'gadget', 'smart']):
                query = query.eq("niche", "tech")
            elif any(keyword in campaign_niche_lower for keyword in ['fitness', 'health', 'workout', 'gym']):
                query = query.eq("niche", "fitness")  
            elif any(keyword in campaign_niche_lower for keyword in ['beauty', 'makeup', 'cosmetics', 'skincare']):
                query = query.eq("niche", "beauty")
            elif any(keyword in campaign_niche_lower for keyword in ['fashion', 'style', 'clothing']):
                query = query.eq("niche", "fashion")
            elif any(keyword in campaign_niche_lower for keyword in ['gaming', 'games', 'esports']):
                query = query.eq("niche", "gaming")
            else:
                # Fall back to partial matching
                query = query.ilike("niche", f"%{campaign_niche_lower.split(',')[0].strip()}%")
        
        # Note: availability column doesn't exist, so we skip this filter
        # query = query.in_("availability", ["good", "excellent", "limited"])
        
        # Order by relevance using available columns
        if call_priority == "high_match":
            query = query.order("engagement_rate", desc=True)
        elif call_priority == "recent_activity":
            # last_campaign_date doesn't exist, fallback to created_at
            query = query.order("created_at", desc=True)
        else:  # all
            query = query.order("followers_count_numeric", desc=True)
        
        # Limit results
        query = query.limit(max_creators)
        
        result = query.execute()
        
        if not result.data:
            logger.warning(f"❌ No creators found for campaign {campaign_id}")
            return []
        
        # Convert database rows to Creator objects
        creators = []
        for creator_row in result.data:
            try:
                creator = Creator(
                    id=creator_row["id"],
                    name=creator_row["name"],
                    email=creator_row.get("email", ""),
                    platform=_safe_platform_conversion(creator_row.get("platform", "youtube")),
                    followers=creator_row.get("followers_count_numeric") or 0,
                    niche=creator_row.get("niche", "general"),
                    typical_rate=float(creator_row.get("collaboration_rate") or creator_row.get("typical_rate") or 1000),
                    engagement_rate=float(creator_row.get("engagement_rate") or 0.0),
                    average_views=int(creator_row.get("avg_views") or creator_row.get("average_views") or 0),
                    last_campaign_date="2024-01-01",  # Default date since column doesn't exist
                    availability=_safe_availability_conversion("good"),  # Default value since column doesn't exist
                    location=creator_row.get("country") or creator_row.get("location") or "Unknown",
                    phone_number=creator_row.get("phone_number", ""),
                    languages=["English"],  # Default since column doesn't exist
                    specialties=[],  # Default since column doesn't exist
                    audience_demographics={},  # Default since column doesn't exist
                    performance_metrics={},  # Default since column doesn't exist
                    recent_campaigns=[],  # Default since column doesn't exist
                    rate_history={},  # Default since column doesn't exist
                    preferred_collaboration_style=""  # Default since column doesn't exist
                )
                creators.append(creator)
                
            except Exception as e:
                logger.error(f"❌ Error parsing creator {creator_row.get('name', 'unknown')}: {str(e)}")
                continue
        
        logger.info(f"✅ Found {len(creators)} creators for campaign {campaign_id}")
        return creators
        
    except Exception as e:
        logger.error(f"❌ Error fetching creators: {str(e)}")
        return []

async def _discover_creators_for_campaign(
    campaign_data: CampaignData,
    max_results: int,
    min_followers: int,
    max_rate: Optional[float]
) -> List[Creator]:
    """Discover creators for campaign preview (without triggering calls)"""
    try:
        if not db_service.supabase:
            return await _get_mock_creators_for_campaign(campaign_data, max_results)
        
        query = db_service.supabase.table("creators").select("*")
        
        # Apply filters using correct column names
        query = query.gte("followers_count_numeric", min_followers)
        
        if max_rate:
            # Use collaboration_rate if available, otherwise skip this filter
            query = query.lte("collaboration_rate", max_rate)
        
        if campaign_data.product_niche and campaign_data.product_niche.lower() != "general":
            # Use the same flexible niche matching
            campaign_niche_lower = campaign_data.product_niche.lower()
            
            if any(keyword in campaign_niche_lower for keyword in ['tech', 'technology', 'gadget', 'smart']):
                query = query.eq("niche", "tech")
            elif any(keyword in campaign_niche_lower for keyword in ['fitness', 'health', 'workout', 'gym']):
                query = query.eq("niche", "fitness")  
            elif any(keyword in campaign_niche_lower for keyword in ['beauty', 'makeup', 'cosmetics', 'skincare']):
                query = query.eq("niche", "beauty")
            elif any(keyword in campaign_niche_lower for keyword in ['fashion', 'style', 'clothing']):
                query = query.eq("niche", "fashion")
            elif any(keyword in campaign_niche_lower for keyword in ['gaming', 'games', 'esports']):
                query = query.eq("niche", "gaming")
            else:
                query = query.ilike("niche", f"%{campaign_niche_lower.split(',')[0].strip()}%")
        
        query = query.order("engagement_rate", desc=True).limit(max_results)
        
        result = query.execute()
        
        # Convert to Creator objects with correct field mapping
        creators = []
        for creator_row in result.data:
            try:
                creator = Creator(
                    id=creator_row["id"],
                    name=creator_row["name"],
                    email=creator_row.get("email", ""),
                    platform=_safe_platform_conversion(creator_row.get("platform", "youtube")),
                    followers=creator_row.get("followers_count_numeric") or 0,
                    niche=creator_row.get("niche", "general"),
                    typical_rate=float(creator_row.get("collaboration_rate") or creator_row.get("typical_rate") or 1000),
                    engagement_rate=float(creator_row.get("engagement_rate") or 0.0),
                    average_views=int(creator_row.get("avg_views") or creator_row.get("average_views") or 0),
                    last_campaign_date="2024-01-01",  # Default date since column doesn't exist
                    availability=_safe_availability_conversion("good"),  # Default value since column doesn't exist
                    location=creator_row.get("country") or creator_row.get("location") or "Unknown",
                    phone_number=creator_row.get("phone_number", ""),
                    languages=["English"],
                    specialties=[],
                    audience_demographics={},
                    performance_metrics={},
                    recent_campaigns=[],
                    rate_history={},
                    preferred_collaboration_style=""
                )
                creators.append(creator)
                
            except Exception as e:
                logger.error(f"❌ Error parsing creator for discovery: {str(e)}")
                continue
        
        return creators
        
    except Exception as e:
        logger.error(f"❌ Error in creator discovery: {str(e)}")
        return []

async def _fetch_available_campaigns(status: str, limit: int) -> List[Dict[str, Any]]:
    """Fetch available campaigns from database"""
    try:
        if not db_service.supabase:
            return _get_mock_campaigns()
        
        query = db_service.supabase.table("campaigns").select("*")
        
        if status != "all":
            query = query.eq("status", status)
        
        query = query.order("created_at", desc=True).limit(limit)
        
        result = query.execute()
        return result.data or []
        
    except Exception as e:
        logger.error(f"❌ Error fetching campaigns: {str(e)}")
        return []

async def _stream_campaign_execution(
    campaign_id: str,
    force_refresh: bool,
    max_creators: int,
    call_priority: str
) -> AsyncGenerator[str, None]:
    """
    Stream campaign execution with real-time updates
    """
    task_id = str(uuid.uuid4())
    
    try:
        # Send initial update
        yield f"data: {json.dumps({
            'message': f'🎯 Starting campaign execution for ID: {campaign_id}',
            'status': 'initializing',
            'timestamp': datetime.now().isoformat(),
            'progress': 0,
            'data': {'task_id': task_id, 'campaign_id': campaign_id}
        })}\n\n"
        
        # 1. Fetch campaign data
        yield f"data: {json.dumps({
            'message': '📊 Fetching campaign data from database...',
            'status': 'fetching_campaign',
            'timestamp': datetime.now().isoformat(),
            'progress': 10
        })}\n\n"
        
        campaign_data = await _fetch_campaign_data(campaign_id)
        if not campaign_data:
            yield f"data: {json.dumps({
                'message': f'❌ Campaign not found: {campaign_id}',
                'status': 'error',
                'timestamp': datetime.now().isoformat(),
                'progress': -1
            })}\n\n"
            return
        
        yield f"data: {json.dumps({
            'message': f'✅ Campaign found: {campaign_data.brand_name} - {campaign_data.product_name}',
            'status': 'campaign_loaded',
            'timestamp': datetime.now().isoformat(),
            'progress': 20,
            'data': {
                'brand_name': campaign_data.brand_name,
                'product_name': campaign_data.product_name,
                'budget': campaign_data.total_budget
            }
        })}\n\n"
        
        # 2. Find creators
        yield f"data: {json.dumps({
            'message': '🔍 Finding creators for this campaign...',
            'status': 'finding_creators',
            'timestamp': datetime.now().isoformat(),
            'progress': 25
        })}\n\n"
        
        creators = await _fetch_campaign_creators(
            campaign_id, 
            campaign_data,
            max_creators,
            call_priority,
            force_refresh
        )
        
        if not creators:
            yield f"data: {json.dumps({
                'message': f'⚠️ No eligible creators found for campaign {campaign_id}',
                'status': 'no_creators',
                'timestamp': datetime.now().isoformat(),
                'progress': 25,
                'data': {
                    'suggestions': [
                        'Try expanding the search criteria',
                        'Check if the product niche matches available creators',
                        'Add more creators to the database for this niche'
                    ]
                }
            })}\n\n"
            return
        
        # Prepare creator details (same format as regular API)
        creator_details = [
            {
                "id": creator.id,
                "name": creator.name,
                "email": creator.email,
                "phone": creator.phone_number,
                "niche": creator.niche,
                "followers": creator.followers,
                "typical_rate": creator.typical_rate,
                "match_score": getattr(creator, 'match_score', 0.8)
            }
            for creator in creators
        ]
        
        yield f"data: {json.dumps({
            'message': f'✅ Found {len(creators)} eligible creators',
            'status': 'creators_found',
            'timestamp': datetime.now().isoformat(),
            'progress': 35,
            'data': {
                'creators_found': len(creators),
                'calls_initiated': len(creators),
                'estimated_duration_minutes': len(creators) * 3,
                'creator_details': creator_details[:3]  # Show first 3 for streaming
            }
        })}\n\n"
        
        # 3. Start the same background task as the regular API, but with streaming updates
        yield f"data: {json.dumps({
            'message': '🚀 Starting campaign execution (same as regular API)...',
            'status': 'starting_execution',
            'timestamp': datetime.now().isoformat(),
            'progress': 40
        })}\n\n"
        
        # Store initial state for monitoring (same as regular API)
        from main import active_campaigns
        from models.campaign import CampaignOrchestrationState
        
        # Create initial state (same as _execute_campaign_calls)
        initial_state = CampaignOrchestrationState(
            campaign_id=campaign_data.id,
            campaign_data=campaign_data,
            current_stage="discovery",
            started_at=datetime.now(),
            estimated_completion_minutes=15
        )
        active_campaigns[task_id] = initial_state
        
        yield f"data: {json.dumps({
            'message': f'📊 Campaign state stored for monitoring: {task_id}',
            'status': 'state_stored',
            'timestamp': datetime.now().isoformat(),
            'progress': 45,
            'data': {'monitor_url': f'/api/campaign-trigger/monitor/{task_id}'}
        })}\n\n"
        
        # Use the enhanced orchestrator (same as _execute_campaign_calls)
        from agents.enhanced_orchestrator import EnhancedCampaignOrchestrator
        orchestrator = EnhancedCampaignOrchestrator()
        
        try:
            yield f"data: {json.dumps({
                'message': '🧠 Initializing enhanced orchestrator...',
                'status': 'orchestrator_init',
                'timestamp': datetime.now().isoformat(),
                'progress': 50
            })}\n\n"
            
            # Start orchestration task (same as background task)
            orchestration_task = asyncio.create_task(
                orchestrator.orchestrate_enhanced_campaign(
                    campaign_data=campaign_data,
                    task_id=task_id
                )
            )
            
            # Monitor progress by checking the active_campaigns state
            last_stage = "discovery"
            stage_progress = {
                "discovery": 55,
                "strategy": 65, 
                "negotiations": 75,
                "contracts": 85,
                "completion": 95,
                "completed": 100,
                "failed": -1
            }
            
            while not orchestration_task.done():
                await asyncio.sleep(2)  # Check every 2 seconds
                
                # Get current state from active_campaigns
                current_state = active_campaigns.get(task_id)
                if current_state:
                    current_stage = getattr(current_state, 'current_stage', 'unknown')
                    
                    # Update when stage changes
                    if current_stage != last_stage:
                        progress = stage_progress.get(current_stage, 50)
                        
                        stage_messages = {
                            "discovery": "🔍 Discovering influencers...",
                            "strategy": "🧠 Generating AI strategy...", 
                            "negotiations": "📞 Conducting negotiations...",
                            "contracts": "📝 Generating contracts...",
                            "completion": "🏁 Finalizing campaign...",
                            "completed": "✅ Campaign completed!",
                            "failed": "❌ Campaign failed"
                        }
                        
                        message = stage_messages.get(current_stage, f"Processing stage: {current_stage}")
                        
                        yield f"data: {json.dumps({
                            'message': message,
                            'status': current_stage,
                            'timestamp': datetime.now().isoformat(),
                            'progress': progress,
                            'data': {
                                'stage': current_stage,
                                'successful_negotiations': getattr(current_state, 'successful_negotiations', 0),
                                'total_cost': getattr(current_state, 'total_cost', 0)
                            }
                        })}\n\n"
                        
                        last_stage = current_stage
                        
                        # Exit if completed or failed
                        if current_stage in ['completed', 'failed']:
                            break
                
                # Timeout after 5 minutes
                elapsed = datetime.now() - initial_state.started_at
                if elapsed.total_seconds() > 300:
                    yield f"data: {json.dumps({
                        'message': '⏰ Operation timeout - taking longer than expected',
                        'status': 'timeout_warning',
                        'timestamp': datetime.now().isoformat(),
                        'progress': 90
                    })}\n\n"
                    break
            
            # Wait for final result
            final_state = await orchestration_task
            
            # Update active_campaigns with final results (same as background task)
            active_campaigns[task_id] = final_state
            
            # Send final completion update (same format as regular API)
            successful_negotiations = getattr(final_state, 'successful_negotiations', 0)
            total_cost = getattr(final_state, 'total_cost', 0)
            total_contracts = len(getattr(final_state, 'contracts', []))
            
            yield f"data: {json.dumps({
                'message': '🎉 Campaign execution completed successfully!',
                'status': 'completed',
                'timestamp': datetime.now().isoformat(),
                'progress': 100,
                'data': {
                    'task_id': task_id,
                    'campaign_id': campaign_id,
                    'creators_found': len(creators),
                    'calls_initiated': len(creators),
                    'successful_negotiations': successful_negotiations,
                    'total_contracts': total_contracts,
                    'total_cost': total_cost,
                    'estimated_duration_minutes': len(creators) * 3,
                    'monitor_url': f'/api/campaign-trigger/monitor/{task_id}',
                    'creator_details': creator_details,
                    'next_steps': [
                        "AI agents completed calling each creator",
                        "Negotiations were conducted by AI",
                        "Results are available for sponsor review",
                        f"Check full results at /api/campaign-trigger/monitor/{task_id}"
                    ]
                }
            })}\n\n"
            
        except Exception as orchestration_error:
            yield f"data: {json.dumps({
                'message': f'❌ Orchestration error: {str(orchestration_error)}',
                'status': 'orchestration_error',
                'timestamp': datetime.now().isoformat(),
                'progress': -1
            })}\n\n"
        
    except Exception as e:
        logger.error(f"❌ Streaming campaign execution failed: {str(e)}")
        yield f"data: {json.dumps({
            'message': f'❌ Campaign execution failed: {str(e)}',
            'status': 'error',
            'timestamp': datetime.now().isoformat(),
            'progress': -1,
            'data': {'error': str(e)}
        })}\n\n"

async def _execute_campaign_calls(
    task_id: str,
    campaign_data: CampaignData,
    creators: List[Creator],
    call_priority: str
):
    """Execute AI calls to creators in background"""
    try:
        logger.info(f"🎯 Starting campaign calls execution: {task_id}")
        
        # Store initial state immediately for monitoring
        from main import active_campaigns
        from models.campaign import CampaignOrchestrationState
        from datetime import datetime
        
        # Create initial state
        initial_state = CampaignOrchestrationState(
            campaign_id=campaign_data.id,
            campaign_data=campaign_data,
            current_stage="discovery",
            started_at=datetime.now(),
            estimated_completion_minutes=15
        )
        active_campaigns[task_id] = initial_state
        logger.info(f"📊 Campaign state stored for monitoring: {task_id}")
        
        # Use the enhanced orchestrator to handle the calls
        from agents.enhanced_orchestrator import EnhancedCampaignOrchestrator
        orchestrator = EnhancedCampaignOrchestrator()
        
        final_state = await orchestrator.orchestrate_enhanced_campaign(
            campaign_data=campaign_data,
            task_id=task_id
        )
        
        # Update with final results
        active_campaigns[task_id] = final_state
        
        logger.info(f"✅ Campaign calls completed: {task_id}")
        logger.info(f"📊 Successful negotiations: {final_state.successful_negotiations}")
        
    except Exception as e:
        logger.error(f"❌ Campaign calls execution failed: {task_id} - {str(e)}")
        # Still keep error state for monitoring
        from main import active_campaigns
        if task_id in active_campaigns:
            state = active_campaigns[task_id]
            state.error_message = str(e)
            state.current_stage = "error"

def _estimate_completion_time(state) -> str:
    """Estimate when the campaign will complete"""
    try:
        total_negotiations = len(getattr(state, 'negotiations', []))
        completed_negotiations = len([n for n in getattr(state, 'negotiations', []) if n.status == 'completed'])
        
        if total_negotiations == 0:
            return "Unknown"
        
        if completed_negotiations == total_negotiations:
            return "Completed"
        
        remaining = total_negotiations - completed_negotiations
        estimated_minutes = remaining * 3  # ~3 minutes per call
        
        completion_time = datetime.now()
        completion_time = completion_time.replace(
            minute=completion_time.minute + estimated_minutes
        )
        
        return completion_time.strftime("%Y-%m-%d %H:%M:%S")
        
    except Exception:
        return "Unknown"

# ================================
# MOCK DATA FUNCTIONS (for testing)
# ================================

def _get_mock_campaign_data(campaign_id: str) -> CampaignData:
    """Get mock campaign data for testing"""
    return CampaignData(
        id=campaign_id,
        product_name="TestPro Device",
        brand_name="TestTech Solutions",
        product_description="Revolutionary testing device for tech enthusiasts",
        target_audience="Tech enthusiasts aged 25-40",
        campaign_goal="Increase product awareness and drive sales",
        product_niche="technology",
        total_budget=10000.0,
        sponsor_email="sponsor@testtech.com",
        sponsor_name="John Smith",
        sponsor_phone="+1234567890"
    )

async def _get_mock_creators_for_campaign(campaign_data: CampaignData, max_creators: int) -> List[Creator]:
    """Get mock creators for testing"""
    mock_creators_data = [
        {
            "id": "sarah_tech_001",
            "name": "TechReviewer_Sarah",
            "email": "sarah.tech@example.com",
            "platform": "YouTube",
            "followers": 500000,
            "niche": "tech",
            "typical_rate": 4500,
            "engagement_rate": 4.2,
            "average_views": 180000,
            "last_campaign_date": "2024-11-15",
            "availability": "good",
            "location": "Mumbai, India",
            "phone_number": "+91 9999999999",  # MOCK DATA PHONE - If you see this, system is using fallback
            "languages": ["English", "Hindi"],
            "specialties": ["smartphone_reviews", "gadget_unboxing"],
            "audience_demographics": {"age_18_24": 35, "age_25_34": 40},
            "performance_metrics": {"brand_safety_score": 9.5},
            "recent_campaigns": [],
            "rate_history": {"2024": 4500},
            "preferred_collaboration_style": "Professional and detail-oriented"
        },
        {
            "id": "mike_fitness_002",
            "name": "FitnessGuru_Mike",
            "email": "mike.fitness@example.com",
            "platform": "Instagram",
            "followers": 300000,
            "niche": "fitness",
            "typical_rate": 3200,
            "engagement_rate": 5.8,
            "average_views": 120000,
            "last_campaign_date": "2024-11-01",
            "availability": "limited",
            "location": "Los Angeles, USA",
            "phone_number": "+91 8888888888",  # MOCK DATA PHONE - If you see this, system is using fallback  
            "languages": ["English", "Spanish"],
            "specialties": ["workout_routines", "supplement_reviews"],
            "audience_demographics": {"age_18_24": 25, "age_25_34": 45},
            "performance_metrics": {"brand_safety_score": 9.8},
            "recent_campaigns": [],
            "rate_history": {"2024": 3200},
            "preferred_collaboration_style": "High-energy and authentic"
        }
    ]
    
    creators = []
    for creator_data in mock_creators_data[:max_creators]:
        try:
            creator = Creator(**creator_data)
            creators.append(creator)
        except Exception as e:
            logger.error(f"❌ Error creating mock creator: {str(e)}")
    
    return creators

def _get_mock_campaigns() -> List[Dict[str, Any]]:
    """Get mock campaigns for testing"""
    return [
        {
            "id": "campaign_001",
            "product_name": "TechPro Earbuds",
            "brand_name": "AudioMax",
            "product_niche": "technology",
            "total_budget": 15000.0,
            "status": "active",
            "created_at": "2024-11-20T10:00:00Z",
            "sponsor_email": "sponsor@audiomax.com"
        },
        {
            "id": "campaign_002",
            "product_name": "FitPro Protein",
            "brand_name": "FitLife",
            "product_niche": "fitness",
            "total_budget": 12000.0,
            "status": "active",
            "created_at": "2024-11-19T15:30:00Z",
            "sponsor_email": "sponsor@fitlife.com"
        }
    ]

def _safe_platform_conversion(platform: str) -> Platform:
    """Convert platform string to Platform enum safely"""
    try:
        # Map common platform values to enum values
        platform_map = {
            "youtube": Platform.YOUTUBE,
            "youtube.com": Platform.YOUTUBE,
            "instagram": Platform.INSTAGRAM,
            "tiktok": Platform.TIKTOK,
            "twitch": Platform.TWITCH,
            "twitch.tv": Platform.TWITCH
        }
        
        platform_lower = platform.lower().strip()
        
        # Try direct mapping first
        if platform_lower in platform_map:
            return platform_map[platform_lower]
        
        # Try enum value directly (capitalized)
        try:
            return Platform(platform.title())
        except ValueError:
            pass
        
        # Default fallback
        logger.warning(f"⚠️ Unknown platform '{platform}', defaulting to YouTube")
        return Platform.YOUTUBE
        
    except Exception as e:
        logger.error(f"❌ Error converting platform '{platform}': {str(e)}")
        return Platform.YOUTUBE

def _safe_availability_conversion(availability: str = "good") -> Availability:
    """Convert availability string to Availability enum safely"""
    try:
        # Map common availability values
        availability_map = {
            "excellent": Availability.EXCELLENT,
            "good": Availability.GOOD,
            "limited": Availability.LIMITED,
            "busy": Availability.BUSY
        }
        
        availability_lower = availability.lower().strip()
        
        if availability_lower in availability_map:
            return availability_map[availability_lower]
        
        # Default to good availability
        return Availability.GOOD
        
    except Exception as e:
        logger.error(f"❌ Error converting availability '{availability}': {str(e)}")
        return Availability.GOOD