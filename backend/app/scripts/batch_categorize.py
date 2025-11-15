"""
Batch categorize all queries in the database.
Useful for processing existing queries or re-processing after algorithm updates.

Run with: python -m app.scripts.batch_categorize
"""

import asyncio
import sys
from sqlalchemy.orm import Session
from app.database import SessionLocal, engine
from app.models.query import Query, QueryStatus
from app.services.ai_categorization import AICategorization

async def batch_categorize(
    limit: int = None,
    only_uncategorized: bool = True,
    dry_run: bool = False
):
    """
    Categorize queries in batches.
    
    Args:
        limit: Max number of queries to process (None = all)
        only_uncategorized: Only process queries with category=GENERAL
        dry_run: Print what would be done without actually updating
    """
    db = SessionLocal()
    
    try:
        # Build query
        query = db.query(Query)
        
        if only_uncategorized:
            query = query.filter(Query.category == "general")
        
        if limit:
            query = query.limit(limit)
        
        queries = query.all()
        total = len(queries)
        
        print(f"\n🤖 Batch Categorization")
        print(f"{'='*50}")
        print(f"Queries to process: {total}")
        print(f"Dry run: {dry_run}")
        print(f"{'='*50}\n")
        
        if dry_run:
            print("DRY RUN - No changes will be made\n")
        
        if total == 0:
            print("✅ No queries to process!")
            return
        
        # Process queries
        success_count = 0
        error_count = 0
        
        for i, query_obj in enumerate(queries, 1):
            try:
                print(f"[{i}/{total}] Processing query #{query_obj.id}...")
                
                if not dry_run:
                    # Actually process
                    await AICategorization.process_query(db, query_obj.id)
                    success_count += 1
                else:
                    # Just print what would happen
                    result = await AICategorization.categorize_with_ai(query_obj)
                    print(f"  Would set: {result['category']} / {result['priority']}")
                    print(f"  Reasoning: {result['reasoning'][:100]}...")
                    success_count += 1
                
                # Small delay to avoid rate limits
                await asyncio.sleep(0.5)
                
            except Exception as e:
                print(f"  ❌ Error: {e}")
                error_count += 1
                continue
        
        # Summary
        print(f"\n{'='*50}")
        print(f"✅ Success: {success_count}")
        print(f"❌ Errors: {error_count}")
        print(f"{'='*50}\n")
        
    finally:
        db.close()

async def categorize_single(query_id: int):
    """Categorize a single query by ID"""
    db = SessionLocal()
    
    try:
        query = db.query(Query).filter(Query.id == query_id).first()
        
        if not query:
            print(f"❌ Query #{query_id} not found")
            return
        
        print(f"🤖 Categorizing query #{query_id}...")
        print(f"Subject: {query.subject}")
        print(f"Content preview: {query.content[:100]}...\n")
        
        result = await AICategorization.process_query(db, query_id)
        
        print(f"\n✅ Categorized as:")
        print(f"  Category: {result.category.value}")
        print(f"  Priority: {result.priority.value}")
        print(f"  Tags: {', '.join(result.tags)}")
        
    finally:
        db.close()

def main():
    """CLI interface for batch categorization"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Batch categorize queries with AI")
    parser.add_argument(
        "--limit",
        type=int,
        default=None,
        help="Maximum number of queries to process"
    )
    parser.add_argument(
        "--all",
        action="store_true",
        help="Process all queries, not just uncategorized ones"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be done without making changes"
    )
    parser.add_argument(
        "--query-id",
        type=int,
        default=None,
        help="Process a single query by ID"
    )
    
    args = parser.parse_args()
    
    # Run async function
    if args.query_id:
        asyncio.run(categorize_single(args.query_id))
    else:
        asyncio.run(batch_categorize(
            limit=args.limit,
            only_uncategorized=not args.all,
            dry_run=args.dry_run
        ))

if __name__ == "__main__":
    main()
