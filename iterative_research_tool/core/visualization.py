"""Terminal visualization utilities for LangGraph flows."""

import sys
import time
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
        self.visited_nodes.add(node_name)
        self.node_times[node_name] = time.time()
        
        # Print node transition
        print(f"\n{Fore.YELLOW}▶ Executing node: {Style.BRIGHT}{node_name}{Style.RESET_ALL}")
        
    def show_node_complete(self, node_name: str, duration: Optional[float] = None):
        """Show that a node execution is complete.
        
        Args:
            node_name: Name of the completed node
            duration: Duration of the node execution in seconds
        """
        if not self.show_progress:
            return
            
        if duration is None and node_name in self.node_times:
            duration = time.time() - self.node_times[node_name]
            
        if duration is not None:
            print(f"{Fore.GREEN}✓ Completed node: {Style.BRIGHT}{node_name}{Style.RESET_ALL} {Fore.BLUE}({duration:.2f}s){Style.RESET_ALL}")
        else:
            print(f"{Fore.GREEN}✓ Completed node: {Style.BRIGHT}{node_name}{Style.RESET_ALL}")
            
    def show_thought(self, thought: str):
        """Show a thought from the thinking process.
        
        Args:
            thought: The thought to display
        """
        if not self.show_thoughts:
            return
            
        # Format and display the thought
        print(f"\n{Fore.MAGENTA}💭 Thinking:{Style.RESET_ALL}")
        
        # Wrap and indent the thought for better readability
        wrapped_thought = self._wrap_text(thought, width=80, indent=2)
        print(f"{Fore.WHITE}{wrapped_thought}{Style.RESET_ALL}")
        
    def show_plan(self, plan: str):
        """Show the generated plan.
        
        Args:
            plan: The generated plan to display
        """
        if not self.show_progress:
            return
            
        print(f"\n{Fore.CYAN}📝 Generated Plan:{Style.RESET_ALL}")
        # We don't print the full plan here as it might be very long
        print(f"{Fore.CYAN}Plan generated successfully.{Style.RESET_ALL}")
        
    def end_visualization(self):
        """End the visualization."""
        if not self.show_progress:
            return
            
        print(f"\n{Fore.CYAN}╔{'═' * 60}╗{Style.RESET_ALL}")
        print(f"{Fore.CYAN}║{Style.RESET_ALL} {Fore.WHITE}{Style.BRIGHT}Execution Complete{Style.RESET_ALL}{' ' * 43}{Fore.CYAN}║{Style.RESET_ALL}")
        print(f"{Fore.CYAN}╚{'═' * 60}╝{Style.RESET_ALL}\n")
        
    def _wrap_text(self, text: str, width: int = 80, indent: int = 0) -> str:
        """Wrap text to a specified width with indentation.
        
        Args:
            text: Text to wrap
            width: Maximum width of each line
            indent: Number of spaces to indent each line
            
        Returns:
            Wrapped and indented text
        """
        lines = []
        for line in text.split('\n'):
            # Process each line
            current_line = ' ' * indent
            for word in line.split():
                # If adding this word would exceed the width
                if len(current_line) + len(word) + 1 > width and len(current_line) > indent:
                    # Add the current line to lines and start a new one
                    lines.append(current_line)
                    current_line = ' ' * indent
                
                # Add the word to the current line
                if len(current_line) > indent:
                    current_line += ' '
                current_line += word
            
            # Add the last line
            if current_line:
                lines.append(current_line)
        
        return '\n'.join(lines)


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
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
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