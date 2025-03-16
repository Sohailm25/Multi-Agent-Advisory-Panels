# Iterative Research Document Generator: Perplexity + Claude

I'll outline a design for a tool that creates exhaustive, textbook-quality research documents through iterative AI enhancement. This approach can minimize hallucinations while progressively improving depth and quality.

## Architecture Overview

```
[Base Document] → [Perplexity Research] → [Claude Enhancement] → [Document V2] → [Repeat...]
```

### Core Components

1. **Document Manager**
   - Maintains the evolving document state
   - Tracks revision history
   - Handles document structure and formatting

2. **Research Module** (Perplexity API)
   - Retrieves factual information from reliable sources
   - Grounds document claims in verifiable data
   - Adds citations and references

3. **Enhancement Module** (Claude API)
   - Restructures content for logical flow
   - Expands sections that need more detail
   - Improves explanations and clarity
   - Identifies knowledge gaps

4. **Verification System**
   - Cross-references claims against multiple sources
   - Flags uncertain statements for additional research
   - Maintains confidence scores for document sections

## Implementation Approach

Let me create a basic implementation outline using Python:

## Hallucination Prevention Mechanisms

To specifically address the hallucination problem, the tool implements several safeguards:

1. **Source-Grounded Research**
   - Perplexity API provides search-grounded information
   - Every fact is tied to a specific source
   - Citations are tracked throughout the document

2. **Confidence Scoring**
   - Each section gets a confidence score based on citation quality
   - Sections with low confidence are flagged for additional research
   - Speculative language is detected and marked

3. **Cross-Model Verification**
   - Using two different LLM systems (Perplexity and Claude) creates natural verification
   - Each model's strengths complement the other's limitations

4. **Iterative Refinement**
   - Multiple passes allow for progressive fact-checking
   - Each iteration can address issues from previous rounds
   - Version history tracks changes and can identify potential fabrications

5. **Explicit Uncertainty Marking**
   - Statements without citations are explicitly marked
   - The system differentiates between factual statements and inferences

## Enhancement Strategies

The Claude enhancement module can be configured with specific instructions to:

1. **Identify knowledge gaps** - "What's missing from this section?"
2. **Request additional research** - "This claim needs verification"
3. **Restructure for clarity** - Organize content logically
4. **Apply domain expertise** - Add insights based on established knowledge

## Usage Example

To use this tool for a comprehensive research project:

1. Start with a basic outline of your research topic
2. Initialize the tool with your API keys
3. Set the maximum number of iterations and confidence threshold
4. Run the research cycle
5. Export the final document in your preferred format

The implementation includes logic for handling the document's evolution through multiple iterations, tracking confidence scores, and maintaining citation information throughout the process.


Iterative Research Document Generator:

import os
import json
import time
from typing import Dict, List, Optional, Tuple
import anthropic
import requests
from pydantic import BaseModel

class DocumentSection(BaseModel):
    """Represents a section in the research document."""
    title: str
    content: str
    confidence_score: float = 0.0
    citations: List[Dict] = []
    subsections: List["DocumentSection"] = []
    
class ResearchDocument(BaseModel):
    """Represents the full research document."""
    title: str
    version: int = 1
    sections: List[DocumentSection] = []
    metadata: Dict = {}
    
class IterativeResearchTool:
    """Main tool that orchestrates the research document generation process."""
    
    def __init__(
        self, 
        perplexity_api_key: str, 
        claude_api_key: str,
        max_iterations: int = 5,
        confidence_threshold: float = 0.8
    ):
        self.perplexity_api_key = perplexity_api_key
        self.claude_client = anthropic.Anthropic(api_key=claude_api_key)
        self.max_iterations = max_iterations
        self.confidence_threshold = confidence_threshold
        self.document_history = []
        
    def initialize_document(self, title: str, initial_outline: Optional[str] = None) -> ResearchDocument:
        """Create the initial document based on a title and optional outline."""
        doc = ResearchDocument(title=title)
        
        if initial_outline:
            # Use Claude to structure the initial outline into proper sections
            response = self.claude_client.messages.create(
                model="claude-3-opus-20240229",
                max_tokens=4000,
                temperature=0.2,
                system="You are a research document organizer. Convert the provided outline into a structured document with main sections and subsections.",
                messages=[
                    {"role": "user", "content": f"Title: {title}\n\nOutline:\n{initial_outline}\n\nConvert this into a structured document format with properly organized sections."}
                ]
            )
            
            # Parse Claude's response to create initial document structure
            structured_outline = response.content[0].text
            doc = self._parse_structured_outline(title, structured_outline)
        
        self.document_history.append(doc)
        return doc
    
    def _parse_structured_outline(self, title: str, structured_outline: str) -> ResearchDocument:
        """Parse a structured outline into a ResearchDocument object."""
        # Implementation to convert Claude's text response into a structured ResearchDocument
        # This would parse the text to identify sections and subsections
        
        # Simplified implementation for demonstration
        doc = ResearchDocument(title=title)
        sections = []
        
        # Simple parsing logic - in a real implementation this would be more robust
        current_lines = []
        current_title = ""
        
        for line in structured_outline.split('\n'):
            line = line.strip()
            if not line:
                continue
                
            if line.startswith('# '):
                # Main section
                if current_title and current_lines:
                    sections.append(DocumentSection(
                        title=current_title,
                        content='\n'.join(current_lines)
                    ))
                current_title = line.replace('# ', '')
                current_lines = []
            else:
                current_lines.append(line)
        
        # Add the last section
        if current_title and current_lines:
            sections.append(DocumentSection(
                title=current_title,
                content='\n'.join(current_lines)
            ))
        
        doc.sections = sections
        return doc
    
    def research_with_perplexity(self, document: ResearchDocument) -> ResearchDocument:
        """Enhance document with factual information from Perplexity API."""
        enhanced_doc = document.copy(deep=True)
        enhanced_doc.version += 1
        
        for i, section in enumerate(enhanced_doc.sections):
            # Generate research query based on section title and content
            query = f"Provide comprehensive, factual information about: {section.title}"
            
            # Call Perplexity API for deep research
            research_data = self._call_perplexity_api(query)
            
            # Extract facts and citations from research data
            facts, citations = self._extract_facts_and_citations(research_data)
            
            # Incorporate research into section content
            enhanced_content = self._merge_content_with_research(section.content, facts)
            
            # Update the section
            enhanced_doc.sections[i].content = enhanced_content
            enhanced_doc.sections[i].citations.extend(citations)
            
            # Calculate confidence score based on citation quality
            enhanced_doc.sections[i].confidence_score = self._calculate_confidence_score(citations)
        
        self.document_history.append(enhanced_doc)
        return enhanced_doc
    
    def _call_perplexity_api(self, query: str) -> Dict:
        """Call Perplexity API for deep research."""
        # This would be replaced with actual Perplexity API implementation
        headers = {
            "Authorization": f"Bearer {self.perplexity_api_key}",
            "Content-Type": "application/json"
        }
        
        data = {
            "query": query,
            "mode": "deep_research"  # Assuming Perplexity has such a mode
        }
        
        # Placeholder for API call
        # response = requests.post("https://api.perplexity.ai/research", headers=headers, json=data)
        # return response.json()
        
        # Mock response for demonstration
        return {
            "results": [
                {"content": f"Research data for {query}", "source": "example.com", "reliability": 0.9}
            ]
        }
    
    def _extract_facts_and_citations(self, research_data: Dict) -> Tuple[List[str], List[Dict]]:
        """Extract facts and citations from research data."""
        # This would parse the Perplexity API response to extract useful facts and their sources
        
        # Mock implementation
        facts = [result["content"] for result in research_data.get("results", [])]
        citations = [
            {"source": result["source"], "reliability": result.get("reliability", 0.5)}
            for result in research_data.get("results", [])
        ]
        
        return facts, citations
    
    def _merge_content_with_research(self, existing_content: str, facts: List[str]) -> str:
        """Merge existing content with new research facts."""
        # Simple concatenation for demonstration
        # In a real implementation, this might use an LLM to intelligently merge content
        combined_content = existing_content
        
        if facts:
            combined_content += "\n\nAdditional Research:\n"
            for fact in facts:
                combined_content += f"- {fact}\n"
        
        return combined_content
    
    def _calculate_confidence_score(self, citations: List[Dict]) -> float:
        """Calculate confidence score based on citation quality and quantity."""
        if not citations:
            return 0.0
        
        # Simple averaging of reliability scores
        reliability_scores = [citation.get("reliability", 0.5) for citation in citations]
        return sum(reliability_scores) / len(reliability_scores)
    
    def enhance_with_claude(self, document: ResearchDocument) -> ResearchDocument:
        """Use Claude to enhance, restructure and expand the document."""
        enhanced_doc = document.copy(deep=True)
        enhanced_doc.version += 1
        
        # Convert document to text format for Claude
        doc_text = self._document_to_text(document)
        
        # Create system prompt for Claude
        system_prompt = """
        You are a research document enhancer. Your task is to:
        1. Improve the structure and organization of the document
        2. Expand sections that need more detail or explanation
        3. Identify and fill knowledge gaps
        4. Ensure logical flow between sections
        5. Improve clarity of explanations
        6. Add practical applications and examples
        7. Maintain academic rigor and avoid speculation
        
        For any statement without citations or with low confidence, mark it for additional research.
        """
        
        # Call Claude API to enhance document
        response = self.claude_client.messages.create(
            model="claude-3-opus-20240229",
            max_tokens=100000,
            temperature=0.2,
            system=system_prompt,
            messages=[
                {
                    "role": "user", 
                    "content": f"Enhance the following research document:\n\n{doc_text}"
                }
            ]
        )
        
        # Parse Claude's enhanced document
        enhanced_text = response.content[0].text
        enhanced_doc = self._text_to_document(document.title, enhanced_text, document.version + 1)
        
        self.document_history.append(enhanced_doc)
        return enhanced_doc
    
    def _document_to_text(self, document: ResearchDocument) -> str:
        """Convert a ResearchDocument to markdown text format."""
        text = f"# {document.title}\n\n"
        
        for section in document.sections:
            text += f"## {section.title}\n\n"
            text += f"{section.content}\n\n"
            
            if section.citations:
                text += "### Citations\n\n"
                for i, citation in enumerate(section.citations):
                    text += f"{i+1}. {citation['source']} (Reliability: {citation['reliability']})\n"
            
            text += f"Confidence Score: {section.confidence_score}\n\n"
            
            for subsection in section.subsections:
                text += f"### {subsection.title}\n\n"
                text += f"{subsection.content}\n\n"
        
        return text
    
    def _text_to_document(self, title: str, text: str, version: int) -> ResearchDocument:
        """Convert markdown text back to a ResearchDocument structure."""
        # This would parse the markdown to recreate the document structure
        # Simplified implementation for demonstration
        
        doc = ResearchDocument(title=title, version=version)
        sections = []
        
        # Simple parsing logic
        lines = text.split('\n')
        current_section = None
        current_subsection = None
        current_content = []
        
        for line in lines:
            if line.startswith('## '):
                # Save previous section if exists
                if current_section:
                    current_section.content = '\n'.join(current_content)
                    sections.append(current_section)
                
                # Start new section
                current_section = DocumentSection(title=line.replace('## ', '').strip(), content="")
                current_content = []
                current_subsection = None
                
            elif line.startswith('### ') and line != '### Citations':
                # Save content to current section before starting subsection
                if current_subsection:
                    current_subsection.content = '\n'.join(current_content)
                    current_section.subsections.append(current_subsection)
                    
                # Start new subsection
                current_subsection = DocumentSection(title=line.replace('### ', '').strip(), content="")
                current_content = []
                
            elif line.startswith('Confidence Score: ') and current_section:
                try:
                    current_section.confidence_score = float(line.replace('Confidence Score: ', '').strip())
                except ValueError:
                    pass
                
            else:
                current_content.append(line)
        
        # Save the last section/subsection
        if current_subsection:
            current_subsection.content = '\n'.join(current_content)
            current_section.subsections.append(current_subsection)
        elif current_section:
            current_section.content = '\n'.join(current_content)
            sections.append(current_section)
        
        doc.sections = sections
        return doc
    
    def verify_content(self, document: ResearchDocument) -> Tuple[ResearchDocument, List[str]]:
        """Verify document content and identify areas needing more research."""
        verified_doc = document.copy(deep=True)
        issues = []
        
        for i, section in enumerate(verified_doc.sections):
            # Check confidence score
            if section.confidence_score < self.confidence_threshold:
                issues.append(f"Section '{section.title}' has low confidence ({section.confidence_score})")
                
            # Look for statements without citations
            if "claim" in section.content.lower() and not section.citations:
                issues.append(f"Section '{section.title}' contains claims without citations")
                
            # Check for speculative language
            speculative_terms = ["might", "could", "possibly", "perhaps", "maybe"]
            for term in speculative_terms:
                if term in section.content.lower():
                    issues.append(f"Section '{section.title}' contains speculative language ('{term}')")
        
        return verified_doc, issues
    
    def run_research_iteration(self, document: ResearchDocument) -> Tuple[ResearchDocument, List[str]]:
        """Run a single research iteration on the document."""
        # Step 1: Enhance with factual information from Perplexity
        researched_doc = self.research_with_perplexity(document)
        
        # Step 2: Enhance structure and content with Claude
        enhanced_doc = self.enhance_with_claude(researched_doc)
        
        # Step 3: Verify content and identify issues
        verified_doc, issues = self.verify_content(enhanced_doc)
        
        return verified_doc, issues
    
    def run_full_research_cycle(self, title: str, initial_outline: str) -> ResearchDocument:
        """Run the full research cycle until completion or max iterations."""
        # Initialize document
        current_doc = self.initialize_document(title, initial_outline)
        
        for iteration in range(self.max_iterations):
            print(f"Running iteration {iteration + 1}/{self.max_iterations}")
            
            # Run iteration
            current_doc, issues = self.run_research_iteration(current_doc)
            
            # Check if we've reached sufficient quality
            if not issues and all(section.confidence_score >= self.confidence_threshold 
                                for section in current_doc.sections):
                print(f"Research complete after {iteration + 1} iterations")
                break
                
            print(f"Found {len(issues)} issues to address in next iteration")
        
        return current_doc
    
    def export_document(self, document: ResearchDocument, format: str = "markdown") -> str:
        """Export the document in the specified format."""
        if format == "markdown":
            return self._document_to_text(document)
        elif format == "json":
            return document.json(indent=2)
        else:
            raise ValueError(f"Unsupported format: {format}")

# Example usage
if __name__ == "__main__":
    # Initialize tool
    tool = IterativeResearchTool(
        perplexity_api_key="your-perplexity-api-key",
        claude_api_key="your-claude-api-key",
        max_iterations=5,
        confidence_threshold=0.8
    )
    
    # Run research cycle
    final_document = tool.run_full_research_cycle(
        title="Advanced Machine Learning Techniques",
        initial_outline="""
        1. Introduction to Machine Learning
        2. Supervised Learning Algorithms
        3. Unsupervised Learning
        4. Deep Learning
        5. Reinforcement Learning
        6. Practical Applications
        7. Future Directions
        """
    )
    
    # Export final document
    markdown_output = tool.export_document(final_document, format="markdown")
    
    # Save to file
    with open("advanced_ml_research.md", "w") as f:
        f.write(markdown_output)
        
    print(f"Final document created with {len(final_document.sections)} sections")
    print(f"Average confidence score: {sum(s.confidence_score for s in final_document.sections)/len(final_document.sections)}")