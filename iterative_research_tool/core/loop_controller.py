"""Controller for the iterative research process."""

import json
import logging
import re
from typing import Dict, List, Any, Optional, Tuple

from iterative_research_tool.core.config import ToolConfig
from iterative_research_tool.core.claude_client import ClaudeClient
from iterative_research_tool.core.prompt_manager import PromptManager
from iterative_research_tool.core.models import ResearchDocument

logger = logging.getLogger(__name__)


class LoopController:
    """Controller for the iterative research process."""
    
    def __init__(
        self, 
        config: ToolConfig,
        claude_client: ClaudeClient,
        prompt_manager: PromptManager
    ):
        """Initialize the loop controller.
        
        Args:
            config: Tool configuration
            claude_client: Claude client for analysis
            prompt_manager: Prompt manager for loading prompts
        """
        self.config = config
        self.claude_client = claude_client
        self.prompt_manager = prompt_manager
        self.previous_metrics = {}
        self.iteration_metrics = []
    
    def assess_progress(
        self,
        current_document: ResearchDocument,
        previous_document: Optional[ResearchDocument],
        iteration_number: int,
        original_query: str
    ) -> Dict[str, Any]:
        """Assess research progress and decide whether to continue or terminate.
        
        Args:
            current_document: Current state of the document
            previous_document: Previous state of the document
            iteration_number: Current iteration number
            original_query: Original research query
            
        Returns:
            Assessment results including recommendation
        """
        # If we're on the first iteration or controller termination is disabled,
        # always continue up to max iterations
        if (iteration_number == 1 or 
            not self.config.research.use_controller_termination or
            not previous_document):
            logger.info("First iteration or controller disabled - continuing research")
            return {
                "iteration_number": iteration_number,
                "progress_metrics": {
                    "new_information_rate": 100.0,
                    "topic_coverage": 30.0,
                    "analysis_depth": 3,
                    "question_resolution_rate": 0.0
                },
                "recommendation": "continue",
                "confidence": 100,
                "rationale": "Initial research phase",
                "focus_areas": ["Continue with broad research"]
            }
        
        # Generate summaries for the documents
        current_summary = self._generate_summary(current_document)
        
        # Format the controller prompt
        controller_prompt = self.prompt_manager.format_prompt(
            "loop_controller_prompt",
            iteration_number=iteration_number,
            original_user_query=original_query,
            current_document_summary=current_summary,
            previous_iteration_metrics=json.dumps(self.previous_metrics, indent=2) if self.previous_metrics else "{}"
        )
        
        # Call Claude to analyze progress
        result = self.claude_client.generate(
            system_prompt="",  # System prompt is included in the controller prompt template
            user_prompt=controller_prompt,
            max_tokens=4000
        )
        
        # Parse JSON from Claude's response
        assessment = self._extract_json_from_response(result["text"])
        
        if not assessment:
            logger.warning("Failed to parse controller assessment, defaulting to continue")
            assessment = {
                "iteration_number": iteration_number,
                "progress_metrics": {
                    "new_information_rate": 50.0,
                    "topic_coverage": 50.0,
                    "analysis_depth": 5,
                    "question_resolution_rate": 50.0
                },
                "recommendation": "continue",
                "confidence": 70,
                "rationale": "Unable to parse metrics, continuing by default",
                "focus_areas": ["Continue with general research"]
            }
        
        # Store metrics for next iteration
        self.previous_metrics = assessment
        self.iteration_metrics.append(assessment)
        
        # Log assessment
        logger.info(f"Iteration {iteration_number} assessment:")
        logger.info(f"  New information rate: {assessment['progress_metrics']['new_information_rate']}%")
        logger.info(f"  Topic coverage: {assessment['progress_metrics']['topic_coverage']}%")
        logger.info(f"  Analysis depth: {assessment['progress_metrics']['analysis_depth']}/10")
        logger.info(f"  Recommendation: {assessment['recommendation']} (confidence: {assessment['confidence']}%)")
        logger.info(f"  Rationale: {assessment['rationale']}")
        
        # If below minimum new information rate for 3 consecutive iterations, recommend termination
        if (len(self.iteration_metrics) >= 3 and
            all(m['progress_metrics']['new_information_rate'] < self.config.research.min_new_info_rate 
                for m in self.iteration_metrics[-3:])):
            logger.info("Three consecutive iterations with minimal new information - recommending termination")
            assessment['recommendation'] = 'terminate'
            assessment['rationale'] = "Three consecutive iterations produced minimal new information"
            assessment['confidence'] = 95
        
        return assessment
    
    def _generate_summary(self, document: ResearchDocument) -> str:
        """Generate a summary of the document suitable for controller analysis.
        
        Args:
            document: Document to summarize
            
        Returns:
            Document summary
        """
        # Create a simplified representation of the document
        summary = f"# {document.title} (Version {document.version})\n\n"
        
        # Add statistics
        section_count = len(document.sections)
        total_content_length = sum(len(s.content) for s in document.sections)
        avg_confidence = sum(s.confidence_score for s in document.sections) / max(section_count, 1)
        citation_count = sum(len(s.citations) for s in document.sections)
        
        summary += f"## Document Statistics\n"
        summary += f"- Section count: {section_count}\n"
        summary += f"- Total content length: {total_content_length} characters\n"
        summary += f"- Average confidence score: {avg_confidence:.2f}\n"
        summary += f"- Total citations: {citation_count}\n\n"
        
        # Add section summaries (titles and brief content snippets)
        summary += f"## Section Summaries\n\n"
        for section in document.sections:
            summary += f"### {section.title}\n"
            
            # Include a snippet of content (first 200 chars)
            content_snippet = section.content[:200] + "..." if len(section.content) > 200 else section.content
            summary += f"{content_snippet}\n\n"
            
            # Add confidence and citation count
            summary += f"Confidence: {section.confidence_score:.2f}, Citations: {len(section.citations)}\n\n"
        
        return summary
    
    def _extract_json_from_response(self, response_text: str) -> Optional[Dict[str, Any]]:
        """Extract JSON object from Claude's response.
        
        Args:
            response_text: Text response from Claude
            
        Returns:
            Extracted JSON object or None if parsing failed
        """
        # Try to find JSON in the response using regex
        json_pattern = r'\{(?:[^{}]|(?:\{(?:[^{}]|(?:\{[^{}]*\}))*\}))*\}'
        match = re.search(json_pattern, response_text)
        
        if match:
            json_str = match.group(0)
            try:
                return json.loads(json_str)
            except json.JSONDecodeError:
                logger.error("Failed to parse JSON from controller response")
                return None
        
        logger.error("No JSON object found in controller response")
        return None
    
    def extract_research_questions(self, claude_response: str) -> List[Dict[str, str]]:
        """Extract research questions from Claude's response.
        
        Args:
            claude_response: Text response from Claude
            
        Returns:
            List of research question objects
        """
        logger.debug(f"Extracting research questions from response (length: {len(claude_response)})")
        
        # Check for empty or invalid response
        if not claude_response or len(claude_response.strip()) < 10:
            logger.warning("Response too short to contain research questions")
            return []
        
        # Log response preview for debugging
        response_preview = claude_response[:500].replace('\n', ' ') + "..." if len(claude_response) > 500 else claude_response
        logger.debug(f"Response preview: {response_preview}")
        
        # Look for JSON in triple backticks
        json_pattern = r'```json\s*(.*?)\s*```'
        matches = re.findall(json_pattern, claude_response, re.DOTALL)
        
        if matches:
            for i, json_str in enumerate(matches):
                logger.debug(f"Found JSON block {i+1}: {json_str[:100]}...")
                try:
                    data = json.loads(json_str)
                    if 'research_questions' in data:
                        logger.info(f"Successfully extracted {len(data['research_questions'])} research questions")
                        return data['research_questions']
                except json.JSONDecodeError as e:
                    logger.error(f"Failed to parse research questions JSON: {e}")
        else:
            logger.warning("No JSON blocks found in triple backticks")
        
        # Try more general JSON extraction
        logger.info("Trying alternative JSON extraction method")
        json_pattern = r'\{\s*"research_questions"\s*:\s*\[(.*?)\]\s*\}'
        match = re.search(json_pattern, claude_response, re.DOTALL)
        if match:
            try:
                # Add the brackets back and try to parse
                json_str = '{' + f'"research_questions": [{match.group(1)}]' + '}'
                data = json.loads(json_str)
                if 'research_questions' in data:
                    logger.info(f"Successfully extracted {len(data['research_questions'])} research questions using alternative method")
                    return data['research_questions']
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse research questions using alternative method: {e}")
        
        # Fallback: try to extract questions without JSON parsing
        logger.info("Using fallback question extraction method")
        questions = []
        question_pattern = r'(?:^|\n)(?:\d+\.\s*)?(?:Question|Research Question):\s*(.*?)(?:\n|$)'
        importance_pattern = r'(?:^|\n)(?:Importance|Significance):\s*(.*?)(?:\n|$)'
        insights_pattern = r'(?:^|\n)(?:Expected Insights|Insights):\s*(.*?)(?:\n|$)'
        
        for match in re.finditer(question_pattern, claude_response, re.MULTILINE):
            question_text = match.group(1).strip()
            # Try to find importance near this question
            importance = "Important for advancing the research"
            importance_match = re.search(importance_pattern, claude_response[match.end():match.end() + 500])
            if importance_match:
                importance = importance_match.group(1).strip()
            
            # Try to find expected insights
            insights = "Better understanding of the topic"
            insights_match = re.search(insights_pattern, claude_response[match.end():match.end() + 500])
            if insights_match:
                insights = insights_match.group(1).strip()
            
            questions.append({
                "question": question_text,
                "importance": importance,
                "expected_insights": insights
            })
        
        if questions:
            logger.info(f"Extracted {len(questions)} questions using fallback method")
            return questions
        
        logger.warning("Could not extract any research questions using any method")
        return [] 