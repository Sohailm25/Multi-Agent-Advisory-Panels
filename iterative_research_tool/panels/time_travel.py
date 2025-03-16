"""Time travel module for rewinding and exploring alternative paths."""

import os
import json
import logging
import time
from typing import Dict, List, Any, Optional
from copy import deepcopy

logger = logging.getLogger(__name__)

class TimeTravel:
    """Enables time travel functionality for exploring alternative paths."""
    
    def __init__(self, max_checkpoints: int = 10):
        """Initialize the time travel module.
        
        Args:
            max_checkpoints: Maximum number of checkpoints to store
        """
        self.max_checkpoints = max_checkpoints
        self.checkpoints = {}
        self.checkpoint_order = []
    
    def save_state(self, state: Dict[str, Any], checkpoint_name: str):
        """Save the current state as a checkpoint.
        
        Args:
            state: The state to save
            checkpoint_name: Name of the checkpoint
        """
        # Make a deep copy to avoid reference issues
        self.checkpoints[checkpoint_name] = deepcopy(state)
        
        # Add to order if not already present
        if checkpoint_name not in self.checkpoint_order:
            self.checkpoint_order.append(checkpoint_name)
        
        # Enforce maximum number of checkpoints
        if len(self.checkpoint_order) > self.max_checkpoints:
            oldest = self.checkpoint_order.pop(0)
            if oldest in self.checkpoints:
                del self.checkpoints[oldest]
        
        logger.info(f"Saved checkpoint: {checkpoint_name}")
    
    def load_state(self, checkpoint_name: str) -> Optional[Dict[str, Any]]:
        """Load a state from a checkpoint.
        
        Args:
            checkpoint_name: Name of the checkpoint to load
            
        Returns:
            The state at the checkpoint, or None if not found
        """
        if checkpoint_name in self.checkpoints:
            # Return a deep copy to avoid reference issues
            return deepcopy(self.checkpoints[checkpoint_name])
        else:
            logger.warning(f"Checkpoint not found: {checkpoint_name}")
            return None
    
    def get_checkpoints(self) -> List[str]:
        """Get the list of available checkpoints.
        
        Returns:
            List of checkpoint names
        """
        return self.checkpoint_order
    
    def create_branch(self, checkpoint_name: str, branch_name: str) -> bool:
        """Create a new branch from a checkpoint.
        
        Args:
            checkpoint_name: Name of the checkpoint to branch from
            branch_name: Name of the new branch
            
        Returns:
            True if successful, False otherwise
        """
        if checkpoint_name in self.checkpoints:
            # Create a new checkpoint with the branch name
            self.checkpoints[branch_name] = deepcopy(self.checkpoints[checkpoint_name])
            
            # Add to order
            self.checkpoint_order.append(branch_name)
            
            # Enforce maximum number of checkpoints
            if len(self.checkpoint_order) > self.max_checkpoints:
                oldest = self.checkpoint_order.pop(0)
                if oldest in self.checkpoints:
                    del self.checkpoints[oldest]
            
            logger.info(f"Created branch {branch_name} from checkpoint {checkpoint_name}")
            return True
        else:
            logger.warning(f"Cannot create branch: checkpoint {checkpoint_name} not found")
            return False
    
    def compare_states(self, checkpoint1: str, checkpoint2: str) -> Dict[str, Any]:
        """Compare two checkpoints and return the differences.
        
        Args:
            checkpoint1: First checkpoint name
            checkpoint2: Second checkpoint name
            
        Returns:
            Dictionary of differences
        """
        if checkpoint1 not in self.checkpoints or checkpoint2 not in self.checkpoints:
            logger.warning(f"Cannot compare: one or both checkpoints not found")
            return {"error": "One or both checkpoints not found"}
        
        state1 = self.checkpoints[checkpoint1]
        state2 = self.checkpoints[checkpoint2]
        
        # Simple comparison for now - could be enhanced with deep diff
        differences = {
            "checkpoint1": checkpoint1,
            "checkpoint2": checkpoint2,
            "differences": []
        }
        
        # Compare top-level keys
        for key in set(list(state1.keys()) + list(state2.keys())):
            if key not in state1:
                differences["differences"].append(f"Key '{key}' only in {checkpoint2}")
            elif key not in state2:
                differences["differences"].append(f"Key '{key}' only in {checkpoint1}")
            elif state1[key] != state2[key]:
                differences["differences"].append(f"Key '{key}' differs between checkpoints")
        
        return differences 