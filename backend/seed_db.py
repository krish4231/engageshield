import asyncio
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from ml.data.synthetic_generator import SyntheticDataGenerator
from app.database import async_session_factory
from app.models.engagement import Engagement


async def seed():
    print("Generating synthetic data...")
    gen = SyntheticDataGenerator(seed=42)
    # Generate a smaller set for quick testing
    data = gen.generate(
        num_normal_users=50,
        num_bot_users=20,
        num_coordinated_groups=2,
        coord_group_size=5,
        num_target_accounts=5,
    )
    
    engagements = data["engagements"]
    print(f"Generated {len(engagements)} engagements. Inserting to DB...")
    
    async with async_session_factory() as session:
        # Convert dicts to ORM objects
        objects = []
        for eng_data in engagements:
            # Remove internal fields
            clean_data = {k: v for k, v in eng_data.items() if not k.startswith("_")}
            # SQLite datetime conversion
            from datetime import datetime
            clean_data["engagement_timestamp"] = datetime.fromisoformat(clean_data["engagement_timestamp"])
            objects.append(Engagement(**clean_data))
            
        session.add_all(objects)
        await session.commit()
        print("Data seeded successfully!")

if __name__ == "__main__":
    asyncio.run(seed())
