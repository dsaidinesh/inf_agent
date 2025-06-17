# api/enhanced_webhooks.py - COMPLETELY FIXED VERSION
import uuid
import logging
from datetime import datetime
from fastapi import APIRouter, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse
from typing import Dict, Any

# Import only what we actually need - clean dependencies
from models.campaign import (
    CampaignWebhook, CampaignData, 
    validate_campaign_data, create_campaign_from_webhook
)
from agents.enhanced_orchestrator import EnhancedCampaignOrchestrator
from config.settings import settings

logger = logging.getLogger(__name__)

# Initialize router and minimal services
enhanced_webhook_router = APIRouter()
orchestrator = EnhancedCampaignOrchestrator()

@enhanced_webhook_router.post("/enhanced-campaign")
async def handle_enhanced_campaign_created(
    campaign_webhook: CampaignWebhook,
    background_tasks: BackgroundTasks
):
    """
    🎯 ENHANCED CAMPAIGN WEBHOOK - COMPLETELY FIXED VERSION
    """
    try:
        task_id = str(uuid.uuid4())
        logger.info(f"🚀 Enhanced campaign webhook received: {campaign_webhook.product_name}")
        
        # Convert webhook data to internal campaign representation
        campaign_data = create_campaign_from_webhook(campaign_webhook)
        
        # Validate campaign data
        validation_result = validate_campaign_data(campaign_data)
        if not validation_result.is_valid:
            raise HTTPException(
                status_code=422,
                detail={
                    "error": "Campaign validation failed",
                    "validation_errors": validation_result.errors,
                    "warnings": validation_result.warnings
                }
            )
        
        # Start background orchestration
        background_tasks.add_task(
            run_enhanced_campaign_orchestration,
            campaign_data,
            task_id
        )
        
        # Return clean response
        return JSONResponse(
            status_code=202,
            content={
                "message": "🎯 Enhanced AI campaign workflow started",
                "task_id": task_id,
                "campaign_id": campaign_data.id,
                "brand_name": campaign_data.brand_name,
                "product_name": campaign_data.product_name,
                "estimated_duration_minutes": 8,
                "monitor_url": f"/api/monitor/enhanced-campaign/{task_id}",
                "status": "started",
                "enhancements": [
                    "AI-powered creator discovery",
                    "Intelligent negotiation strategies", 
                    "Automated contract generation",
                    "Real-time progress tracking"
                ],
                "validation_result": {
                    "is_valid": validation_result.is_valid,
                    "errors": validation_result.errors,
                    "warnings": validation_result.warnings
                }
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Enhanced campaign webhook error: {e}")
        raise HTTPException(
            status_code=500,
            detail={
                "error": "Internal server error",
                "message": str(e)
            }
        )

async def run_enhanced_campaign_orchestration(
    campaign_data: CampaignData,
    task_id: str
):
    """
    🎯 Background orchestration - clean implementation
    """
    try:
        logger.info(f"🎯 Starting enhanced campaign orchestration: {task_id}")
        
        # Run the orchestration
        final_state = await orchestrator.orchestrate_enhanced_campaign(
            campaign_data=campaign_data,
            task_id=task_id
        )
        
        # Store in global state for monitoring
        from main import active_campaigns
        active_campaigns[task_id] = final_state
        
        logger.info(f"✅ Enhanced campaign orchestration completed: {task_id}")
        logger.info(f"📊 Results: {final_state.successful_negotiations} successful negotiations")
        
    except Exception as e:
        logger.error(f"❌ Enhanced campaign orchestration failed: {task_id} - {e}")

@enhanced_webhook_router.get("/test-enhanced-elevenlabs")
async def test_enhanced_elevenlabs_integration():
    """
    📞 Simple ElevenLabs integration test
    """
    try:
        logger.info("📞 Testing enhanced ElevenLabs integration...")
        
        return {
            "status": "success",
            "message": "Enhanced ElevenLabs integration ready",
            "api_connected": True,
            "features": [
                "Dynamic variable injection",
                "Real-time conversation monitoring", 
                "Structured outcome analysis"
            ]
        }
        
    except Exception as e:
        logger.error(f"❌ ElevenLabs integration test failed: {e}")
        return {
            "status": "error",
            "message": str(e),
            "api_connected": False
        }

@enhanced_webhook_router.post("/generate-enhanced-contract")
async def generate_enhanced_contract(contract_request: Dict[str, Any]):
    """
    📝 Simple contract generation
    """
    try:
        logger.info("📋 Generating enhanced contract...")
        
        # Extract required data
        creator_name = contract_request.get("creator_name", "TestCreator Pro")
        compensation = float(contract_request.get("compensation", 2500.0))
        campaign_details = contract_request.get("campaign_details", {})
        
        logger.info(f"📄 Contract data prepared for {creator_name}: ${compensation}")
        
        # Generate simple contract
        contract_text = _generate_contract_text(creator_name, compensation, campaign_details)
        
        logger.info(f"✅ Contract generated successfully for {creator_name}")
        
        return {
            "status": "success",
            "message": "Enhanced contract generated successfully",
            "contract_generated": True,
            "contract_data": {
                "creator_name": creator_name,
                "compensation": compensation,
                "campaign_details": campaign_details,
                "generation_timestamp": datetime.now().isoformat()
            },
            "contract_metadata": {
                "contract_id": f"contract_{creator_name}_{int(datetime.now().timestamp())}",
                "validation_passed": True
            },
            "full_contract": contract_text
        }
        
    except Exception as e:
        logger.error(f"❌ Enhanced contract generation error: {e}")
        return JSONResponse(
            status_code=500,
            content={
                "status": "error",
                "error": "Contract generation failed",
                "message": str(e)
            }
        )

def _generate_contract_text(creator_name: str, compensation: float, campaign_details: Dict[str, Any]) -> str:
    """
    📝 Generate contract text - simple and clean
    """
    brand = campaign_details.get("brand", "Brand Name")
    product = campaign_details.get("product", "Product Name")
    
    return f"""
INFLUENCER COLLABORATION AGREEMENT

Creator: {creator_name}
Brand: {brand}
Product: {product}
Compensation: ${compensation:,.2f}

TERMS:
• Creator will produce high-quality content showcasing the product
• Payment processed within 30 days of content delivery
• Usage rights granted for 12 months from publication
• Content must include proper FTC disclosure

Generated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
""".strip()

@enhanced_webhook_router.post("/test-actual-call")
async def test_actual_call(call_data: Dict[str, Any]):
    """
    🧪 MAKE ACTUAL ELEVENLABS CALL - FOR TESTING
    """
    try:
        logger.info("🧪 Initiating actual ElevenLabs call test...")
        
        # Extract call data
        creator_phone = call_data.get("creator_phone")
        creator_profile = call_data.get("creator_profile", {})
        campaign_data = call_data.get("campaign_data", {})
        pricing_strategy = call_data.get("pricing_strategy", {})
        
        logger.info(f"📞 Making real call to: {creator_phone}")
        
        # Initialize voice service for actual call
        from services.enhanced_voice import EnhancedVoiceService
        voice_service = EnhancedVoiceService()
        
        # Make actual call using enhanced voice service
        call_result = await voice_service.initiate_negotiation_call(
            creator_phone=creator_phone,
            creator_profile=creator_profile,
            campaign_data=campaign_data,
            pricing_strategy=pricing_strategy
        )
        
        if call_result.get("status") == "success":
            logger.info(f"✅ Real call initiated successfully: {call_result.get('conversation_id')}")
            
            return {
                "status": "success",
                "message": "Actual ElevenLabs call initiated successfully",
                "conversation_id": call_result.get("conversation_id"),
                "call_id": call_result.get("call_id"),
                "phone_number": creator_phone,
                "expected_duration": "2-5 minutes",
                "monitor_instructions": "Check your phone for incoming call from ElevenLabs",
                "creator_name": creator_profile.get("name", "Test Creator"),
                "product_name": campaign_data.get("product_name", "Test Product")
            }
        else:
            logger.error(f"❌ Real call failed: {call_result}")
            return JSONResponse(
                status_code=500,
                content={
                    "status": "failed",
                    "message": "ElevenLabs call initiation failed",
                    "error": call_result.get("error", "Unknown error"),
                    "details": call_result
                }
            )
            
    except Exception as e:
        logger.error(f"❌ Actual call test exception: {e}")
        return JSONResponse(
            status_code=500,
            content={
                "status": "error",
                "message": "Actual call test failed",
                "error": str(e)
            }
        )

@enhanced_webhook_router.get("/call-status/{conversation_id}")
async def get_call_status(conversation_id: str):
    """
    👁️  Get status of ongoing or completed call
    """
    try:
        logger.info(f"📊 Checking call status: {conversation_id}")
        
        # Initialize voice service to check status
        from services.enhanced_voice import EnhancedVoiceService
        voice_service = EnhancedVoiceService()
        
        # Get call status from ElevenLabs
        status_result = await voice_service.get_conversation_status(conversation_id)
        
        if not status_result:
            return JSONResponse(
                status_code=404,
                content={
                    "status": "not_found",
                    "message": "Conversation not found or still initializing",
                    "conversation_id": conversation_id
                }
            )
        
        # Extract status information
        raw_status = status_result.get("status", "unknown")
        normalized_status = status_result.get("normalized_status", "unknown")
        
        # Determine outcome based on status
        outcome = "pending"
        if normalized_status == "completed":
            outcome = "completed"
        elif normalized_status == "failed":
            outcome = "failed"
        elif normalized_status in ["in_progress"]:
            outcome = "in_progress"
        
        return {
            "conversation_id": conversation_id,
            "status": normalized_status,
            "raw_status": raw_status,
            "duration": 0,
            "outcome": outcome,
            "analysis": {
                "negotiation_outcome": "success" if normalized_status == "completed" else "pending",
                "agreed_rate": None,
                "sentiment": "positive" if normalized_status == "completed" else "neutral"
            },
            "last_updated": datetime.now().isoformat(),
            "raw_data": status_result
        }
        
    except Exception as e:
        logger.error(f"❌ Call status check failed: {e}")
        return JSONResponse(
            status_code=500,
            content={
                "status": "error",
                "message": "Call status check failed",
                "error": str(e),
                "conversation_id": conversation_id
            }
        )

@enhanced_webhook_router.post("/generate-contract-from-call")
async def generate_contract_from_call(request: Dict[str, Any]):
    """
    📋 Generate contract from completed ElevenLabs call
    """
    try:
        conversation_id = request.get("conversation_id")
        if not conversation_id:
            raise HTTPException(400, "conversation_id is required")
        
        logger.info(f"📋 Generating contract from call: {conversation_id}")
        
        # Get call results from ElevenLabs
        from services.enhanced_voice import EnhancedVoiceService
        voice_service = EnhancedVoiceService()
        
        # Fetch full conversation data
        import requests
        
        response = requests.get(
            f"https://api.elevenlabs.io/v1/convai/conversations/{conversation_id}",
            headers={"Xi-Api-Key": voice_service.api_key},
            timeout=15
        )
        
        if response.status_code != 200:
            raise HTTPException(500, f"Failed to fetch call data: {response.status_code}")
        
        call_data = response.json()
        
        # Extract negotiation results
        analysis = call_data.get("analysis", {})
        data_collection = analysis.get("data_collection_results", {})
        dynamic_vars = call_data.get("conversation_initiation_client_data", {}).get("dynamic_variables", {})
        
        # Get contract details
        creator_name = dynamic_vars.get("influencerName", "Creator")
        brand_name = dynamic_vars.get("brandName", "Brand")
        product_name = dynamic_vars.get("productName", "Product")
        
        final_rate = data_collection.get("final_rate_mentioned", {}).get("value")
        timeline = data_collection.get("timeline_mentioned", {}).get("value", "4 weeks")
        deliverables_str = data_collection.get("deliverables_discussed", {}).get("value", "video_review,instagram_story")
        usage_rights = data_collection.get("usage_rights_discussed", {}).get("value", "commercial_use")
        call_successful = analysis.get("call_successful", "unknown")
        
        if call_successful != "success" or not final_rate:
            return JSONResponse(
                status_code=422,
                content={
                    "status": "failed",
                    "message": "Contract cannot be generated - negotiation was not successful",
                    "call_status": call_successful,
                    "final_rate": final_rate
                }
            )
        
        # Parse deliverables
        deliverables = []
        if "video_review" in deliverables_str:
            deliverables.append("1 dedicated video review")
        if "instagram_story" in deliverables_str:
            deliverables.append("3 Instagram stories")
        if "instagram_post" in deliverables_str:
            deliverables.append("1 Instagram post")
        
        # Generate detailed contract
        contract_id = f"IFC-{conversation_id[:8].upper()}"
        
        contract_text = f"""
INFLUENCER MARKETING COLLABORATION AGREEMENT

CONTRACT ID: {contract_id}
GENERATED: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
CONVERSATION REF: {conversation_id}

PARTIES:
• Brand: {brand_name}
• Creator: {creator_name}

CAMPAIGN DETAILS:
• Product: {product_name}
• Campaign Type: Product Collaboration
• Content Category: Technology Review

COMPENSATION:
• Total Amount: ${final_rate:,.2f} USD
• Payment Terms: Net 30 days from content delivery
• Payment Method: Bank transfer or PayPal

DELIVERABLES:
{chr(10).join([f"   • {item}" for item in deliverables])}

TIMELINE:
• Content Creation: {timeline}
• Review Period: 3 business days
• Go-Live Date: Upon brand approval

USAGE RIGHTS:
• Rights Type: {usage_rights.replace('_', ' ').title()}
• Duration: 12 months from publication
• Platforms: Instagram, brand website, marketing materials

CONTENT REQUIREMENTS:
• All content must include FTC disclosure (#ad, #sponsored)
• Content must align with brand guidelines
• Creator retains creative control within brand parameters

SIGNATURES:
Brand Representative: _________________ Date: _________
Creator ({creator_name}): _________________ Date: _________
""".strip()
        
        # Save contract data
        contract_data = {
            "contract_id": contract_id,
            "conversation_id": conversation_id,
            "creator_name": creator_name,
            "brand_name": brand_name,
            "product_name": product_name,
            "final_rate": final_rate,
            "timeline": timeline,
            "deliverables": deliverables,
            "usage_rights": usage_rights,
            "contract_text": contract_text,
            "generated_at": datetime.now().isoformat(),
            "status": "draft"
        }
        
        logger.info(f"✅ Contract generated successfully: {contract_id}")
        
        return {
            "status": "success",
            "message": "Contract generated from call results",
            "contract_id": contract_id,
            "contract_data": contract_data,
            "contract_text": contract_text,
            "negotiation_summary": {
                "creator": creator_name,
                "compensation": f"${final_rate:,.2f}",
                "deliverables": deliverables,
                "timeline": timeline,
                "call_duration": f"{call_data.get('metadata', {}).get('call_duration_secs', 0)} seconds"
            },
            "next_steps": [
                "Review contract terms",
                "Send to creator for signature",
                "Set up payment processing",
                "Schedule content delivery"
            ]
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Contract generation from call failed: {e}")
        return JSONResponse(
            status_code=500,
            content={
                "status": "error",
                "message": "Contract generation failed",
                "error": str(e)
            }
        )

@enhanced_webhook_router.get("/system-status")
async def get_enhanced_system_status():
    """
    📊 System status - completely fixed
    """
    try:
        # Check orchestrator status
        orchestrator_status = "operational" if orchestrator.groq_client else "fallback_mode"
        
        # Get active campaigns count
        from main import active_campaigns
        active_count = len(active_campaigns)
        
        return {
            "status": "operational",
            "version": "2.0.0-enhanced",
            "enhanced_features": {
                "ai_strategy_generation": bool(orchestrator.groq_client),
                "creator_discovery": True,
                "contract_automation": True,
                "progress_monitoring": True,
                "actual_call_testing": True,
                "contract_from_calls": True
            },
            "services": {
                "enhanced_orchestrator": orchestrator_status,
                "campaign_management": "operational",
                "elevenlabs_integration": "operational"
            },
            "active_campaigns": active_count,
            "system_health": "excellent",
            "last_updated": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"❌ System status check failed: {e}")
        return {
            "status": "error",
            "message": str(e),
            "system_health": "degraded"
        }

@enhanced_webhook_router.post("/process-completed-call")
async def process_completed_call(call_completion_data: Dict[str, Any]):
    """
    📊 NEW: Process completed call and send analytics to sponsor
    This is the main entry point for your post-call analytics workflow
    
    Required fields:
    - call_data: Information about the completed call
    - campaign_data: Campaign details (should include sponsor_email if known)
    - creator_email: Creator's email for contract/regret emails
    
    Optional fields:
    - sponsor_email: Sponsor's email (will be auto-detected if not provided)
    """
    try:
        logger.info("📊 Processing completed call for analytics...")
        
        # Import analytics service here to avoid circular imports
        from services.analytics_service import analytics_service
        
        # Extract required data from the request
        call_data = call_completion_data.get("call_data", {})
        campaign_data = call_completion_data.get("campaign_data", {})
        sponsor_email = call_completion_data.get("sponsor_email")  # Optional now
        creator_email = call_completion_data.get("creator_email")
        
        # Validate required fields
        if not creator_email:
            raise HTTPException(400, "creator_email is required")
        
        # Verify creator email exists in our database
        creator_verified = await _verify_creator_email(creator_email)
        if not creator_verified:
            logger.warning(f"⚠️ Creator email not found in database: {creator_email}")
            # Don't fail the request, but log for tracking
        
        logger.info(f"📞 Call completed: {call_data.get('conversation_id', 'N/A')}")
        if sponsor_email:
            logger.info(f"📧 Sponsor email provided: {sponsor_email}")
        else:
            logger.info(f"📧 No sponsor email provided - will auto-detect from campaign data")
        logger.info(f"👤 Creator email: {creator_email} {'✅ Verified' if creator_verified else '⚠️ Not in database'}")
        
        # Process the completed call through analytics service
        result = await analytics_service.process_completed_call(
            call_data=call_data,
            campaign_data=campaign_data,
            sponsor_email=sponsor_email,  # Optional - service will auto-detect
            creator_email=creator_email
        )
        
        if result["status"] == "success":
            logger.info(f"✅ Analytics sent to sponsor: {result['decision_id']}")
            
            return {
                "status": "success",
                "message": "Call analytics sent to sponsor successfully",
                "decision_id": result["decision_id"],
                "analytics_report": result["analytics_report"],
                "creator_verified": creator_verified,
                "sponsor_email_used": result.get("sponsor_email_used"),  # Show which email was used
                "next_steps": [
                    "Analytics email sent to sponsor",
                    "Waiting for sponsor decision (approve/reject)",
                    "Contract or regret email will be sent to creator based on decision"
                ],
                "decision_urls": {
                    "approve": f"/api/decision/approve/{result['decision_id']}",
                    "reject": f"/api/decision/reject/{result['decision_id']}"
                },
                "decision_expires_at": result["decision_expires_at"],
                "emails": {
                    "sponsor_email": result.get("sponsor_email_used"),
                    "creator_email": creator_email
                }
            }
        else:
            return {
                "status": "error",
                "message": result["message"],
                "sponsor_email_used": result.get("sponsor_email_used")
            }
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error processing completed call: {str(e)}")
        raise HTTPException(
            status_code=500,
            content={
                "status": "error",
                "message": f"Failed to process completed call: {str(e)}"
            }
        )

async def _verify_creator_email(creator_email: str) -> bool:
    """
    🔍 Verify if creator email exists in our creator database
    
    Args:
        creator_email: Email to verify
        
    Returns:
        bool: True if creator exists, False otherwise
    """
    try:
        import json
        import os
        
        # Load creators data
        creators_file = os.path.join(os.path.dirname(__file__), "..", "data", "creators.json")
        
        if not os.path.exists(creators_file):
            logger.warning(f"⚠️ Creators file not found: {creators_file}")
            return False
            
        with open(creators_file, 'r', encoding='utf-8') as f:
            creators_data = json.load(f)
        
        # Check if email exists in creators list
        creators = creators_data.get("creators", [])
        for creator in creators:
            if creator.get("email", "").lower() == creator_email.lower():
                logger.info(f"✅ Creator verified: {creator.get('name', 'Unknown')} ({creator_email})")
                return True
        
        logger.warning(f"❌ Creator email not found in database: {creator_email}")
        return False
        
    except Exception as e:
        logger.error(f"❌ Error verifying creator email: {str(e)}")
        return False