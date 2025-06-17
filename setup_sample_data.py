# setup_sample_data.py
"""
🎯 Setup Sample Data for Campaign Trigger Testing
This script populates your Supabase database with sample campaigns and creators
so you can test the campaign trigger endpoints immediately.
"""

import asyncio
import logging
import uuid
from datetime import datetime, timedelta
from services.supabase_database import SupabaseDatabaseService

logger = logging.getLogger(__name__)

class SampleDataSetup:
    def __init__(self):
        self.db_service = SupabaseDatabaseService()
    
    async def setup_all_sample_data(self):
        """Setup all sample data for testing"""
        try:
            logger.info("🚀 Setting up sample data for campaign trigger testing...")
            
            # 1. Setup sample campaigns
            await self.setup_sample_campaigns()
            
            # 2. Setup sample creators
            await self.setup_sample_creators()
            
            logger.info("✅ Sample data setup completed successfully!")
            return True
            
        except Exception as e:
            logger.error(f"❌ Sample data setup failed: {str(e)}")
            return False
    
    async def setup_sample_campaigns(self):
        """Setup sample campaigns in Supabase"""
        sample_campaigns = [
            {
                "id": "11111111-2222-3333-4444-555555555555",  # tech_campaign_001
                "product_name": "TechPro Wireless Earbuds",
                "brand_name": "AudioMax Technologies",
                "product_description": "Premium wireless earbuds with noise cancellation and superior sound quality for tech enthusiasts and professionals",
                "target_audience": "Tech enthusiasts, gamers, and professionals aged 20-40",
                "campaign_goal": "Launch new product and establish market presence in tech community",
                "product_niche": "tech",
                "total_budget": 15000.0,
                "status": "active",
                "sponsor_email": "sponsor@audiomax-tech.com",
                "sponsor_name": "Sarah Johnson",
                "sponsor_phone": "+1-555-0123",
                "sponsor_company": "AudioMax Technologies Inc.",
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat()
            },
            {
                "id": "22222222-3333-4444-5555-666666666666",  # fitness_campaign_002 
                "product_name": "FitPro Protein Powder",
                "brand_name": "LifeFit Nutrition",
                "product_description": "Premium whey protein powder for muscle building and recovery, perfect for serious athletes and fitness enthusiasts",
                "target_audience": "Fitness enthusiasts, gym-goers, and athletes aged 18-35",
                "campaign_goal": "Increase brand awareness and drive sales in the fitness community",
                "product_niche": "fitness",
                "total_budget": 12000.0,
                "status": "active",
                "sponsor_email": "marketing@lifefit-nutrition.com",
                "sponsor_name": "Mike Rodriguez",
                "sponsor_phone": "+1-555-0456",
                "sponsor_company": "LifeFit Nutrition Corp.",
                "created_at": (datetime.now() - timedelta(days=1)).isoformat(),
                "updated_at": datetime.now().isoformat()
            },
            {
                "id": "33333333-4444-5555-6666-777777777777",  # beauty_campaign_003
                "product_name": "GlowUp Skincare Set",
                "brand_name": "PureGlow Beauty",
                "product_description": "Complete skincare routine set with natural ingredients for healthy, glowing skin",
                "target_audience": "Beauty enthusiasts and skincare lovers aged 16-35",
                "campaign_goal": "Build brand awareness and drive online sales",
                "product_niche": "beauty",
                "total_budget": 18000.0,
                "status": "active",
                "sponsor_email": "campaigns@pureglow-beauty.com",
                "sponsor_name": "Emma Chen",
                "sponsor_phone": "+1-555-0789",
                "sponsor_company": "PureGlow Beauty LLC",
                "created_at": (datetime.now() - timedelta(days=2)).isoformat(),
                "updated_at": datetime.now().isoformat()
            }
        ]
        
        try:
            if not self.db_service.supabase:
                logger.warning("⚠️ Supabase not available - campaigns not created")
                return
            
            for campaign in sample_campaigns:
                # Check if campaign already exists
                existing = self.db_service.supabase.table("campaigns").select("id").eq("id", campaign["id"]).execute()
                
                if existing.data:
                    logger.info(f"📋 Campaign {campaign['id']} already exists - updating...")
                    # Update existing campaign
                    self.db_service.supabase.table("campaigns").update(campaign).eq("id", campaign["id"]).execute()
                else:
                    logger.info(f"📋 Creating campaign: {campaign['product_name']}")
                    # Insert new campaign
                    self.db_service.supabase.table("campaigns").insert(campaign).execute()
            
            logger.info(f"✅ Setup {len(sample_campaigns)} sample campaigns")
            
        except Exception as e:
            logger.error(f"❌ Error setting up campaigns: {str(e)}")
            raise
    
    async def setup_sample_creators(self):
        """Setup sample creators in Supabase"""
        sample_creators = [
            {
                "id": "aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee",  # creator_tech_001
                "name": "TechReviewer_Sarah",
                "email": "sarah.tech@example.com",
                "platform": "YouTube",
                "followers_count": "850K",
                "followers_count_numeric": 850000,
                "niche": "tech",
                "engagement_rate": 4.8,
                "phone_number": "+1-555-TECH-001"
            },
            {
                "id": "bbbbbbbb-cccc-dddd-eeee-ffffffffffff",  # creator_tech_002
                "name": "GadgetGuru_Alex",
                "email": "alex.gadgets@example.com",
                "platform": "YouTube",
                "followers_count": "1.2M",
                "followers_count_numeric": 1200000,
                "niche": "tech",
                "engagement_rate": 5.2,
                "phone_number": "+1-555-TECH-002"
            },
            {
                "id": "cccccccc-dddd-eeee-ffff-aaaaaaaaaaaa",  # creator_fitness_001
                "name": "FitnessGuru_Mike",
                "email": "mike.fitness@example.com",
                "platform": "Instagram",
                "followers_count": "650K",
                "followers_count_numeric": 650000,
                "niche": "fitness",
                "engagement_rate": 6.5,
                "phone_number": "+1-555-FIT-001"
            },
            {
                "id": "dddddddd-eeee-ffff-aaaa-bbbbbbbbbbbb",  # creator_fitness_002
                "name": "YogaLife_Emma",
                "email": "emma.yoga@example.com", 
                "platform": "Instagram",
                "followers_count": "420K",
                "followers_count_numeric": 420000,
                "niche": "fitness",
                "engagement_rate": 7.8,
                "phone_number": "+1-555-FIT-002"
            },
            {
                "id": "eeeeeeee-ffff-aaaa-bbbb-cccccccccccc",  # creator_beauty_001
                "name": "BeautyInfluencer_Priya",
                "email": "priya.beauty@example.com",
                "platform": "TikTok",
                "followers_count": "1.5M",
                "followers_count_numeric": 1500000,
                "niche": "beauty",
                "engagement_rate": 8.2,
                "phone_number": "+1-555-BEAUTY-001"
            },
            {
                "id": "ffffffff-aaaa-bbbb-cccc-dddddddddddd",  # creator_beauty_002
                "name": "SkinCareExpert_Lisa",
                "email": "lisa.skincare@example.com",
                "platform": "YouTube",
                "followers_count": "920K",
                "followers_count_numeric": 920000,
                "niche": "beauty",
                "engagement_rate": 5.9,
                "phone_number": "+1-555-BEAUTY-002"
            }
        ]
        
        try:
            if not self.db_service.supabase:
                logger.warning("⚠️ Supabase not available - creators not created")
                return
            
            for creator in sample_creators:
                # Check if creator already exists
                existing = self.db_service.supabase.table("creators").select("id").eq("id", creator["id"]).execute()
                
                if existing.data:
                    logger.info(f"👤 Creator {creator['id']} already exists - updating...")
                    # Update existing creator
                    self.db_service.supabase.table("creators").update(creator).eq("id", creator["id"]).execute()
                else:
                    logger.info(f"👤 Creating creator: {creator['name']}")
                    # Insert new creator
                    self.db_service.supabase.table("creators").insert(creator).execute()
            
            logger.info(f"✅ Setup {len(sample_creators)} sample creators")
            
        except Exception as e:
            logger.error(f"❌ Error setting up creators: {str(e)}")
            raise
    
    async def verify_setup(self):
        """Verify that sample data was setup correctly"""
        try:
            if not self.db_service.supabase:
                logger.warning("⚠️ Supabase not available - cannot verify setup")
                return False
            
            # Check campaigns
            campaigns_result = self.db_service.supabase.table("campaigns").select("id, product_name, brand_name").execute()
            campaigns_count = len(campaigns_result.data) if campaigns_result.data else 0
            
            # Check creators  
            creators_result = self.db_service.supabase.table("creators").select("id, name, niche").execute()
            creators_count = len(creators_result.data) if creators_result.data else 0
            
            logger.info(f"📊 Database verification:")
            logger.info(f"   📋 Campaigns: {campaigns_count}")
            logger.info(f"   👤 Creators: {creators_count}")
            
            if campaigns_count >= 3 and creators_count >= 6:
                logger.info("✅ Sample data setup verification successful!")
                return True
            else:
                logger.warning("⚠️ Sample data setup may be incomplete")
                return False
                
        except Exception as e:
            logger.error(f"❌ Setup verification failed: {str(e)}")
            return False

async def main():
    """Main function to run sample data setup"""
    setup = SampleDataSetup()
    
    print("🚀 Starting sample data setup for campaign trigger testing...")
    
    success = await setup.setup_all_sample_data()
    
    if success:
        print("\n📊 Verifying setup...")
        verified = await setup.verify_setup()
        
        if verified:
            print("\n✅ Sample data setup completed successfully!")
            print("\n🎯 You can now test the campaign trigger endpoints:")
            print("   1. GET /api/campaign-trigger/campaigns - List available campaigns")
            print("   2. GET /api/campaign-trigger/discover/{campaign_id} - Preview creators for a campaign")
            print("   3. POST /api/campaign-trigger/trigger/{campaign_id} - Trigger AI calls")
            print("   4. GET /api/campaign-trigger/monitor/{task_id} - Monitor call progress")
            print("\n📋 Sample campaign IDs:")
            print("   - tech_campaign_001 (TechPro Wireless Earbuds)")
            print("   - fitness_campaign_002 (FitPro Protein Powder)")
            print("   - beauty_campaign_003 (GlowUp Skincare Set)")
        else:
            print("\n⚠️ Setup completed but verification had issues")
    else:
        print("\n❌ Sample data setup failed")

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())