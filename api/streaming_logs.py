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
        """Negotiations phase with streaming updates"""
        state.current_stage = "negotiations"
        
        if not state.discovered_influencers:
            await self.stream_update("⚠️ No influencers discovered for negotiations", "negotiations", 50)
            return
        
        # Store current state for contract email access
        self._current_state = state
        
        total_influencers = len(state.discovered_influencers)
        base_progress = 40
        progress_per_influencer = 30 / total_influencers if total_influencers > 0 else 0
        
        # Process each influencer with streaming updates
        for i, influencer_match in enumerate(state.discovered_influencers):
            creator = influencer_match.creator
            current_progress = base_progress + (i * progress_per_influencer)
            
            await self.stream_update(
                f"📞 Calling {creator.name} ({i+1}/{total_influencers})...", 
                "negotiating", 
                int(current_progress),
                {"creator_name": creator.name, "creator_index": i+1, "total_creators": total_influencers}
            )
            
            # Create negotiation record
            negotiation = await self._conduct_negotiation_with_streaming(creator, state.campaign_data, influencer_match, i+1, total_creators)
            state.negotiations.append(negotiation)
            
            if negotiation.status.value == "success":
                state.successful_negotiations += 1
                state.total_cost += negotiation.final_rate
                await self.stream_update(
                    f"✅ Successful negotiation: {creator.name} - ${negotiation.final_rate:,}", 
                    "success", 
                    int(current_progress + progress_per_influencer),
                    {"creator_name": creator.name, "final_rate": negotiation.final_rate}
                )
            else:
                state.failed_negotiations += 1
                await self.stream_update(
                    f"❌ Failed negotiation: {creator.name}", 
                    "failed", 
                    int(current_progress + progress_per_influencer),
                    {"creator_name": creator.name, "failure_reason": negotiation.failure_reason}
                )
    
    async def _conduct_negotiation_with_streaming(self, creator, campaign_data, influencer_match, creator_index, total_creators):
        """Conduct negotiation with streaming updates"""
        from models.campaign import NegotiationState, NegotiationStatus
        
        negotiation = NegotiationState(
            creator_id=creator.id,
            campaign_id=campaign_data.id
        )
        
        try:
            await self.stream_update(
                f"☎️ Dialing {creator.name} at {creator.phone_number}...", 
                "calling", 
                None,
                {"creator_name": creator.name, "phone": creator.phone_number}
            )
            
            # Real voice service negotiation
            success, call_data = await self._conduct_real_negotiation(creator, campaign_data, influencer_match)
            
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
                    f"🎉 {creator.name} accepted ${negotiation.final_rate:,} for the campaign!", 
                    "accepted", 
                    None,
                    {"creator_name": creator.name, "final_rate": negotiation.final_rate, "duration": negotiation.call_duration_seconds}
                )
            else:
                negotiation.status = NegotiationStatus.FAILED
                negotiation.failure_reason = call_data.get("failure_reason", "Negotiation failed")
                negotiation.conversation_id = call_data.get("conversation_id")
                
                await self.stream_update(
                    f"💔 {creator.name} declined the campaign offer", 
                    "declined", 
                    None,
                    {"creator_name": creator.name, "reason": negotiation.failure_reason}
                )
            
            negotiation.completed_at = datetime.now()
            return negotiation
            
        except Exception as e:
            await self.stream_update(f"❌ Error calling {creator.name}: {str(e)}", "error", None)
            negotiation.status = NegotiationStatus.FAILED
            negotiation.failure_reason = str(e)
            negotiation.completed_at = datetime.now()
            return negotiation
    
    async def _run_contracts_phase_with_streaming(self, state: CampaignOrchestrationState):
        """Contracts phase with streaming updates"""
        state.current_stage = "contracts"
        
        successful_negotiations = [
            neg for neg in state.negotiations 
            if neg.status.value == "success"
        ]
        
        if not successful_negotiations:
            await self.stream_update("⚠️ No successful negotiations - skipping contracts", "contracts", 85)
            return
        
        await self.stream_update(
            f"📝 Generating {len(successful_negotiations)} contracts...", 
            "contracts", 
            85
        )
        
        # Generate contracts and send via email
        for i, negotiation in enumerate(successful_negotiations):
            try:
                # Generate contract data
                contract = self._create_contract(negotiation, state.campaign_data)
                state.contracts.append(contract)
                
                # Update negotiation with contract info
                negotiation.negotiated_terms["contract_generated"] = True
                negotiation.negotiated_terms["contract_id"] = contract["contract_id"]
                
                await self.stream_update(
                    f"📄 Contract generated: {contract['contract_id']}", 
                    "contract_generated", 
                    85 + (i * 5)
                )
                
                # Send contract via analytics workflow
                await self.stream_update(
                    f"📧 Sending to sponsor for approval...", 
                    "sending_approval", 
                    85 + (i * 5) + 2
                )
                
                await self._send_contract_email(negotiation, state.campaign_data, contract)
                
            except Exception as e:
                await self.stream_update(f"❌ Contract generation failed: {e}", "error", None)
    
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