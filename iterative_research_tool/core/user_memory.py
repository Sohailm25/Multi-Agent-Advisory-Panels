"""User memory tracking module for building and maintaining user profiles."""

import os
import json
import logging
import time
from pathlib import Path
from typing import Dict, List, Any, Optional, Set
from datetime import datetime

# Anthropic imports for analysis
from anthropic import Anthropic

logger = logging.getLogger(__name__)

class UserMemory:
    """Tracks and maintains user memory and profiles over time."""
    
    def __init__(
        self, 
        memory_file: Optional[str] = None,
        claude_api_key: Optional[str] = None,
        claude_model: str = "claude-3-7-sonnet-20250219"
    ):
        """Initialize the user memory tracker.
        
        Args:
            memory_file: Path to the memory file
            claude_api_key: API key for Claude (for analysis)
            claude_model: Claude model to use for analysis
        """
        self.memory_file = memory_file or os.path.expanduser("~/.config/iterative_research_tool/user_memory.json")
        self.claude_api_key = claude_api_key
        self.claude_model = claude_model
        self.claude_client = Anthropic(api_key=claude_api_key) if claude_api_key else None
        
        # Ensure the directory exists
        os.makedirs(os.path.dirname(self.memory_file), exist_ok=True)
        
        # Load existing memory or create new
        self.memory = self._load_memory()
        
    def _load_memory(self) -> Dict[str, Any]:
        """Load memory from file or create new memory structure.
        
        Returns:
            The memory dictionary
        """
        try:
            if os.path.exists(self.memory_file):
                with open(self.memory_file, "r", encoding="utf-8") as f:
                    memory = json.load(f)
                logger.info(f"Loaded user memory from {self.memory_file}")
                return memory
        except Exception as e:
            logger.error(f"Error loading user memory: {e}")
        
        # Create new memory structure if file doesn't exist or loading failed
        memory = {
            "user_profile": {
                "goals": [],
                "hard_truths": [],
                "struggles": [],
                "mental_blocks": [],
                "cognitive_biases": [],
                "strengths": [],
                "interests": [],
                "values": []
            },
            "interaction_history": [],
            "query_patterns": {},
            "feedback_history": [],
            "last_updated": datetime.now().isoformat(),
            "creation_date": datetime.now().isoformat()
        }
        
        return memory
    
    def _save_memory(self):
        """Save memory to file."""
        try:
            # Update last updated timestamp
            self.memory["last_updated"] = datetime.now().isoformat()
            
            # Save to file
            with open(self.memory_file, "w", encoding="utf-8") as f:
                json.dump(self.memory, f, indent=2)
                
            logger.info(f"Saved user memory to {self.memory_file}")
        except Exception as e:
            logger.error(f"Error saving user memory: {e}")
    
    def add_interaction(self, query: str, response: str, feedback: Optional[Dict[str, Any]] = None):
        """Add a new interaction to the memory.
        
        Args:
            query: The user's query
            response: The system's response
            feedback: Optional feedback from the user
        """
        # Create interaction record
        interaction = {
            "timestamp": datetime.now().isoformat(),
            "query": query,
            "response_summary": response[:500] + "..." if len(response) > 500 else response,
            "feedback": feedback
        }
        
        # Add to interaction history
        self.memory["interaction_history"].append(interaction)
        
        # Update query patterns
        query_words = set(query.lower().split())
        for word in query_words:
            if len(word) > 3:  # Only track meaningful words
                if word not in self.memory["query_patterns"]:
                    self.memory["query_patterns"][word] = 1
                else:
                    self.memory["query_patterns"][word] += 1
        
        # Add feedback to history if provided
        if feedback:
            feedback_record = {
                "timestamp": datetime.now().isoformat(),
                "query": query,
                "rating": feedback.get("rating"),
                "comments": feedback.get("comments"),
                "improvements": feedback.get("improvements")
            }
            self.memory["feedback_history"].append(feedback_record)
        
        # Save updated memory
        self._save_memory()
        
        # Analyze the interaction if Claude API key is available
        if self.claude_api_key:
            self._analyze_interaction(query, response, feedback)
    
    def _analyze_interaction(self, query: str, response: str, feedback: Optional[Dict[str, Any]] = None):
        """Analyze the interaction to update the user profile.
        
        Args:
            query: The user's query
            response: The system's response
            feedback: Optional feedback from the user
        """
        if not self.claude_client:
            return
            
        try:
            # Prepare context from recent interactions
            recent_interactions = self.memory["interaction_history"][-10:]  # Last 10 interactions
            interaction_context = "\n".join([
                f"Query: {interaction['query']}\nFeedback: {interaction.get('feedback', 'None')}"
                for interaction in recent_interactions
            ])
            
            # Current profile
            current_profile = json.dumps(self.memory["user_profile"], indent=2)
            
            # Create analysis prompt
            analysis_prompt = f"""
            Based on the user's query and interaction history, update their profile by identifying any new insights about them.
            
            Current User Profile:
            {current_profile}
            
            Recent Interaction History:
            {interaction_context}
            
            Latest Query:
            {query}
            
            Latest Feedback:
            {json.dumps(feedback) if feedback else "None"}
            
            Please analyze this information and provide updates to the user profile in JSON format. 
            Focus on identifying:
            1. Goals the user might have
            2. Hard truths they need to hear
            3. Struggles they're facing
            4. Mental blocks that might be holding them back
            5. Cognitive biases they might be exhibiting
            6. Strengths they demonstrate
            7. Interests they show
            8. Values they seem to hold
            
            Only include new insights that aren't already in the current profile, or updates to existing insights.
            Return a JSON object with the categories as keys and arrays of strings as values.
            """
            
            # Get analysis from Claude
            message = self.claude_client.messages.create(
                model=self.claude_model,
                max_tokens=1000,
                temperature=0.5,
                system="You are an expert psychologist and analyst who helps build detailed user profiles based on their interactions.",
                messages=[
                    {"role": "user", "content": analysis_prompt}
                ]
            )
            
            analysis_text = message.content[0].text
            
            # Extract JSON from the response
            try:
                # Find JSON in the response
                json_start = analysis_text.find("{")
                json_end = analysis_text.rfind("}") + 1
                
                if json_start >= 0 and json_end > json_start:
                    json_str = analysis_text[json_start:json_end]
                    analysis = json.loads(json_str)
                    
                    # Update user profile with new insights
                    for category, insights in analysis.items():
                        if category in self.memory["user_profile"] and isinstance(insights, list):
                            # Add new insights that aren't already in the profile
                            existing_insights = set(self.memory["user_profile"][category])
                            for insight in insights:
                                if insight not in existing_insights:
                                    self.memory["user_profile"][category].append(insight)
                    
                    # Save updated memory
                    self._save_memory()
                    logger.info("Updated user profile with new insights from analysis")
            except Exception as e:
                logger.error(f"Error parsing analysis JSON: {e}")
                
        except Exception as e:
            logger.error(f"Error analyzing interaction: {e}")
    
    def get_context_for_query(self, query: str) -> str:
        """Get relevant context from memory for a new query.
        
        Args:
            query: The user's query
            
        Returns:
            Context string to include with the query
        """
        # Extract user profile
        profile = self.memory["user_profile"]
        
        # Format the context
        context = "User Profile:\n"
        
        # Add goals
        if profile["goals"]:
            context += "- Goals:\n  " + "\n  ".join(profile["goals"]) + "\n"
        
        # Add hard truths
        if profile["hard_truths"]:
            context += "- Hard Truths:\n  " + "\n  ".join(profile["hard_truths"]) + "\n"
        
        # Add struggles
        if profile["struggles"]:
            context += "- Struggles:\n  " + "\n  ".join(profile["struggles"]) + "\n"
        
        # Add mental blocks
        if profile["mental_blocks"]:
            context += "- Mental Blocks:\n  " + "\n  ".join(profile["mental_blocks"]) + "\n"
        
        # Add cognitive biases
        if profile["cognitive_biases"]:
            context += "- Cognitive Biases:\n  " + "\n  ".join(profile["cognitive_biases"]) + "\n"
        
        # Add strengths
        if profile["strengths"]:
            context += "- Strengths:\n  " + "\n  ".join(profile["strengths"]) + "\n"
        
        # Add recent feedback patterns
        if self.memory["feedback_history"]:
            recent_feedback = self.memory["feedback_history"][-5:]  # Last 5 feedback entries
            avg_rating = sum(fb.get("rating", 0) for fb in recent_feedback) / len(recent_feedback)
            context += f"- Recent Feedback: Average rating {avg_rating:.1f}/5\n"
            
            # Common improvement requests
            improvement_words = " ".join([fb.get("improvements", "") for fb in recent_feedback])
            if improvement_words:
                context += f"- Common improvement requests: {improvement_words[:100]}...\n"
        
        return context
    
    def get_memory_file_path(self) -> str:
        """Get the path to the memory file.
        
        Returns:
            Path to the memory file
        """
        return self.memory_file 