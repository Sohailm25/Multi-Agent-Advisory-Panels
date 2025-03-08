"""Document parsing utilities for processing Claude's responses."""

import re
import logging
from typing import List, Optional, Dict, Any

from iterative_research_tool.core.models import DocumentSection

logger = logging.getLogger(__name__)


class DocumentParser:
    """Utility class for parsing markdown documents from Claude's responses."""
    
    @staticmethod
    def parse_markdown(content: str) -> List[DocumentSection]:
        """Parse markdown content from Claude into DocumentSection objects.
        
        Args:
            content: Markdown content from Claude
            
        Returns:
            List of DocumentSection objects
        """
        logger.debug(f"Parsing markdown content of length {len(content)}")
        
        if not content or len(content.strip()) < 10:
            logger.warning("Content too short to parse")
            return []
            
        sections = []
        
        # Split content by second-level headers (##)
        section_pattern = r'(?:^|\n)##\s+(.+?)\s*(?:\n|$)((?:.+?)?)(?=(?:\n##\s+|$))'
        section_matches = list(re.finditer(section_pattern, content, re.DOTALL))
        
        if not section_matches:
            # Try to extract at least one section from the content
            logger.warning("No section headers found, creating a default section")
            # Create a default section with the content
            title = "Main Section"
            
            # Try to extract a title from first-level header
            title_match = re.search(r'^#\s+(.+?)(?:\n|$)', content)
            if title_match:
                title = title_match.group(1).strip()
                content = content.replace(title_match.group(0), '', 1).strip()
                
            sections.append(DocumentParser._create_section(title, content))
            return sections
        
        # Process each section
        for match in section_matches:
            title = match.group(1).strip()
            content = match.group(2).strip()
            
            sections.append(DocumentParser._create_section(title, content))
        
        # Add confidence scores and extract citations
        for section in sections:
            section.citations = DocumentParser._extract_citations(section.content)
            if section.citations:
                # Calculate average reliability if citations have reliability scores
                reliability_scores = [c.get('reliability', 0.8) for c in section.citations]
                section.confidence_score = sum(reliability_scores) / len(reliability_scores)
            else:
                section.confidence_score = 0.5
        
        return sections
    
    @staticmethod
    def _create_section(title: str, content: str) -> DocumentSection:
        """Create a DocumentSection from title and content.
        
        Args:
            title: Section title
            content: Section content
            
        Returns:
            DocumentSection object
        """
        # Extract subsections (third-level headers)
        subsections = []
        main_content = content
        
        subsection_pattern = r'(?:^|\n)###\s+(.+?)\s*(?:\n|$)((?:.+?)?)(?=(?:\n###\s+|$))'
        subsection_matches = list(re.finditer(subsection_pattern, content, re.DOTALL))
        
        if subsection_matches:
            # Extract the content before the first subsection
            first_subsection_start = subsection_matches[0].start()
            main_content = content[:first_subsection_start].strip()
            
            # Process each subsection
            for match in subsection_matches:
                subsection_title = match.group(1).strip()
                subsection_content = match.group(2).strip()
                
                subsection = DocumentSection(
                    title=subsection_title,
                    content=subsection_content
                )
                subsections.append(subsection)
        
        # Create the main section
        section = DocumentSection(
            title=title,
            content=main_content,
            subsections=subsections
        )
        
        return section
    
    @staticmethod
    def _extract_citations(content: str) -> List[Dict[str, Any]]:
        """Extract citations from section content.
        
        Args:
            content: Section content
            
        Returns:
            List of citation dictionaries
        """
        citations = []
        
        # Look for citations in format [1], [2], etc.
        citation_refs = re.findall(r'\[(\d+)\]', content)
        citation_numbers = set(int(ref) for ref in citation_refs)
        
        # Extract citation section if it exists
        citation_section_match = re.search(r'(?:^|\n)(?:References|Citations|Sources):\s*\n((?:.+?)?)(?=\n##|\n\*\*Confidence Score|\Z)', content, re.DOTALL | re.IGNORECASE)
        
        if citation_section_match:
            citation_content = citation_section_match.group(1).strip()
            
            # Pattern for numbered citations
            # Example: 1. https://example.com (Reliability: 0.80)
            citation_pattern = r'(?:^|\n)(\d+)\.\s+(.*?)(?:\(Reliability:\s*([\d.]+)\))?(?:\n|$)'
            for match in re.finditer(citation_pattern, citation_content, re.MULTILINE):
                number = int(match.group(1))
                source = match.group(2).strip()
                reliability = float(match.group(3)) if match.group(3) else 0.8
                
                if number in citation_numbers or not citation_numbers:
                    citations.append({
                        'source': source,
                        'reliability': reliability
                    })
        
        # If we didn't find formatted citations but have reference numbers, create placeholder citations
        if citation_numbers and not citations:
            for num in sorted(citation_numbers):
                citations.append({
                    'source': f"Unknown source #{num}",
                    'reliability': 0.8
                })
        
        return citations 