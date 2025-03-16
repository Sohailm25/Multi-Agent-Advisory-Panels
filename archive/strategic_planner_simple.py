"""Strategic Planner module without LangGraph dependency."""

import logging
import os
import json
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime

# Anthropic imports
from anthropic import Anthropic

# Visualization imports (simplified)
from colorama import Fore, Style, init

# Initialize colorama
init()

logger = logging.getLogger(__name__)

class TerminalVisualizer:
    """Simple terminal visualizer for the strategic planner."""
    
    def __init__(self, show_progress: bool = True):
        """Initialize the terminal visualizer.
        
        Args:
            show_progress: Whether to show progress indicators
        """
        self.show_progress = show_progress
        
    def show_header(self, title: str):
        """Show a header in the terminal.
        
        Args:
            title: The title to display
        """
        if not self.show_progress:
            return
            
        print(f"\n{Fore.CYAN}╔{'═' * 60}╗{Style.RESET_ALL}")
        print(f"{Fore.CYAN}║{Style.RESET_ALL} {Fore.WHITE}{Style.BRIGHT}{title}{Style.RESET_ALL}{' ' * (59 - len(title))}{Fore.CYAN}║{Style.RESET_ALL}")
        print(f"{Fore.CYAN}╚{'═' * 60}╝{Style.RESET_ALL}")
        
    def show_step(self, step_name: str):
        """Show a step in the terminal.
        
        Args:
            step_name: The name of the step
        """
        if not self.show_progress:
            return
            
        print(f"\n{Fore.YELLOW}▶ {Style.BRIGHT}{step_name}{Style.RESET_ALL}")
        
    def show_thought(self, thought: str):
        """Show a thought in the terminal.
        
        Args:
            thought: The thought to display
        """
        if not self.show_progress:
            return
            
        print(f"\n{Fore.MAGENTA}💭 Thinking:{Style.RESET_ALL}")
        print(f"{Fore.WHITE}{thought}{Style.RESET_ALL}")
        
    def show_success(self, message: str):
        """Show a success message in the terminal.
        
        Args:
            message: The message to display
        """
        if not self.show_progress:
            return
            
        print(f"{Fore.GREEN}✓ {message}{Style.RESET_ALL}")
        
    def show_footer(self):
        """Show a footer in the terminal."""
        if not self.show_progress:
            return
            
        print(f"\n{Fore.CYAN}╔{'═' * 60}╗{Style.RESET_ALL}")
        print(f"{Fore.CYAN}║{Style.RESET_ALL} {Fore.WHITE}{Style.BRIGHT}Execution Complete{Style.RESET_ALL}{' ' * 43}{Fore.CYAN}║{Style.RESET_ALL}")
        print(f"{Fore.CYAN}╚{'═' * 60}╝{Style.RESET_ALL}\n")


class FeedbackCollector:
    """Collect feedback on generated plans."""
    
    def __init__(self, save_feedback: bool = True, feedback_file: Optional[str] = None):
        """Initialize the feedback collector.
        
        Args:
            save_feedback: Whether to save feedback to a file
            feedback_file: Path to the feedback file
        """
        self.save_feedback = save_feedback
        self.feedback_file = feedback_file or "plan_feedback.txt"
        
    def collect_feedback(self, query: str, plan: str) -> Dict[str, Any]:
        """Collect feedback on a generated plan.
        
        Args:
            query: The original query
            plan: The generated plan
            
        Returns:
            Dictionary containing feedback data
        """
        print(f"\n{Fore.CYAN}╔{'═' * 60}╗{Style.RESET_ALL}")
        print(f"{Fore.CYAN}║{Style.RESET_ALL} {Fore.WHITE}{Style.BRIGHT}Plan Feedback{Style.RESET_ALL}{' ' * 47}{Fore.CYAN}║{Style.RESET_ALL}")
        print(f"{Fore.CYAN}╚{'═' * 60}╝{Style.RESET_ALL}")
        
        print(f"\nPlease rate the generated plan (1-5, where 5 is excellent):")
        
        # Collect rating
        rating = None
        while rating is None:
            try:
                user_input = input(f"{Fore.YELLOW}Rating (1-5): {Style.RESET_ALL}")
                rating = int(user_input)
                if rating < 1 or rating > 5:
                    print(f"{Fore.RED}Please enter a number between 1 and 5.{Style.RESET_ALL}")
                    rating = None
            except ValueError:
                print(f"{Fore.RED}Please enter a valid number.{Style.RESET_ALL}")
        
        # Collect comments
        print(f"\nPlease provide any additional comments (optional):")
        comments = input(f"{Fore.YELLOW}Comments: {Style.RESET_ALL}")
        
        # Collect improvement suggestions
        print(f"\nHow could the plan be improved? (optional):")
        improvements = input(f"{Fore.YELLOW}Improvements: {Style.RESET_ALL}")
        
        # Create feedback data
        feedback = {
            "timestamp": datetime.now().isoformat(),
            "query": query,
            "rating": rating,
            "comments": comments,
            "improvements": improvements
        }
        
        # Save feedback if enabled
        if self.save_feedback:
            self._save_feedback(feedback)
            
        print(f"\n{Fore.GREEN}Thank you for your feedback!{Style.RESET_ALL}")
        
        return feedback
    
    def _save_feedback(self, feedback: Dict[str, Any]):
        """Save feedback to a file.
        
        Args:
            feedback: Feedback data to save
        """
        try:
            with open(self.feedback_file, "a", encoding="utf-8") as f:
                f.write(f"--- Feedback: {feedback['timestamp']} ---\n")
                f.write(f"Query: {feedback['query']}\n")
                f.write(f"Rating: {feedback['rating']}/5\n")
                if feedback['comments']:
                    f.write(f"Comments: {feedback['comments']}\n")
                if feedback['improvements']:
                    f.write(f"Improvements: {feedback['improvements']}\n")
                f.write("\n")
                
            logger.info(f"Feedback saved to {self.feedback_file}")
        except Exception as e:
            logger.error(f"Error saving feedback: {e}")


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


class StrategicPlannerSimple:
    """Strategic Planner without LangGraph dependency."""
    
    def __init__(
        self, 
        claude_api_key: str, 
        claude_model: str = "claude-3-7-sonnet-20250219", 
        prompt_dir: Optional[str] = None,
        visualize: bool = True,
        collect_feedback: bool = True,
        feedback_file: Optional[str] = None,
        use_memory: bool = True,
        memory_file: Optional[str] = None
    ):
        """Initialize the strategic planner.
        
        Args:
            claude_api_key: API key for Claude
            claude_model: Claude model to use
            prompt_dir: Directory containing prompt templates
            visualize: Whether to visualize the execution in the terminal
            collect_feedback: Whether to collect feedback on the generated plan
            feedback_file: Path to the feedback file
            use_memory: Whether to use user memory
            memory_file: Path to the memory file
        """
        self.claude_client = Anthropic(api_key=claude_api_key)
        self.claude_model = claude_model
        
        # Load the strategic planner prompt
        self.prompt_template = self._load_prompt_template(prompt_dir)
        
        # Set up visualization and feedback
        self.visualize = visualize
        self.collect_feedback = collect_feedback
        self.visualizer = TerminalVisualizer() if visualize else None
        self.feedback_collector = FeedbackCollector(
            save_feedback=collect_feedback,
            feedback_file=feedback_file
        ) if collect_feedback else None
        
        # Set up user memory
        self.use_memory = use_memory
        self.user_memory = UserMemory(
            memory_file=memory_file,
            claude_api_key=claude_api_key,
            claude_model=claude_model
        ) if use_memory else None
        
    def _load_prompt_template(self, prompt_dir: Optional[str] = None) -> str:
        """Load the strategic planner prompt template.
        
        Args:
            prompt_dir: Directory containing prompt templates
            
        Returns:
            The prompt template as a string
        """
        # Default prompt directories to check
        prompt_dirs = [
            prompt_dir,
            os.getenv("PROMPTS_DIRECTORY"),
            "prompts",
            os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "prompts"),
        ]
        
        # Filter out None values
        prompt_dirs = [d for d in prompt_dirs if d]
        
        # Try to find the prompt file in the directories
        prompt_filename = "strategic_planner.md"
        for directory in prompt_dirs:
            if not directory:
                continue
                
            prompt_path = Path(directory) / prompt_filename
            if prompt_path.exists():
                logger.info(f"Loading prompt template from {prompt_path}")
                with open(prompt_path, "r", encoding="utf-8") as f:
                    return f.read() + "\n\n{user_context}\n\nResearch Query: {query}\n\n"
        
        # If prompt file not found, use the default prompt
        logger.warning(f"Prompt file {prompt_filename} not found in any of the prompt directories. Using default prompt.")
        return """
You are a Strategic Research Planner, an expert at breaking down complex research questions into clear, actionable plans.

Your task is to analyze the given research query and develop a comprehensive strategic plan that:
1. Identifies the core components and sub-questions within the main research query
2. Outlines a logical sequence of investigation steps
3. Highlights potential challenges and how to address them
4. Suggests specific resources, methodologies, or frameworks to apply
5. Provides clear success criteria for each stage of the research

Think step-by-step and be thorough in your analysis. Your plan should be detailed enough that someone could follow it to conduct high-quality research on the topic.

{user_context}

Research Query: {query}

Strategic Research Plan:
"""
    
    def run(self, query: str) -> str:
        """Run the strategic planner on the given query.
        
        Args:
            query: The research query to plan for
            
        Returns:
            The strategic plan as a string
        """
        logger.info(f"Running strategic planner for query: {query}")
        
        # Start visualization
        if self.visualize:
            self.visualizer.show_header("Strategic Planner")
        
        try:
            # Step 1: Load user context
            if self.visualize:
                self.visualizer.show_step("Loading user context")
                
            user_context = ""
            if self.use_memory and self.user_memory:
                user_context = self.user_memory.get_context_for_query(query)
                if self.visualize:
                    self.visualizer.show_thought(f"Loaded user context:\n{user_context}")
            
            # Step 2: Generate thoughts
            if self.visualize:
                self.visualizer.show_step("Generating thoughts")
                
            # Generate thoughts using Claude
            system_prompt = "You are a strategic research planner. Think step by step about the query to understand its components and requirements."
            
            # Add user context to system prompt if available
            if user_context:
                system_prompt += f"\n\nUser Context:\n{user_context}"
            
            thoughts_message = self.claude_client.messages.create(
                model=self.claude_model,
                max_tokens=1000,
                temperature=0.7,
                system=system_prompt,
                messages=[
                    {"role": "user", "content": f"I need to research: {query}\n\nWhat are the key components, challenges, and approaches I should consider? Think step by step."}
                ]
            )
            
            thoughts = thoughts_message.content[0].text
            
            # Show thoughts in the visualizer
            if self.visualize:
                self.visualizer.show_thought(thoughts)
                self.visualizer.show_success("Generated thoughts")
            
            # Step 3: Create plan
            if self.visualize:
                self.visualizer.show_step("Creating strategic plan")
                
            # Format the prompt with user context
            formatted_prompt = self.prompt_template.format(
                query=query,
                user_context=user_context or ""
            )
            
            plan_message = self.claude_client.messages.create(
                model=self.claude_model,
                max_tokens=2000,
                temperature=0.5,
                system="You are a strategic research planner. Create a detailed, structured research plan.",
                messages=[
                    {"role": "user", "content": formatted_prompt}
                ]
            )
            
            plan = plan_message.content[0].text
            
            if self.visualize:
                self.visualizer.show_success("Generated strategic plan")
            
            # Step 4: Collect feedback
            feedback = None
            if self.collect_feedback and self.feedback_collector:
                if self.visualize:
                    self.visualizer.show_step("Collecting feedback")
                    
                feedback = self.feedback_collector.collect_feedback(
                    query=query,
                    plan=plan
                )
                
                if self.visualize:
                    self.visualizer.show_success("Collected feedback")
            
            # Step 5: Update user memory
            if self.use_memory and self.user_memory:
                if self.visualize:
                    self.visualizer.show_step("Updating user memory")
                    
                self.user_memory.add_interaction(
                    query=query,
                    response=plan,
                    feedback=feedback
                )
                
                if self.visualize:
                    memory_file = self.user_memory.get_memory_file_path()
                    self.visualizer.show_success(f"Updated user memory at: {memory_file}")
            
            # End visualization
            if self.visualize:
                self.visualizer.show_footer()
            
            return plan
            
        except Exception as e:
            logger.error(f"Error running strategic planner: {str(e)}")
            if self.visualize:
                self.visualizer.show_footer()
            return f"Error: {str(e)}" 