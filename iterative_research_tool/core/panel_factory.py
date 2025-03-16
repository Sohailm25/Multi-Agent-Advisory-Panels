"""Panel Factory module for dynamically loading and creating panels."""

import os
import importlib
import logging
import inspect
from typing import Dict, Any, Type, Optional, List
import pkgutil

# Local imports
from iterative_research_tool.panels import BasePanel

logger = logging.getLogger(__name__)

class PanelFactory:
    """Factory class for creating panel instances dynamically.
    
    This class discovers and instantiates panels from the panels directory,
    allowing users to add their own custom panels easily.
    """
    
    def __init__(self):
        """Initialize the panel factory."""
        self.panel_classes: Dict[str, Type[BasePanel]] = {}
        self.panel_modules = {}
        
    def discover_panels(self, additional_paths: List[str] = None) -> None:
        """Discover and register all panel classes from the panels directory.
        
        Args:
            additional_paths: Optional list of additional directory paths to search for panels
        """
        from iterative_research_tool import panels
        
        # Register built-in panels
        self._discover_panels_in_package(panels)
        
        # Register panels from additional paths if provided
        if additional_paths:
            for path in additional_paths:
                if os.path.isdir(path):
                    logger.info(f"Discovering panels in additional path: {path}")
                    self._discover_panels_in_directory(path)
                else:
                    logger.warning(f"Additional path does not exist: {path}")
    
    def _discover_panels_in_package(self, package):
        """Discover panels in a Python package.
        
        Args:
            package: The Python package to search for panels
        """
        logger.info(f"Discovering panels in package: {package.__name__}")
        
        for _, module_name, is_pkg in pkgutil.iter_modules(package.__path__, package.__name__ + '.'):
            if not is_pkg and not module_name.endswith('__init__'):
                try:
                    module = importlib.import_module(module_name)
                    self._register_panels_from_module(module)
                except ImportError as e:
                    logger.error(f"Error importing module {module_name}: {e}")
    
    def _discover_panels_in_directory(self, directory_path: str) -> None:
        """Discover panels in a directory.
        
        Args:
            directory_path: Path to directory to search for panel modules
        """
        for file_name in os.listdir(directory_path):
            if file_name.endswith(".py") and not file_name.startswith("__"):
                module_path = os.path.join(directory_path, file_name)
                module_name = file_name[:-3]  # Remove .py extension
                
                try:
                    # Add directory to path temporarily
                    import sys
                    sys.path.insert(0, os.path.dirname(directory_path))
                    
                    # Import the module
                    module_spec = importlib.util.spec_from_file_location(module_name, module_path)
                    if module_spec and module_spec.loader:
                        module = importlib.util.module_from_spec(module_spec)
                        module_spec.loader.exec_module(module)
                        self._register_panels_from_module(module)
                    
                    # Remove directory from path
                    sys.path.pop(0)
                except Exception as e:
                    logger.error(f"Error loading module {module_name} from {module_path}: {e}")
    
    def _register_panels_from_module(self, module) -> None:
        """Register all panel classes from a module.
        
        Args:
            module: The module to search for panel classes
        """
        for name, obj in inspect.getmembers(module):
            if (inspect.isclass(obj) and 
                issubclass(obj, BasePanel) and 
                obj != BasePanel):
                
                # Normalize the panel name to hyphenated format
                panel_type = self._class_name_to_panel_type(name)
                
                logger.info(f"Registering panel: {panel_type} -> {obj.__module__}.{name}")
                self.panel_classes[panel_type] = obj
                self.panel_modules[panel_type] = module
    
    def _class_name_to_panel_type(self, class_name: str) -> str:
        """Convert a class name to a panel type string.
        
        Args:
            class_name: The class name to convert
            
        Returns:
            The panel type string in hyphenated format
        """
        # Remove 'Panel' suffix if present
        if class_name.endswith('Panel'):
            name = class_name[:-5]
        else:
            name = class_name
        
        # Convert CamelCase to hyphenated-lowercase
        import re
        s1 = re.sub('(.)([A-Z][a-z]+)', r'\1-\2', name)
        hyphenated = re.sub('([a-z0-9])([A-Z])', r'\1-\2', s1).lower()
        
        return hyphenated
    
    def create_panel(self, panel_type: str, **kwargs) -> BasePanel:
        """Create a panel instance of the specified type.
        
        Args:
            panel_type: The type of panel to create
            **kwargs: Additional arguments to pass to the panel constructor
            
        Returns:
            An instance of the specified panel type
            
        Raises:
            ValueError: If the panel type is not registered
        """
        if panel_type not in self.panel_classes:
            available_panels = ", ".join(sorted(self.panel_classes.keys()))
            raise ValueError(f"Unknown panel type: {panel_type}. Available panels: {available_panels}")
        
        panel_class = self.panel_classes[panel_type]
        logger.info(f"Creating panel instance: {panel_type} ({panel_class.__module__}.{panel_class.__name__})")
        
        return panel_class(**kwargs)
    
    def list_available_panels(self) -> List[str]:
        """List all available panel types.
        
        Returns:
            List of available panel types
        """
        return sorted(self.panel_classes.keys())
    
    def get_panel_info(self, panel_type: str) -> Dict[str, Any]:
        """Get information about a panel.
        
        Args:
            panel_type: The type of panel to get information for
            
        Returns:
            Dictionary with panel information
            
        Raises:
            ValueError: If the panel type is not registered
        """
        if panel_type not in self.panel_classes:
            available_panels = ", ".join(sorted(self.panel_classes.keys()))
            raise ValueError(f"Unknown panel type: {panel_type}. Available panels: {available_panels}")
        
        panel_class = self.panel_classes[panel_type]
        
        info = {
            "name": panel_class.__name__,
            "module": panel_class.__module__,
            "docstring": panel_class.__doc__ or "No documentation available.",
        }
        
        return info

# Create a singleton instance
panel_factory = PanelFactory() 