# services/enhanced_voice.py - COMPLETE FINAL WORKING VERSION
import asyncio
import logging
import requests
import random
import json
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta

from config.settings import settings

logger = logging.getLogger(__name__)

class EnhancedVoiceService:
    """
    🎯 COMPLETE FINAL ELEVENLABS INTEGRATION
    
    All methods properly implemented and working
    """
    
    def __init__(self):
        self.api_key = settings.elevenlabs_api_key
        self.agent_id = settings.elevenlabs_agent_id
        self.phone_number_id = settings.elevenlabs_phone_number_id
        self.base_url = "https://api.elevenlabs.io"
        
        # Optimized timeouts based on ElevenLabs documentation
        self.request_timeout = 30
        self.status_check_timeout = 15
        self.retry_attempts = 3
        self.retry_delay = 2
        
        self.use_mock = not all([self.api_key, self.agent_id, self.phone_number_id])
        
        if self.use_mock:
            logger.warning("⚠️ ElevenLabs credentials incomplete - using mock calls")
        else:
            logger.info("✅ ElevenLabs service initialized with real API")
    
    async def test_credentials(self) -> Dict[str, Any]:
        """Test ElevenLabs API credentials with proper validation"""
        if self.use_mock:
            return {
                "status": "mock_mode",
                "message": "Using mock mode - no real API calls",
                "api_connected": False
            }
        
        try:
            # Test API connectivity with simple request
            response = requests.get(
                f"{self.base_url}/v1/user",
                headers={"Xi-Api-Key": self.api_key},
                timeout=self.status_check_timeout
            )
            
            if response.status_code == 200:
                return {
                    "status": "success",
                    "message": "ElevenLabs API credentials valid",
                    "api_connected": True
                }
            else:
                return {
                    "status": "failed",
                    "message": f"API validation failed: {response.status_code}",
                    "error": response.text[:200],
                    "api_connected": False
                }
                
        except Exception as e:
            return {
                "status": "error",
                "message": f"Credential test failed: {str(e)}",
                "api_connected": False
            }
    
    def _prepare_dynamic_variables(self, creator_profile, campaign_data, pricing_strategy=None):
        """
        🔧 PREPARE DYNAMIC VARIABLES FOR ELEVENLABS
        
        This method prepares all the context data for ElevenLabs agents
        Now uses the new format with InfluencerProfile as JSON object
        """
        
        if pricing_strategy is None:
            pricing_strategy = {"initial_offer": 1000, "max_offer": 1500}
        
        # Use the same format as _generate_dynamic_variables for consistency
        return self._generate_dynamic_variables(creator_profile, campaign_data, pricing_strategy)
    
    async def initiate_negotiation_call(
        self,
        creator_phone: str,
        creator_profile: Dict[str, Any],
        campaign_data: Dict[str, Any],
        pricing_strategy: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        🔥 INITIATE ELEVENLABS CALL - COMPLETE WORKING VERSION
        """
        
        if self.use_mock:
            return await self._mock_enhanced_call(creator_phone, creator_profile, campaign_data)
        
        # Retry logic for network issues
        for attempt in range(self.retry_attempts):
            try:
                logger.info(f"📱 Initiating ElevenLabs call (attempt {attempt + 1})")
                
                # Generate dynamic variables
                dynamic_vars = self._generate_dynamic_variables(
                    creator_profile, campaign_data, pricing_strategy
                )
                
                # Make API call with proper error handling
                response = await self._make_outbound_call_request(
                    creator_phone, dynamic_vars
                )
                
                # Validate response before proceeding
                if response.get("status") == "success":
                    conversation_id = response.get("conversation_id")
                    
                    # Ensure we have conversation_id for contract generation
                    if not conversation_id:
                        raise ValueError("Missing conversation_id in API response")
                    
                    logger.info(f"✅ Call initiated successfully: {conversation_id}")
                    return response
                
                elif attempt < self.retry_attempts - 1:
                    logger.warning(f"⚠️ Call failed, retrying in {self.retry_delay}s...")
                    await asyncio.sleep(self.retry_delay)
                    continue
                else:
                    logger.error(f"❌ All retry attempts failed: {response}")
                    return response
                    
            except Exception as e:
                logger.error(f"❌ Call exception (attempt {attempt + 1}): {e}")
                
                if attempt < self.retry_attempts - 1:
                    await asyncio.sleep(self.retry_delay)
                    continue
                else:
                    # Return error response for contract generation handling
                    return {
                        "status": "failed",
                        "error": str(e),
                        "phone_number": creator_phone,
                        "retry_attempts": self.retry_attempts
                    }
        
        # Fallback should not reach here
        return {
            "status": "failed",
            "error": "Unknown failure after all retries",
            "phone_number": creator_phone
        }
    
    async def _make_outbound_call_request(
        self,
        phone_number: str,
        dynamic_variables: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Make the actual API request with proper validation"""
        
        try:
            # Prepare request payload
            payload = {
                "agent_id": self.agent_id,
                "agent_phone_number_id": self.phone_number_id,
                "to_number": phone_number,
                "conversation_initiation_client_data": {
                    "dynamic_variables": dynamic_variables
                }
            }
            
            # Make request using asyncio for timeout handling
            loop = asyncio.get_event_loop()
            
            def make_request():
                return requests.post(
                    f"{self.base_url}/v1/convai/twilio/outbound-call",
                    headers={"Xi-Api-Key": self.api_key},
                    json=payload,
                    timeout=self.request_timeout
                )
            
            response = await loop.run_in_executor(None, make_request)
            
            # Proper response validation
            if response.status_code == 200:
                try:
                    result = response.json()
                    
                    # Validate required fields for contract generation
                    if "conversation_id" not in result:
                        logger.error("❌ Missing conversation_id in successful response")
                        return {
                            "status": "failed",
                            "error": "Missing conversation_id in API response",
                            "raw_response": result
                        }
                    
                    return {
                        "status": "success",
                        "conversation_id": result["conversation_id"],
                        "call_id": result.get("call_id"),
                        "phone_number": phone_number,
                        "raw_response": result
                    }
                    
                except json.JSONDecodeError as e:
                    logger.error(f"❌ Invalid JSON response: {e}")
                    return {
                        "status": "failed",
                        "error": f"Invalid JSON response: {e}",
                        "raw_response": response.text
                    }
            else:
                logger.error(f"❌ API error {response.status_code}: {response.text}")
                return {
                    "status": "failed",
                    "error": f"API Error {response.status_code}: {response.text}",
                    "status_code": response.status_code
                }
                
        except requests.exceptions.Timeout:
            return {
                "status": "failed",
                "error": "Request timeout - ElevenLabs API not responding"
            }
        except Exception as e:
            return {
                "status": "failed",
                "error": f"Request failed: {str(e)}"
            }
    
    async def get_conversation_status(self, conversation_id: str) -> Optional[Dict[str, Any]]:
        """
        📡 GET CONVERSATION STATUS
        """
        
        if self.use_mock or conversation_id.startswith("mock_"):
            return await self._mock_status_check(conversation_id)
        
        try:
            loop = asyncio.get_event_loop()
            
            def make_status_request():
                return requests.get(
                    f"{self.base_url}/v1/convai/conversations/{conversation_id}",
                    headers={"Xi-Api-Key": self.api_key},
                    timeout=self.status_check_timeout
                )
            
            response = await loop.run_in_executor(None, make_status_request)
            
            if response.status_code == 200:
                result = response.json()
                
                # Add monitoring metadata
                result["monitoring_metadata"] = {
                    "fetched_at": datetime.now().isoformat(),
                    "service": "elevenlabs_api"
                }
                
                # Map ElevenLabs status to our expected states
                status = result.get("status", "unknown")
                result["normalized_status"] = self._normalize_conversation_status(status)
                
                return result
            else:
                logger.error(f"❌ Status check failed {response.status_code}: {response.text}")
                return {
                    "status": "error",
                    "normalized_status": "failed",
                    "error": f"API Error {response.status_code}",
                    "conversation_id": conversation_id
                }
                
        except Exception as e:
            logger.error(f"❌ Status check exception: {e}")
            return {
                "status": "error",
                "normalized_status": "failed", 
                "error": str(e),
                "conversation_id": conversation_id
            }
    
    def _normalize_conversation_status(self, elevenlabs_status: str) -> str:
        """Map ElevenLabs status to standard states"""
        status_mapping = {
            "initiated": "in_progress",
            "in-progress": "in_progress", 
            "processing": "in_progress",
            "done": "completed",
            "completed": "completed",
            "failed": "failed",
            "error": "failed",
            "timeout": "failed"
        }
        return status_mapping.get(elevenlabs_status.lower(), "unknown")
    
    async def wait_for_conversation_completion_with_analysis(
        self,
        conversation_id: str,
        max_wait_seconds: int = 300
    ) -> Dict[str, Any]:
        """
        🔄 WAIT FOR CONVERSATION COMPLETION WITH ANALYSIS
        """
        
        if self.use_mock or conversation_id.startswith("mock_"):
            return await self._mock_conversation_completion(conversation_id)
        
        start_time = datetime.now()
        poll_interval = 10  # Poll every 10 seconds
        
        logger.info(f"🔄 Waiting for conversation completion: {conversation_id}")
        
        while (datetime.now() - start_time).total_seconds() < max_wait_seconds:
            try:
                status_data = await self.get_conversation_status(conversation_id)
                
                if not status_data:
                    logger.warning("⚠️ No status data received, continuing to poll...")
                    await asyncio.sleep(poll_interval)
                    continue
                
                normalized_status = status_data.get("normalized_status", "unknown")
                
                if normalized_status == "completed":
                    logger.info("✅ Conversation completed successfully")
                    
                    # Extract analysis data
                    analysis_data = self._extract_analysis_data(status_data)
                    
                    return {
                        "status": "completed",
                        "conversation_data": status_data,
                        "analysis_data": analysis_data,
                        "completion_time": datetime.now().isoformat()
                    }
                
                elif normalized_status == "failed":
                    logger.error("❌ Conversation failed")
                    return {
                        "status": "failed",
                        "conversation_data": status_data,
                        "error": status_data.get("error", "Conversation failed"),
                        "failure_time": datetime.now().isoformat()
                    }
                
                # Still in progress, continue polling
                logger.info(f"📞 Conversation in progress: {normalized_status}")
                await asyncio.sleep(poll_interval)
                
            except Exception as e:
                logger.error(f"❌ Error during conversation monitoring: {e}")
                await asyncio.sleep(poll_interval)
        
        # Timeout reached
        logger.warning(f"⏰ Conversation timeout after {max_wait_seconds}s")
        return {
            "status": "timeout",
            "error": f"Conversation did not complete within {max_wait_seconds} seconds",
            "conversation_id": conversation_id
        }
    
    def _extract_analysis_data(self, conversation_data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract structured analysis from conversation data"""
        
        # Default analysis structure
        analysis = {
            "negotiation_outcome": "unknown",
            "agreed_rate": None,
            "conversation_sentiment": "neutral",
            "key_points": [],
            "next_steps": [],
            "call_successful": None,
            "summary": "",
            "duration_seconds": 0
        }
        
        # Extract from transcript if available
        transcript = conversation_data.get("transcript", [])
        if transcript:
            analysis["transcript_length"] = len(transcript)
            analysis["key_points"] = self._extract_key_points(transcript)
        
        # Extract from ElevenLabs analysis if present
        if "analysis" in conversation_data:
            elevenlabs_analysis = conversation_data["analysis"]
            
            # Extract call success status
            call_successful = elevenlabs_analysis.get("call_successful")
            analysis["call_successful"] = call_successful
            
            # Extract data collection results
            data_collection = elevenlabs_analysis.get("data_collection_results", {})
            
            # Extract final agreed rate
            final_rate_data = data_collection.get("final_rate_mentioned", {})
            if isinstance(final_rate_data, dict) and "value" in final_rate_data:
                analysis["agreed_rate"] = final_rate_data["value"]
            
            # Extract other useful fields
            analysis["summary"] = elevenlabs_analysis.get("transcript_summary", "")
            
            # Map call success to negotiation outcome
            if call_successful == "success":
                analysis["negotiation_outcome"] = "accepted"
                analysis["conversation_sentiment"] = "positive"
            elif final_rate_data and final_rate_data.get("value"):
                # If a rate was agreed, consider it successful even without explicit call_successful
                analysis["negotiation_outcome"] = "accepted"
                analysis["conversation_sentiment"] = "positive"
            else:
                analysis["negotiation_outcome"] = "unknown"
        
        # Extract metadata for duration
        metadata = conversation_data.get("metadata", {})
        analysis["duration_seconds"] = metadata.get("call_duration_secs", 0)
        
        return analysis
    
    def _extract_key_points(self, transcript: List[Dict[str, Any]]) -> List[str]:
        """Extract key conversation points from transcript"""
        key_points = []
        
        for entry in transcript:
            text = entry.get("text", "").lower()
            
            # Look for pricing mentions
            if any(word in text for word in ["$", "price", "rate", "cost", "budget"]):
                key_points.append(f"Pricing discussed: {entry.get('text', '')[:100]}")
            
            # Look for agreement indicators
            if any(word in text for word in ["agree", "yes", "deal", "accept"]):
                key_points.append(f"Agreement indicated: {entry.get('text', '')[:100]}")
            
            # Look for objections
            if any(word in text for word in ["no", "can't", "unable", "too"]):
                key_points.append(f"Objection raised: {entry.get('text', '')[:100]}")
        
        return key_points[:5]  # Return top 5 key points
    
    def _generate_dynamic_variables(
        self,
        creator_profile: Dict[str, Any],
        campaign_data: Dict[str, Any],
        pricing_strategy: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        🎯 GENERATE DYNAMIC VARIABLES FOR ELEVENLABS AGENT
        
        New format with 4 key variables:
        1. InfluencerProfile - JSON object with all influencer details
        2. campaignBrief - Campaign description and details 
        3. PriceRange - Budget and pricing information
        4. influencerName - Simple name reference
        """
        
        # 1. InfluencerProfile - JSON object with ALL comprehensive influencer data
        influencer_profile_data = {
            # Basic Information
            "name": creator_profile.get("name", "Creator"),
            "channel": creator_profile.get("id", creator_profile.get("channel", "unknown_channel")),
            "email": creator_profile.get("email", ""),
            "phone_number": creator_profile.get("phone_number", ""),
            
            # Platform & Content Details
            "platform": creator_profile.get("platform", "Social Media"),
            "niche": creator_profile.get("niche", "General").title(),
            "about": creator_profile.get("about") or f"Content creator specializing in {creator_profile.get('niche', 'lifestyle')} content",
            "specialties": creator_profile.get("specialties", []),
            "preferred_collaboration_style": creator_profile.get("preferred_collaboration_style", "Professional and collaborative"),
            
            # Audience & Performance Metrics
            "followers": f"{creator_profile.get('followers', 0)//1000}K" if creator_profile.get('followers', 0) >= 1000 else str(creator_profile.get('followers', 0)),
            "followers_numeric": creator_profile.get("followers", 0),
            "audienceType": creator_profile.get("audience_type") or f"{creator_profile.get('niche', 'General').title()} Enthusiasts",
            "engagement": f"{creator_profile.get('engagement_rate', 0.0)}%",
            "engagement_rate_numeric": creator_profile.get("engagement_rate", 0.0),
            "avgViews": f"{creator_profile.get('average_views', 0)//1000}K" if creator_profile.get('average_views', 0) >= 1000 else str(creator_profile.get('average_views', 0)),
            "average_views_numeric": creator_profile.get("average_views", 0),
            
            # Demographics & Audience Insights
            "audience_demographics": creator_profile.get("audience_demographics", {}),
            "performance_metrics": creator_profile.get("performance_metrics", {}),
            
            # Location & Languages
            "location": creator_profile.get("location", "Unknown"),
            "languages": creator_profile.get("languages", ["English"]),
            
            # Business & Collaboration Details
            "collaboration_rate": creator_profile.get("typical_rate", pricing_strategy.get("initial_offer", 1000)),
            "rate_history": creator_profile.get("rate_history", {}),
            "availability": creator_profile.get("availability", "good"),
            "last_campaign_date": creator_profile.get("last_campaign_date", ""),
            "recent_campaigns": creator_profile.get("recent_campaigns", []),
            
            # Creator Tier & Estimated Metrics
            "creator_tier": self._determine_creator_tier(creator_profile.get("followers", 0)),
            "estimated_cpm": self._calculate_estimated_cpm(creator_profile.get("typical_rate", 1000), creator_profile.get("average_views", 1000))
        }
        
        # 2. campaignBrief - Comprehensive campaign information
        campaign_brief = f"""
Brand: {campaign_data.get('brand_name', 'Brand')}
Product: {campaign_data.get('product_name', 'Product')}
Description: {campaign_data.get('product_description', 'Product description')}
Target Audience: {campaign_data.get('target_audience', 'General audience')}
Campaign Goal: {campaign_data.get('campaign_goal', 'Brand awareness')}
Niche: {campaign_data.get('product_niche', 'general')}
Content Type: Video review, social media posts
Timeline: 7-14 days
Usage Rights: Organic posts with 6-month brand rights
        """.strip()
        
        # 3. PriceRange - Budget and pricing strategy
        initial_offer = pricing_strategy.get("initial_offer", 1000)
        max_budget = pricing_strategy.get("max_offer", initial_offer * 1.5)
        budget_range = f"Initial Offer: ${initial_offer:,.0f} | Max Budget: ${max_budget:,.0f} | Negotiable based on deliverables and timeline"
        
        # 4. influencerName - Simple name for easy reference
        influencer_name = creator_profile.get("name", "Creator")
        
        # Convert InfluencerProfile to formatted string (Eleven Labs expects string format)
        influencer_profile_string = self._format_influencer_profile_as_string(influencer_profile_data)
        
        # Return the new dynamic variables format
        dynamic_variables = {
            "InfluencerProfile": influencer_profile_string,  # Formatted string with ALL data
            "campaignBrief": campaign_brief,                 # Campaign details string
            "PriceRange": budget_range,                      # Budget information string  
            "influencerName": influencer_name                # Simple name string
        }
        
        logger.info(f"🎯 Generated dynamic variables for {influencer_name}")
        logger.debug(f"   InfluencerProfile: {influencer_profile_data}")
        logger.debug(f"   PriceRange: {budget_range}")
        
        return dynamic_variables
    
    def _determine_creator_tier(self, followers: int) -> str:
        """Determine creator tier based on follower count"""
        if followers < 100_000:
            return "micro_influencer"
        elif followers < 1_000_000:
            return "macro_influencer"
        else:
            return "mega_influencer"
    
    def _calculate_estimated_cpm(self, typical_rate: float, average_views: int) -> float:
        """Calculate estimated cost per thousand views"""
        if average_views > 0:
            return round((typical_rate / average_views) * 1000, 2)
        return 0.0
    
    def _format_influencer_profile_as_string(self, profile_data: Dict[str, Any]) -> str:
        """
        Format comprehensive influencer profile data as a structured string
        that includes ALL available details for Eleven Labs agent
        """
        
        # Helper function to format lists
        def format_list(items):
            if isinstance(items, list):
                return ", ".join(str(item) for item in items)
            return str(items)
        
        # Helper function to format nested objects
        def format_object(obj):
            if isinstance(obj, dict):
                return "; ".join(f"{k}: {v}" for k, v in obj.items())
            return str(obj)
        
        # Build comprehensive formatted string with ALL data
        formatted_parts = []
        
        # Basic Information
        formatted_parts.append(f"name: {profile_data.get('name', 'N/A')}")
        formatted_parts.append(f"channel: {profile_data.get('channel', 'N/A')}")
        formatted_parts.append(f"email: {profile_data.get('email', 'N/A')}")
        formatted_parts.append(f"phone: {profile_data.get('phone_number', 'N/A')}")
        
        # Platform & Content Details
        formatted_parts.append(f"platform: {profile_data.get('platform', 'N/A')}")
        formatted_parts.append(f"niche: {profile_data.get('niche', 'N/A')}")
        formatted_parts.append(f"about: {profile_data.get('about', 'N/A')}")
        formatted_parts.append(f"specialties: {format_list(profile_data.get('specialties', []))}")
        formatted_parts.append(f"collaboration_style: {profile_data.get('preferred_collaboration_style', 'N/A')}")
        
        # Audience & Performance Metrics
        formatted_parts.append(f"followers: {profile_data.get('followers', 'N/A')}")
        formatted_parts.append(f"followers_numeric: {profile_data.get('followers_numeric', 0)}")
        formatted_parts.append(f"audience_type: {profile_data.get('audienceType', 'N/A')}")
        formatted_parts.append(f"engagement: {profile_data.get('engagement', 'N/A')}")
        formatted_parts.append(f"engagement_numeric: {profile_data.get('engagement_rate_numeric', 0)}")
        formatted_parts.append(f"avg_views: {profile_data.get('avgViews', 'N/A')}")
        formatted_parts.append(f"avg_views_numeric: {profile_data.get('average_views_numeric', 0)}")
        
        # Demographics & Insights  
        demographics = profile_data.get('audience_demographics', {})
        if demographics:
            formatted_parts.append(f"demographics: {format_object(demographics)}")
        
        performance = profile_data.get('performance_metrics', {})
        if performance:
            formatted_parts.append(f"performance: {format_object(performance)}")
        
        # Location & Languages
        formatted_parts.append(f"location: {profile_data.get('location', 'N/A')}")
        formatted_parts.append(f"languages: {format_list(profile_data.get('languages', []))}")
        
        # Business & Collaboration Details
        formatted_parts.append(f"collaboration_rate: {profile_data.get('collaboration_rate', 0)}")
        
        rate_history = profile_data.get('rate_history', {})
        if rate_history:
            formatted_parts.append(f"rate_history: {format_object(rate_history)}")
            
        formatted_parts.append(f"availability: {profile_data.get('availability', 'N/A')}")
        formatted_parts.append(f"last_campaign: {profile_data.get('last_campaign_date', 'N/A')}")
        
        recent_campaigns = profile_data.get('recent_campaigns', [])
        if recent_campaigns:
            campaigns_str = "; ".join(f"{camp.get('brand', 'N/A')} ({camp.get('date', 'N/A')})" for camp in recent_campaigns[:3])
            formatted_parts.append(f"recent_campaigns: {campaigns_str}")
        
        # Calculated Metrics
        formatted_parts.append(f"creator_tier: {profile_data.get('creator_tier', 'N/A')}")
        formatted_parts.append(f"estimated_cpm: ${profile_data.get('estimated_cpm', 0)}")
        
        # Join all parts with appropriate separators
        return " | ".join(formatted_parts)
    
    # Mock methods for testing
    async def _mock_enhanced_call(
        self,
        creator_phone: str,
        creator_profile: Dict[str, Any],
        campaign_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Mock call for testing"""
        await asyncio.sleep(1)  # Simulate API delay
        
        mock_conversation_id = f"mock_conv_{random.randint(1000, 9999)}"
        
        return {
            "status": "success",
            "conversation_id": mock_conversation_id,
            "call_id": f"mock_call_{random.randint(1000, 9999)}",
            "phone_number": creator_phone,
            "mock": True
        }
    
    async def _mock_status_check(self, conversation_id: str) -> Dict[str, Any]:
        """Mock status check"""
        await asyncio.sleep(0.5)
        
        return {
            "status": "completed",
            "normalized_status": "completed",
            "conversation_id": conversation_id,
            "transcript": [
                {"role": "agent", "text": "Hello! I'd like to discuss a collaboration opportunity."},
                {"role": "user", "text": "Sure, I'm interested. What's the offer?"},
                {"role": "agent", "text": "We can offer $1,500 for a sponsored post."},
                {"role": "user", "text": "That sounds good, I accept!"}
            ],
            "analysis": {
                "outcome": "accepted",
                "agreed_price": 1500,
                "sentiment": "positive"
            },
            "mock": True
        }
    
    async def _mock_conversation_completion(self, conversation_id: str) -> Dict[str, Any]:
        """Mock conversation completion"""
        await asyncio.sleep(2)  # Simulate conversation time
        
        status_data = await self._mock_status_check(conversation_id)
        analysis_data = self._extract_analysis_data(status_data)
        
        return {
            "status": "completed",
            "conversation_data": status_data,
            "analysis_data": analysis_data,
            "completion_time": datetime.now().isoformat(),
            "mock": True
        }