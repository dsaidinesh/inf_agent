# services/analytics_service.py
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import uuid
import json
import asyncio

from .email_service import email_service
from config.settings import settings
from .supabase_database import supabase_db

logger = logging.getLogger(__name__)

class CallAnalyticsService:
    """
    📊 POST-CALL ANALYTICS SERVICE
    Generates structured analytics after calls and manages sponsor decision workflow
    """
    
    def __init__(self):
        self.email_service = email_service
        # Remove in-memory storage - now using Supabase
        
        # 🚀 NEW: Sponsor email lookup database (in production, this would be a real database)
        self.sponsor_lookup = {
            # Brand name -> Sponsor email mapping
            "techcorp": "sponsor@techcorp.com",
            "techpro audio": "marketing@techproaudio.com",
            "audiomax technologies": "saidineshsvec@gmail.com",  # Your email for testing
            "beautybrand": "partnerships@beautybrand.com",
            "fitnessplus": "collabs@fitnessplus.com",
            "gameco": "influencer@gameco.com",
            "foodiebrands": "creator@foodiebrands.com",
            "test brand": "sponsor@testbrand.com",
            "your brand": "sponsor@yourbrand.com"
        }
        
        logger.info("✅ Call Analytics Service initialized with Supabase storage")
    
    def _lookup_sponsor_email(self, campaign_data: Dict[str, Any]) -> Optional[str]:
        """
        🔍 Look up sponsor email from various sources
        
        Priority order:
        1. campaign_data["sponsor_email"] (direct)
        2. Sponsor lookup database by brand name
        3. Generate fallback email
        """
        try:
            # Priority 1: Direct sponsor email in campaign data
            if campaign_data.get("sponsor_email"):
                return campaign_data["sponsor_email"]
            
            # Priority 2: Lookup by brand name
            brand_name = campaign_data.get("brand_name", "").lower()
            if brand_name in self.sponsor_lookup:
                sponsor_email = self.sponsor_lookup[brand_name]
                logger.info(f"✅ Found sponsor email in lookup: {sponsor_email}")
                return sponsor_email
            
            # Priority 3: Try partial matches
            for brand_key, email in self.sponsor_lookup.items():
                if brand_key in brand_name or brand_name in brand_key:
                    logger.info(f"✅ Found partial match for '{brand_name}': {email}")
                    return email
            
            # Priority 4: Generate fallback
            brand_clean = brand_name.replace(" ", "").replace("-", "")
            if brand_clean:
                fallback_email = f"sponsor@{brand_clean}.com"
                logger.warning(f"⚠️ Generated fallback email: {fallback_email}")
                return fallback_email
            
            return None
            
        except Exception as e:
            logger.error(f"❌ Error looking up sponsor email: {str(e)}")
            return None
    
    async def process_completed_call(
        self,
        call_data: Dict[str, Any],
        campaign_data: Dict[str, Any],
        sponsor_email: Optional[str] = None,
        creator_email: str = None
    ) -> Dict[str, Any]:
        """
        🎯 MAIN WORKFLOW: Process completed call and send analytics to sponsor
        
        Args:
            call_data: Information about the completed call
            campaign_data: Campaign details (may include sponsor_email)
            sponsor_email: Sponsor's email for decision (optional if in campaign_data)
            creator_email: Creator's email for contract/regret emails
            
        Returns:
            Dict with analytics and decision tracking info
        """
        try:
            logger.info(f"📊 Processing completed call analytics for campaign: {campaign_data.get('campaign_name', 'Unknown')}")
            logger.info(f"👤 Creator: {creator_email}")
            
            # 🚀 NEW: Auto-extract sponsor email from campaign data if not provided
            if not sponsor_email:
                sponsor_email = self._lookup_sponsor_email(campaign_data)
                if sponsor_email:
                    logger.info(f"✅ Using sponsor email from campaign data: {sponsor_email}")
                else:
                    # Fallback: Generate from brand name
                    brand_name = campaign_data.get("brand_name", "brand")
                    sponsor_email = f"sponsor@{brand_name.lower().replace(' ', '')}.com"
                    logger.warning(f"⚠️ No sponsor email found! Using fallback: {sponsor_email}")
                    logger.warning("💡 TIP: Add sponsor_email to campaign_data for better delivery")
            
            # STEP 1: Generate structured analytics
            analytics_report = await self._generate_call_analytics(call_data, campaign_data)
            
            # STEP 2: Create decision tracking ID
            decision_id = f"DEC-{str(uuid.uuid4())[:8].upper()}"
            
            # STEP 3: Store decision data in Supabase database
            stored = await self._store_decision_in_database(
                decision_id=decision_id,
                call_data=call_data,
                campaign_data=campaign_data,
                analytics_report=analytics_report,
                sponsor_email=sponsor_email,
                creator_email=creator_email,
                conversation_id=call_data.get("conversation_id")
            )
            
            if not stored:
                logger.warning("⚠️ Decision not stored in database - using fallback")
            
            # STEP 4: Send analytics email to sponsor
            email_sent = await self._send_analytics_to_sponsor(
                analytics_report=analytics_report,
                sponsor_email=sponsor_email,
                decision_id=decision_id,
                campaign_data=campaign_data
            )
            
            if email_sent:
                logger.info(f"✅ Analytics sent to sponsor: {sponsor_email} | Decision ID: {decision_id}")
                logger.info(f"📧 Creator email stored for later: {creator_email}")
                return {
                    "status": "success",
                    "decision_id": decision_id,
                    "analytics_report": analytics_report,
                    "email_sent": True,
                    "sponsor_email_used": sponsor_email,
                    "stored_in_database": stored,
                    "next_steps": "Waiting for sponsor decision",
                    "decision_expires_at": (datetime.now() + timedelta(hours=48)).isoformat()
                }
            else:
                logger.error(f"❌ Failed to send analytics email to {sponsor_email}")
                return {
                    "status": "error",
                    "message": "Failed to send analytics email",
                    "analytics_report": analytics_report,
                    "sponsor_email_used": sponsor_email,
                    "stored_in_database": stored
                }
                
        except Exception as e:
            logger.error(f"❌ Error processing completed call: {str(e)}")
            return {
                "status": "error",
                "message": f"Failed to process call analytics: {str(e)}"
            }
    
    async def _generate_call_analytics(
        self,
        call_data: Dict[str, Any],
        campaign_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        📈 Generate structured analytics table from call data
        """
        try:
            # Extract call information
            conversation_id = call_data.get("conversation_id", "N/A")
            call_duration = call_data.get("call_duration_seconds", 0)
            call_status = call_data.get("status", "unknown")
            
            # Extract negotiation results
            negotiation_data = call_data.get("negotiation_results", {})
            agreed_rate = negotiation_data.get("final_rate", 0)
            original_rate = campaign_data.get("offered_rate", 0)
            
            # Extract influencer information
            influencer_data = call_data.get("influencer_data", {})
            influencer_name = influencer_data.get("name", "Unknown Influencer")
            influencer_platform = influencer_data.get("platform", "Social Media")
            
            # Calculate metrics
            rate_difference = agreed_rate - original_rate if original_rate else 0
            rate_change_percent = (rate_difference / original_rate * 100) if original_rate else 0
            call_duration_minutes = round(call_duration / 60, 1)
            
            # Determine negotiation outcome
            if call_status == "completed" and agreed_rate > 0:
                outcome = "✅ Successful"
                outcome_color = "green"
            elif call_status == "completed":
                outcome = "⚠️ Completed - No Agreement"
                outcome_color = "orange"
            else:
                outcome = "❌ Failed"
                outcome_color = "red"
            
            # Create structured analytics report
            analytics_report = {
                "report_id": f"RPT-{str(uuid.uuid4())[:8].upper()}",
                "generated_at": datetime.now().isoformat(),
                "campaign_info": {
                    "campaign_name": campaign_data.get("campaign_name", "Unknown Campaign"),
                    "brand_name": campaign_data.get("brand_name", "Unknown Brand"),
                    "product_name": campaign_data.get("product_name", "Unknown Product"),
                    "total_budget": campaign_data.get("total_budget", 0)
                },
                "call_summary": {
                    "conversation_id": conversation_id,
                    "influencer_name": influencer_name,
                    "influencer_platform": influencer_platform,
                    "call_duration_minutes": call_duration_minutes,
                    "call_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "outcome": outcome,
                    "outcome_color": outcome_color
                },
                "financial_analysis": {
                    "original_offered_rate": original_rate,
                    "final_agreed_rate": agreed_rate,
                    "rate_difference": rate_difference,
                    "rate_change_percent": round(rate_change_percent, 1),
                    "budget_impact": f"{(agreed_rate / campaign_data.get('total_budget', 1) * 100):.1f}%" if campaign_data.get('total_budget') else "N/A"
                },
                "deliverables_agreed": negotiation_data.get("deliverables", []),
                "timeline_agreed": negotiation_data.get("timeline", "Not specified"),
                "special_terms": negotiation_data.get("special_terms", []),
                "conversation_highlights": negotiation_data.get("key_quotes", []),
                "influencer_enthusiasm": negotiation_data.get("creator_enthusiasm", "N/A"),
                "recommendation": self._generate_recommendation(call_data, campaign_data)
            }
            
            logger.info(f"📊 Analytics generated: {outcome} | Rate: ${agreed_rate} | Duration: {call_duration_minutes}min")
            
            return analytics_report
            
        except Exception as e:
            logger.error(f"❌ Error generating call analytics: {str(e)}")
            return {
                "error": f"Failed to generate analytics: {str(e)}",
                "generated_at": datetime.now().isoformat()
            }
    
    def _generate_recommendation(
        self,
        call_data: Dict[str, Any],
        campaign_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        🎯 Generate AI recommendation based on call results
        """
        negotiation_data = call_data.get("negotiation_results", {})
        agreed_rate = negotiation_data.get("final_rate", 0)
        original_rate = campaign_data.get("offered_rate", 0)
        enthusiasm = negotiation_data.get("creator_enthusiasm", 0)
        
        # Calculate recommendation score
        score = 0
        reasons = []
        
        if agreed_rate > 0:
            score += 40
            reasons.append("✅ Successful rate negotiation")
        
        if enthusiasm >= 7:
            score += 30
            reasons.append("✅ High influencer enthusiasm")
        elif enthusiasm >= 5:
            score += 15
            reasons.append("⚠️ Moderate influencer enthusiasm")
        
        rate_increase = ((agreed_rate - original_rate) / original_rate * 100) if original_rate else 0
        if rate_increase <= 20:
            score += 20
            reasons.append("✅ Reasonable rate increase")
        elif rate_increase <= 50:
            score += 10
            reasons.append("⚠️ Moderate rate increase")
        else:
            reasons.append("❌ High rate increase")
        
        if len(negotiation_data.get("deliverables", [])) > 0:
            score += 10
            reasons.append("✅ Clear deliverables agreed")
        
        # Generate recommendation
        if score >= 80:
            recommendation = "🟢 STRONGLY RECOMMEND - Proceed with contract"
            recommendation_color = "green"
        elif score >= 60:
            recommendation = "🟡 RECOMMEND - Good opportunity with minor considerations"
            recommendation_color = "orange"
        elif score >= 40:
            recommendation = "🟡 CONSIDER - Mixed results, review carefully"
            recommendation_color = "orange"
        else:
            recommendation = "🔴 NOT RECOMMENDED - Significant concerns"
            recommendation_color = "red"
        
        return {
            "recommendation": recommendation,
            "recommendation_color": recommendation_color,
            "confidence_score": score,
            "reasoning": reasons,
            "key_considerations": self._get_key_considerations(call_data, campaign_data)
        }
    
    def _get_key_considerations(
        self,
        call_data: Dict[str, Any],
        campaign_data: Dict[str, Any]
    ) -> List[str]:
        """Get key considerations for sponsor decision"""
        considerations = []
        
        negotiation_data = call_data.get("negotiation_results", {})
        agreed_rate = negotiation_data.get("final_rate", 0)
        original_rate = campaign_data.get("offered_rate", 0)
        
        if agreed_rate > original_rate:
            increase = agreed_rate - original_rate
            considerations.append(f"💰 Rate increased by ${increase} from original offer")
        
        if negotiation_data.get("special_terms"):
            considerations.append("📋 Special terms were negotiated")
        
        timeline = negotiation_data.get("timeline", "")
        if "urgent" in timeline.lower() or "asap" in timeline.lower():
            considerations.append("⏰ Urgent timeline requested")
        
        enthusiasm = negotiation_data.get("creator_enthusiasm", 0)
        if enthusiasm < 5:
            considerations.append("😐 Influencer showed low enthusiasm")
        
        return considerations
    
    async def _send_analytics_to_sponsor(
        self,
        analytics_report: Dict[str, Any],
        sponsor_email: str,
        decision_id: str,
        campaign_data: Dict[str, Any]
    ) -> bool:
        """
        📧 Send structured analytics email to sponsor for decision
        """
        try:
            campaign_name = campaign_data.get("campaign_name", "Your Campaign")
            subject = f"📊 Call Analytics & Decision Required - {campaign_name}"
            
            # Create decision URLs (these would link to your web interface)
            base_url = settings.base_url or "http://localhost:8000"
            approve_url = f"{base_url}/api/decision/approve/{decision_id}"
            reject_url = f"{base_url}/api/decision/reject/{decision_id}"
            
            # Generate HTML email content
            html_content = self._create_analytics_email_template(
                analytics_report=analytics_report,
                decision_id=decision_id,
                approve_url=approve_url,
                reject_url=reject_url
            )
            
            # Generate plain text version
            text_content = self._create_analytics_text_template(
                analytics_report=analytics_report,
                decision_id=decision_id
            )
            
            # Send email
            success = await self.email_service._send_email(
                to_email=sponsor_email,
                subject=subject,
                html_content=html_content,
                text_content=text_content
            )
            
            if success:
                logger.info(f"✅ Analytics email sent to sponsor: {sponsor_email}")
            else:
                logger.error(f"❌ Failed to send analytics email to {sponsor_email}")
            
            return success
            
        except Exception as e:
            logger.error(f"❌ Error sending analytics email: {str(e)}")
            return False
    
    def _create_analytics_email_template(
        self,
        analytics_report: Dict[str, Any],
        decision_id: str,
        approve_url: str,
        reject_url: str
    ) -> str:
        """
        📧 Create beautiful HTML email template for analytics
        """
        call_summary = analytics_report.get("call_summary", {})
        financial = analytics_report.get("financial_analysis", {})
        campaign_info = analytics_report.get("campaign_info", {})
        recommendation = analytics_report.get("recommendation", {})
        
        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Call Analytics Report</title>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 700px; margin: 0 auto; padding: 20px; }}
                .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0; }}
                .content {{ background: #f9f9f9; padding: 30px; border-radius: 0 0 10px 10px; }}
                .analytics-table {{ background: white; border-radius: 8px; overflow: hidden; margin: 20px 0; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
                .table-header {{ background: #667eea; color: white; padding: 15px; font-weight: bold; }}
                .table-row {{ padding: 12px 15px; border-bottom: 1px solid #eee; display: flex; justify-content: space-between; }}
                .table-row:last-child {{ border-bottom: none; }}
                .metric-label {{ font-weight: bold; color: #555; }}
                .metric-value {{ color: #333; }}
                .recommendation-box {{ background: white; padding: 20px; border-radius: 8px; border-left: 4px solid #667eea; margin: 20px 0; }}
                .decision-buttons {{ text-align: center; margin: 30px 0; }}
                .approve-btn {{ display: inline-block; background: #28a745; color: white; padding: 15px 30px; text-decoration: none; border-radius: 6px; margin: 10px; font-weight: bold; }}
                .reject-btn {{ display: inline-block; background: #dc3545; color: white; padding: 15px 30px; text-decoration: none; border-radius: 6px; margin: 10px; font-weight: bold; }}
                .footer {{ text-align: center; margin-top: 30px; color: #666; font-size: 14px; }}
                .highlight {{ background: rgba(102, 126, 234, 0.1); padding: 2px 6px; border-radius: 4px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>📊 Call Analytics Report</h1>
                    <p>Campaign: {campaign_info.get('campaign_name', 'Unknown')}</p>
                    <p>Decision Required</p>
                </div>
                
                <div class="content">
                    <h2>📞 Call Summary</h2>
                    <div class="analytics-table">
                        <div class="table-header">Call Details</div>
                        <div class="table-row">
                            <span class="metric-label">Influencer</span>
                            <span class="metric-value">{call_summary.get('influencer_name', 'N/A')}</span>
                        </div>
                        <div class="table-row">
                            <span class="metric-label">Platform</span>
                            <span class="metric-value">{call_summary.get('influencer_platform', 'N/A')}</span>
                        </div>
                        <div class="table-row">
                            <span class="metric-label">Call Duration</span>
                            <span class="metric-value">{call_summary.get('call_duration_minutes', 0)} minutes</span>
                        </div>
                        <div class="table-row">
                            <span class="metric-label">Outcome</span>
                            <span class="metric-value">{call_summary.get('outcome', 'N/A')}</span>
                        </div>
                    </div>
                    
                    <h2>💰 Financial Analysis</h2>
                    <div class="analytics-table">
                        <div class="table-header">Negotiation Results</div>
                        <div class="table-row">
                            <span class="metric-label">Original Offer</span>
                            <span class="metric-value">${financial.get('original_offered_rate', 0):,.2f}</span>
                        </div>
                        <div class="table-row">
                            <span class="metric-label">Final Agreed Rate</span>
                            <span class="metric-value highlight">${financial.get('final_agreed_rate', 0):,.2f}</span>
                        </div>
                        <div class="table-row">
                            <span class="metric-label">Rate Change</span>
                            <span class="metric-value">{financial.get('rate_change_percent', 0):+.1f}%</span>
                        </div>
                        <div class="table-row">
                            <span class="metric-label">Budget Impact</span>
                            <span class="metric-value">{financial.get('budget_impact', 'N/A')}</span>
                        </div>
                    </div>
                    
                    <h2>📋 Agreement Details</h2>
                    <div class="analytics-table">
                        <div class="table-header">Deliverables & Timeline</div>
                        <div class="table-row">
                            <span class="metric-label">Deliverables</span>
                            <span class="metric-value">{', '.join(analytics_report.get('deliverables_agreed', ['Not specified']))}</span>
                        </div>
                        <div class="table-row">
                            <span class="metric-label">Timeline</span>
                            <span class="metric-value">{analytics_report.get('timeline_agreed', 'Not specified')}</span>
                        </div>
                        <div class="table-row">
                            <span class="metric-label">Influencer Enthusiasm</span>
                            <span class="metric-value">{analytics_report.get('influencer_enthusiasm', 'N/A')}/10</span>
                        </div>
                    </div>
                    
                    <div class="recommendation-box">
                        <h3>🎯 AI Recommendation</h3>
                        <p><strong>{recommendation.get('recommendation', 'No recommendation available')}</strong></p>
                        <p><strong>Confidence Score:</strong> {recommendation.get('confidence_score', 0)}/100</p>
                        <h4>Key Reasoning:</h4>
                        <ul>
                        {chr(10).join([f"<li>{reason}</li>" for reason in recommendation.get('reasoning', [])])}
                        </ul>
                    </div>
                    
                    <div class="decision-buttons">
                        <h3>🤔 Your Decision Required</h3>
                        <p>Please review the analytics above and decide whether to proceed with this influencer:</p>
                        
                        <a href="{approve_url}" class="approve-btn">
                            ✅ APPROVE - Send Contract
                        </a>
                        
                        <a href="{reject_url}" class="reject-btn">
                            ❌ REJECT - Send Regret Email
                        </a>
                    </div>
                    
                    <div class="footer">
                        <p><strong>Decision ID:</strong> {decision_id}</p>
                        <p><strong>Report Generated:</strong> {analytics_report.get('generated_at', 'N/A')}</p>
                        <p><em>This decision will expire in 48 hours</em></p>
                        <p>Powered by <strong>InfluencerFlow AI</strong></p>
                    </div>
                </div>
            </div>
        </body>
        </html>
        """
    
    def _create_analytics_text_template(
        self,
        analytics_report: Dict[str, Any],
        decision_id: str
    ) -> str:
        """
        📧 Create plain text version of analytics email
        """
        call_summary = analytics_report.get("call_summary", {})
        financial = analytics_report.get("financial_analysis", {})
        campaign_info = analytics_report.get("campaign_info", {})
        recommendation = analytics_report.get("recommendation", {})
        
        return f"""
CALL ANALYTICS REPORT - DECISION REQUIRED
========================================

Campaign: {campaign_info.get('campaign_name', 'Unknown')}
Decision ID: {decision_id}

CALL SUMMARY:
-------------
Influencer: {call_summary.get('influencer_name', 'N/A')}
Platform: {call_summary.get('influencer_platform', 'N/A')}
Duration: {call_summary.get('call_duration_minutes', 0)} minutes
Outcome: {call_summary.get('outcome', 'N/A')}

FINANCIAL ANALYSIS:
------------------
Original Offer: ${financial.get('original_offered_rate', 0):,.2f}
Final Agreed Rate: ${financial.get('final_agreed_rate', 0):,.2f}
Rate Change: {financial.get('rate_change_percent', 0):+.1f}%
Budget Impact: {financial.get('budget_impact', 'N/A')}

AGREEMENT DETAILS:
-----------------
Deliverables: {', '.join(analytics_report.get('deliverables_agreed', ['Not specified']))}
Timeline: {analytics_report.get('timeline_agreed', 'Not specified')}
Influencer Enthusiasm: {analytics_report.get('influencer_enthusiasm', 'N/A')}/10

AI RECOMMENDATION:
-----------------
{recommendation.get('recommendation', 'No recommendation available')}
Confidence Score: {recommendation.get('confidence_score', 0)}/100

Key Reasoning:
{chr(10).join([f"• {reason}" for reason in recommendation.get('reasoning', [])])}

DECISION REQUIRED:
-----------------
Please review the analytics above and make your decision:

✅ APPROVE: Reply with "APPROVE {decision_id}" to send contract
❌ REJECT: Reply with "REJECT {decision_id} [your message]" to send regret email

This decision will expire in 48 hours.

---
Report Generated: {analytics_report.get('generated_at', 'N/A')}
Powered by InfluencerFlow AI
        """
    
    async def process_sponsor_decision(
        self,
        decision_id: str,
        decision: str,
        sponsor_message: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        🎯 Process sponsor's decision (approve/reject)
        
        Args:
            decision_id: The decision tracking ID
            decision: "approve" or "reject"
            sponsor_message: Optional message from sponsor (for rejections)
            
        Returns:
            Dict with processing results
        """
        try:
            # Get decision data from database
            decision_data = await self._get_decision_from_database(decision_id)
            
            if not decision_data:
                return {
                    "status": "error",
                    "message": "Decision ID not found or expired"
                }
            
            # Check if decision is still pending
            if decision_data["status"] != "pending":
                return {
                    "status": "error",
                    "message": f"Decision already processed: {decision_data['status']}"
                }
            
            # Update decision status in database
            new_status = decision.lower()
            await self._update_decision_status(
                decision_id=decision_id,
                status=new_status,
                sponsor_message=sponsor_message
            )
            
            if decision.lower() == "approve":
                # Send contract to influencer
                result = await self._send_contract_to_influencer(decision_data)
                # Update contract_sent status
                if result["status"] == "success":
                    await self._update_decision_status(decision_id, new_status, contract_sent=True)
                logger.info(f"✅ Decision {decision_id}: APPROVED - Contract sent")
            else:
                # Send regret email to influencer
                result = await self._send_regret_to_influencer(decision_data, sponsor_message)
                logger.info(f"❌ Decision {decision_id}: REJECTED - Regret email sent")
            
            return result
            
        except Exception as e:
            logger.error(f"❌ Error processing sponsor decision: {str(e)}")
            return {
                "status": "error",
                "message": f"Failed to process decision: {str(e)}"
            }
    
    async def _send_contract_to_influencer(self, decision_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        📄 Send contract to influencer after sponsor approval
        """
        try:
            from .contract_service import contract_service
            
            call_data = decision_data["call_data"]
            campaign_data = decision_data["campaign_data"]
            creator_email = decision_data["creator_email"]  # Use stored creator email
            
            # Prepare influencer data with the verified creator email
            influencer_data = call_data.get("influencer_data", {})
            influencer_data["email"] = creator_email  # Ensure we use the verified email
            
            logger.info(f"📄 Sending contract to creator: {creator_email}")
            
            # Send contract using existing contract service
            success = await contract_service.process_successful_call(
                call_data=call_data,
                influencer_data=influencer_data,
                campaign_data=campaign_data
            )
            
            if success:
                logger.info(f"✅ Contract sent successfully to {creator_email}")
                return {
                    "status": "success",
                    "message": "Contract sent to influencer successfully",
                    "action": "contract_sent",
                    "influencer_email": creator_email
                }
            else:
                logger.error(f"❌ Failed to send contract to {creator_email}")
                return {
                    "status": "error",
                    "message": "Failed to send contract to influencer"
                }
                
        except Exception as e:
            logger.error(f"❌ Error sending contract to influencer: {str(e)}")
            return {
                "status": "error",
                "message": f"Failed to send contract: {str(e)}"
            }
    
    async def _send_regret_to_influencer(
        self, 
        decision_data: Dict[str, Any], 
        sponsor_message: Optional[str]
    ) -> Dict[str, Any]:
        """
        😔 Send regret email to influencer after sponsor rejection
        """
        try:
            call_data = decision_data["call_data"]
            campaign_data = decision_data["campaign_data"]
            creator_email = decision_data["creator_email"]  # Use stored creator email
            
            influencer_data = call_data.get("influencer_data", {})
            influencer_name = influencer_data.get("name", "Influencer")
            campaign_name = campaign_data.get("campaign_name", "the campaign")
            brand_name = campaign_data.get("brand_name", "the brand")
            
            logger.info(f"😔 Sending regret email to creator: {creator_email}")
            
            # Create regret email subject
            subject = f"Update on {campaign_name} Collaboration"
            
            # Create regret email content
            if sponsor_message:
                custom_message = f"\n\nMessage from {brand_name}:\n\"{sponsor_message}\""
            else:
                custom_message = ""
            
            message = f"""
Hi {influencer_name},

Thank you for your time and interest in collaborating with {brand_name} on {campaign_name}.

After careful consideration of our recent conversation and campaign requirements, we have decided to move forward with a different approach for this particular campaign.

We genuinely appreciate the time you took to discuss this opportunity with us, and we were impressed by your enthusiasm and professionalism.{custom_message}

We hope to have the opportunity to work together on future campaigns that might be a better fit.

Thank you again for your time and consideration.

Best regards,
{brand_name} Team
via InfluencerFlow AI
            """
            
            # Send regret email
            success = await self.email_service.send_notification_email(
                to_email=creator_email,
                subject=subject,
                message=message
            )
            
            if success:
                logger.info(f"📧 Regret email sent successfully to {creator_email}")
                return {
                    "status": "success",
                    "message": "Regret email sent to influencer successfully",
                    "action": "regret_sent",
                    "influencer_email": creator_email
                }
            else:
                logger.error(f"❌ Failed to send regret email to {creator_email}")
                return {
                    "status": "error",
                    "message": "Failed to send regret email to influencer"
                }
                
        except Exception as e:
            logger.error(f"❌ Error sending regret email: {str(e)}")
            return {
                "status": "error",
                "message": f"Failed to send regret email: {str(e)}"
            }
    
    def get_pending_decisions(self) -> Dict[str, Any]:
        """
        📋 Get all pending sponsor decisions from Supabase database
        """
        try:
            if not supabase_db.supabase:
                return {
                    "total_pending": 0,
                    "decisions": [],
                    "message": "Database not available"
                }
            
            # Query pending decisions from database
            result = supabase_db.supabase.table("agent_decisions").select("*").eq("status", "pending").execute()
            
            if not result.data:
                return {
                    "total_pending": 0,
                    "decisions": []
                }
            
            # Format decisions for response
            decisions = []
            for data in result.data:
                decisions.append({
                    "decision_id": data["decision_id"],
                    "conversation_id": data.get("conversation_id"),
                    "campaign_name": data["campaign_data"].get("campaign_name"),
                    "influencer_name": data["call_data"].get("influencer_data", {}).get("name"),
                    "creator_email": data.get("creator_email"),
                    "sponsor_email": data.get("sponsor_email"),
                    "final_rate": data.get("final_rate"),
                    "created_at": data["created_at"],
                    "expires_at": data["expires_at"],
                    "status": data["status"]
                })
            
            return {
                "total_pending": len(decisions),
                "decisions": decisions
            }
            
        except Exception as e:
            logger.error(f"❌ Error getting pending decisions: {str(e)}")
            return {
                "total_pending": 0,
                "decisions": [],
                "error": str(e)
            }
    
    async def _store_decision_in_database(
        self,
        decision_id: str,
        call_data: Dict[str, Any],
        campaign_data: Dict[str, Any],
        analytics_report: Dict[str, Any],
        sponsor_email: str,
        creator_email: str,
        conversation_id: str = None
    ) -> bool:
        """
        💾 Store decision data in Supabase database
        """
        try:
            if not supabase_db.supabase:
                logger.warning("⚠️ Supabase not available, decision not stored")
                return False
            
            # Prepare data for database
            decision_data = {
                "decision_id": decision_id,
                "conversation_id": conversation_id or call_data.get("conversation_id"),
                "campaign_id": campaign_data.get("id"),  # If available
                "creator_email": creator_email,
                "sponsor_email": sponsor_email,
                "status": "pending",
                "call_data": call_data,
                "campaign_data": campaign_data,
                "analytics_report": analytics_report,
                "final_rate": call_data.get("negotiation_results", {}).get("final_rate", 0),
                "expires_at": (datetime.now() + timedelta(hours=48)).isoformat(),
                "created_at": datetime.now().isoformat()
            }
            
            # Insert into database
            result = supabase_db.supabase.table("agent_decisions").insert(decision_data).execute()
            
            if result.data:
                logger.info(f"✅ Decision stored in database: {decision_id}")
                return True
            else:
                logger.error(f"❌ Failed to store decision in database: {decision_id}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Error storing decision in database: {str(e)}")
            return False
    
    async def _get_decision_from_database(self, decision_id: str) -> Optional[Dict[str, Any]]:
        """
        🔍 Retrieve decision data from Supabase database
        """
        try:
            if not supabase_db.supabase:
                logger.warning("⚠️ Supabase not available")
                return None
            
            # Query database for decision
            result = supabase_db.supabase.table("agent_decisions").select("*").eq("decision_id", decision_id).execute()
            
            if result.data and len(result.data) > 0:
                decision_data = result.data[0]
                
                # Check if decision has expired - handle timezone properly
                expires_at_str = decision_data["expires_at"]
                
                # Remove timezone info from expires_at to compare with timezone-naive datetime.now()
                if expires_at_str.endswith('Z'):
                    expires_at_str = expires_at_str[:-1]  # Remove 'Z'
                elif '+' in expires_at_str:
                    expires_at_str = expires_at_str.split('+')[0]  # Remove timezone offset
                
                expires_at = datetime.fromisoformat(expires_at_str)
                
                if datetime.now() > expires_at:
                    # Mark as expired
                    await self._update_decision_status(decision_id, "expired")
                    logger.warning(f"⏰ Decision {decision_id} has expired")
                    return None
                
                logger.info(f"✅ Retrieved decision from database: {decision_id}")
                return decision_data
            else:
                logger.warning(f"⚠️ Decision not found in database: {decision_id}")
                return None
                
        except Exception as e:
            logger.error(f"❌ Error retrieving decision from database: {str(e)}")
            return None
    
    async def _update_decision_status(
        self,
        decision_id: str,
        status: str,
        sponsor_message: str = None,
        contract_sent: bool = None
    ) -> bool:
        """
        📝 Update decision status in Supabase database
        """
        try:
            if not supabase_db.supabase:
                return False
            
            update_data = {
                "status": status,
                "decided_at": datetime.now().isoformat() if status in ["approved", "rejected"] else None,
                "updated_at": datetime.now().isoformat()
            }
            
            if sponsor_message:
                update_data["sponsor_message"] = sponsor_message
            
            if contract_sent is not None:
                update_data["contract_sent"] = contract_sent
            
            result = supabase_db.supabase.table("agent_decisions").update(update_data).eq("decision_id", decision_id).execute()
            
            if result.data:
                logger.info(f"✅ Updated decision status: {decision_id} -> {status}")
                return True
            else:
                logger.error(f"❌ Failed to update decision status: {decision_id}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Error updating decision status: {str(e)}")
            return False

# Create global analytics service instance
analytics_service = CallAnalyticsService() 