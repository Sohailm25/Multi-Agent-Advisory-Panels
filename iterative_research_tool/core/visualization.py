"""Terminal visualization utilities for LangGraph flows."""

import sys
import time
import os
import json
from typing import Dict, List, Any, Optional
import logging
from colorama import Fore, Style, init

# Initialize colorama
init()

logger = logging.getLogger(__name__)

class TerminalVisualizer:
    """Visualize LangGraph execution in the terminal."""
    
    def __init__(self, show_progress: bool = True, show_thoughts: bool = True):
        """Initialize the terminal visualizer.
        
        Args:
            show_progress: Whether to show progress indicators
            show_thoughts: Whether to show thinking process
        """
        self.show_progress = show_progress
        self.show_thoughts = show_thoughts
        self.current_node = None
        self.visited_nodes = set()
        self.node_times = {}
        
    def start_visualization(self, graph_name: str):
        """Start visualizing a graph execution.
        
        Args:
            graph_name: Name of the graph being executed
        """
        if not self.show_progress:
            return
            
        print(f"\n{Fore.CYAN}╔{'═' * 60}╗{Style.RESET_ALL}")
        print(f"{Fore.CYAN}║{Style.RESET_ALL} {Fore.WHITE}{Style.BRIGHT}Executing {graph_name}{Style.RESET_ALL}{' ' * (50 - len(graph_name))}{Fore.CYAN}║{Style.RESET_ALL}")
        print(f"{Fore.CYAN}╚{'═' * 60}╝{Style.RESET_ALL}")
        
    def update_node(self, node_name: str):
        """Update the current node being executed.
        
        Args:
            node_name: Name of the current node
        """
        if not self.show_progress:
            return
            
        self.current_node = node_name
        self.node_times[node_name] = time.time()
        
        print(f"\n{Fore.YELLOW}▶ Executing: {node_name}{Style.RESET_ALL}")
        
    def update_agent_status(self, agent_name: str, status: str):
        """Update the status of an agent.
        
        Args:
            agent_name: Name of the agent
            status: Status of the agent (e.g., "processing", "complete")
        """
        if not self.show_progress:
            return
            
        status_color = Fore.YELLOW if status == "processing" else Fore.GREEN
        print(f"\n{status_color}▶ Agent: {agent_name} - Status: {status}{Style.RESET_ALL}")
        
    def show_node_complete(self, node_name: str, duration: Optional[float] = None):
        """Show that a node has completed execution.
        
        Args:
            node_name: Name of the completed node
            duration: Duration of the node execution in seconds
        """
        if not self.show_progress:
            return
            
        self.visited_nodes.add(node_name)
        
        if duration is None and node_name in self.node_times:
            duration = time.time() - self.node_times[node_name]
            
        duration_str = f" ({duration:.2f}s)" if duration is not None else ""
        print(f"{Fore.GREEN}✓ Completed: {node_name}{duration_str}{Style.RESET_ALL}")
        
    def show_thought(self, thought: str):
        """Show a thought from the thinking process.
        
        Args:
            thought: The thought to show
        """
        if not self.show_thoughts:
            return
            
        wrapped_thought = self._wrap_text(thought, width=80, indent=2)
        
        print(f"\n{Fore.BLUE}💭 Thinking:{Style.RESET_ALL}")
        print(f"{Fore.BLUE}{wrapped_thought}{Style.RESET_ALL}")
        
    def show_analysis(self, analysis: str):
        """Show an analysis of the query.
        
        Args:
            analysis: The analysis to show
        """
        if not self.show_thoughts:
            return
            
        wrapped_analysis = self._wrap_text(analysis, width=80, indent=2)
        
        print(f"\n{Fore.BLUE}🔍 Analysis:{Style.RESET_ALL}")
        print(f"{Fore.BLUE}{wrapped_analysis}{Style.RESET_ALL}")
        
    def show_plan(self, plan: str):
        """Show a generated plan.
        
        Args:
            plan: The plan to show
        """
        if not self.show_progress:
            return
            
        wrapped_plan = self._wrap_text(plan, width=80, indent=2)
        
        print(f"\n{Fore.GREEN}📝 Plan:{Style.RESET_ALL}")
        print(f"{Fore.WHITE}{wrapped_plan}{Style.RESET_ALL}")
        
    def show_final_output(self, output: str):
        """Show the final output.
        
        Args:
            output: The final output to show
        """
        if not self.show_progress:
            return
            
        wrapped_output = self._wrap_text(output, width=80, indent=2)
        
        print(f"\n{Fore.GREEN}🏁 Final Output:{Style.RESET_ALL}")
        print(f"{Fore.WHITE}{wrapped_output}{Style.RESET_ALL}")
        
    def show_error(self, error: str):
        """Show an error message.
        
        Args:
            error: The error message to show
        """
        if not self.show_progress:
            return
            
        wrapped_error = self._wrap_text(error, width=80, indent=2)
        
        print(f"\n{Fore.RED}❌ Error:{Style.RESET_ALL}")
        print(f"{Fore.RED}{wrapped_error}{Style.RESET_ALL}")
        
    def show_message(self, message: str):
        """Show a general message.
        
        Args:
            message: The message to show
        """
        if not self.show_progress:
            return
            
        wrapped_message = self._wrap_text(message, width=80, indent=2)
        
        print(f"\n{Fore.CYAN}ℹ️ {wrapped_message}{Style.RESET_ALL}")
        
    def show_success(self, message: str):
        """Show a success message.
        
        Args:
            message: The success message to show
        """
        if not self.show_progress:
            return
            
        wrapped_message = self._wrap_text(message, width=80, indent=2)
        
        print(f"\n{Fore.GREEN}✅ {wrapped_message}{Style.RESET_ALL}")
        
    def end_visualization(self):
        """End the visualization."""
        if not self.show_progress:
            return
            
        print(f"\n{Fore.CYAN}╔{'═' * 60}╗{Style.RESET_ALL}")
        print(f"{Fore.CYAN}║{Style.RESET_ALL} {Fore.WHITE}{Style.BRIGHT}Execution Complete{Style.RESET_ALL}{' ' * 43}{Fore.CYAN}║{Style.RESET_ALL}")
        print(f"{Fore.CYAN}╚{'═' * 60}╝{Style.RESET_ALL}")
        
    def _wrap_text(self, text: str, width: int = 80, indent: int = 0) -> str:
        """Wrap text to a specified width.
        
        Args:
            text: The text to wrap
            width: The maximum width of each line
            indent: The number of spaces to indent each line
            
        Returns:
            The wrapped text
        """
        if not text:
            return ""
            
        # Split the text into lines
        lines = text.split("\n")
        wrapped_lines = []
        
        for line in lines:
            # If the line is empty, add it as is
            if not line.strip():
                wrapped_lines.append(" " * indent)
                continue
                
            # If the line is shorter than the width, add it as is
            if len(line) <= width - indent:
                wrapped_lines.append(" " * indent + line)
                continue
                
            # Otherwise, wrap the line
            current_line = " " * indent
            for word in line.split():
                if len(current_line) + len(word) + 1 <= width:
                    if current_line != " " * indent:
                        current_line += " "
                    current_line += word
                else:
                    wrapped_lines.append(current_line)
                    current_line = " " * indent + word
            
            if current_line:
                wrapped_lines.append(current_line)
                
        return "\n".join(wrapped_lines)


class FeedbackCollector:
    """Collect feedback on generated plans."""
    
    def __init__(self, feedback_file: Optional[str] = None):
        """Initialize the feedback collector.
        
        Args:
            feedback_file: Path to the feedback file
        """
        self.feedback_file = feedback_file or os.path.expanduser("~/.config/iterative_research_tool/feedback.json")
        
        # Ensure the directory exists
        os.makedirs(os.path.dirname(self.feedback_file), exist_ok=True)
        
    def prompt_for_feedback(self, query: str, response: str) -> Dict[str, Any]:
        """Prompt the user for feedback on the generated response.
        
        Args:
            query: The original query
            response: The generated response
            
        Returns:
            The collected feedback
        """
        print(f"\n{Fore.CYAN}╔{'═' * 60}╗{Style.RESET_ALL}")
        print(f"{Fore.CYAN}║{Style.RESET_ALL} {Fore.WHITE}{Style.BRIGHT}Feedback{Style.RESET_ALL}{' ' * 51}{Fore.CYAN}║{Style.RESET_ALL}")
        print(f"{Fore.CYAN}╚{'═' * 60}╝{Style.RESET_ALL}")
        
        print(f"\n{Fore.CYAN}Would you like to provide feedback on the response? (y/n){Style.RESET_ALL}")
        feedback_choice = input("> ").strip().lower()
        
        if feedback_choice != "y":
            return {}
            
        feedback = {}
        
        # Collect rating
        print(f"\n{Fore.CYAN}How would you rate the response on a scale of 1-5?{Style.RESET_ALL}")
        rating = input("> ").strip()
        try:
            feedback["rating"] = int(rating)
        except ValueError:
            print(f"{Fore.YELLOW}Invalid rating. Using default value of 3.{Style.RESET_ALL}")
            feedback["rating"] = 3
            
        # Collect strengths
        print(f"\n{Fore.CYAN}What were the strengths of the response? (Press Enter to skip){Style.RESET_ALL}")
        strengths = input("> ").strip()
        if strengths:
            feedback["strengths"] = strengths
            
        # Collect weaknesses
        print(f"\n{Fore.CYAN}What were the weaknesses of the response? (Press Enter to skip){Style.RESET_ALL}")
        weaknesses = input("> ").strip()
        if weaknesses:
            feedback["weaknesses"] = weaknesses
            
        # Collect suggestions
        print(f"\n{Fore.CYAN}Do you have any suggestions for improvement? (Press Enter to skip){Style.RESET_ALL}")
        suggestions = input("> ").strip()
        if suggestions:
            feedback["suggestions"] = suggestions
            
        # Add metadata
        feedback["query"] = query
        feedback["timestamp"] = time.strftime("%Y-%m-%d %H:%M:%S")
        
        # Save feedback
        self._save_feedback(feedback)
        
        print(f"\n{Fore.GREEN}Thank you for your feedback!{Style.RESET_ALL}")
        
        return feedback
        
    def _save_feedback(self, feedback: Dict[str, Any]):
        """Save feedback to the feedback file.
        
        Args:
            feedback: The feedback to save
        """
        try:
            # Load existing feedback
            existing_feedback = []
            if os.path.exists(self.feedback_file):
                with open(self.feedback_file, "r") as f:
                    try:
                        existing_feedback = json.load(f)
                    except json.JSONDecodeError:
                        logger.warning(f"Error parsing feedback file. Creating new file.")
                        existing_feedback = []
                        
            # Add new feedback
            existing_feedback.append(feedback)
            
            # Save feedback
            with open(self.feedback_file, "w") as f:
                json.dump(existing_feedback, f, indent=2)
                
            logger.info(f"Feedback saved to {self.feedback_file}")
            
        except Exception as e:
            logger.error(f"Error saving feedback: {e}")
            
    def get_feedback_file_path(self) -> str:
        """Get the path to the feedback file.
        
        Returns:
            The path to the feedback file
        """
        return self.feedback_file 


class Visualizer(TerminalVisualizer):
    """Alias for TerminalVisualizer to maintain backward compatibility."""
    
    def __init__(self, show_progress: bool = True, show_thoughts: bool = True):
        """Initialize the visualizer.
        
        Args:
            show_progress: Whether to show progress indicators
            show_thoughts: Whether to show thinking process
        """
        super().__init__(show_progress=show_progress, show_thoughts=show_thoughts)
    
    # Functions specifically needed by strategic_planner.py
    def display_welcome(self, title: str):
        """Display a welcome message.
        
        Args:
            title: The title to display
        """
        self.start_visualization(title)
    
    def display_query(self, query: str):
        """Display the query.
        
        Args:
            query: The query to display
        """
        self.show_message(f"Query: {query}")
    
    def update_status(self, status: str):
        """Update the status.
        
        Args:
            status: The status to display
        """
        self.show_message(status)
    
    def display_plan(self, plan: Any):
        """Display a plan.
        
        Args:
            plan: The plan to display
        """
        if isinstance(plan, dict):
            plan_str = json.dumps(plan, indent=2)
        else:
            plan_str = str(plan)
        
        self.show_plan(plan_str)
    
    def display_error(self, error: str):
        """Display an error message.
        
        Args:
            error: The error message to display
        """
        self.show_error(error)
    
    def display_success(self, message: str):
        """Display a success message.
        
        Args:
            message: The success message to display
        """
        self.show_success(message)
    
    def display_message(self, message: str):
        """Display a general message.
        
        Args:
            message: The message to display
        """
        self.show_message(message)
        
    def collect_feedback(self) -> Dict[str, Any]:
        """Collect feedback.
        
        Returns:
            The collected feedback
        """
        # Implement feedback collection if needed
        return {
            "rating": 5,
            "comments": "Automated test feedback",
            "helpful": True
        } 