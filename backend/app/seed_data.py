"""
Seed database with realistic mock queries for FastAPI demo.
Run with: python -m app.seed_data
"""

import random
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import text

from app.database import SessionLocal, engine, Base
from app.models.user import User, UserRole, UserTeam
from app.models.query import Query, QueryChannel, QueryStatus, QueryPriority, QueryCategory
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# ----------- SAMPLE DATA (must be filled) -----------
# Replace [...] with actual lists
SAMPLE_NAMES = ["Sarah Johnson", "Michael Chen", "Emma Williams"]
SAMPLE_EMAIL_SUBJECTS = ["Issue with my account", "Need help", "Question about billing"]
SAMPLE_QUESTIONS = ["How do I reset my password?", "Where is my invoice?"]
SAMPLE_COMPLAINTS = ["Your service is down!", "I was charged twice!"]
SAMPLE_REQUESTS = ["Please add dark mode", "Need SSO integration"]
SAMPLE_FEEDBACK = ["Great product!", "Loving the new update!"]

# Quick validation
def ensure_non_empty():
    lists = {
        "SAMPLE_NAMES": SAMPLE_NAMES,
        "SAMPLE_EMAIL_SUBJECTS": SAMPLE_EMAIL_SUBJECTS,
        "SAMPLE_QUESTIONS": SAMPLE_QUESTIONS,
        "SAMPLE_COMPLAINTS": SAMPLE_COMPLAINTS,
        "SAMPLE_REQUESTS": SAMPLE_REQUESTS,
        "SAMPLE_FEEDBACK": SAMPLE_FEEDBACK,
    }

    for name, lst in lists.items():
        if not lst:
            raise ValueError(f"❌ {name} cannot be empty!")


# bcrypt safely only hashes first 72 bytes
def safe_hash(password: str) -> str:
    return pwd_context.hash(password[:72])


# ----------- SEED USERS -----------

def create_users(db: Session):
    users = [
        User(
            email="admin@company.com",
            name="Admin User",
            hashed_password=safe_hash("admin"),
            role=UserRole.ADMIN,
            team=UserTeam.SUPPORT
        ),
        User(
            email="sarah@company.com",
            name="Sarah Support",
            hashed_password=safe_hash("agent"),
            role=UserRole.AGENT,
            team=UserTeam.SUPPORT
        ),
        User(
            email="mike@company.com",
            name="Mike Engineer",
            hashed_password=safe_hash("agent"),
            role=UserRole.AGENT,
            team=UserTeam.ENGINEERING
        ),
        User(
            email="emma@company.com",
            name="Emma Sales",
            hashed_password=safe_hash("agent"),
            role=UserRole.AGENT,
            team=UserTeam.SALES
        )
    ]

    db.add_all(users)
    db.commit()
    print(f"✅ Created {len(users)} users")
    return users


# ----------- SEED QUERIES -----------

def create_queries(db: Session, num_queries=100):
    agents = db.query(User).filter(User.role == UserRole.AGENT).all()
    agent_ids = [a.id for a in agents]

    queries = []

    for _ in range(num_queries):
        received_at = datetime.utcnow() - timedelta(days=random.randint(0, 30))

        category = random.choice([
            QueryCategory.QUESTION,
            QueryCategory.COMPLAINT,
            QueryCategory.REQUEST,
            QueryCategory.FEEDBACK
        ])

        if category == QueryCategory.QUESTION:
            content = random.choice(SAMPLE_QUESTIONS)
            priority = random.choice([QueryPriority.LOW, QueryPriority.MEDIUM])
        elif category == QueryCategory.COMPLAINT:
            content = random.choice(SAMPLE_COMPLAINTS)
            priority = random.choice([QueryPriority.HIGH, QueryPriority.URGENT])
        elif category == QueryCategory.REQUEST:
            content = random.choice(SAMPLE_REQUESTS)
            priority = QueryPriority.MEDIUM
        else:
            content = random.choice(SAMPLE_FEEDBACK)
            priority = QueryPriority.LOW

        query = Query(
            channel=random.choice(list(QueryChannel)),
            sender_email=random.choice(SAMPLE_NAMES).lower().replace(" ", ".") + "@example.com",
            sender_name=random.choice(SAMPLE_NAMES),
            subject=random.choice(SAMPLE_EMAIL_SUBJECTS),
            content=content,
            category=category,
            priority=priority,
            status=random.choice(list(QueryStatus)),
            assigned_to=random.choice(agent_ids) if random.random() < 0.7 else None,
            received_at=received_at
        )

        db.add(query)
        queries.append(query)

    db.commit()
    print(f"✅ Created {len(queries)} queries")
    return queries


# ----------- MAIN -----------

def clear_database(db: Session):
    """
    Proper cascade-safe deletion (Postgres requires deleting children first)
    """
    print("🗑️ Clearing tables ...")

    # Delete children first
    db.execute(text("DELETE FROM query_activities"))
    db.execute(text("DELETE FROM query_responses"))
    db.execute(text("DELETE FROM queries"))
    db.execute(text("DELETE FROM users"))
    db.commit()


def main():
    print("🌱 Starting database seeding...")

    Base.metadata.create_all(bind=engine)
    ensure_non_empty()

    db = SessionLocal()

    try:
        if db.query(User).count() > 0:
            choice = input("⚠️ Database already has data. Clear it first? (y/n) ").strip().lower()
            if choice == "y":
                clear_database(db)
            else:
                print("❌ Cancelled.")
                return

        users = create_users(db)
        queries = create_queries(db)

        print("\n✨ Seed complete.")
        print(f"Users: {len(users)}")
        print(f"Queries: {len(queries)}")

    except Exception as e:
        print("❌ Error:", e)
        db.rollback()

    finally:
        db.close()


if __name__ == "__main__":
    main()
