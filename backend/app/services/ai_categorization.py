"""
AI-powered query categorization and priority detection.
Uses OpenAI GPT models for intelligent classification.
"""

import json
import re
from typing import Dict, List, Tuple
from sqlalchemy.orm import Session
from app.core.openai_client import client
from app.core.config import settings
from app.models.query import Query, QueryCategory, QueryPriority

class AICategorization:
    """AI-powered categorization and prioritization service"""
    
    # Urgency keywords for rule-based detection
    URGENT_KEYWORDS = [
        'urgent', 'asap', 'immediately', 'emergency', 'critical',
        'down', 'broken', 'not working', 'can\'t access', 'crashed',
        'losing money', 'losing business', 'production down',
        'security breach', 'data loss', 'can\'t login'
    ]
    
    HIGH_PRIORITY_KEYWORDS = [
        'important', 'soon', 'issue', 'problem', 'error',
        'billing issue', 'charged twice', 'refund needed',
        'account locked', 'payment failed'
    ]
    
    COMPLAINT_KEYWORDS = [
        'terrible', 'awful', 'worst', 'disappointed', 'frustrated',
        'angry', 'unacceptable', 'scam', 'fraud', 'complaint'
    ]
    
    @staticmethod
    def detect_priority_rules_based(query: Query) -> QueryPriority:
        """
        Rule-based priority detection using keyword matching.
        This runs first as a fast heuristic before AI classification.
        """
        text = f"{query.subject} {query.content}".lower()
        
        # Check for urgent keywords
        if any(keyword in text for keyword in AICategorization.URGENT_KEYWORDS):
            return QueryPriority.URGENT
        
        # Check for high priority indicators
        if any(keyword in text for keyword in AICategorization.HIGH_PRIORITY_KEYWORDS):
            return QueryPriority.HIGH
        
        # Complaints are at least medium priority
        if any(keyword in text for keyword in AICategorization.COMPLAINT_KEYWORDS):
            return QueryPriority.HIGH
        
        # Questions and feedback are typically lower priority
        question_words = ['how', 'what', 'when', 'where', 'why', 'can i', 'is there']
        if any(text.startswith(word) for word in question_words):
            return QueryPriority.LOW
        
        # Default
        return QueryPriority.MEDIUM
    
    @staticmethod
    async def categorize_with_ai(query: Query) -> Dict[str, any]:
        """
        Use OpenAI GPT to categorize query and detect priority.
        Returns dict with: category, priority, tags, reasoning
        """
        
        # Construct prompt for GPT
        system_prompt = """You are an AI assistant for customer support ticket classification.
Your job is to analyze customer messages and classify them accurately.

Categories:
- question: Customer asking for information or clarification
- request: Customer requesting a feature, change, or action
- complaint: Customer expressing dissatisfaction or reporting a problem
- feedback: Customer providing positive or constructive feedback
- bug_report: Customer reporting a technical bug or error
- general: Anything that doesn't fit other categories

Priority Levels:
- urgent: Critical issues affecting business operations, security, or causing data loss
- high: Important issues like billing problems, account access, or significant bugs
- medium: Standard requests, questions, or minor issues
- low: General inquiries, feedback, or feature requests

You must respond with ONLY valid JSON in this exact format:
{
  "category": "complaint",
  "priority": "high",
  "tags": ["billing", "refund", "payment"],
  "reasoning": "Brief explanation of classification",
  "sentiment": "negative"
}"""

        user_prompt = f"""Classify this customer message:

Subject: {query.subject}

Message:
{query.content}

Channel: {query.channel.value}
Sender: {query.sender_name or query.sender_email or 'Unknown'}"""

        try:
            # Call OpenAI API
            response = await client.chat.completions.create(
                model=settings.OPENAI_MODEL if hasattr(settings, 'OPENAI_MODEL') else "gpt-4o-mini",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.3,  # Low temperature for consistent results
                max_tokens=300,
                response_format={"type": "json_object"}  # Force JSON response
            )
            
            # Parse response
            result_text = response.choices[0].message.content
            result = json.loads(result_text)
            
            print(f"✅ AI categorized query #{query.id}: {result['category']} / {result['priority']}")
            
            return result
            
        except json.JSONDecodeError as e:
            print(f"⚠️  Failed to parse AI response: {e}")
            # Fallback to rule-based
            return AICategorization._fallback_categorization(query)
            
        except Exception as e:
            print(f"❌ AI categorization error: {e}")
            # Fallback to rule-based
            return AICategorization._fallback_categorization(query)
    
    @staticmethod
    def _fallback_categorization(query: Query) -> Dict[str, any]:
        """
        Fallback to rule-based categorization if AI fails.
        This ensures the system always works even without OpenAI.
        """
        text = f"{query.subject} {query.content}".lower()
        
        # Detect category
        if any(word in text for word in AICategorization.COMPLAINT_KEYWORDS):
            category = "complaint"
        elif any(word in text for word in ['?', 'how', 'what', 'why', 'when', 'where']):
            category = "question"
        elif any(word in text for word in ['please add', 'can you', 'request', 'need', 'want']):
            category = "request"
        elif any(word in text for word in ['bug', 'error', 'crash', 'not working', 'broken']):
            category = "bug_report"
        elif any(word in text for word in ['love', 'great', 'awesome', 'thanks', 'appreciate']):
            category = "feedback"
        else:
            category = "general"
        
        # Detect priority
        priority = AICategorization.detect_priority_rules_based(query).value
        
        # Extract basic tags
        tags = []
        tag_keywords = {
            'billing': ['payment', 'invoice', 'charge', 'refund', 'billing'],
            'technical': ['error', 'bug', 'crash', 'not working'],
            'account': ['login', 'password', 'access', 'signup'],
            'feature': ['feature', 'add', 'request', 'integration']
        }
        
        for tag, keywords in tag_keywords.items():
            if any(kw in text for kw in keywords):
                tags.append(tag)
        
        return {
            "category": category,
            "priority": priority,
            "tags": tags,
            "reasoning": "Rule-based classification (AI unavailable)",
            "sentiment": "negative" if category == "complaint" else "neutral"
        }
    
    @staticmethod
    async def process_query(db: Session, query_id: int) -> Query:
        """
        Full processing pipeline for a query:
        1. Get query from database
        2. Run AI categorization
        3. Update query with results
        4. Log activity
        5. Return updated query
        """
        from app.models.activity import QueryActivity
        
        # Get query
        query = db.query(Query).filter(Query.id == query_id).first()
        if not query:
            raise ValueError(f"Query {query_id} not found")
        
        print(f"🤖 Processing query #{query_id}...")
        
        # Run AI categorization
        result = await AICategorization.categorize_with_ai(query)
        
        # Update query
        query.category = QueryCategory[result['category'].upper()]
        query.priority = QueryPriority[result['priority'].upper()]
        query.tags = result.get('tags', [])
        
        db.commit()
        db.refresh(query)
        
        # Log activity
        activity = QueryActivity(
            query_id=query_id,
            action="auto_categorized",
            details={
                "category": result['category'],
                "priority": result['priority'],
                "tags": result.get('tags', []),
                "reasoning": result.get('reasoning', ''),
                "method": "ai" if "AI unavailable" not in result.get('reasoning', '') else "rules"
            }
        )
        db.add(activity)
        db.commit()
        
        print(f"✅ Query #{query_id} processed: {query.category.value} / {query.priority.value}")
        
        return query
    
    @staticmethod
    def extract_tags(query: Query) -> List[str]:
        """
        Extract relevant tags from query content.
        Uses keyword matching for common topics.
        """
        text = f"{query.subject} {query.content}".lower()
        tags = []
        
        # Define tag patterns
        tag_patterns = {
            # Departments
            'billing': ['payment', 'invoice', 'charge', 'refund', 'billing', 'subscription'],
            'technical': ['error', 'bug', 'crash', 'not working', 'broken', 'issue'],
            'account': ['login', 'password', 'access', 'signup', 'register', 'account'],
            'sales': ['pricing', 'plan', 'upgrade', 'purchase', 'buy'],
            
            # Product areas
            'api': ['api', 'integration', 'webhook', 'endpoint'],
            'mobile': ['mobile', 'app', 'ios', 'android'],
            'dashboard': ['dashboard', 'interface', 'ui', 'frontend'],
            'data': ['export', 'import', 'data', 'csv', 'excel'],
            
            # Actions
            'feature-request': ['add', 'feature', 'request', 'need', 'would like'],
            'documentation': ['docs', 'documentation', 'guide', 'tutorial', 'how to'],
        }
        
        # Match patterns
        for tag, keywords in tag_patterns.items():
            if any(keyword in text for keyword in keywords):
                tags.append(tag)
        
        # Remove duplicates and limit to 5 tags
        return list(set(tags))[:5]

# Convenience function for quick access
async def categorize_query(query_id: int, db: Session) -> Query:
    """Convenience function to categorize a query"""
    return await AICategorization.process_query(db, query_id)
