"""
Synthetic data generator for EngageShield.
Generates realistic engagement data with normal users, bot accounts,
and coordinated networks for training and demo purposes.
"""

import random
import uuid
import json
from datetime import datetime, timedelta
from typing import List, Dict, Any
import math


class SyntheticDataGenerator:
    """Generate realistic synthetic social media engagement data."""

    def __init__(self, seed: int = 42):
        random.seed(seed)
        self.users = []
        self.engagements = []
        self.user_metadata = {}

    def generate(
        self,
        num_normal_users: int = 500,
        num_bot_users: int = 150,
        num_coordinated_groups: int = 5,
        coord_group_size: int = 20,
        num_target_accounts: int = 50,
        engagements_per_normal: int = 30,
        engagements_per_bot: int = 100,
        days: int = 30,
    ) -> Dict[str, Any]:
        """Generate the full synthetic dataset."""
        base_time = datetime.utcnow() - timedelta(days=days)

        # Generate target accounts
        targets = [f"target_{i:04d}" for i in range(num_target_accounts)]

        # Generate normal users
        normal_users = self._generate_normal_users(
            num_normal_users, targets, engagements_per_normal, base_time, days
        )

        # Generate bot users
        bot_users = self._generate_bot_users(
            num_bot_users, targets, engagements_per_bot, base_time, days
        )

        # Generate coordinated network groups
        coord_users = self._generate_coordinated_groups(
            num_coordinated_groups, coord_group_size, targets, base_time, days
        )

        all_engagements = normal_users + bot_users + coord_users

        # Generate labels
        labels = {}
        for eng in all_engagements:
            uid = eng["source_user_id"]
            if uid not in labels:
                labels[uid] = eng.get("_label", "legitimate")

        self.engagements = all_engagements

        return {
            "engagements": all_engagements,
            "labels": labels,
            "stats": {
                "total_engagements": len(all_engagements),
                "total_users": len(labels),
                "normal_users": num_normal_users,
                "bot_users": num_bot_users,
                "coordinated_users": num_coordinated_groups * coord_group_size,
                "target_accounts": num_target_accounts,
            },
        }

    def _generate_normal_users(
        self, count: int, targets: List[str], eng_per_user: int, base_time: datetime, days: int
    ) -> List[Dict]:
        """Generate organic engagement from normal users."""
        engagements = []

        for i in range(count):
            user_id = f"normal_{i:04d}"
            username = f"user_{random.randint(1000, 9999)}"

            # Normal users have diverse, occasional engagement
            account_age = random.randint(90, 2000)
            followers = random.randint(50, 5000)
            following = random.randint(30, 2000)
            total_posts = random.randint(20, 500)

            # Randomly select targets (diverse)
            user_targets = random.sample(targets, min(random.randint(3, 15), len(targets)))

            num_engagements = random.randint(
                max(1, eng_per_user // 2), eng_per_user * 2
            )

            for j in range(num_engagements):
                # Human-like timing: mostly during waking hours, random intervals
                hour = random.choices(
                    range(24),
                    weights=[1, 0.5, 0.2, 0.1, 0.1, 0.2, 0.5, 2, 4, 5, 6, 6,
                             7, 7, 6, 5, 5, 4, 4, 5, 5, 4, 3, 2],
                    k=1
                )[0]
                day_offset = random.uniform(0, days)
                minute = random.randint(0, 59)
                second = random.randint(0, 59)
                ts = base_time + timedelta(days=day_offset, hours=hour, minutes=minute, seconds=second)

                eng_type = random.choices(
                    ["like", "comment", "follow", "share"],
                    weights=[50, 20, 15, 15],
                    k=1
                )[0]

                content = None
                if eng_type == "comment":
                    content = random.choice([
                        "Great post!", "Love this!", "Interesting perspective",
                        "Thanks for sharing", "I agree", "Nice work!",
                        "This is really helpful", "Amazing content",
                        "Can you elaborate?", "Very informative",
                    ])

                engagements.append({
                    "source_user_id": user_id,
                    "source_username": username,
                    "target_user_id": random.choice(user_targets),
                    "target_username": None,
                    "engagement_type": eng_type,
                    "content": content,
                    "platform": "generic",
                    "engagement_value": 1.0,
                    "source_follower_count": followers + random.randint(-10, 10),
                    "source_following_count": following,
                    "source_account_age_days": account_age,
                    "source_total_posts": total_posts,
                    "engagement_timestamp": ts.isoformat(),
                    "_label": "legitimate",
                })

        return engagements

    def _generate_bot_users(
        self, count: int, targets: List[str], eng_per_user: int, base_time: datetime, days: int
    ) -> List[Dict]:
        """Generate bot-like engagement patterns."""
        engagements = []

        for i in range(count):
            user_id = f"bot_{i:04d}"
            username = f"x_user_{random.randint(10000, 99999)}"

            # Bots: new accounts, weird ratios, lots of activity
            account_age = random.randint(1, 30)
            followers = random.randint(0, 50)
            following = random.randint(500, 5000)
            total_posts = random.randint(0, 10)

            # Bots target fewer accounts (less diverse)
            user_targets = random.sample(targets, min(random.randint(1, 3), len(targets)))

            num_engagements = random.randint(eng_per_user, eng_per_user * 3)

            # Bot timing pattern: very regular intervals
            base_interval = random.uniform(5, 120)  # seconds between actions

            for j in range(num_engagements):
                # Machine-like timing: 24/7, regular intervals
                ts = base_time + timedelta(
                    seconds=j * base_interval + random.uniform(-2, 2)
                )

                # Bots mostly do likes (cheap engagement)
                eng_type = random.choices(
                    ["like", "follow", "comment"],
                    weights=[70, 20, 10],
                    k=1
                )[0]

                content = None
                if eng_type == "comment":
                    # Repetitive/generic comments
                    content = random.choice([
                        "Nice!", "👍", "🔥🔥🔥", "Great!", "Wow!",
                        "Nice!", "👍", "🔥🔥🔥", "Great!", "Wow!",
                    ])

                engagements.append({
                    "source_user_id": user_id,
                    "source_username": username,
                    "target_user_id": random.choice(user_targets),
                    "target_username": None,
                    "engagement_type": eng_type,
                    "content": content,
                    "platform": "generic",
                    "engagement_value": 1.0,
                    "source_follower_count": followers,
                    "source_following_count": following,
                    "source_account_age_days": account_age,
                    "source_total_posts": total_posts,
                    "engagement_timestamp": ts.isoformat(),
                    "_label": "fake",
                })

        return engagements

    def _generate_coordinated_groups(
        self, num_groups: int, group_size: int, targets: List[str],
        base_time: datetime, days: int
    ) -> List[Dict]:
        """Generate coordinated fake engagement network groups."""
        engagements = []

        for g in range(num_groups):
            # Each group targets the SAME accounts
            group_targets = random.sample(targets, min(random.randint(2, 5), len(targets)))

            # Group members engage at synchronized times
            group_base_times = [
                base_time + timedelta(hours=random.uniform(0, days * 24))
                for _ in range(random.randint(10, 30))  # 10-30 synchronized action bursts
            ]

            for m in range(group_size):
                user_id = f"coord_g{g}_m{m:03d}"
                username = f"user{random.randint(100, 999)}_{random.choice(['official', 'real', 'pro', 'fan'])}"

                account_age = random.randint(5, 60)
                followers = random.randint(10, 200)
                following = random.randint(100, 1000)

                for action_time in group_base_times:
                    # Synchronized with slight jitter (±minutes)
                    ts = action_time + timedelta(seconds=random.uniform(-300, 300))

                    for target in group_targets:
                        eng_type = random.choices(
                            ["like", "comment", "share"],
                            weights=[60, 25, 15],
                            k=1
                        )[0]

                        content = None
                        if eng_type == "comment":
                            content = random.choice([
                                "This is amazing!", "Best ever!", "So inspiring!",
                                "Everyone should see this!", "Incredible work!",
                            ])

                        engagements.append({
                            "source_user_id": user_id,
                            "source_username": username,
                            "target_user_id": target,
                            "target_username": None,
                            "engagement_type": eng_type,
                            "content": content,
                            "platform": "generic",
                            "engagement_value": 1.0,
                            "source_follower_count": followers,
                            "source_following_count": following,
                            "source_account_age_days": account_age,
                            "source_total_posts": random.randint(5, 50),
                            "engagement_timestamp": ts.isoformat(),
                            "_label": "fake",
                        })

                # Also interact within the group (creates dense internal edges)
                other_members = [f"coord_g{g}_m{om:03d}" for om in range(group_size) if om != m]
                for _ in range(random.randint(2, 8)):
                    ts = base_time + timedelta(hours=random.uniform(0, days * 24))
                    engagements.append({
                        "source_user_id": user_id,
                        "source_username": username,
                        "target_user_id": random.choice(other_members),
                        "target_username": None,
                        "engagement_type": random.choice(["like", "follow", "comment"]),
                        "content": None,
                        "platform": "generic",
                        "engagement_value": 1.0,
                        "source_follower_count": followers,
                        "source_following_count": following,
                        "source_account_age_days": account_age,
                        "source_total_posts": random.randint(5, 50),
                        "engagement_timestamp": ts.isoformat(),
                        "_label": "fake",
                    })

        return engagements


def save_dataset(output_path: str = "ml/data/synthetic_dataset.json"):
    """Generate and save the synthetic dataset."""
    gen = SyntheticDataGenerator(seed=42)
    data = gen.generate()

    # Remove internal label from engagements for export
    clean_engagements = []
    for eng in data["engagements"]:
        clean = {k: v for k, v in eng.items() if not k.startswith("_")}
        clean_engagements.append(clean)

    output = {
        "engagements": clean_engagements,
        "labels": data["labels"],
        "stats": data["stats"],
    }

    with open(output_path, "w") as f:
        json.dump(output, f, default=str, indent=2)

    print(f"Generated dataset with {data['stats']['total_engagements']} engagements")
    print(f"Users: {data['stats']['total_users']} ({data['stats']['normal_users']} normal, "
          f"{data['stats']['bot_users']} bots, {data['stats']['coordinated_users']} coordinated)")
    print(f"Saved to {output_path}")

    return output


if __name__ == "__main__":
    save_dataset()
