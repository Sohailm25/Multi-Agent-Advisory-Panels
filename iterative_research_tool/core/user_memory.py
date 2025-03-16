"""User memory tracking module for building and maintaining user profiles."""

import os
import json
import logging
import time
from pathlib import Path
from typing import Dict, List, Any, Optional, Set
from datetime import datetime

# Local imports
from iterative_research_tool.core.llm_client import LLMClientFactory

logger = logging.getLogger(__name__)

class UserMemory:
    """Tracks and maintains user memory and profiles over time."""
    
    def __init__(
        self, 
        memory_file: Optional[str] = None,
        llm_provider: str = "anthropic",
        api_key: Optional[str] = None,
        model: Optional[str] = None
    ):
        """Initialize the user memory tracker.
        
        Args:
            memory_file: Path to the memory file
            llm_provider: The LLM provider to use (anthropic, openai, or perplexity)
            api_key: API key for the LLM provider
            model: Model to use for analysis (if None, uses the default model for the provider)
        """
        self.memory_file = memory_file or os.path.expanduser("~/.config/iterative_research_tool/user_memory.json")
        self.llm_provider = llm_provider.lower()
        self.api_key = api_key
        
        # Set up the LLM client
        try:
            self.llm_client = LLMClientFactory.create_client(self.llm_provider, self.api_key)
            # Set the model or use the default for the provider
            self.model = model or LLMClientFactory.get_default_model(self.llm_provider)
            logger.info(f"UserMemory using LLM provider: {self.llm_provider} with model: {self.model}")
        except Exception as e:
            logger.warning(f"Could not initialize LLM client for UserMemory: {str(e)}")
            self.llm_client = None
            self.model = None
        
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
                with open(self.memory_file, "r") as f:
                    memory = json.load(f)
                    # Ensure the memory has all required keys
                    if "queries" not in memory:
                        memory["queries"] = []
                    return memory
            else:
                # Create new memory structure
                return {
                    "user_profile": {
                        "interests": [],
                        "goals": [],
                        "preferences": {},
                        "expertise_areas": []
                    },
                    "interactions": [],
                    "topics": {},
                    "queries": [],
                    "last_updated": datetime.now().isoformat()
                }
        except json.JSONDecodeError:
            logger.warning(f"Error parsing memory file. Creating new memory.")
            return {
                "user_profile": {
                    "interests": [],
                    "goals": [],
                    "preferences": {},
                    "expertise_areas": []
                },
                "interactions": [],
                "topics": {},
                "queries": [],
                "last_updated": datetime.now().isoformat()
            }
    
    def _save_memory(self):
        """Save memory to file."""
        try:
            # Update last_updated timestamp
            self.memory["last_updated"] = datetime.now().isoformat()
            
            with open(self.memory_file, "w") as f:
                json.dump(self.memory, f, indent=2)
                
            logger.info(f"Memory saved to {self.memory_file}")
        except Exception as e:
            logger.error(f"Error saving memory: {e}")
    
    def update_from_interaction(self, query: str, response: str, feedback: Optional[Dict[str, Any]] = None):
        """Update memory based on a new interaction.
        
        Args:
            query: The user's query
            response: The system's response
            feedback: Optional feedback from the user
        """
        # Add the interaction to the history
        interaction = {
            "timestamp": datetime.now().isoformat(),
            "query": query,
            "response_summary": self._summarize_response(response),
            "feedback": feedback
        }
        
        self.memory["interactions"].append(interaction)
        
        # Update user profile based on the interaction
        if self.llm_client:
            self._update_profile_from_interaction(query, response)
        
        # Save the updated memory
        self._save_memory()
    
    def _summarize_response(self, response: str) -> str:
        """Create a short summary of the response for storage.
        
        Args:
            response: The full response
            
        Returns:
            A summary of the response
        """
        # For now, just take the first 100 characters
        return response[:100] + "..." if len(response) > 100 else response
    
    def _update_profile_from_interaction(self, query: str, response: str):
        """Update the user profile based on the interaction.
        
        Args:
            query: The user's query
            response: The system's response
        """
        if not self.llm_client:
            return
            
        try:
            # Create a prompt for Claude to analyze the interaction
            prompt = f"""
            You are an AI assistant that analyzes user interactions to build a user profile.
            
            Here is a recent interaction:
            
            USER QUERY: {query}
            
            SYSTEM RESPONSE: {response}
            
            Based on this interaction, please extract:
            1. Potential user interests
            2. Possible user goals
            3. Any preferences the user might have
            4. Areas of expertise the user might have
            
            Format your response as JSON with the following structure:
            {{
                "interests": ["interest1", "interest2", ...],
                "goals": ["goal1", "goal2", ...],
                "preferences": {{"preference_type1": "value1", "preference_type2": "value2", ...}},
                "expertise_areas": ["area1", "area2", ...]
            }}
            
            Only include items that you can reasonably infer from the interaction.
            """
            
            # Call Claude to analyze the interaction
            response = self.llm_client.create_message(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=1000
            )
            
            analysis_text = response.content[0].text
            
            # Extract the JSON from the response
            try:
                # Find JSON in the response
                json_start = analysis_text.find("{")
                json_end = analysis_text.rfind("}") + 1
                
                if json_start >= 0 and json_end > json_start:
                    json_str = analysis_text[json_start:json_end]
                    analysis = json.loads(json_str)
                    
                    # Update the user profile
                    self._update_profile_with_analysis(analysis)
                else:
                    logger.warning("Could not find JSON in Claude's response")
            except json.JSONDecodeError:
                logger.warning("Error parsing JSON from Claude's response")
                
        except Exception as e:
            logger.error(f"Error updating profile from interaction: {e}")
    
    def _update_profile_with_analysis(self, analysis: Dict[str, Any]):
        """Update the user profile with the analysis from Claude.
        
        Args:
            analysis: The analysis from Claude
        """
        # Update interests
        if "interests" in analysis and isinstance(analysis["interests"], list):
            current_interests = set(self.memory["user_profile"]["interests"])
            new_interests = set(analysis["interests"])
            self.memory["user_profile"]["interests"] = list(current_interests.union(new_interests))
        
        # Update goals
        if "goals" in analysis and isinstance(analysis["goals"], list):
            current_goals = set(self.memory["user_profile"]["goals"])
            new_goals = set(analysis["goals"])
            self.memory["user_profile"]["goals"] = list(current_goals.union(new_goals))
        
        # Update preferences
        if "preferences" in analysis and isinstance(analysis["preferences"], dict):
            self.memory["user_profile"]["preferences"].update(analysis["preferences"])
        
        # Update expertise areas
        if "expertise_areas" in analysis and isinstance(analysis["expertise_areas"], list):
            current_expertise = set(self.memory["user_profile"]["expertise_areas"])
            new_expertise = set(analysis["expertise_areas"])
            self.memory["user_profile"]["expertise_areas"] = list(current_expertise.union(new_expertise))
    
    def get_user_context(self) -> str:
        """Get a context string summarizing what we know about the user.
        
        Returns:
            A context string for use in prompts
        """
        profile = self.memory["user_profile"]
        
        # Build the context string
        context_parts = []
        
        # Add interests
        if profile["interests"]:
            context_parts.append(f"User Interests: {', '.join(profile['interests'])}")
        
        # Add goals
        if profile["goals"]:
            context_parts.append(f"User Goals: {', '.join(profile['goals'])}")
        
        # Add preferences
        if profile["preferences"]:
            pref_str = ", ".join([f"{k}: {v}" for k, v in profile["preferences"].items()])
            context_parts.append(f"User Preferences: {pref_str}")
        
        # Add expertise areas
        if profile["expertise_areas"]:
            context_parts.append(f"User Expertise: {', '.join(profile['expertise_areas'])}")
        
        # Add recent interactions
        recent_interactions = self.memory["interactions"][-3:] if self.memory["interactions"] else []
        if recent_interactions:
            context_parts.append("Recent Interactions:")
            for interaction in recent_interactions:
                query_summary = interaction["query"][:50] + "..." if len(interaction["query"]) > 50 else interaction["query"]
                context_parts.append(f"- Query: {query_summary}")
        
        # Combine all parts
        if context_parts:
            return "\n".join(context_parts)
        else:
            return "No user context available."
    
    def get_context_for_query(self, query: str) -> str:
        """Get context relevant to a specific query.
        
        Args:
            query: The query to get context for
            
        Returns:
            Context relevant to the query
        """
        # For now, just return the general user context
        # In the future, this could use semantic search to find relevant past interactions
        return self.get_user_context()
    
    def get_memory_file_path(self) -> str:
        """Get the path to the memory file.
        
        Returns:
            The path to the memory file
        """
        return self.memory_file
    
    def clear_memory(self):
        """Clear all memory data."""
        self.memory = {
            "user_profile": {
                "interests": [],
                "goals": [],
                "preferences": {},
                "expertise_areas": []
            },
            "interactions": [],
            "topics": {},
            "queries": [],
            "last_updated": datetime.now().isoformat()
        }
        self._save_memory()
        logger.info("Memory cleared")

    def analyze_interests(self, queries: List[str]) -> Dict[str, Any]:
        """Analyze user interests based on their queries.
        
        Args:
            queries: List of user queries
            
        Returns:
            Analysis of user interests
        """
        if not queries:
            return {}
            
        if not self.llm_client:
            logger.warning("LLM client not available for interest analysis")
            return {}
            
        # Prepare the prompt
        prompt = f"""Based on the following user queries, analyze the user's interests, preferences, and focus areas.

User queries:
{json.dumps(queries, indent=2)}

Please provide a comprehensive analysis with the following sections:
1. Primary Interest Areas
2. Potential Industry Focus
3. Level of Expertise (based on query complexity)
4. Strategic Focus (operational, tactical, strategic)
5. Potential Professional Role

Format your response as JSON with these sections as keys.
"""
        
        try:
            # Call the LLM for analysis
            response = self.llm_client.create_message(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=2000
            )
            
            # Extract the JSON from the response
            if hasattr(response, 'content') and isinstance(response.content, list):
                response_text = response.content[0].text
            else:
                response_text = response.choices[0].message.content
            
            # Find JSON in the response
            json_start = response_text.find("{")
            json_end = response_text.rfind("}") + 1
            
            if json_start >= 0 and json_end > json_start:
                json_str = response_text[json_start:json_end]
                analysis = json.loads(json_str)
                return analysis
            else:
                logger.warning("Could not find JSON in interest analysis response")
                return {}
                
        except Exception as e:
            logger.error(f"Error analyzing interests: {str(e)}")
            return {}
    
    def get_context(self, query: str) -> Dict[str, Any]:
        """Get relevant context for a query based on user memory.
        
        Args:
            query: The current query
            
        Returns:
            Relevant context for the query
        """
        # If no memory exists, return empty context
        if not self.memory["interactions"] or not self.llm_client:
            return {}
            
        # Extract previous queries and responses
        previous_interactions = [
            {
                "query": interaction["query"],
                "date": interaction["timestamp"]
            }
            for interaction in self.memory["interactions"][-10:]  # Last 10 interactions
        ]
        
        # If interests are available, include them
        interests = self.memory.get("interests", {})
        
        # Prepare the context extraction prompt
        prompt = f"""Based on the user's current query and their history, identify relevant context that would be helpful for generating a strategic plan.

Current Query: {query}

User's recent interactions:
{json.dumps(previous_interactions, indent=2)}

User's analyzed interests and preferences:
{json.dumps(interests, indent=2)}

Please extract only the most relevant context from this information that would help in addressing the current query.
Format your response as JSON with relevant context categories as keys.
"""
        
        try:
            # Call the LLM for context extraction
            response = self.llm_client.create_message(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=1000
            )
            
            # Extract the JSON from the response
            if hasattr(response, 'content') and isinstance(response.content, list):
                response_text = response.content[0].text
            else:
                response_text = response.choices[0].message.content
            
            # Find JSON in the response
            json_start = response_text.find("{")
            json_end = response_text.rfind("}") + 1
            
            if json_start >= 0 and json_end > json_start:
                json_str = response_text[json_start:json_end]
                context = json.loads(json_str)
                return context
            else:
                logger.warning("Could not find JSON in context extraction response")
                return {}
                
        except Exception as e:
            logger.error(f"Error extracting context: {str(e)}")
            return {}
    
    def update_memory(self, query: str, context: Dict[str, Any], output: Dict[str, Any]) -> None:
        """Update memory with a new interaction.
        
        Args:
            query: The query from the interaction
            context: The context used for the interaction
            output: The output from the interaction
        """
        # Add the interaction to memory
        interaction = {
            "query": query,
            "context": context,
            "output_summary": {
                "panel_type": output.get("panel_type", ""),
                "model": output.get("model", ""),
                "feedback": output.get("feedback", None)
            },
            "timestamp": time.time(),
            "datetime": datetime.now().isoformat()
        }
        
        self.memory["interactions"].append(interaction)
        
        # Update queries list
        if query not in self.memory["queries"]:
            self.memory["queries"].append(query)
            
            # Periodically analyze interests (every 5 new queries)
            if len(self.memory["queries"]) % 5 == 0:
                interests = self.analyze_interests(self.memory["queries"])
                if interests:
                    self.memory["interests"] = interests
        
        # Save updated memory
        self._save_memory() 