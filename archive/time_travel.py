"""Time travel module for exploring alternative strategic paths."""

import logging
import os
import json
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
from pathlib import Path

# LangGraph imports
from langgraph.checkpoint.memory import MemorySaver

logger = logging.getLogger(__name__)

class TimeTravel:
    """Time travel functionality for exploring alternative strategic paths."""
    
    def __init__(
        self,
        checkpoint_dir: Optional[str] = None,
        max_checkpoints: int = 100
    ):
        """Initialize the time travel module.
        
        Args:
            checkpoint_dir: Directory to store checkpoints
            max_checkpoints: Maximum number of checkpoints to keep
        """
        self.checkpoint_dir = checkpoint_dir or os.path.expanduser("~/.config/iterative_research_tool/checkpoints")
        self.max_checkpoints = max_checkpoints
        
        # Ensure the checkpoint directory exists
        os.makedirs(self.checkpoint_dir, exist_ok=True)
        
        # Initialize the memory saver
        self.memory_saver = MemorySaver(self.checkpoint_dir)
        
        # Load checkpoint index
        self.checkpoint_index = self._load_checkpoint_index()
        
    def _load_checkpoint_index(self) -> Dict[str, Any]:
        """Load the checkpoint index.
        
        Returns:
            The checkpoint index
        """
        index_path = os.path.join(self.checkpoint_dir, "index.json")
        if os.path.exists(index_path):
            try:
                with open(index_path, "r") as f:
                    return json.load(f)
            except json.JSONDecodeError:
                logger.warning(f"Error parsing checkpoint index. Creating new index.")
                return {"checkpoints": []}
        else:
            return {"checkpoints": []}
    
    def _save_checkpoint_index(self):
        """Save the checkpoint index."""
        index_path = os.path.join(self.checkpoint_dir, "index.json")
        with open(index_path, "w") as f:
            json.dump(self.checkpoint_index, f, indent=2)
    
    def save_checkpoint(self, state: Dict[str, Any], query: str) -> str:
        """Save a checkpoint.
        
        Args:
            state: The state to save
            query: The query associated with the state
            
        Returns:
            The checkpoint ID
        """
        # Generate a checkpoint ID
        checkpoint_id = f"checkpoint_{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        # Save the checkpoint
        self.memory_saver.save(checkpoint_id, state)
        
        # Update the index
        self.checkpoint_index["checkpoints"].append({
            "id": checkpoint_id,
            "timestamp": datetime.now().isoformat(),
            "query": query,
            "state_summary": self._generate_state_summary(state)
        })
        
        # Trim old checkpoints if needed
        if len(self.checkpoint_index["checkpoints"]) > self.max_checkpoints:
            old_checkpoint = self.checkpoint_index["checkpoints"].pop(0)
            old_checkpoint_path = os.path.join(self.checkpoint_dir, f"{old_checkpoint['id']}.json")
            if os.path.exists(old_checkpoint_path):
                os.remove(old_checkpoint_path)
        
        # Save the updated index
        self._save_checkpoint_index()
        
        return checkpoint_id
    
    def load_checkpoint(self, checkpoint_id: str) -> Optional[Dict[str, Any]]:
        """Load a checkpoint.
        
        Args:
            checkpoint_id: The ID of the checkpoint to load
            
        Returns:
            The loaded state, or None if the checkpoint doesn't exist
        """
        try:
            return self.memory_saver.load(checkpoint_id)
        except FileNotFoundError:
            logger.error(f"Checkpoint {checkpoint_id} not found.")
            return None
    
    def get_recent_checkpoints(self, n: int = 5) -> List[Dict[str, Any]]:
        """Get the most recent checkpoints.
        
        Args:
            n: Number of checkpoints to return
            
        Returns:
            List of checkpoint metadata
        """
        return self.checkpoint_index["checkpoints"][-n:]
    
    def rewind(self, steps: int) -> Optional[Tuple[Dict[str, Any], str]]:
        """Rewind to a previous checkpoint.
        
        Args:
            steps: Number of steps to rewind
            
        Returns:
            Tuple of (state, query) for the rewound checkpoint, or None if invalid
        """
        if steps <= 0 or steps > len(self.checkpoint_index["checkpoints"]):
            logger.error(f"Invalid rewind steps: {steps}. Valid range: 1-{len(self.checkpoint_index['checkpoints'])}")
            return None
        
        # Get the checkpoint to rewind to
        checkpoint_index = len(self.checkpoint_index["checkpoints"]) - steps
        checkpoint = self.checkpoint_index["checkpoints"][checkpoint_index]
        
        # Load the checkpoint
        state = self.load_checkpoint(checkpoint["id"])
        if state is None:
            return None
        
        return state, checkpoint["query"]
    
    def _generate_state_summary(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Generate a summary of the state for the index.
        
        Args:
            state: The state to summarize
            
        Returns:
            A summary of the state
        """
        summary = {}
        
        # Include basic information
        if "query" in state:
            summary["query"] = state["query"]
        
        if "panel_type" in state:
            summary["panel_type"] = state["panel_type"]
        
        if "current_agent" in state:
            summary["current_agent"] = state["current_agent"]
        
        # Include a list of agents that have run
        if "agent_outputs" in state:
            summary["agents_run"] = list(state["agent_outputs"].keys())
        
        return summary 