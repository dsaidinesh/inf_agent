# api/decision_api.py
from fastapi import APIRouter, HTTPException, Form, Query
from fastapi.responses import HTMLResponse, RedirectResponse
from typing import Dict, Any, Optional
import logging

from services.analytics_service import analytics_service

logger = logging.getLogger(__name__)

decision_router = APIRouter()

@decision_router.get("/approve/{decision_id}")
async def approve_decision(decision_id: str):
    """
    ✅ Approve sponsor decision - sends contract to influencer
    """
    try:
        logger.info(f"📊 Processing approval for decision: {decision_id}")
        
        result = await analytics_service.process_sponsor_decision(
            decision_id=decision_id,
            decision="approve"
        )
        
        if result["status"] == "success":
            return HTMLResponse(content=f"""
            <!DOCTYPE html>
            <html>
            <head>
                <title>Decision Approved</title>
                <style>
                    body {{ font-family: Arial, sans-serif; text-align: center; padding: 50px; }}
                    .success {{ color: #28a745; font-size: 24px; margin: 20px 0; }}
                    .details {{ background: #f8f9fa; padding: 20px; border-radius: 8px; margin: 20px auto; max-width: 500px; }}
                </style>
            </head>
            <body>
                <h1>✅ Decision Approved!</h1>
                <div class="success">Contract has been sent to the influencer</div>
                <div class="details">
                    <p><strong>Decision ID:</strong> {decision_id}</p>
                    <p><strong>Action:</strong> {result.get('action', 'N/A')}</p>
                    <p><strong>Influencer Email:</strong> {result.get('influencer_email', 'N/A')}</p>
                </div>
                <p>The influencer will receive a contract email with all the negotiated terms.</p>
            </body>
            </html>
            """)
        else:
            # Handle error cases with user-friendly HTML instead of exceptions
            return HTMLResponse(content=f"""
            <!DOCTYPE html>
            <html>
            <head>
                <title>Decision Processing Issue</title>
                <style>
                    body {{ font-family: Arial, sans-serif; text-align: center; padding: 50px; }}
                    .error {{ color: #dc3545; font-size: 24px; margin: 20px 0; }}
                    .details {{ background: #f8f9fa; padding: 20px; border-radius: 8px; margin: 20px auto; max-width: 600px; }}
                    .info {{ background: #d1ecf1; padding: 15px; border-radius: 4px; margin: 20px 0; }}
                </style>
            </head>
            <body>
                <h1>⚠️ Decision Cannot Be Processed</h1>
                <div class="error">{result.get('message', 'Unknown error occurred')}</div>
                <div class="details">
                    <p><strong>Decision ID:</strong> {decision_id}</p>
                    <div class="info">
                        <p><strong>Possible reasons:</strong></p>
                        <ul style="text-align: left;">
                            <li>This decision link has already been used</li>
                            <li>The decision has expired (48-hour limit)</li>
                            <li>The server was restarted, clearing temporary data</li>
                        </ul>
                    </div>
                </div>
                <p>If you need to make a decision on this collaboration, please contact the campaign manager directly.</p>
            </body>
            </html>
            """, status_code=200)  # Use 200 instead of 400 for better user experience
            
    except Exception as e:
        logger.error(f"❌ Error processing approval: {str(e)}")
        # Return user-friendly error page instead of throwing exception
        return HTMLResponse(content=f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>System Error</title>
            <style>
                body {{ font-family: Arial, sans-serif; text-align: center; padding: 50px; }}
                .error {{ color: #dc3545; font-size: 24px; margin: 20px 0; }}
                .details {{ background: #f8f9fa; padding: 20px; border-radius: 8px; margin: 20px auto; max-width: 600px; }}
            </style>
        </head>
        <body>
            <h1>❌ System Error</h1>
            <div class="error">Unable to process your decision at this time</div>
            <div class="details">
                <p><strong>Decision ID:</strong> {decision_id}</p>
                <p>Please try again later or contact support if the issue persists.</p>
                <p><small>Error: {str(e)}</small></p>
            </div>
        </body>
        </html>
        """, status_code=500)

@decision_router.get("/reject/{decision_id}")
async def reject_decision_form(decision_id: str):
    """
    ❌ Show rejection form for sponsor to provide message
    """
    return HTMLResponse(content=f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Reject Decision</title>
        <style>
            body {{ font-family: Arial, sans-serif; max-width: 600px; margin: 50px auto; padding: 20px; }}
            .form-group {{ margin: 20px 0; }}
            label {{ display: block; margin-bottom: 5px; font-weight: bold; }}
            textarea {{ width: 100%; padding: 10px; border: 1px solid #ddd; border-radius: 4px; }}
            button {{ background: #dc3545; color: white; padding: 12px 24px; border: none; border-radius: 4px; cursor: pointer; }}
            button:hover {{ background: #c82333; }}
            .warning {{ background: #fff3cd; padding: 15px; border-radius: 4px; margin: 20px 0; }}
        </style>
    </head>
    <body>
        <h1>❌ Reject Collaboration</h1>
        <div class="warning">
            <strong>Note:</strong> This will send a polite rejection email to the influencer.
        </div>
        
        <form method="post" action="/api/decision/reject/{decision_id}">
            <div class="form-group">
                <label for="message">Optional Message to Influencer:</label>
                <textarea id="message" name="message" rows="4" placeholder="We appreciate your interest, but we've decided to go with a different approach for this campaign..."></textarea>
            </div>
            
            <div class="form-group">
                <button type="submit">Send Rejection Email</button>
            </div>
        </form>
        
        <p><small><strong>Decision ID:</strong> {decision_id}</small></p>
    </body>
    </html>
    """)

@decision_router.post("/reject/{decision_id}")
async def reject_decision(decision_id: str, message: str = Form("")):
    """
    ❌ Process rejection decision - sends regret email to influencer
    """
    try:
        logger.info(f"📊 Processing rejection for decision: {decision_id}")
        
        result = await analytics_service.process_sponsor_decision(
            decision_id=decision_id,
            decision="reject",
            sponsor_message=message if message.strip() else None
        )
        
        if result["status"] == "success":
            return HTMLResponse(content=f"""
            <!DOCTYPE html>
            <html>
            <head>
                <title>Decision Rejected</title>
                <style>
                    body {{ font-family: Arial, sans-serif; text-align: center; padding: 50px; }}
                    .rejected {{ color: #dc3545; font-size: 24px; margin: 20px 0; }}
                    .details {{ background: #f8f9fa; padding: 20px; border-radius: 8px; margin: 20px auto; max-width: 500px; }}
                </style>
            </head>
            <body>
                <h1>❌ Decision Rejected</h1>
                <div class="rejected">Regret email has been sent to the influencer</div>
                <div class="details">
                    <p><strong>Decision ID:</strong> {decision_id}</p>
                    <p><strong>Action:</strong> {result.get('action', 'N/A')}</p>
                    <p><strong>Influencer Email:</strong> {result.get('influencer_email', 'N/A')}</p>
                </div>
                <p>The influencer has been politely notified that we won't be proceeding with this collaboration.</p>
            </body>
            </html>
            """)
        else:
            # Handle error cases with user-friendly HTML instead of exceptions
            return HTMLResponse(content=f"""
            <!DOCTYPE html>
            <html>
            <head>
                <title>Decision Processing Issue</title>
                <style>
                    body {{ font-family: Arial, sans-serif; text-align: center; padding: 50px; }}
                    .error {{ color: #dc3545; font-size: 24px; margin: 20px 0; }}
                    .details {{ background: #f8f9fa; padding: 20px; border-radius: 8px; margin: 20px auto; max-width: 600px; }}
                    .info {{ background: #d1ecf1; padding: 15px; border-radius: 4px; margin: 20px 0; }}
                </style>
            </head>
            <body>
                <h1>⚠️ Decision Cannot Be Processed</h1>
                <div class="error">{result.get('message', 'Unknown error occurred')}</div>
                <div class="details">
                    <p><strong>Decision ID:</strong> {decision_id}</p>
                    <div class="info">
                        <p><strong>Possible reasons:</strong></p>
                        <ul style="text-align: left;">
                            <li>This decision link has already been used</li>
                            <li>The decision has expired (48-hour limit)</li>
                            <li>The server was restarted, clearing temporary data</li>
                        </ul>
                    </div>
                </div>
                <p>If you need to make a decision on this collaboration, please contact the campaign manager directly.</p>
            </body>
            </html>
            """, status_code=200)
            
    except Exception as e:
        logger.error(f"❌ Error processing rejection: {str(e)}")
        # Return user-friendly error page instead of throwing exception
        return HTMLResponse(content=f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>System Error</title>
            <style>
                body {{ font-family: Arial, sans-serif; text-align: center; padding: 50px; }}
                .error {{ color: #dc3545; font-size: 24px; margin: 20px 0; }}
                .details {{ background: #f8f9fa; padding: 20px; border-radius: 8px; margin: 20px auto; max-width: 600px; }}
            </style>
        </head>
        <body>
            <h1>❌ System Error</h1>
            <div class="error">Unable to process your decision at this time</div>
            <div class="details">
                <p><strong>Decision ID:</strong> {decision_id}</p>
                <p>Please try again later or contact support if the issue persists.</p>
                <p><small>Error: {str(e)}</small></p>
            </div>
        </body>
        </html>
        """, status_code=500)

@decision_router.get("/pending")
async def get_pending_decisions():
    """
    📋 Get all pending sponsor decisions
    """
    try:
        pending = analytics_service.get_pending_decisions()
        return {
            "status": "success",
            "pending_decisions": pending
        }
    except Exception as e:
        logger.error(f"❌ Error getting pending decisions: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get pending decisions: {str(e)}")

@decision_router.post("/test-analytics")
async def test_analytics_workflow(test_data: Dict[str, Any]):
    """
    🧪 Test the analytics workflow with sample data
    """
    try:
        logger.info("🧪 Testing analytics workflow...")
        
        # Sample call data
        call_data = {
            "conversation_id": "test_conv_12345",
            "call_duration_seconds": 180,
            "status": "completed",
            "negotiation_results": {
                "final_rate": test_data.get("final_rate", 2500),
                "deliverables": ["1 Instagram post", "3 Instagram stories"],
                "timeline": "2 weeks",
                "creator_enthusiasm": 8,
                "special_terms": ["Usage rights for 6 months"]
            },
            "influencer_data": {
                "name": test_data.get("influencer_name", "Test Influencer"),
                "email": test_data.get("influencer_email", "test@example.com"),
                "platform": "Instagram"
            }
        }
        
        # Sample campaign data
        campaign_data = {
            "campaign_name": test_data.get("campaign_name", "Test Product Launch"),
            "brand_name": test_data.get("brand_name", "Test Brand"),
            "product_name": "Test Product Pro",
            "total_budget": 10000,
            "offered_rate": test_data.get("original_rate", 2000)
        }
        
        # Test sponsor email
        sponsor_email = test_data.get("sponsor_email", "sponsor@testbrand.com")
        
        # Process the completed call
        result = await analytics_service.process_completed_call(
            call_data=call_data,
            campaign_data=campaign_data,
            sponsor_email=sponsor_email
        )
        
        if result["status"] == "success":
            return {
                "status": "success",
                "message": "Analytics workflow test completed successfully",
                "decision_id": result["decision_id"],
                "analytics_sent": result["email_sent"],
                "test_urls": {
                    "approve": f"/api/decision/approve/{result['decision_id']}",
                    "reject": f"/api/decision/reject/{result['decision_id']}"
                },
                "analytics_report": result["analytics_report"]
            }
        else:
            return {
                "status": "error",
                "message": result["message"]
            }
            
    except Exception as e:
        logger.error(f"❌ Error testing analytics workflow: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Test failed: {str(e)}") 