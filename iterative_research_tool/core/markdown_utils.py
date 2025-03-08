"""Utilities for processing markdown documents."""

import re
from typing import List, Dict, Optional, Tuple
import logging

from iterative_research_tool.core.models import DocumentSection, ResearchDocument

logger = logging.getLogger(__name__)


def parse_markdown(content: str) -> Tuple[str, List[DocumentSection]]:
    """Parse markdown content into document title and sections.
    
    Args:
        content: Markdown content to parse
        
    Returns:
        Tuple of (title, list of sections)
    """
    lines = content.split('\n')
    
    # Extract title (first h1)
    title = "Untitled Document"
    for line in lines:
        if line.startswith('# '):
            title = line.replace('# ', '').strip()
            break
    
    # Parse sections (h2 headers)
    sections = []
    current_section = None
    current_subsection = None
    current_content = []
    
    for line in lines:
        if line.startswith('## '):
            # Save previous section if it exists
            if current_section:
                if current_subsection:
                    current_subsection.content = '\n'.join(current_content).strip()
                    current_section.subsections.append(current_subsection)
                    current_subsection = None
                else:
                    current_section.content = '\n'.join(current_content).strip()
                sections.append(current_section)
            
            # Start new section
            section_title = line.replace('## ', '').strip()
            current_section = DocumentSection(title=section_title, content="")
            current_content = []
            
        elif line.startswith('### '):
            # Save content to current section or subsection
            if current_subsection:
                current_subsection.content = '\n'.join(current_content).strip()
                current_section.subsections.append(current_subsection)
            elif current_content and current_section:
                current_section.content = '\n'.join(current_content).strip()
                
            # Start new subsection
            subsection_title = line.replace('### ', '').strip()
            current_subsection = DocumentSection(title=subsection_title, content="")
            current_content = []
            
        else:
            current_content.append(line)
    
    # Save the last section/subsection
    if current_section:
        if current_subsection:
            current_subsection.content = '\n'.join(current_content).strip()
            current_section.subsections.append(current_subsection)
        else:
            current_section.content = '\n'.join(current_content).strip()
        sections.append(current_section)
    
    return title, sections


def extract_citations_from_markdown(content: str) -> List[Dict]:
    """Extract citations from markdown content.
    
    This looks for citation formats like:
    1. [Source](http://example.com)
    2. Source: http://example.com
    
    Args:
        content: Markdown content to parse
        
    Returns:
        List of citation dictionaries with 'source' key
    """
    citations = []
    
    # Pattern for [text](url)
    link_pattern = r'\[(.*?)\]\((https?://[^\s)]+)\)'
    for match in re.finditer(link_pattern, content):
        text, url = match.groups()
        citations.append({
            'source': url,
            'text': text,
            'reliability': 0.8  # Default reliability score
        })
    
    # Pattern for "Source: url"
    source_pattern = r'(?:Source|Reference|Citation):\s*(https?://[^\s]+)'
    for match in re.finditer(source_pattern, content, re.IGNORECASE):
        url = match.group(1)
        citations.append({
            'source': url,
            'reliability': 0.8  # Default reliability score
        })
    
    return citations


def markdown_to_document(content: str) -> ResearchDocument:
    """Convert markdown content to a ResearchDocument.
    
    Args:
        content: Markdown content
        
    Returns:
        ResearchDocument instance
    """
    title, sections = parse_markdown(content)
    
    # Extract citations and calculate confidence scores
    for section in sections:
        section.citations = extract_citations_from_markdown(section.content)
        
        # Set confidence score based on citations
        if section.citations:
            reliability_scores = [c.get('reliability', 0.8) for c in section.citations]
            section.confidence_score = sum(reliability_scores) / len(reliability_scores)
        else:
            section.confidence_score = 0.0
        
        # Process subsections
        for subsection in section.subsections:
            subsection.citations = extract_citations_from_markdown(subsection.content)
            
            if subsection.citations:
                reliability_scores = [c.get('reliability', 0.8) for c in subsection.citations]
                subsection.confidence_score = sum(reliability_scores) / len(reliability_scores)
            else:
                subsection.confidence_score = 0.0
    
    return ResearchDocument(title=title, sections=sections)


def create_version_history_document(documents: List[ResearchDocument]) -> str:
    """Create a version history document from a list of document versions.
    
    Args:
        documents: List of document versions in chronological order
        
    Returns:
        Markdown content of version history
    """
    if not documents:
        return "# Version History\n\nNo versions available."
    
    content = "# Version History\n\n"
    
    for i, doc in enumerate(documents):
        content += f"## Version {doc.version}\n\n"
        
        # Add summary of changes if this isn't the first version
        if i > 0:
            prev_doc = documents[i-1]
            content += "### Changes from Previous Version\n\n"
            
            # Compare sections
            current_sections = {s.title: s for s in doc.sections}
            prev_sections = {s.title: s for s in prev_doc.sections}
            
            # New sections
            new_sections = set(current_sections.keys()) - set(prev_sections.keys())
            if new_sections:
                content += "#### Added Sections\n\n"
                for section_title in new_sections:
                    content += f"- {section_title}\n"
                content += "\n"
            
            # Removed sections
            removed_sections = set(prev_sections.keys()) - set(current_sections.keys())
            if removed_sections:
                content += "#### Removed Sections\n\n"
                for section_title in removed_sections:
                    content += f"- {section_title}\n"
                content += "\n"
            
            # Changed sections
            common_sections = set(current_sections.keys()) & set(prev_sections.keys())
            changed_sections = []
            
            for section_title in common_sections:
                curr_section = current_sections[section_title]
                prev_section = prev_sections[section_title]
                
                # Compare content length as a simple metric
                curr_len = len(curr_section.content)
                prev_len = len(prev_section.content)
                change_percentage = abs(curr_len - prev_len) / max(prev_len, 1) * 100
                
                if change_percentage > 5:  # Consider significant if >5% change
                    change_type = "Expanded" if curr_len > prev_len else "Condensed"
                    confidence_change = curr_section.confidence_score - prev_section.confidence_score
                    confidence_status = "Increased" if confidence_change > 0 else "Decreased"
                    
                    changed_sections.append({
                        'title': section_title,
                        'change_type': change_type,
                        'change_percentage': change_percentage,
                        'confidence_change': confidence_change,
                        'confidence_status': confidence_status
                    })
            
            if changed_sections:
                content += "#### Modified Sections\n\n"
                for section in changed_sections:
                    content += f"- {section['title']}: {section['change_type']} by {section['change_percentage']:.1f}%, "
                    content += f"Confidence {section['confidence_status']} by {abs(section['confidence_change']):.2f}\n"
                content += "\n"
            
            # Overall confidence change
            avg_prev_conf = sum(s.confidence_score for s in prev_doc.sections) / max(len(prev_doc.sections), 1)
            avg_curr_conf = sum(s.confidence_score for s in doc.sections) / max(len(doc.sections), 1)
            conf_change = avg_curr_conf - avg_prev_conf
            
            content += f"**Overall Confidence**: {avg_curr_conf:.2f} "
            if conf_change > 0:
                content += f"(Increased by {conf_change:.2f})\n\n"
            else:
                content += f"(Decreased by {abs(conf_change):.2f})\n\n"
        
        # Add section summaries
        content += "### Section Summaries\n\n"
        for section in doc.sections:
            content += f"- **{section.title}** (Confidence: {section.confidence_score:.2f})\n"
            if section.citations:
                content += f"  - Citations: {len(section.citations)}\n"
            if section.subsections:
                content += f"  - Subsections: {len(section.subsections)}\n"
        
        content += "\n---\n\n"
    
    return content 