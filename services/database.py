import logging
from typing import Dict, Any
from datetime import datetime

from models.campaign import CampaignOrchestrationState

logger = logging.getLogger(__name__)

# Import enhanced Supabase database service if available
try:
    from .supabase_database import supabase_db
    SUPABASE_AVAILABLE = True
    logger.info("🚀 Enhanced Supabase database service available")
except ImportError:
    SUPABASE_AVAILABLE = False
    logger.warning("⚠️ Supabase database service not available - using mock mode")

class DatabaseService:
    """Service for database operations"""
    
    def __init__(self):
        self.connection = None
        # In a real implementation, this would initialize SQLAlchemy connection
        logger.info("🗄️  Database service initialized (mock mode)")
    
    async def sync_campaign_results(self, orchestration_state: CampaignOrchestrationState):
        """Enhanced sync campaign results - uses Supabase if available"""
        try:
            logger.info(f"💾 Syncing campaign {orchestration_state.campaign_id} to database")
            
            # Try Supabase first, fallback to mock
            if SUPABASE_AVAILABLE:
                logger.info("🚀 Using enhanced Supabase database service")
                await supabase_db.sync_campaign_results(orchestration_state)
                logger.info("✅ Enhanced Supabase database sync completed")
            else:
                logger.info("📝 Using mock database service")
                # Update campaigns table
                await self._update_campaign_record(orchestration_state)
                
                # Insert outreach logs
                await self._insert_outreach_logs(orchestration_state)
                
                # Insert contracts
                await self._insert_contracts(orchestration_state)
                
                # Insert payments
                await self._insert_payments(orchestration_state)
                
                logger.info("✅ Mock database sync completed")
            
        except Exception as e:
            logger.error(f"❌ Database sync failed: {e}")
            raise
    
    async def _update_campaign_record(self, state: CampaignOrchestrationState):
        """Update campaign record with results"""
        # Mock database update
        update_data = {
            "campaign_id": state.campaign_id,
            "status": "completed" if state.completed_at else "active",
            "influencer_count": state.successful_negotiations,
            "total_cost": state.total_cost,
            "updated_at": datetime.now().isoformat()
        }
        logger.info(f"📝 Campaign record updated: {update_data}")
    
    async def _insert_outreach_logs(self, state: CampaignOrchestrationState):
        """Insert outreach logs"""
        for negotiation in state.negotiations:
            log_data = {
                "campaign_id": state.campaign_id,
                "creator_id": negotiation.creator_id,
                "call_status": negotiation.call_status.value,
                "email_status": negotiation.email_status.value,
                "call_duration_minutes": negotiation.call_duration_seconds // 60,
                "call_recording_url": negotiation.call_recording_url,
                "call_transcript": negotiation.call_transcript,
                "last_contact_date": negotiation.last_contact_date.isoformat(),
                "notes": f"Negotiation {negotiation.status.value}",
                "sentiment": "positive" if negotiation.status.value == "success" else "neutral"
            }
            logger.info(f"📞 Outreach log inserted: {log_data}")
    
    async def _insert_contracts(self, state: CampaignOrchestrationState):
        """Insert contract records"""
        successful_negotiations = [n for n in state.negotiations if n.status.value == "success"]
        
        for negotiation in successful_negotiations:
            contract_data = {
                "campaign_id": state.campaign_id,
                "creator_id": negotiation.creator_id,
                "terms": negotiation.negotiated_terms,
                "deliverables": negotiation.negotiated_terms.get("deliverables", []),
                "payment_amount": negotiation.final_rate,
                "payment_schedule": negotiation.negotiated_terms.get("payment_schedule", {}),
                "status": "draft"
            }
            logger.info(f"📝 Contract inserted: {contract_data}")
    
    async def _insert_payments(self, state: CampaignOrchestrationState):
        """Insert payment records"""
        successful_negotiations = [n for n in state.negotiations if n.status.value == "success"]
        
        for negotiation in successful_negotiations:
            payment_data = {
                "contract_id": f"contract_{negotiation.creator_id}",
                "amount": negotiation.final_rate,
                "status": "pending",
                "payment_method": "bank_transfer",
                "due_date": (datetime.now()).isoformat()
            }
            logger.info(f"💰 Payment record inserted: {payment_data}")