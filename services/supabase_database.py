# services/supabase_database.py
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import asyncio
import json
from supabase import create_client, Client
from sqlalchemy import create_engine, text
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from models.campaign import CampaignOrchestrationState, CampaignData
from config.settings import settings

logger = logging.getLogger(__name__)

class SupabaseDatabaseService:
    """Enhanced database service using Supabase for email-enabled influencer AI platform"""
    
    def __init__(self):
        """Initialize Supabase client"""
        self.supabase: Client = None
        self._initialize_supabase()
        logger.info("🗄️ Supabase Database Service initialized")
    
    def _initialize_supabase(self):
        """Initialize Supabase client for REST API operations"""
        try:
            if settings.supabase_url and settings.supabase_key:
                self.supabase = create_client(settings.supabase_url, settings.supabase_key)
                logger.info("✅ Supabase client initialized successfully")
            else:
                logger.warning("⚠️ Supabase credentials missing - API operations will be disabled")
        except Exception as e:
            logger.error(f"❌ Failed to initialize Supabase client: {str(e)}")
    
    # ================================
    # CAMPAIGN OPERATIONS
    # ================================
    
    async def sync_campaign_results(self, orchestration_state: CampaignOrchestrationState):
        """Enhanced campaign sync with email functionality"""
        try:
            logger.info(f"💾 Syncing campaign {orchestration_state.campaign_id} to Supabase")
            
            # Update campaign record
            await self._update_campaign_record(orchestration_state)
            
            # Insert outreach logs
            await self._insert_outreach_logs(orchestration_state)
            
            # Insert contracts
            await self._insert_contracts(orchestration_state)
            
            # Insert payments
            await self._insert_payments(orchestration_state)
            
            logger.info("✅ Supabase database sync completed")
            
        except Exception as e:
            logger.error(f"❌ Supabase database sync failed: {e}")
            raise
    
    async def _update_campaign_record(self, state: CampaignOrchestrationState):
        """Update campaign record including sponsor email information"""
        try:
            campaign_data = state.campaign_data
            
            update_data = {
                "id": state.campaign_id,
                "product_name": campaign_data.product_name,
                "brand_name": campaign_data.brand_name,
                "product_description": campaign_data.product_description,
                "target_audience": campaign_data.target_audience,
                "campaign_goal": campaign_data.campaign_goal,
                "product_niche": campaign_data.product_niche,
                "total_budget": campaign_data.total_budget,
                "status": "completed" if state.completed_at else "active",
                "influencer_count": state.successful_negotiations,
                # 🚀 NEW: Email fields
                "sponsor_email": getattr(campaign_data, 'sponsor_email', None),
                "sponsor_name": getattr(campaign_data, 'sponsor_name', None),
                "sponsor_phone": getattr(campaign_data, 'sponsor_phone', None),
                "sponsor_company": getattr(campaign_data, 'sponsor_company', None),
                "updated_at": datetime.now().isoformat()
            }
            
            if self.supabase:
                # Use upsert to insert or update
                result = self.supabase.table("campaigns").upsert(update_data).execute()
                logger.info(f"📝 Campaign record upserted in Supabase: {state.campaign_id}")
            else:
                logger.info(f"📝 MOCK: Campaign record update: {update_data}")
                
        except Exception as e:
            logger.error(f"❌ Error updating campaign record: {str(e)}")
            raise
    
    # ================================
    # EMAIL LOGGING OPERATIONS
    # ================================
    
    async def log_email_sent(
        self,
        campaign_id: str,
        creator_id: Optional[str],
        email_type: str,
        recipient_email: str,
        recipient_name: str,
        subject: str,
        content_preview: str,
        sendgrid_message_id: Optional[str] = None
    ) -> str:
        """Log email sent to database"""
        try:
            email_log = {
                "campaign_id": campaign_id,
                "creator_id": creator_id,
                "email_type": email_type,
                "recipient_email": recipient_email,
                "recipient_name": recipient_name,
                "subject": subject,
                "content_preview": content_preview[:200],  # Limit to 200 chars
                "status": "sent",
                "sendgrid_message_id": sendgrid_message_id,
                "sent_at": datetime.now().isoformat()
            }
            
            if self.supabase:
                result = self.supabase.table("email_logs").insert(email_log).execute()
                log_id = result.data[0]["id"]
                logger.info(f"📧 Email logged in database: {log_id}")
                return log_id
            else:
                logger.info(f"📧 MOCK: Email log: {email_log}")
                return "mock-email-log-id"
                
        except Exception as e:
            logger.error(f"❌ Error logging email: {str(e)}")
            return None
    
    # ================================
    # SPONSOR DECISION OPERATIONS
    # ================================
    
    async def store_sponsor_decision(
        self,
        decision_id: str,
        campaign_id: str,
        creator_id: str,
        sponsor_email: str,
        creator_email: str,
        analytics_report: Dict[str, Any],
        call_data: Dict[str, Any],
        campaign_data: Dict[str, Any],
        expires_at: datetime
    ) -> bool:
        """Store sponsor decision data for tracking"""
        try:
            decision_data = {
                "decision_id": decision_id,
                "campaign_id": campaign_id,
                "creator_id": creator_id,
                "sponsor_email": sponsor_email,
                "creator_email": creator_email,
                "decision_status": "pending",
                "analytics_report": analytics_report,
                "call_data": call_data,
                "campaign_data": campaign_data,
                "expires_at": expires_at.isoformat()
            }
            
            if self.supabase:
                result = self.supabase.table("sponsor_decisions").insert(decision_data).execute()
                logger.info(f"💼 Sponsor decision stored: {decision_id}")
                return True
            else:
                logger.info(f"💼 MOCK: Sponsor decision stored: {decision_data}")
                return True
                
        except Exception as e:
            logger.error(f"❌ Error storing sponsor decision: {str(e)}")
            return False
    
    async def get_creator_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        """Get creator information by email address"""
        try:
            if self.supabase:
                result = self.supabase.table("creators").select("*").eq("email", email).execute()
                
                if result.data:
                    return result.data[0]
                else:
                    return None
            else:
                logger.info(f"👤 MOCK: Get creator by email: {email}")
                return None
                
        except Exception as e:
            logger.error(f"❌ Error getting creator by email: {str(e)}")
            return None
    
    # ================================
    # LEGACY COMPATIBILITY
    # ================================
    
    async def _insert_outreach_logs(self, state: CampaignOrchestrationState):
        """Insert outreach logs (enhanced for email tracking)"""
        for negotiation in state.negotiations:
            log_data = {
                "campaign_id": state.campaign_id,
                "creator_id": negotiation.creator_id,
                "channel": "voice",
                "message_type": "call",
                "status": negotiation.call_status.value,
                "call_duration_seconds": negotiation.call_duration_seconds,
                "call_successful": str(negotiation.call_status.value == "success"),
                "transcript_summary": negotiation.call_transcript[:500] if negotiation.call_transcript else None,
                "timestamp": negotiation.last_contact_date.isoformat()
            }
            
            if self.supabase:
                try:
                    self.supabase.table("outreach_logs").insert(log_data).execute()
                    logger.info(f"📞 Outreach log synced: {negotiation.creator_id}")
                except Exception as e:
                    logger.error(f"❌ Error syncing outreach log: {str(e)}")
            else:
                logger.info(f"📞 MOCK: Outreach log: {log_data}")
    
    async def _insert_contracts(self, state: CampaignOrchestrationState):
        """Insert contract records"""
        successful_negotiations = [n for n in state.negotiations if n.status.value == "success"]
        
        for negotiation in successful_negotiations:
            contract_data = {
                "campaign_id": state.campaign_id,
                "creator_id": negotiation.creator_id,
                "terms": negotiation.negotiated_terms,
                "payment_amount": negotiation.final_rate,
                "payment_schedule": negotiation.negotiated_terms.get("payment_schedule", {}),
                "status": "draft"
            }
            
            if self.supabase:
                try:
                    self.supabase.table("contracts").insert(contract_data).execute()
                    logger.info(f"📝 Contract synced: {negotiation.creator_id}")
                except Exception as e:
                    logger.error(f"❌ Error syncing contract: {str(e)}")
            else:
                logger.info(f"📝 MOCK: Contract: {contract_data}")
    
    async def _insert_payments(self, state: CampaignOrchestrationState):
        """Insert payment records"""
        successful_negotiations = [n for n in state.negotiations if n.status.value == "success"]
        
        for negotiation in successful_negotiations:
            payment_data = {
                "contract_id": f"contract_{negotiation.creator_id}",
                "amount": negotiation.final_rate,
                "status": "pending",
                "payment_method": "bank_transfer",
                "due_date": datetime.now().isoformat()
            }
            
            if self.supabase:
                try:
                    self.supabase.table("payments").insert(payment_data).execute()
                    logger.info(f"💰 Payment record synced: {negotiation.creator_id}")
                except Exception as e:
                    logger.error(f"❌ Error syncing payment: {str(e)}")
            else:
                logger.info(f"💰 MOCK: Payment: {payment_data}")
    
    async def test_connection(self) -> bool:
        """Test database connection"""
        try:
            if self.supabase:
                # Test Supabase connection
                result = self.supabase.table("campaigns").select("id").limit(1).execute()
                logger.info("✅ Supabase connection test successful")
                return True
            else:
                logger.warning("⚠️ Supabase client not initialized")
                return False
                
        except Exception as e:
            logger.error(f"❌ Database connection test failed: {str(e)}")
            return False

# Create global instance
supabase_db = SupabaseDatabaseService() 