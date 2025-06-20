from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
import asyncio
import json
import logging
from datetime import datetime
from typing import AsyncGenerator, Optional, Dict, Any

# Import your existing project components
from agents.enhanced_orchestrator import EnhancedCampaignOrchestrator
from models.campaign import CampaignData, CampaignOrchestrationState
from config.settings import settings

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Agent Streaming Logs", version="1.0.0")

# Add CORS middleware to allow frontend connections
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your frontend domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global orchestrator instance
orchestrator: Optional[EnhancedCampaignOrchestrator] = None

def get_orchestrator() -> EnhancedCampaignOrchestrator:
    """Get or create orchestrator instance"""
    global orchestrator
    if orchestrator is None:
        orchestrator = EnhancedCampaignOrchestrator()
    return orchestrator

class StreamingOrchestrator(EnhancedCampaignOrchestrator):
    """
    Enhanced orchestrator that yields streaming updates during campaign execution
    """
    
    def __init__(self, stream_callback=None):
        super().__init__()
        self.stream_callback = stream_callback
    
    async def stream_update(self, message: str, status: str, progress: int = None, data: Dict[str, Any] = None):
        """Send a streaming update to the frontend"""
        if self.stream_callback:
            update = {
                'message': message,
                'status': status,
                'timestamp': datetime.now().isoformat(),
                'progress': progress,
                'data': data or {}
            }
            await self.stream_callback(f"data: {json.dumps(update)}\n\n")
    
    async def orchestrate_enhanced_campaign_with_streaming(
        self,
        campaign_data: CampaignData,
        task_id: str
    ) -> CampaignOrchestrationState:
        """
        Enhanced campaign orchestration with real-time streaming updates
        """
        
        await self.stream_update(
            "🎯 Starting enhanced campaign orchestration...", 
            "starting", 
            0,
            {"task_id": task_id, "campaign_name": f"{campaign_data.brand_name} - {campaign_data.product_name}"}
        )
        
        # Initialize state
        state = CampaignOrchestrationState(
            campaign_id=campaign_data.id,
            campaign_data=campaign_data
        )
        
        try:
            # Phase 1: Discovery
            await self.stream_update("🔍 Phase 1: Starting influencer discovery...", "discovery", 10)
            await self._run_discovery_phase_with_streaming(state)
            
            # Phase 2: AI Strategy Generation  
            await self.stream_update("🧠 Phase 2: Generating AI strategy...", "strategy", 25)
            await self._run_strategy_phase_with_streaming(state)
            
            # Phase 3: Negotiations
            await self.stream_update("📞 Phase 3: Starting negotiations...", "negotiations", 40)
            await self._run_negotiations_phase_with_streaming(state)
            
            # Phase 4: Contracts
            await self.stream_update("📝 Phase 4: Generating contracts...", "contracts", 80)
            await self._run_contracts_phase_with_streaming(state)
            
            # Phase 5: Completion
            await self.stream_update("🏁 Phase 5: Finalizing campaign...", "completion", 95)
            await self._run_completion_phase_with_streaming(state)
            
            await self.stream_update(
                f"✅ Campaign orchestration completed successfully!", 
                "completed", 
                100,
                {
                    "successful_negotiations": state.successful_negotiations,
                    "total_contracts": len(state.contracts),
                    "total_cost": state.total_cost
                }
            )
            
            return state
            
        except Exception as e:
            await self.stream_update(f"❌ Campaign orchestration failed: {str(e)}", "error", -1)
            state.current_stage = "failed"
            state.completed_at = datetime.now()
            return state
    
    async def _run_discovery_phase_with_streaming(self, state: CampaignOrchestrationState):
        """Discovery phase with streaming updates"""
        state.current_stage = "discovery"
        
        await self.stream_update("🔍 Searching for matching influencers...", "discovery", 12)
        
        # Use discovery agent to find influencers
        discovered = await self.discovery_agent.discover_influencers(
            product_niche=state.campaign_data.product_niche,
            total_budget=state.campaign_data.total_budget
        )
        
        state.discovered_influencers = discovered
        
        await self.stream_update(
            f"🔍 Discovery complete: Found {len(discovered)} matching influencers", 
            "discovery", 
            20,
            {"influencer_count": len(discovered)}
        )
        
        # 📝 NEW: Log influencer discovery to outreach_logs table
        if discovered:
            try:
                from services.outreach_logger import outreach_logger
                await outreach_logger.log_influencer_discovery(
                    campaign_id=state.campaign_id,
                    discovered_influencers=discovered
                )
                await self.stream_update("📝 Logged influencer discoveries to database", "discovery", 22)
                logger.info(f"📝 Logged discovery of {len(discovered)} influencers to outreach_logs")
            except Exception as e:
                logger.warning(f"⚠️ Failed to log influencer discovery: {str(e)}")
                await self.stream_update("⚠️ Warning: Discovery logging failed", "discovery", 22)
        
        # Stream details about discovered influencers
        for i, match in enumerate(discovered[:3]):  # Show top 3
            await self.stream_update(
                f"   👤 {match.creator.name} - {match.similarity_score:.2f} match, ${match.estimated_rate:,}", 
                "discovery", 
                20 + (i * 2)
            )
    
    async def _run_strategy_phase_with_streaming(self, state: CampaignOrchestrationState):
        """Strategy phase with streaming updates"""
        state.current_stage = "strategy"
        
        if self.groq_client:
            try:
                await self.stream_update("🧠 Generating AI-powered negotiation strategy...", "strategy", 30)
                strategy = await self._generate_ai_strategy(state)
                state.ai_strategy = strategy
                await self.stream_update("🧠 AI strategy generated successfully", "strategy", 35)
            except Exception as e:
                await self.stream_update(f"⚠️ AI strategy generation failed: {e}", "strategy", 35)
                state.ai_strategy = "Default strategy due to AI error"
        else:
            await self.stream_update("📋 Using default strategy (Groq not available)", "strategy", 35)
            state.ai_strategy = "Default strategy - Groq not available"
    
    async def _run_negotiations_phase_with_streaming(self, state: CampaignOrchestrationState):
        """Negotiations phase with detailed streaming updates"""
        state.current_stage = "negotiations"
        
        if not state.discovered_influencers:
            await self.stream_update("⚠️ No influencers discovered for negotiations", "negotiations", 50)
            return
        
        # Store current state for contract email access
        self._current_state = state
        
        total_influencers = len(state.discovered_influencers)
        base_progress = 40
        progress_per_influencer = 35 / total_influencers if total_influencers > 0 else 0
        
        await self.stream_update(
            f"📞 Starting negotiations with {total_influencers} creators...", 
            "negotiations_start", 
            base_progress,
            {"total_creators": total_influencers}
        )
        
        # Process each influencer with detailed streaming updates
        for i, influencer_match in enumerate(state.discovered_influencers):
            creator = influencer_match.creator
            current_progress = base_progress + (i * progress_per_influencer)
            
            # Show which creator we're calling now
            await self.stream_update(
                f"👤 Calling creator {i+1}/{total_influencers}: {creator.name}", 
                "creator_start", 
                int(current_progress),
                {
                    "creator_name": creator.name, 
                    "creator_index": i+1, 
                    "total_creators": total_influencers,
                    "followers": creator.followers,
                    "estimated_rate": influencer_match.estimated_rate
                }
            )
            
            # Create negotiation record with detailed streaming
            negotiation = await self._conduct_negotiation_with_streaming(creator, state.campaign_data, influencer_match, i+1, total_influencers)
            state.negotiations.append(negotiation)
            
            # Update totals and show progress
            if negotiation.status.value == "success":
                state.successful_negotiations += 1
                state.total_cost += negotiation.final_rate
                
                # Show running totals
                await self.stream_update(
                    f"✅ Progress: {state.successful_negotiations} accepted, ${state.total_cost:,} total cost", 
                    "progress_update", 
                    int(current_progress + progress_per_influencer * 0.8),
                    {
                        "successful_count": state.successful_negotiations,
                        "total_cost": state.total_cost,
                        "completed_count": i+1,
                        "remaining_count": total_influencers - (i+1)
                    }
                )
            else:
                state.failed_negotiations += 1
                
                # Show running totals for failures too
                await self.stream_update(
                    f"📊 Progress: {i+1}/{total_influencers} contacted, {state.successful_negotiations} accepted", 
                    "progress_update", 
                    int(current_progress + progress_per_influencer * 0.8),
                    {
                        "successful_count": state.successful_negotiations,
                        "failed_count": state.failed_negotiations,
                        "completed_count": i+1,
                        "remaining_count": total_influencers - (i+1)
                    }
                )
            
            # Small delay between creators to make it feel more natural
            if i < total_influencers - 1:  # Don't delay after the last creator
                await self.stream_update(
                    f"⏭️ Moving to next creator...", 
                    "transition", 
                    int(current_progress + progress_per_influencer),
                    {"next_creator_index": i+2}
                )
                import asyncio
                await asyncio.sleep(0.5)
        
        # Final summary of negotiations phase
        await self.stream_update(
            f"📞 Negotiations completed: {state.successful_negotiations}/{total_influencers} creators accepted", 
            "negotiations_complete", 
            75,
            {
                "successful_negotiations": state.successful_negotiations,
                "failed_negotiations": state.failed_negotiations,
                "total_cost": state.total_cost,
                "average_rate": state.total_cost / max(1, state.successful_negotiations)
            }
        )
    
    async def _conduct_negotiation_with_streaming(self, creator, campaign_data, influencer_match, creator_index, total_creators):
        """Conduct negotiation with detailed streaming updates"""
        from models.campaign import NegotiationState, NegotiationStatus
        
        negotiation = NegotiationState(
            creator_id=creator.id,
            campaign_id=campaign_data.id
        )
        
        try:
            # Phase 1: Initial call setup
            await self.stream_update(
                f"📱 Preparing call to {creator.name}...", 
                "call_setup", 
                None,
                {"creator_name": creator.name, "creator_index": creator_index, "total_creators": total_creators}
            )
            
            # Phase 2: Dialing
            await self.stream_update(
                f"☎️ Dialing {creator.name} at {creator.phone_number[-4:]}****...", 
                "dialing", 
                None,
                {"creator_name": creator.name, "phone_masked": f"{creator.phone_number[-4:]}****"}
            )
            
            # Phase 3: Call connecting (add small delay to show this step)
            import asyncio
            await asyncio.sleep(0.5)
            await self.stream_update(
                f"📞 Call connecting to {creator.name}...", 
                "connecting", 
                None,
                {"creator_name": creator.name}
            )
            
            # Phase 4: Call in progress
            await self.stream_update(
                f"🎤 Call in progress with {creator.name} - negotiating terms...", 
                "negotiating", 
                None,
                {"creator_name": creator.name, "estimated_rate": influencer_match.estimated_rate}
            )
            
            # Real voice service negotiation
            success, call_data = await self._conduct_real_negotiation(creator, campaign_data, influencer_match)
            
            # Phase 5: Call completed - show results
            call_duration = call_data.get("duration_seconds", 0)
            if call_duration > 0:
                await self.stream_update(
                    f"📋 Call with {creator.name} completed ({call_duration}s)", 
                    "call_completed", 
                    None,
                    {"creator_name": creator.name, "duration": call_duration}
                )
            
            # Phase 6: Result analysis
            if success:
                negotiation.status = NegotiationStatus.SUCCESS
                negotiation.final_rate = call_data.get("final_rate", influencer_match.estimated_rate)
                negotiation.conversation_id = call_data.get("conversation_id")
                negotiation.call_duration_seconds = call_data.get("duration_seconds", 0)
                negotiation.negotiated_terms = call_data.get("terms", {
                    "deliverables": ["1 Instagram post", "3 Stories"],
                    "timeline": "2 weeks",
                    "usage_rights": "1 year"
                })
                
                await self.stream_update(
                    f"🎉 SUCCESS: {creator.name} accepted ${negotiation.final_rate:,}!", 
                    "accepted", 
                    None,
                    {
                        "creator_name": creator.name, 
                        "final_rate": negotiation.final_rate, 
                        "duration": negotiation.call_duration_seconds,
                        "savings": max(0, influencer_match.estimated_rate - negotiation.final_rate),
                        "conversation_id": negotiation.conversation_id
                    }
                )
                
                # Show that outreach logging is happening
                if negotiation.conversation_id:
                    await self.stream_update(
                        f"📝 Logged successful call with conversation ID: {negotiation.conversation_id}", 
                        "outreach_logged", 
                        None,
                        {"conversation_id": negotiation.conversation_id}
                    )
            else:
                negotiation.status = NegotiationStatus.FAILED
                negotiation.failure_reason = call_data.get("failure_reason", "Negotiation failed")
                negotiation.conversation_id = call_data.get("conversation_id")
                
                await self.stream_update(
                    f"❌ DECLINED: {creator.name} - {negotiation.failure_reason}", 
                    "declined", 
                    None,
                    {"creator_name": creator.name, "reason": negotiation.failure_reason, "conversation_id": negotiation.conversation_id}
                )
                
                # Show that outreach logging is happening for failed calls too
                if negotiation.conversation_id:
                    await self.stream_update(
                        f"📝 Logged failed call with conversation ID: {negotiation.conversation_id}", 
                        "outreach_logged", 
                        None,
                        {"conversation_id": negotiation.conversation_id}
                    )
            
            negotiation.completed_at = datetime.now()
            return negotiation
            
        except Exception as e:
            # Don't show technical timeout errors - show user-friendly messages
            if "timeout" in str(e).lower():
                await self.stream_update(
                    f"⏱️ {creator.name} call taking longer than expected - continuing...", 
                    "call_delayed", 
                    None,
                    {"creator_name": creator.name}
                )
            else:
                await self.stream_update(
                    f"❌ Unable to reach {creator.name} - call failed", 
                    "call_failed", 
                    None,
                    {"creator_name": creator.name, "error": "Connection failed"}
                )
            
            negotiation.status = NegotiationStatus.FAILED
            negotiation.failure_reason = "Call connection failed"
            negotiation.completed_at = datetime.now()
            return negotiation
    
    async def _run_contracts_phase_with_streaming(self, state: CampaignOrchestrationState):
        """Contracts phase with detailed streaming updates"""
        state.current_stage = "contracts"
        
        successful_negotiations = [
            neg for neg in state.negotiations 
            if neg.status.value == "success"
        ]
        
        if not successful_negotiations:
            await self.stream_update("⚠️ No successful negotiations - skipping contracts", "contracts", 80)
            return
        
        await self.stream_update(
            f"📝 Preparing {len(successful_negotiations)} contracts for successful negotiations...", 
            "contracts_start", 
            80,
            {"contract_count": len(successful_negotiations)}
        )
        
        # Generate contracts and send via email
        for i, negotiation in enumerate(successful_negotiations):
            try:
                creator_name = next(
                    (match.creator.name for match in state.discovered_influencers 
                     if match.creator.id == negotiation.creator_id), 
                    "Unknown Creator"
                )
                
                await self.stream_update(
                    f"📄 Generating contract for {creator_name}...", 
                    "contract_generating", 
                    80 + (i * 3),
                    {"creator_name": creator_name, "contract_index": i+1}
                )
                
                # Generate contract data
                contract = self._create_contract(negotiation, state.campaign_data)
                state.contracts.append(contract)
                
                # Update negotiation with contract info
                negotiation.negotiated_terms["contract_generated"] = True
                negotiation.negotiated_terms["contract_id"] = contract["contract_id"]
                
                await self.stream_update(
                    f"✅ Contract ready: {contract['contract_id'][:8]}...", 
                    "contract_ready", 
                    80 + (i * 3) + 1,
                    {"creator_name": creator_name, "contract_id": contract['contract_id']}
                )
                
                # Send contract via analytics workflow
                await self.stream_update(
                    f"📧 Sending contract to sponsor for {creator_name}...", 
                    "contract_sending", 
                    80 + (i * 3) + 2,
                    {"creator_name": creator_name}
                )
                
                await self._send_contract_email(negotiation, state.campaign_data, contract)
                
                await self.stream_update(
                    f"✉️ Contract sent successfully for {creator_name}", 
                    "contract_sent", 
                    80 + (i * 3) + 3,
                    {"creator_name": creator_name}
                )
                
            except Exception as e:
                await self.stream_update(
                    f"❌ Contract generation failed for {creator_name}: {str(e)}", 
                    "contract_error", 
                    None,
                    {"creator_name": creator_name, "error": str(e)}
                )
        
        # Final contracts summary
        await self.stream_update(
            f"📝 All contracts completed: {len(state.contracts)} contracts sent to sponsor", 
            "contracts_complete", 
            95,
            {
                "total_contracts": len(state.contracts),
                "successful_negotiations": len(successful_negotiations)
            }
        )
    
    async def _run_completion_phase_with_streaming(self, state: CampaignOrchestrationState):
        """Completion phase with streaming updates"""
        state.current_stage = "completed"
        state.completed_at = datetime.now()
        
        # Calculate duration
        duration = (state.completed_at - state.started_at).total_seconds()
        
        await self.stream_update(
            f"🏁 Campaign completed in {duration:.1f} seconds", 
            "completed", 
            98,
            {
                "duration_seconds": duration,
                "successful_negotiations": state.successful_negotiations,
                "total_contracts": len(state.contracts),
                "total_cost": state.total_cost
            }
        )

async def enhanced_campaign_with_streaming(campaign_data: CampaignData, task_id: str) -> AsyncGenerator[str, None]:
    """
    Run enhanced campaign orchestration with real-time streaming updates
    """
    
    updates_queue = asyncio.Queue()
    
    async def stream_callback(message: str):
        """Callback to send updates to the frontend"""
        await updates_queue.put(message)
    
    # Create streaming orchestrator
    streaming_orchestrator = StreamingOrchestrator(stream_callback=stream_callback)
    
    # Start the campaign in a background task
    campaign_task = asyncio.create_task(
        streaming_orchestrator.orchestrate_enhanced_campaign_with_streaming(campaign_data, task_id)
    )
    
    try:
        # Stream updates as they come
        while not campaign_task.done():
            try:
                # Wait for either an update or task completion (with short timeout)
                update = await asyncio.wait_for(updates_queue.get(), timeout=0.1)
                yield update
            except asyncio.TimeoutError:
                # Check if task is still running
                if campaign_task.done():
                    break
                continue
        
        # Get any remaining updates
        while not updates_queue.empty():
            update = updates_queue.get_nowait()
            yield update
        
        # Wait for final result
        final_state = await campaign_task
        
        # Send final completion message
        final_update = {
            'message': f'🎯 Campaign orchestration completed!',
            'status': 'completed',
            'timestamp': datetime.now().isoformat(),
            'progress': 100,
            'data': {
                "final_state": "completed",
                "successful_negotiations": final_state.successful_negotiations,
                "total_contracts": len(final_state.contracts)
            }
        }
        yield f"data: {json.dumps(final_update)}\n\n"
        
    except Exception as e:
        error_update = {
            'message': f'❌ Campaign orchestration failed: {str(e)}',
            'status': 'error',
            'timestamp': datetime.now().isoformat(),
            'progress': -1
        }
        yield f"data: {json.dumps(error_update)}\n\n"

async def demo_agent_with_logging() -> AsyncGenerator[str, None]:
    """Demo agent function that yields progress updates (fallback for testing)"""
    yield f"data: {json.dumps({'message': 'Demo agent starting...', 'status': 'starting', 'timestamp': datetime.now().isoformat(), 'progress': 0})}\n\n"
    
    # Simulate agent work
    await asyncio.sleep(1)
    yield f"data: {json.dumps({'message': 'Processing data...', 'status': 'processing', 'timestamp': datetime.now().isoformat(), 'progress': 25})}\n\n"
    
    await asyncio.sleep(2)
    yield f"data: {json.dumps({'message': 'Analyzing results...', 'status': 'analyzing', 'timestamp': datetime.now().isoformat(), 'progress': 75})}\n\n"
    
    await asyncio.sleep(1)
    yield f"data: {json.dumps({'message': 'Task completed!', 'status': 'completed', 'timestamp': datetime.now().isoformat(), 'progress': 100})}\n\n"

@app.get("/agent/stream")
async def stream_agent_logs():
    """
    Endpoint that streams agent logs in real-time using Server-Sent Events (SSE).
    
    This is a demo endpoint - use /agent/campaign/stream for real campaigns
    """
    logger.info("Starting demo agent log stream")
    
    return StreamingResponse(
        demo_agent_with_logging(),
        media_type="text/plain",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Content-Type": "text/plain; charset=utf-8"
        }
    )

@app.post("/agent/campaign/stream")
async def stream_enhanced_campaign_logs(campaign_data: CampaignData):
    """
    Endpoint that streams real enhanced campaign orchestration logs
    """
    logger.info(f"Starting enhanced campaign stream: {campaign_data.brand_name} - {campaign_data.product_name}")
    
    task_id = f"campaign_{int(datetime.now().timestamp())}"
    
    return StreamingResponse(
        enhanced_campaign_with_streaming(campaign_data, task_id),
        media_type="text/plain",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Content-Type": "text/plain; charset=utf-8"
        }
    )

@app.get("/")
async def root():
    """Health check endpoint"""
    return {"message": "Agent Streaming API is running"}

@app.get("/health")
async def health_check():
    """Detailed health check with timestamp"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "service": "agent-streaming-logs"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info") 