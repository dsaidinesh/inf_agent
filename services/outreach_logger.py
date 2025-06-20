# services/outreach_logger.py
import logging
from typing import List, Optional, Dict, Any
from datetime import datetime
import uuid

from models.campaign import Creator, CreatorMatch, CampaignData
from .supabase_database import SupabaseDatabaseService

logger = logging.getLogger(__name__)

class OutreachLoggerService:
    """
    📝 OUTREACH LOGGER SERVICE
    Logs outreach activities to Supabase database using actual ElevenLabs conversation IDs
    """
    
    def __init__(self):
        self.db_service = SupabaseDatabaseService()
        logger.info("📝 Outreach Logger Service initialized")
    
    async def log_influencer_discovery(
        self,
        campaign_id: str,
        discovered_influencers: List[CreatorMatch],
        conversation_id: Optional[str] = None
    ) -> bool:
        """
        📝 Log when influencers are discovered for a campaign
        Creates an outreach log entry for each discovered influencer
        NOTE: This method should only be used for discovery logging, not call logging
        """
        try:
            logger.info(f"📝 Logging discovery of {len(discovered_influencers)} influencers for campaign {campaign_id}")
            
            if not self.db_service.supabase:
                logger.warning("⚠️ Supabase not available - outreach logging disabled")
                return False
            
            # Log each discovered influencer
            logged_count = 0
            for influencer_match in discovered_influencers:
                creator = influencer_match.creator
                
                # Generate discovery-specific conversation ID (not for actual calls)
                timestamp = int(datetime.now().timestamp())
                unique_suffix = str(uuid.uuid4())[:8]  # Short UUID suffix
                discovery_conversation_id = f"discovery_{campaign_id}_{creator.id}_{timestamp}_{unique_suffix}"
                
                # Prepare outreach log data
                outreach_log = {
                    "id": str(uuid.uuid4()),
                    "campaign_id": self._ensure_uuid(campaign_id),
                    "creator_id": self._ensure_uuid(creator.id),
                    "conversation_id": discovery_conversation_id,
                    "channel": "discovery",
                    "message_type": "influencer_discovery",
                    "content": {
                        "discovery_method": "ai_matching",
                        "similarity_score": influencer_match.similarity_score,
                        "estimated_rate": influencer_match.estimated_rate,
                        "match_reasons": influencer_match.match_reasons,
                        "creator_details": {
                            "name": creator.name,
                            "email": creator.email,
                            "platform": creator.platform.value if hasattr(creator.platform, 'value') else str(creator.platform),
                            "followers": creator.followers,
                            "niche": creator.niche,
                            "engagement_rate": creator.engagement_rate
                        }
                    },
                    "status": "discovered",
                    "timestamp": datetime.now().isoformat()
                }
                
                try:
                    # Insert into outreach_logs table
                    result = self.db_service.supabase.table("outreach_logs").insert(outreach_log).execute()
                    
                    if result.data:
                        logged_count += 1
                        logger.info(f"✅ Logged discovery: {creator.name} ({creator.id})")
                    else:
                        logger.warning(f"⚠️ Failed to log discovery for {creator.name}")
                        
                except Exception as e:
                    error_message = str(e)
                    
                    # Handle duplicate key constraint specifically
                    if "duplicate key value violates unique constraint" in error_message and "conversation_id" in error_message:
                        logger.warning(f"⚠️ Duplicate conversation ID detected for {creator.name}, skipping (already logged)")
                        # Don't increment logged_count, but don't treat as error either
                        continue
                    else:
                        logger.error(f"❌ Error logging discovery for {creator.name}: {error_message}")
                        continue
            
            logger.info(f"📝 Successfully logged {logged_count}/{len(discovered_influencers)} influencer discoveries")
            return logged_count > 0
            
        except Exception as e:
            logger.error(f"❌ Failed to log influencer discovery: {str(e)}")
            return False
    
    async def log_outreach_attempt(
        self,
        campaign_id: str,
        creator_id: str,
        conversation_id: str,  # NOW REQUIRED - must be actual ElevenLabs conversation ID
        channel: str = "voice",
        message_type: str = "call_attempt",
        status: str = "initiated",
        additional_data: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        📝 Log individual outreach attempts (calls, emails, etc.)
        REQUIRES actual conversation_id from ElevenLabs - no longer generates IDs automatically
        """
        try:
            if not self.db_service.supabase:
                logger.warning("⚠️ Supabase not available - outreach logging disabled")
                return False
            
            # Validate that conversation_id is provided
            if not conversation_id:
                logger.error("❌ conversation_id is required for outreach logging")
                return False
            
            logger.info(f"📝 Logging outreach attempt with ElevenLabs conversation ID: {conversation_id}")
            
            # Prepare log data
            log_data = {
                "id": str(uuid.uuid4()),
                "campaign_id": self._ensure_uuid(campaign_id),
                "creator_id": self._ensure_uuid(creator_id),
                "conversation_id": conversation_id,  # Use actual ElevenLabs conversation ID
                "channel": channel,
                "message_type": message_type,
                "content": additional_data or {},
                "status": status,
                "timestamp": datetime.now().isoformat()
            }
            
            # Insert into database
            result = self.db_service.supabase.table("outreach_logs").insert(log_data).execute()
            
            if result.data:
                logger.info(f"📝 Successfully logged {message_type} with conversation ID: {conversation_id}")
                return True
            else:
                logger.warning(f"⚠️ Failed to log {message_type} for creator {creator_id}")
                return False
                
        except Exception as e:
            error_message = str(e)
            
            # Handle duplicate key constraint specifically
            if "duplicate key value violates unique constraint" in error_message and "conversation_id" in error_message:
                logger.warning(f"⚠️ Duplicate conversation ID {conversation_id} - already logged")
                return True  # Consider this a success since it was already logged
            else:
                logger.error(f"❌ Error logging outreach attempt: {error_message}")
                return False
    
    async def update_outreach_status(
        self,
        conversation_id: str,
        new_status: str,
        additional_data: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        📝 Update the status of an existing outreach log entry
        """
        try:
            if not self.db_service.supabase:
                logger.warning("⚠️ Supabase not available - status update disabled")
                return False
            
            # Prepare update data
            update_data = {
                "status": new_status,
                "timestamp": datetime.now().isoformat()
            }
            
            # Add additional data if provided
            if additional_data:
                # Get existing content and merge with new data
                existing = self.db_service.supabase.table("outreach_logs").select("content").eq("conversation_id", conversation_id).execute()
                
                if existing.data:
                    existing_content = existing.data[0].get("content", {})
                    existing_content.update(additional_data)
                    update_data["content"] = existing_content
            
            # Update the record
            result = self.db_service.supabase.table("outreach_logs").update(update_data).eq("conversation_id", conversation_id).execute()
            
            if result.data:
                logger.info(f"📝 Updated outreach status to {new_status} for conversation {conversation_id}")
                return True
            else:
                logger.warning(f"⚠️ Failed to update status for conversation {conversation_id}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Error updating outreach status: {str(e)}")
            return False
    
    async def get_outreach_logs_for_campaign(self, campaign_id: str) -> List[Dict[str, Any]]:
        """
        📊 Retrieve all outreach logs for a specific campaign
        """
        try:
            if not self.db_service.supabase:
                logger.warning("⚠️ Supabase not available - returning empty logs")
                return []
            
            result = self.db_service.supabase.table("outreach_logs").select("*").eq("campaign_id", self._ensure_uuid(campaign_id)).order("timestamp", desc=True).execute()
            
            if result.data:
                logger.info(f"📊 Retrieved {len(result.data)} outreach logs for campaign {campaign_id}")
                return result.data
            else:
                logger.info(f"📊 No outreach logs found for campaign {campaign_id}")
                return []
                
        except Exception as e:
            logger.error(f"❌ Error retrieving outreach logs: {str(e)}")
            return []
    
    def _ensure_uuid(self, value: str) -> str:
        """
        🔧 Ensure the value is a valid UUID string, generate one if not
        """
        try:
            # Try to parse as UUID to validate
            uuid.UUID(value)
            return value
        except (ValueError, TypeError):
            # If not a valid UUID, generate a new one based on the input
            if value:
                # Create a deterministic UUID based on the input string
                import hashlib
                namespace = uuid.UUID('6ba7b810-9dad-11d1-80b4-00c04fd430c8')  # Standard namespace
                return str(uuid.uuid5(namespace, str(value)))
            else:
                # Generate a random UUID if no input
                return str(uuid.uuid4())

# Global instance
outreach_logger = OutreachLoggerService() 