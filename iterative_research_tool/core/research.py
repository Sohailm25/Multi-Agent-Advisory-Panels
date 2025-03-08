"""Main implementation of the Iterative Research Tool."""

import os
import json
import time
import logging
import re
from typing import Dict, List, Optional, Tuple, Any
from pathlib import Path

from iterative_research_tool.core.config import ToolConfig
from iterative_research_tool.core.claude_client import ClaudeClient
from iterative_research_tool.core.perplexity_client import PerplexityClient
from iterative_research_tool.core.prompt_manager import PromptManager
from iterative_research_tool.core.loop_controller import LoopController
from iterative_research_tool.core.models import DocumentSection, ResearchDocument
from iterative_research_tool.core.document_parser import DocumentParser
from iterative_research_tool.core.markdown_utils import (
    markdown_to_document, create_version_history_document
)
from iterative_research_tool.core.logging_utils import ProgressLogger

logger = logging.getLogger(__name__)


class CostLimitExceededError(Exception):
    """Exception raised when the cost limit would be exceeded."""
    pass


class IterativeResearchTool:
    """Main tool that orchestrates the research document generation process."""
    
    def __init__(
        self, 
        config: ToolConfig,
        progress_logger: Optional[ProgressLogger] = None
    ):
        """Initialize the research tool.
        
        Args:
            config: Tool configuration
            progress_logger: Logger for tracking progress
        """
        self.config = config
        self.perplexity_client = PerplexityClient(
            api_key=config.api.perplexity_api_key,
            model=config.research.perplexity_model,
            temperature=config.research.temperature
        )
        self.claude_client = ClaudeClient(
            api_key=config.api.claude_api_key,
            model=config.research.claude_model,
            temperature=config.research.temperature
        )
        
        # Set up prompt manager
        self.prompt_manager = PromptManager(config.prompts.prompts_directory)
        
        # Set up loop controller
        self.loop_controller = LoopController(
            config=config,
            claude_client=self.claude_client,
            prompt_manager=self.prompt_manager
        )
        
        # Set up progress logger
        self.progress_logger = progress_logger or ProgressLogger(
            logger=logger,
            total_steps=config.research.max_iterations * 3 + 2  # Init + iterations*3 steps + final
        )
        
        # Tracking costs
        self.total_cost = 0.0
        self.perplexity_calls = 0
        self.claude_calls = 0
        
        # Store document history
        self.document_history = []
        
        # Store original query
        self.original_query = ""
    
    def initialize_document(self, markdown_content: str) -> ResearchDocument:
        """Initialize document from markdown content.
        
        Args:
            markdown_content: Markdown content to parse
            
        Returns:
            ResearchDocument instance
        """
        self.progress_logger.start("Initializing document from markdown content")
        
        # Parse markdown content into document structure
        document = markdown_to_document(markdown_content)
        
        # Extract and store the original query from the document title if not already set
        if document.title and document.title != "Untitled Document":
            if not hasattr(self, 'original_query') or not self.original_query:
                self.original_query = document.title
                logger.debug(f"Extracted original query from document title: '{document.title}'")
        
        # Add to history
        self.document_history.append(document)
        
        self.progress_logger.step("Document initialized")
        
        return document
    
    def _check_cost_limit(self, estimated_cost: float) -> None:
        """Check if the estimated cost would exceed the limit.
        
        Args:
            estimated_cost: Estimated cost of the operation
            
        Raises:
            CostLimitExceededError: If the cost limit would be exceeded
        """
        potential_total = self.total_cost + estimated_cost
        
        if potential_total > self.config.cost_limits.max_cost_per_call:
            raise CostLimitExceededError(
                f"Operation would exceed cost limit (${potential_total:.2f} > ${self.config.cost_limits.max_cost_per_call:.2f})"
            )
    
    def formulate_initial_query(self, input_text: str) -> str:
        """Formulate optimized initial query from user input.
        
        Args:
            input_text: User input text
            
        Returns:
            Formatted query
        """
        # Log the full input text for debugging
        logger.debug(f"Full input text for query formulation: '{input_text}'")
        logger.info(f"Formulating initial query from input: {input_text[:100]}...")
        
        # Always store the original query
        if not hasattr(self, 'original_query') or not self.original_query:
            self.original_query = input_text
            logger.debug(f"Stored original query: '{self.original_query}'")
        
        # If not using custom prompts, return the raw input
        if not self.config.prompts.use_custom_prompts:
            logger.info("Using raw input as query (custom prompts disabled)")
            return input_text
        
        try:
            # Format the CLI input prompt
            logger.debug("Formatting CLI input prompt")
            cli_prompt = self.prompt_manager.format_prompt(
                "cli_input_prompt",
                user_cli_input=input_text
            )
            
            # Call Claude to generate optimized queries
            logger.debug("Calling Claude to generate optimized queries")
            result = self.claude_client.generate(
                system_prompt="",  # System prompt is included in the prompt template
                user_prompt=cli_prompt,
                max_tokens=2000
            )
            
            # Update metrics
            self.claude_calls += 1
            
            # Log the generated query for debugging
            generated_query = result["text"]
            if not generated_query or len(generated_query.strip()) < 10:
                logger.warning("Claude returned an empty or very short query response")
                logger.info("Falling back to raw input as query")
                return input_text
                
            logger.debug(f"Generated optimized query: {generated_query[:200]}...")
            
            # Return the optimized queries
            return generated_query
        except Exception as e:
            logger.error(f"Error formulating initial query: {e}")
            logger.info("Falling back to raw input as query")
            return input_text
    
    def research_with_perplexity(
        self, 
        document: ResearchDocument, 
        query: str
    ) -> ResearchDocument:
        """Enhance document with factual information from Perplexity API.
        
        Args:
            document: Document to enhance
            query: Research query
            
        Returns:
            Enhanced document
        """
        self.progress_logger.step("Starting research phase with Perplexity")
        
        # Create a deep copy of the document
        enhanced_doc = document.copy(deep=True)
        enhanced_doc.version += 1
        
        # Extract query text from JSON if needed
        actual_query = query
        if query.strip().startswith('```json') or query.strip().startswith('[{') or query.strip().startswith('{"'):
            logger.info("Detected JSON format query, extracting query text")
            try:
                # Try to parse as JSON
                if '```json' in query:
                    # Extract JSON from markdown code block
                    json_str = re.search(r'```json\s*([\s\S]*?)\s*```', query)
                    if json_str:
                        json_data = json.loads(json_str.group(1))
                    else:
                        raise ValueError("Could not extract JSON from code block")
                else:
                    # Parse raw JSON
                    json_data = json.loads(query)
                
                # Extract query text from different possible JSON structures
                if isinstance(json_data, list) and len(json_data) > 0 and 'query_text' in json_data[0]:
                    # Format: [{"query_text": "...", ...}, ...]
                    actual_query = json_data[0]['query_text']
                elif isinstance(json_data, dict) and 'queries' in json_data and len(json_data['queries']) > 0:
                    # Format: {"queries": [{"query_text": "...", ...}, ...]}
                    actual_query = json_data['queries'][0]['query_text']
                elif isinstance(json_data, dict) and 'query_text' in json_data:
                    # Format: {"query_text": "...", ...}
                    actual_query = json_data['query_text']
                else:
                    logger.warning("Could not extract query text from JSON, using raw query")
            except Exception as e:
                logger.error(f"Error parsing JSON query: {e}")
                logger.info("Using raw query text")
        
        # Use the query directly for research
        logger.info(f"Researching query: {actual_query[:100]}...")
        
        try:
            # Estimate cost
            estimated_cost = self.perplexity_client.estimate_cost(actual_query)
            self._check_cost_limit(estimated_cost)
            
            # Call Perplexity API
            research_data = self.perplexity_client.deep_research(actual_query)
            
            # Update costs
            self.perplexity_calls += 1
            if 'usage' in research_data and 'total_tokens' in research_data['usage']:
                usage = research_data['usage']
                token_cost = (usage['total_tokens'] / 1000) * self.config.cost_limits.perplexity_cost_per_1k_tokens
                search_cost = self.config.cost_limits.perplexity_cost_per_search
                actual_cost = token_cost + search_cost
                self.total_cost += actual_cost
                logger.debug(f"Perplexity call cost: ${actual_cost:.4f} (token: ${token_cost:.4f}, search: ${search_cost:.4f}), Total so far: ${self.total_cost:.4f}")
            else:
                # If usage info not available, use the estimate
                self.total_cost += estimated_cost
                logger.debug(f"Estimated Perplexity call cost: ${estimated_cost:.4f}, Total so far: ${self.total_cost:.4f}")
            
            # Extract information
            content = research_data['text']
            citations = research_data['sources']
            
            # If this is a new document, create a section from the research
            if len(enhanced_doc.sections) == 0:
                section = DocumentSection(
                    title=self.original_query,
                    content=content,
                    citations=citations,
                    confidence_score=0.8 if citations else 0.5
                )
                enhanced_doc.sections.append(section)
            else:
                # Update the main content with the research
                enhanced_doc.sections[0].content = content
                enhanced_doc.sections[0].citations.extend(citations)
                
                # Calculate confidence score based on citation quality
                if citations:
                    reliability_scores = [c.get('reliability', 0.8) for c in citations]
                    enhanced_doc.sections[0].confidence_score = sum(reliability_scores) / len(reliability_scores)
                else:
                    enhanced_doc.sections[0].confidence_score = 0.5
            
            logger.info(f"Research complete with {len(citations)} citations")
            logger.info(f"Confidence score: {enhanced_doc.sections[0].confidence_score:.2f}")
            
        except CostLimitExceededError as e:
            logger.warning(f"Skipping Perplexity research: {e}")
        
        # Add to history
        self.document_history.append(enhanced_doc)
        
        self.progress_logger.step("Completed research phase with Perplexity")
        
        return enhanced_doc
    
    def research_with_batch_queries(self, document: ResearchDocument, queries_json: str) -> ResearchDocument:
        """Perform deeper research with batch queries generated from Claude.
        
        Args:
            document: Document to enhance
            queries_json: JSON data with research questions
            
        Returns:
            Enhanced document
        """
        # Parse the research questions from the JSON
        try:
            # Check if the input is valid JSON
            if not queries_json or queries_json.strip() == "{}":
                logger.warning("Empty JSON data for batch queries")
                return document
                
            # Try to extract JSON object if it's embedded in a larger text
            json_pattern = r'\{(?:[^{}]|(?:\{(?:[^{}]|(?:\{[^{}]*\}))*\}))*\}'
            json_match = re.search(json_pattern, queries_json)
            if json_match:
                extracted_json = json_match.group(0)
                try:
                    data = json.loads(extracted_json)
                except json.JSONDecodeError:
                    # If that fails, try the original string
                    data = json.loads(queries_json)
            else:
                data = json.loads(queries_json)
                
            research_questions = data.get("research_questions", [])
            if not research_questions:
                logger.warning("No research questions found in JSON data")
                return document
            
            logger.info(f"Found {len(research_questions)} research questions for deeper research")
            
            # Format the research questions for the prompt
            questions_json = json.dumps({"research_questions": research_questions}, indent=2)
            
            # Use the prompt manager to format a prompt for Claude to create optimized queries
            try:
                query_generation_prompt = self.prompt_manager.format_prompt(
                    "claude_to_perplexity_deeper_prompt",
                    research_questions=questions_json
                )
                
                logger.info("Calling Claude to generate optimized queries from research questions")
                
                # Call Claude to generate optimized queries
                query_generation_result = self.claude_client.generate_content(query_generation_prompt)
                
                # Debug log
                logger.debug(f"Claude's response for query generation: {query_generation_result[:500]}...")
                
                # Extract the JSON array of queries from Claude's response
                optimized_queries = self._extract_queries_from_json(query_generation_result)
                
                if not optimized_queries:
                    logger.warning("Failed to extract optimized queries, falling back to direct questions")
                    # Use the research questions directly as queries
                    optimized_queries = [{"query_text": q["question"], "depth": "comprehensive"} 
                                         for q in research_questions]
            except Exception as e:
                logger.error(f"Error generating optimized queries: {e}")
                # Fallback: use research questions directly
                optimized_queries = [{"query_text": q["question"], "depth": "comprehensive"} 
                                    for q in research_questions]
            
            logger.info(f"Starting batch research with {len(optimized_queries)} optimized queries")
            
            # Create a deep copy of the document to enhance
            enhanced_doc = document.copy(deep=True)
            enhanced_doc.version += 1
            
            # Keep track of citations to avoid duplicates
            existing_citations = {}
            for section in enhanced_doc.sections:
                for citation in section.citations:
                    source = citation.get('source', '')
                    if source:
                        existing_citations[source] = citation
            
            # Keep track of the total cost for this batch of queries
            batch_cost = 0
            
            # Run each query and enhance the document
            for i, query in enumerate(optimized_queries):
                query_text = query.get("query_text", "")
                if not query_text:
                    continue
                    
                logger.info(f"Processing batch query {i+1}/{len(optimized_queries)}: {query_text[:100]}...")
                
                # Estimate cost
                estimated_cost = self.perplexity_client.estimate_cost(query_text)
                self._check_cost_limit(estimated_cost)
                
                # Run the query - handle REAL URLs in the response
                try:
                    result = self.perplexity_client.deep_research(query_text)
                    
                    # Extract useful content from the result
                    text = result.get("text", "")
                    sources = result.get("sources", [])
                    usage = result.get("usage", {})
                    
                    # Extract citations and add them to the document
                    citations = []
                    for source in sources:
                        if isinstance(source, str):
                            if source not in existing_citations:
                                existing_citations[source] = {
                                    'source': source,
                                    'reliability': 0.8
                                }
                            citations.append(existing_citations[source])
                        elif isinstance(source, dict) and 'url' in source:
                            url = source['url']
                            if url not in existing_citations:
                                existing_citations[url] = {
                                    'source': url,
                                    'reliability': source.get('reliability', 0.8)
                                }
                            citations.append(existing_citations[url])
                    
                    # Calculate cost
                    token_count = usage.get("total_tokens", 0)
                    query_cost = self.perplexity_client.estimate_cost_from_tokens(token_count)
                    batch_cost += query_cost
                    
                    # Update main section content
                    if enhanced_doc.sections:
                        main_section = enhanced_doc.sections[0]
                        
                        # Add query insight as a subsection
                        subsection_title = f"Insights on {query_text[:50]}..." if len(query_text) > 50 else f"Insights on {query_text}"
                        
                        # Clean up the text
                        clean_text = text.replace("```", "").strip()
                        
                        # Create a subsection with the query insights
                        subsection = DocumentSection(
                            title=subsection_title,
                            content=clean_text,
                            citations=citations,
                            confidence_score=0.8 if citations else 0.5
                        )
                        
                        main_section.subsections.append(subsection)
                    
                    logger.info(f"Added insights from query {i+1} with {len(citations)} citations")
                    
                except Exception as e:
                    logger.error(f"Error processing query {i+1}: {e}")
            
            # Update the cost
            self.total_cost += batch_cost
            logger.debug(f"Batch queries total cost: ${batch_cost:.4f}, Overall total: ${self.total_cost:.4f}")
            
            # Update the confidence score of the main section
            if enhanced_doc.sections:
                main_section = enhanced_doc.sections[0]
                subsection_scores = [s.confidence_score for s in main_section.subsections]
                if subsection_scores:
                    main_section.confidence_score = sum(subsection_scores) / len(subsection_scores)
                
            return enhanced_doc
            
        except json.JSONDecodeError as e:
            logger.error(f"Error parsing research questions JSON: {e}")
            return document
        except Exception as e:
            logger.error(f"Error in batch research: {e}")
            return document
            
    def _extract_queries_from_json(self, text: str) -> List[Dict[str, str]]:
        """Extract queries from JSON in text.
        
        Args:
            text: Text containing JSON with queries
            
        Returns:
            List of query objects
        """
        # Look for JSON in triple backticks
        json_pattern = r'```(?:json)?\s*(.*?)\s*```'
        matches = re.findall(json_pattern, text, re.DOTALL)
        
        if matches:
            for match in matches:
                try:
                    data = json.loads(match)
                    if isinstance(data, list):
                        return data
                except json.JSONDecodeError:
                    continue
        
        # Try to extract JSON array directly
        array_pattern = r'\[\s*\{.*?\}\s*(?:,\s*\{.*?\}\s*)*\]'
        match = re.search(array_pattern, text, re.DOTALL)
        if match:
            try:
                return json.loads(match.group(0))
            except json.JSONDecodeError:
                pass
        
        logger.warning("Could not extract queries from text")
        return []
    
    def _extract_query_from_json(self, query_text: str) -> str:
        """Extract query text from JSON if the input appears to be JSON.
        
        Args:
            query_text: Raw query text, may be JSON
            
        Returns:
            Extracted query text or original text if not JSON
        """
        if not query_text:
            return ""
            
        # Check if it starts with a JSON indicator
        if '```json' in query_text or query_text.strip().startswith('{') or query_text.strip().startswith('['):
            try:
                # Try to extract JSON from markdown code block
                if '```json' in query_text:
                    json_pattern = r'```json\s*(.*?)\s*```'
                    match = re.search(json_pattern, query_text, re.DOTALL)
                    if match:
                        json_str = match.group(1)
                        data = json.loads(json_str)
                    else:
                        data = json.loads(query_text)
                else:
                    # Try to parse as raw JSON
                    data = json.loads(query_text)
                
                # Extract query from different possible formats
                if isinstance(data, dict):
                    # Check common keys that might contain the query
                    for key in ['query', 'query_text', 'text', 'question', 'prompt']:
                        if key in data:
                            return data[key]
                    
                    # Check for nested structures
                    if 'research' in data and isinstance(data['research'], dict):
                        for key in ['query', 'query_text', 'text', 'question', 'prompt']:
                            if key in data['research']:
                                return data['research'][key]
                                
                elif isinstance(data, list) and len(data) > 0:
                    # If it's an array, take the first item
                    if isinstance(data[0], dict):
                        for key in ['query', 'query_text', 'text', 'question', 'prompt']:
                            if key in data[0]:
                                return data[0][key]
                    elif isinstance(data[0], str):
                        return data[0]
                
                # If we couldn't find a query, log warning and return original
                logger.warning("Could not extract query from JSON structure")
                
            except json.JSONDecodeError as e:
                logger.warning(f"Error parsing JSON in query: {e}")
                
        # Return the original query if not JSON or if extraction failed
        return query_text
    
    def enhance_with_claude(self, document: ResearchDocument) -> Tuple[ResearchDocument, str]:
        """Enhance document with Claude's insights and analysis.
        
        Args:
            document: Document to enhance
            
        Returns:
            Tuple of (enhanced document, research questions JSON)
        """
        self.progress_logger.step("Starting enhancement phase with Claude")
        
        # Create a deep copy of the document to enhance
        enhanced_doc = document.copy(deep=True)
        enhanced_doc.version += 1
        
        # Extract document content
        document_content = enhanced_doc.to_markdown()
        
        # Debug: Log the document content being passed to Claude
        logger.debug(f"Document content being passed to Claude (first 500 chars):\n{document_content[:500]}...")
        logger.debug(f"Document content length: {len(document_content)} characters")
        logger.debug(f"Document sections count: {len(enhanced_doc.sections)}")
        for i, section in enumerate(enhanced_doc.sections):
            logger.debug(f"Section {i+1} title: {section.title}")
            logger.debug(f"Section {i+1} content preview: {section.content[:100]}...")
        
        try:
            # Get the prompt template
            prompt_template = self.prompt_manager.get_prompt("perplexity_to_claude_prompt")
            
            # Check if the template contains expected markers
            if "SYSTEM PROMPT:" in prompt_template and "DOCUMENT CONTENT:" in prompt_template:
                # Split the template to get the system prompt part
                system_part = prompt_template.split("SYSTEM PROMPT:", 1)[1]
                system_prompt = system_part.split("DOCUMENT CONTENT:", 1)[0].strip()
                
                # Create a clean user message with document content
                user_message = f"""Research document to enhance:

{document_content}

Please analyze and enhance this document following your instructions. Remember to stay strictly on topic and focus solely on the subject matter presented in the document."""
                
                logger.debug(f"Extracted system prompt length: {len(system_prompt)} characters")
                logger.debug(f"System prompt preview: {system_prompt[:200]}...")
                logger.debug(f"User message preview: {user_message[:200]}...")
                
                # Direct Claude API call with proper separation
                result = self.claude_client.generate(
                    system_prompt=system_prompt,
                    user_prompt=user_message,
                    max_tokens=4000,
                    temperature=0.2
                )
                
                # Extract the text from the result dictionary
                claude_response = result.get("text", "")
            else:
                # Fallback to the old method if prompt template doesn't have expected structure
                logger.warning("Prompt template doesn't have expected structure, using old method")
                
                # Format the prompt with the document content explicitly
                formatted_prompt = prompt_template.replace("{document_content}", document_content)
                
                # Split into system prompt and user content if possible
                if "SYSTEM PROMPT:" in formatted_prompt:
                    parts = formatted_prompt.split("SYSTEM PROMPT:", 1)
                    if len(parts) > 1:
                        system_prompt_part = parts[1].strip()
                        
                        # Find the first line after SYSTEM PROMPT: that looks like a section header
                        lines = system_prompt_part.split("\n")
                        system_prompt_end = 0
                        for i, line in enumerate(lines):
                            if line.startswith("PROCESS ") or line.startswith("1. ") or line.strip() == "":
                                system_prompt_end = i
                                break
                        
                        system_prompt = "\n".join(lines[:system_prompt_end]).strip()
                        user_content = "\n".join(lines[system_prompt_end:]).strip()
                        
                        logger.debug(f"Extracted system prompt (first 200 chars): {system_prompt[:200]}...")
                        logger.debug(f"Extracted user content (first 200 chars): {user_content[:200]}...")
                        
                        # Call Claude with separated system and user content
                        result = self.claude_client.generate(
                            system_prompt=system_prompt,
                            user_prompt=user_content + f"\n\nDOCUMENT CONTENT:\n{document_content}",
                            max_tokens=4000,
                            temperature=0.2
                        )
                        claude_response = result.get("text", "")
                    else:
                        # Fall back to generate_content
                        claude_response = self.claude_client.generate_content(formatted_prompt)
                else:
                    # Fall back to generate_content
                    claude_response = self.claude_client.generate_content(formatted_prompt)
            
            # Debug: Log Claude's response 
            logger.debug(f"Claude response preview (first 300 chars):\n{claude_response[:300]}...")
            logger.debug(f"Claude response focuses on topic: {'quantum computing' not in claude_response.lower()}")
            
            # Extract research questions JSON
            research_questions_json = self.loop_controller.extract_research_questions(claude_response)
            
            # Parse the result and update the document
            # Use the document parser to break down Claude's response into sections
            enhanced_sections = DocumentParser.parse_markdown(claude_response)
            
            # Replace sections in the document
            enhanced_doc.sections = enhanced_sections
            
            # Add to history
            self.document_history.append(enhanced_doc)
            
            self.claude_calls += 1
            
            # Update the cost
            if hasattr(self.claude_client, 'last_call_cost') and self.claude_client.last_call_cost:
                self.total_cost += self.claude_client.last_call_cost
                logger.debug(f"Claude call cost: ${self.claude_client.last_call_cost:.4f}, Total so far: ${self.total_cost:.4f}")
            
        except Exception as e:
            logger.error(f"Error enhancing document with Claude: {e}")
            # In case of error, return the original document unmodified
            return document, "{}"
        
        self.progress_logger.step("Completed enhancement phase with Claude")
        
        return enhanced_doc, research_questions_json
    
    def verify_content(self, document: ResearchDocument) -> Tuple[ResearchDocument, List[str]]:
        """Verify document content and identify areas needing more research.
        
        Args:
            document: Document to verify
            
        Returns:
            Tuple of (verified document, list of issues)
        """
        verified_doc = document.copy(deep=True)
        issues = []
        
        for i, section in enumerate(verified_doc.sections):
            # Check confidence score
            if section.confidence_score < self.config.research.confidence_threshold:
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
    
    def run_research_iteration(self, document: ResearchDocument, iteration: int) -> Tuple[ResearchDocument, List[str]]:
        """Run a single research iteration on the document.
        
        Args:
            document: Document to enhance
            iteration: Current iteration number
            
        Returns:
            Tuple of (enhanced document, issues)
        """
        # Step 1: Formulate query based on iteration
        if iteration == 1:
            # First iteration - use the original query directly for the first iteration
            if hasattr(self, 'original_query') and self.original_query:
                logger.info(f"Using original query for iteration 1: {self.original_query[:100]}...")
                
                # For the first iteration, use the original query directly instead of formatting it
                # This avoids potential issues with the query formulation process
                query = self.original_query
                logger.info(f"Using direct query: {query}")
            else:
                # Try to extract query from document title if it exists and is not the default
                if document.title and document.title != "Untitled Document":
                    logger.info(f"Using document title for iteration 1: {document.title}")
                    # Store the document title as the original query
                    self.original_query = document.title
                    query = document.title
                    logger.info(f"Using direct query from title: {query}")
                else:
                    # Fallback to a generic query
                    logger.warning("No original query or valid document title found for iteration 1")
                    query = "Please provide a general overview of this topic."
        else:
            # Use the document content as the context for research
            logger.info(f"Using document content as query for iteration {iteration}")
            query = document.to_markdown()
        
        # Step 2: Enhance with factual information from Perplexity
        logger.info(f"Starting Perplexity research for iteration {iteration}")
        researched_doc = self.research_with_perplexity(document, query)
        
        # Step 3: Enhance structure and content with Claude, get research questions
        logger.info(f"Starting Claude enhancement for iteration {iteration}")
        enhanced_doc, research_questions_json = self.enhance_with_claude(researched_doc)
        
        # Step 4: If using the new workflow and we have research questions, do deeper research
        if self.config.prompts.use_custom_prompts and research_questions_json and self.config.research.batch_queries:
            logger.info("Preparing for deeper research with batch queries")
            try:
                # Format the research questions for the next phase
                user_prompt = self.prompt_manager.format_prompt(
                    "claude_to_perplexity_deeper_prompt",
                    research_questions=research_questions_json
                )
                
                # Call Claude to generate optimized queries
                logger.info("Calling Claude to generate optimized queries from research questions")
                deeper_result = self.claude_client.generate(
                    system_prompt="",  # System prompt is included in the template
                    user_prompt=user_prompt,
                    max_tokens=4000
                )
                
                # Log Claude's response for debugging
                response_preview = deeper_result['text'][:500].replace('\n', ' ') + "..." if len(deeper_result['text']) > 500 else deeper_result['text']
                logger.debug(f"Claude's response for query generation: {response_preview}")
                
                # Update metrics
                self.claude_calls += 1
                usage = deeper_result['usage']
                input_cost = (usage['prompt_tokens'] / 1000) * self.config.cost_limits.claude_cost_per_1k_input_tokens
                output_cost = (usage['completion_tokens'] / 1000) * self.config.cost_limits.claude_cost_per_1k_output_tokens
                actual_cost = input_cost + output_cost
                self.total_cost += actual_cost
                
                # Extract the optimized queries JSON
                optimized_queries = deeper_result['text']
                
                # Perform deeper research with batch queries
                logger.info("Starting batch research with optimized queries")
                deeper_researched_doc = self.research_with_batch_queries(enhanced_doc, optimized_queries)
                
                # Final enhancement with Claude
                logger.info("Performing final enhancement with Claude")
                final_doc, _ = self.enhance_with_claude(deeper_researched_doc)
            except Exception as e:
                logger.error(f"Error during deeper research workflow: {e}")
                logger.info("Falling back to document without deeper research")
                final_doc = enhanced_doc
        else:
            if not self.config.prompts.use_custom_prompts:
                logger.info("Skipping deeper research (custom prompts disabled)")
            elif not research_questions_json:
                logger.info("Skipping deeper research (no research questions found)")
            elif not self.config.research.batch_queries:
                logger.info("Skipping deeper research (batch queries disabled)")
            final_doc = enhanced_doc
        
        # Step 5: Verify content and identify issues
        logger.info("Verifying final document content")
        verified_doc, issues = self.verify_content(final_doc)
        
        return verified_doc, issues
    
    def run_full_research_cycle(self, markdown_content: str) -> Tuple[ResearchDocument, str]:
        """Run the full research cycle until completion or max iterations.
        
        Args:
            markdown_content: Markdown content to enhance
            
        Returns:
            Tuple of (final document, version history markdown)
        """
        # Initialize document
        current_doc = self.initialize_document(markdown_content)
        
        # Calculate the total steps for the progress logger
        total_steps = 1 + (self.config.research.max_iterations * 3) + 1  # init + (iterations * phases) + final
        self.progress_logger = ProgressLogger(logger=logger, total_steps=total_steps)
        self.progress_logger.start("Starting research cycle")
        
        iteration = 0
        previous_doc = None
        
        while iteration < self.config.research.max_iterations:
            iteration += 1
            self.progress_logger.step(f"Starting iteration {iteration}/{self.config.research.max_iterations}")
            
            # Run iteration
            try:
                current_doc, issues = self.run_research_iteration(current_doc, iteration)
                
                # Use loop controller to decide whether to continue if enabled
                if self.config.research.use_controller_termination and iteration > 1:
                    assessment = self.loop_controller.assess_progress(
                        current_document=current_doc,
                        previous_document=previous_doc,
                        iteration_number=iteration,
                        original_query=self.original_query
                    )
                    
                    if assessment["recommendation"] == "terminate":
                        logger.info(f"Loop controller recommends termination: {assessment['rationale']}")
                        logger.info(f"Confidence: {assessment['confidence']}%")
                        break
                
                # Check if we've reached sufficient quality
                if not issues and all(section.confidence_score >= self.config.research.confidence_threshold 
                                    for section in current_doc.sections):
                    logger.info(f"Research complete after {iteration} iterations")
                    break
                
                logger.info(f"Iteration {iteration} found {len(issues)} issues to address")
                if self.config.research.verbose_output and issues:
                    for issue in issues:
                        logger.info(f"  - {issue}")
                
                # Store document for next iteration comparison
                previous_doc = current_doc
                
            except CostLimitExceededError as e:
                logger.warning(f"Stopping research cycle due to cost limit: {e}")
                break
            
        # Create version history document if requested
        version_history = ""
        if self.config.research.track_version_history:
            version_history = create_version_history_document(self.document_history)
        
        # Log final statistics
        self.progress_logger.complete(f"Research completed in {iteration} iterations")
        logger.info(f"Final document: {len(current_doc.sections)} sections")
        logger.info(f"API calls: {self.perplexity_calls} Perplexity, {self.claude_calls} Claude")
        logger.info(f"Total cost: ${self.total_cost:.2f}")
        
        avg_confidence = sum(s.confidence_score for s in current_doc.sections) / max(len(current_doc.sections), 1)
        logger.info(f"Final average confidence score: {avg_confidence:.2f}")
        
        return current_doc, version_history 