"""
Claude AI Service for OpenHealth
Handles all AI interactions using Anthropic's Claude API
"""

import asyncio
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
import json
import logging
from dataclasses import dataclass

from anthropic import AsyncAnthropic
from sqlalchemy.orm import Session
from sqlalchemy import select

from ..config import settings
from ..database.models import (
    Conversation, Message, Venture, User, KnowledgeBase, 
    Meeting, ExtractionSchema, SystemSettings
)

logger = logging.getLogger(__name__)


@dataclass
class VentureAnalysis:
    """Structured venture analysis result"""
    name: str
    description: str
    stage: str
    market_size: str
    funding_status: str
    team_size: Optional[int]
    location: str
    score: int
    score_breakdown: Dict[str, Any]
    key_strengths: List[str]
    concerns: List[str]
    next_steps: List[str]


@dataclass
class MeetingRequest:
    """Structured meeting request"""
    requested: bool
    urgency: str  # 'low', 'medium', 'high'
    preferred_times: List[str]
    meeting_type: str  # 'discovery', 'pitch', 'follow_up'
    duration: int  # minutes
    agenda_items: List[str]


class ClaudeService:
    """Service for interacting with Claude AI"""
    
    def __init__(self):
        if not settings.ANTHROPIC_API_KEY:
            raise ValueError("ANTHROPIC_API_KEY must be set in environment")
        
        self.client = AsyncAnthropic(api_key=settings.ANTHROPIC_API_KEY)
        self.model = settings.DEFAULT_AI_MODEL
        self.max_tokens = settings.MAX_TOKENS
        self.temperature = settings.TEMPERATURE
        
    async def generate_response(
        self,
        messages: List[Dict[str, str]],
        system_prompt: Optional[str] = None,
        user_context: Optional[Dict] = None,
        conversation_context: Optional[Dict] = None,
        db_session: Optional[Session] = None
    ) -> Tuple[str, Dict[str, Any]]:
        """
        Generate AI response with healthcare venture context
        Returns: (response_text, extracted_data)
        """
        try:
            # Build system prompt with healthcare focus
            full_system_prompt = await self._build_system_prompt(
                system_prompt, user_context, conversation_context, db_session
            )
            
            # Prepare messages for Claude
            claude_messages = self._format_messages_for_claude(messages)
            
            # Call Claude API
            response = await self.client.messages.create(
                model=self.model,
                max_tokens=self.max_tokens,
                temperature=self.temperature,
                system=full_system_prompt,
                messages=claude_messages
            )
            
            response_text = response.content[0].text
            
            # Extract structured data from response
            extracted_data = await self._extract_structured_data(
                response_text, messages, user_context
            )
            
            logger.info(f"Generated response: {len(response_text)} chars")
            return response_text, extracted_data
            
        except Exception as e:
            logger.error(f"Error generating Claude response: {e}")
            return self._get_fallback_response(), {}
    
    async def analyze_venture(
        self,
        conversation_messages: List[Dict[str, str]],
        user_context: Dict,
        db_session: Session
    ) -> VentureAnalysis:
        """Analyze healthcare venture from conversation"""
        
        system_prompt = """You are an expert healthcare venture analyst. 
        Analyze the conversation to extract key information about this healthcare venture.
        Focus on: market opportunity, team capability, technology innovation, 
        business model viability, regulatory considerations, and competitive landscape.
        
        Rate the venture on a scale of 1-100 and provide detailed breakdown."""
        
        analysis_prompt = f"""
        Based on this conversation with a healthcare founder, provide a comprehensive 
        venture analysis in the following JSON format:
        
        {{
            "name": "venture name",
            "description": "brief description",
            "stage": "idea|mvp|early_stage|growth",
            "market_size": "small|medium|large|massive",
            "funding_status": "bootstrapped|pre_seed|seed|series_a|later",
            "team_size": number or null,
            "location": "location if mentioned",
            "score": 1-100,
            "score_breakdown": {{
                "market_opportunity": 1-20,
                "team_strength": 1-20,
                "technology_innovation": 1-20,
                "business_model": 1-20,
                "execution_capability": 1-20
            }},
            "key_strengths": ["strength1", "strength2"],
            "concerns": ["concern1", "concern2"],
            "next_steps": ["step1", "step2"]
        }}
        
        Conversation context:
        User: {user_context.get('name', 'Unknown')} from {user_context.get('company', 'Unknown Company')}
        """
        
        messages = conversation_messages + [
            {"role": "user", "content": analysis_prompt}
        ]
        
        try:
            response, _ = await self.generate_response(
                messages=messages,
                system_prompt=system_prompt,
                user_context=user_context,
                db_session=db_session
            )
            
            # Extract JSON from response
            json_start = response.find('{')
            json_end = response.rfind('}') + 1
            
            if json_start >= 0 and json_end > json_start:
                json_str = response[json_start:json_end]
                analysis_data = json.loads(json_str)
                
                return VentureAnalysis(
                    name=analysis_data.get('name', 'Unknown Venture'),
                    description=analysis_data.get('description', ''),
                    stage=analysis_data.get('stage', 'idea'),
                    market_size=analysis_data.get('market_size', 'medium'),
                    funding_status=analysis_data.get('funding_status', 'unknown'),
                    team_size=analysis_data.get('team_size'),
                    location=analysis_data.get('location', ''),
                    score=analysis_data.get('score', 50),
                    score_breakdown=analysis_data.get('score_breakdown', {}),
                    key_strengths=analysis_data.get('key_strengths', []),
                    concerns=analysis_data.get('concerns', []),
                    next_steps=analysis_data.get('next_steps', [])
                )
            
        except Exception as e:
            logger.error(f"Error analyzing venture: {e}")
        
        # Return default analysis if parsing fails
        return VentureAnalysis(
            name="Healthcare Venture",
            description="Analysis pending",
            stage="idea",
            market_size="medium",
            funding_status="unknown",
            team_size=None,
            location="",
            score=50,
            score_breakdown={},
            key_strengths=[],
            concerns=["Incomplete information"],
            next_steps=["Continue conversation"]
        )
    
    async def detect_meeting_request(
        self,
        message_content: str,
        conversation_context: List[Dict[str, str]]
    ) -> MeetingRequest:
        """Detect if user is requesting a meeting"""
        
        system_prompt = """Analyze if the user is requesting a meeting or expressing 
        interest in scheduling one. Look for explicit requests or implicit interest."""
        
        detection_prompt = f"""
        Analyze this message to determine if the user wants to schedule a meeting.
        Return JSON format:
        {{
            "requested": true/false,
            "urgency": "low|medium|high",
            "preferred_times": ["time expressions found"],
            "meeting_type": "discovery|pitch|follow_up",
            "duration": estimated_minutes,
            "agenda_items": ["item1", "item2"]
        }}
        
        Message: "{message_content}"
        """
        
        try:
            response, _ = await self.generate_response(
                messages=[{"role": "user", "content": detection_prompt}],
                system_prompt=system_prompt
            )
            
            # Extract JSON
            json_start = response.find('{')
            json_end = response.rfind('}') + 1
            
            if json_start >= 0 and json_end > json_start:
                json_str = response[json_start:json_end]
                meeting_data = json.loads(json_str)
                
                return MeetingRequest(
                    requested=meeting_data.get('requested', False),
                    urgency=meeting_data.get('urgency', 'medium'),
                    preferred_times=meeting_data.get('preferred_times', []),
                    meeting_type=meeting_data.get('meeting_type', 'discovery'),
                    duration=meeting_data.get('duration', 30),
                    agenda_items=meeting_data.get('agenda_items', [])
                )
                
        except Exception as e:
            logger.error(f"Error detecting meeting request: {e}")
        
        # Default - no meeting requested
        return MeetingRequest(
            requested=False,
            urgency='low',
            preferred_times=[],
            meeting_type='discovery',
            duration=30,
            agenda_items=[]
        )
    
    async def _build_system_prompt(
        self,
        base_prompt: Optional[str],
        user_context: Optional[Dict],
        conversation_context: Optional[Dict],
        db_session: Optional[Session]
    ) -> str:
        """Build comprehensive system prompt with context"""
        
        # Base healthcare AI assistant prompt
        system_parts = [
            """You are OpenHealth AI, an expert healthcare venture assistant. 
            You help healthcare entrepreneurs, founders, and innovators explore ideas, 
            refine business models, and navigate the healthcare landscape.
            
            Key principles:
            - Focus on healthcare innovation and patient impact
            - Consider regulatory requirements (FDA, HIPAA, etc.)
            - Emphasize evidence-based approaches
            - Be encouraging but realistic about challenges
            - Ask thoughtful follow-up questions
            - Suggest next steps and resources
            """
        ]
        
        # Add custom system prompt
        if base_prompt:
            system_parts.append(base_prompt)
        
        # Add user context
        if user_context:
            user_info = f"""
            User context:
            - Name: {user_context.get('name', 'Unknown')}
            - Company: {user_context.get('company', 'Unknown')}
            - Role: {user_context.get('role', 'Unknown')}
            - Background: {user_context.get('metadata', {}).get('background', 'Healthcare entrepreneur')}
            """
            system_parts.append(user_info)
        
        # Add knowledge base context
        if db_session:
            knowledge_context = await self._get_relevant_knowledge(db_session)
            if knowledge_context:
                system_parts.append(f"Relevant knowledge:\n{knowledge_context}")
        
        # Add conversation context
        if conversation_context:
            conv_info = f"""
            Conversation context:
            - Stage: {conversation_context.get('stage', 'initial')}
            - Priority: {conversation_context.get('priority', 'normal')}
            - Previous topics: {conversation_context.get('topics', [])}
            """
            system_parts.append(conv_info)
        
        return "\n\n".join(system_parts)
    
    async def _get_relevant_knowledge(self, db_session: Session) -> str:
        """Retrieve relevant knowledge base entries"""
        try:
            # Get recent healthcare trends and investment criteria
            stmt = select(KnowledgeBase).where(
                KnowledgeBase.category.in_(['healthcare_trends', 'investment_criteria'])
            ).limit(5)
            
            result = db_session.execute(stmt)
            knowledge_entries = result.scalars().all()
            
            if knowledge_entries:
                knowledge_text = []
                for entry in knowledge_entries:
                    knowledge_text.append(f"- {entry.title}: {entry.content[:200]}...")
                
                return "\n".join(knowledge_text)
                
        except Exception as e:
            logger.error(f"Error retrieving knowledge base: {e}")
        
        return ""
    
    def _format_messages_for_claude(
        self, 
        messages: List[Dict[str, str]]
    ) -> List[Dict[str, str]]:
        """Format messages for Claude API"""
        claude_messages = []
        
        for msg in messages:
            if msg['role'] in ['user', 'assistant']:
                claude_messages.append({
                    'role': msg['role'],
                    'content': msg['content']
                })
        
        return claude_messages
    
    async def _extract_structured_data(
        self,
        response_text: str,
        conversation_messages: List[Dict[str, str]],
        user_context: Optional[Dict]
    ) -> Dict[str, Any]:
        """Extract structured data from AI response"""
        extracted_data = {
            'intent': 'general_chat',
            'entities': [],
            'meeting_request': False,
            'venture_info': {},
            'next_actions': []
        }
        
        try:
            # Simple keyword-based extraction
            text_lower = response_text.lower()
            
            # Detect meeting-related content
            meeting_keywords = ['meeting', 'schedule', 'call', 'discuss', 'available']
            if any(keyword in text_lower for keyword in meeting_keywords):
                extracted_data['meeting_request'] = True
                extracted_data['intent'] = 'meeting_scheduling'
            
            # Detect venture analysis content
            venture_keywords = ['company', 'startup', 'business', 'product', 'market']
            if any(keyword in text_lower for keyword in venture_keywords):
                extracted_data['intent'] = 'venture_discussion'
            
            # Extract mentioned entities (simple approach)
            # In production, you'd use NER or more sophisticated extraction
            if user_context and user_context.get('company'):
                if user_context['company'].lower() in text_lower:
                    extracted_data['entities'].append({
                        'type': 'company',
                        'value': user_context['company']
                    })
            
        except Exception as e:
            logger.error(f"Error extracting structured data: {e}")
        
        return extracted_data
    
    def _get_fallback_response(self) -> str:
        """Return fallback response when AI fails"""
        return """I apologize, but I'm experiencing some technical difficulties right now. 
        Let me connect you with a member of our team who can help you with your healthcare venture. 
        In the meantime, feel free to share more details about your project."""


# Global service instance
claude_service = ClaudeService()