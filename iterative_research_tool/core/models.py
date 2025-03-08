"""Data models for document representation."""

from typing import Dict, List, Optional
from pydantic import BaseModel, Field
import copy


class DocumentSection(BaseModel):
    """Represents a section in the research document."""
    title: str
    content: str
    confidence_score: float = 0.0
    citations: List[Dict] = Field(default_factory=list)
    subsections: List["DocumentSection"] = Field(default_factory=list)
    
    def to_markdown(self, level: int = 2) -> str:
        """Convert section to markdown format."""
        hashes = "#" * level
        md = f"{hashes} {self.title}\n\n{self.content}\n\n"
        
        # Add citations if present
        if self.citations:
            md += f"{'#' * (level + 1)} Citations\n\n"
            for i, citation in enumerate(self.citations):
                md += f"{i+1}. {citation.get('source', 'Unknown source')} "
                md += f"(Reliability: {citation.get('reliability', 0.0):.2f})\n"
            md += "\n"
        
        # Add confidence score
        md += f"**Confidence Score**: {self.confidence_score:.2f}\n\n"
        
        # Add subsections
        for subsection in self.subsections:
            md += subsection.to_markdown(level + 1)
            
        return md


class ResearchDocument(BaseModel):
    """Represents the full research document."""
    title: str
    version: int = 1
    sections: List[DocumentSection] = Field(default_factory=list)
    metadata: Dict = Field(default_factory=dict)
    
    def to_markdown(self) -> str:
        """Convert document to markdown format."""
        md = f"# {self.title}\n\n"
        
        # Add metadata if present
        if self.metadata:
            md += "## Metadata\n\n"
            for key, value in self.metadata.items():
                md += f"- **{key}**: {value}\n"
            md += "\n"
        
        # Add sections
        for section in self.sections:
            md += section.to_markdown()
            
        return md
    
    def copy(self, deep: bool = False) -> "ResearchDocument":
        """Create a copy of the document.
        
        Args:
            deep: Whether to make a deep copy of all sections and metadata
        
        Returns:
            A copy of the document
        """
        if not deep:
            # Shallow copy
            return ResearchDocument(
                title=self.title,
                version=self.version,
                sections=self.sections,
                metadata=self.metadata
            )
        
        # Deep copy (completely new objects for sections, subsections, etc.)
        return ResearchDocument(
            title=self.title,
            version=self.version,
            sections=copy.deepcopy(self.sections),
            metadata=copy.deepcopy(self.metadata)
        )
    
    def from_markdown(self, markdown_text: str) -> "ResearchDocument":
        """Parse a markdown document into a ResearchDocument structure.
        
        Returns a new document instance.
        """
        # This is a placeholder for now, will be implemented later
        return self 