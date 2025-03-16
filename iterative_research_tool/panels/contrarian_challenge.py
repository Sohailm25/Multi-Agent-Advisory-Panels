"""Contrarian Challenge System panel for multi-agent advisory planning."""

import logging
from typing import Dict, List, Any, Optional, TypedDict
import json

# LangGraph imports
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode

# Anthropic imports
from anthropic import Anthropic

# Local imports
from iterative_research_tool.panels import BasePanel

logger = logging.getLogger(__name__)

class ContrarianChallengePanel(BasePanel):
    """Contrarian Challenge System panel for multi-agent advisory planning.
    
    This panel stress-tests strategies by challenging assumptions, considering 
    opposing viewpoints, and exploring alternative approaches. It helps identify 
    potential blindspots, logical fallacies, and weaknesses in proposed plans.
    """
    
    def __init__(
        self,
        anthropic_api_key: str,
        model: str = "claude-3-7-sonnet-20250219",
        visualizer = None
    ):
        """Initialize the Contrarian Challenge System panel.
        
        Args:
            anthropic_api_key: API key for Anthropic
            model: Model to use for planning
            visualizer: Visualizer instance for displaying progress
        """
        self.anthropic_api_key = anthropic_api_key
        self.model = model
        self.client = Anthropic(api_key=anthropic_api_key)
        self.visualizer = visualizer
        
        # Define agent prompts
        self.agent_prompts = {
            "problem_analyzer": self._get_problem_analyzer_prompt(),
            "assumption_challenger": self._get_assumption_challenger_prompt(),
            "alternative_viewpoint_generator": self._get_alternative_viewpoint_generator_prompt(),
            "logical_fallacy_detector": self._get_logical_fallacy_detector_prompt(),
            "devils_advocate": self._get_devils_advocate_prompt(),
            "response_evaluator": self._get_response_evaluator_prompt(),
            "robust_strategy_synthesizer": self._get_robust_strategy_synthesizer_prompt()
        }
        
        # Initialize the graph
        self.graph = self._build_graph()
        
    def _get_problem_analyzer_prompt(self) -> str:
        """Get the prompt for the Problem Analyzer agent."""
        return """
        You are a critical problem analyst specializing in deconstructing problems and proposed solutions. Your role is to:
        - Identify the core problem being addressed and its key components
        - Recognize hidden dimensions or aspects of the problem being overlooked
        - Clarify the goals and constraints relevant to the problem
        - Analyze underlying assumptions in how the problem is framed
        - Evaluate whether the problem statement itself is biased or skewed

        Based on the user's query, perform a critical analysis of the problem.
        
        Format your response as a JSON object with the following structure:
        {
            "problem_analysis": {
                "stated_problem": "Brief restatement of the problem as presented",
                "core_components": ["component 1", "component 2", ...],
                "hidden_dimensions": ["dimension 1", "dimension 2", ...],
                "goals_and_constraints": {
                    "explicit_goals": ["goal 1", "goal 2", ...],
                    "implicit_goals": ["goal 1", "goal 2", ...],
                    "stated_constraints": ["constraint 1", "constraint 2", ...],
                    "unstated_constraints": ["constraint 1", "constraint 2", ...]
                },
                "key_assumptions": [
                    {
                        "assumption": "Description of the assumption",
                        "criticality": "High/Medium/Low",
                        "basis": "Stated basis for this assumption, if any"
                    },
                    ...
                ],
                "problem_framing_biases": ["bias 1", "bias 2", ...],
                "alternative_problem_framings": ["framing 1", "framing 2", ...]
            }
        }
        """
        
    def _get_assumption_challenger_prompt(self) -> str:
        """Get the prompt for the Assumption Challenger agent."""
        return """
        You are an assumption challenger who identifies and tests hidden assumptions. Your role is to:
        - Identify explicit and implicit assumptions in the problem and approach
        - Challenge these assumptions with counterexamples and alternative perspectives
        - Evaluate the sensitivity of conclusions to changes in key assumptions
        - Propose scenarios where assumptions would no longer hold
        - Suggest more robust alternative assumptions

        Based on the problem analysis, challenge the key assumptions.
        
        Format your response as a JSON object with the following structure:
        {
            "assumption_challenges": {
                "summary": "Brief summary of your assumption challenges",
                "challenged_assumptions": [
                    {
                        "assumption": "The assumption being challenged",
                        "challenge": "Your challenge to this assumption",
                        "counterexamples": ["counterexample 1", "counterexample 2", ...],
                        "alternative_perspectives": ["perspective 1", "perspective 2", ...],
                        "sensitivity_analysis": "How sensitive conclusions are to this assumption",
                        "breaking_scenarios": ["scenario 1", "scenario 2", ...],
                        "alternative_assumptions": ["assumption 1", "assumption 2", ...]
                    },
                    ...
                ],
                "additional_hidden_assumptions": [
                    {
                        "assumption": "Additional hidden assumption identified",
                        "challenge": "Why this assumption may be problematic",
                        "alternative": "A better assumption to consider"
                    },
                    ...
                ],
                "overall_assessment": "Overall assessment of how assumptions affect the approach"
            }
        }
        """
        
    def _get_alternative_viewpoint_generator_prompt(self) -> str:
        """Get the prompt for the Alternative Viewpoint Generator agent."""
        return """
        You are an alternative viewpoint generator who explores diverse perspectives. Your role is to:
        - Generate multiple alternative viewpoints on the problem
        - Consider perspectives from different disciplines, cultures, and value systems
        - Identify stakeholders with opposing interests and articulate their viewpoints
        - Explore perspectives that directly contradict the mainstream approach
        - Consider historical and future perspectives on the problem

        Based on the problem analysis, generate alternative viewpoints.
        
        Format your response as a JSON object with the following structure:
        {
            "alternative_viewpoints": {
                "summary": "Brief summary of your alternative viewpoints approach",
                "disciplinary_perspectives": [
                    {
                        "discipline": "The discipline/field providing this perspective",
                        "viewpoint": "The perspective from this discipline",
                        "key_insights": ["insight 1", "insight 2", ...],
                        "contrasts_with_original": "How this contrasts with the original framing"
                    },
                    ...
                ],
                "cultural_perspectives": [
                    {
                        "cultural_context": "The cultural context of this perspective",
                        "viewpoint": "The perspective from this cultural context",
                        "key_insights": ["insight 1", "insight 2", ...],
                        "contrasts_with_original": "How this contrasts with the original framing"
                    },
                    ...
                ],
                "stakeholder_perspectives": [
                    {
                        "stakeholder": "The stakeholder providing this perspective",
                        "viewpoint": "The perspective from this stakeholder",
                        "key_interests": ["interest 1", "interest 2", ...],
                        "contrasts_with_original": "How this contrasts with the original framing"
                    },
                    ...
                ],
                "contrarian_perspectives": [
                    {
                        "contrarian_view": "Description of the contrarian view",
                        "rationale": "Rationale behind this view",
                        "key_insights": ["insight 1", "insight 2", ...],
                        "potential_validity": "Assessment of when/where this view might be valid"
                    },
                    ...
                ],
                "temporal_perspectives": [
                    {
                        "time_frame": "The time frame of this perspective (past/future)",
                        "viewpoint": "The perspective from this time frame",
                        "key_insights": ["insight 1", "insight 2", ...],
                        "contrasts_with_current": "How this contrasts with current thinking"
                    },
                    ...
                ],
                "synthesis_of_perspectives": "Synthesis of how these diverse perspectives inform our understanding"
            }
        }
        """
        
    def _get_logical_fallacy_detector_prompt(self) -> str:
        """Get the prompt for the Logical Fallacy Detector agent."""
        return """
        You are a logical fallacy detector specialized in identifying flaws in reasoning. Your role is to:
        - Detect formal and informal logical fallacies in the problem framing and proposed approaches
        - Identify cognitive biases that may be influencing the thinking
        - Evaluate the logical structure and validity of arguments
        - Assess the quality and relevance of evidence being used
        - Point out gaps in reasoning or unwarranted leaps in logic

        Based on the problem analysis and challenged assumptions, identify logical fallacies.
        
        Format your response as a JSON object with the following structure:
        {
            "logical_fallacy_analysis": {
                "summary": "Brief summary of your logical fallacy analysis",
                "formal_fallacies": [
                    {
                        "fallacy_type": "The type of formal fallacy",
                        "instance": "Where this fallacy appears in the reasoning",
                        "explanation": "Explanation of why this is fallacious",
                        "correction": "How the reasoning could be corrected"
                    },
                    ...
                ],
                "informal_fallacies": [
                    {
                        "fallacy_type": "The type of informal fallacy",
                        "instance": "Where this fallacy appears in the reasoning",
                        "explanation": "Explanation of why this is fallacious",
                        "correction": "How the reasoning could be corrected"
                    },
                    ...
                ],
                "cognitive_biases": [
                    {
                        "bias_type": "The type of cognitive bias",
                        "instance": "Where this bias appears in the reasoning",
                        "explanation": "Explanation of how this bias affects the reasoning",
                        "mitigation": "How to mitigate this bias"
                    },
                    ...
                ],
                "evidence_quality_issues": [
                    {
                        "issue_type": "The type of evidence quality issue",
                        "instance": "Where this issue appears",
                        "explanation": "Explanation of the evidence problem",
                        "improvement": "How the evidence could be improved"
                    },
                    ...
                ],
                "reasoning_gaps": [
                    {
                        "gap_description": "Description of the reasoning gap",
                        "location": "Where this gap appears",
                        "impact": "Impact of this gap on conclusions",
                        "bridging_approach": "How to bridge this gap"
                    },
                    ...
                ],
                "overall_logical_assessment": "Overall assessment of the logical quality of the reasoning"
            }
        }
        """
        
    def _get_devils_advocate_prompt(self) -> str:
        """Get the prompt for the Devil's Advocate agent."""
        return """
        You are a devil's advocate who forcefully argues against proposed approaches. Your role is to:
        - Present the strongest possible case against the proposed approach
        - Highlight potential failure modes and vulnerabilities
        - Argue from the perspective of intelligent opposition
        - Stress test the resilience of the approach to criticism
        - Identify the conditions under which the approach would fail

        Based on the problem analysis and previous challenges, play devil's advocate against the approach.
        
        Format your response as a JSON object with the following structure:
        {
            "devils_advocate": {
                "summary": "Brief summary of your devil's advocate position",
                "core_counterarguments": [
                    {
                        "argument": "Your counterargument",
                        "strength": "Assessment of how strong this counterargument is",
                        "basis": "The basis for this counterargument",
                        "rebuttal_difficulty": "Assessment of how difficult this would be to rebut"
                    },
                    ...
                ],
                "failure_modes": [
                    {
                        "failure_mode": "Description of the failure mode",
                        "trigger_conditions": ["condition 1", "condition 2", ...],
                        "impact": "Impact if this failure occurs",
                        "probability": "Assessment of probability",
                        "preventability": "Assessment of how preventable this is"
                    },
                    ...
                ],
                "opposition_perspective": {
                    "opposition_identity": "Identity of the intelligent opposition",
                    "opposition_motivation": "Motivation of the opposition",
                    "opposition_strategy": "Strategy the opposition would use",
                    "opposition_arguments": ["argument 1", "argument 2", ...],
                    "opposition_evidence": ["evidence 1", "evidence 2", ...]
                },
                "stress_test_results": [
                    {
                        "test_scenario": "Description of the stress test scenario",
                        "approach_response": "How the approach would respond",
                        "vulnerabilities_exposed": ["vulnerability 1", "vulnerability 2", ...],
                        "resilience_assessment": "Assessment of resilience in this scenario"
                    },
                    ...
                ],
                "failure_conditions": {
                    "definite_failure_conditions": ["condition 1", "condition 2", ...],
                    "probable_failure_conditions": ["condition 1", "condition 2", ...],
                    "early_warning_signs": ["sign 1", "sign 2", ...],
                    "mitigation_possibilities": ["mitigation 1", "mitigation 2", ...]
                },
                "overall_evaluation": "Overall evaluation from the devil's advocate perspective"
            }
        }
        """
        
    def _get_response_evaluator_prompt(self) -> str:
        """Get the prompt for the Response Evaluator agent."""
        return """
        You are a response evaluator who assesses the strength of responses to challenges. Your role is to:
        - Evaluate how well responses address the challenges raised
        - Assess the completeness and robustness of responses
        - Identify remaining vulnerabilities not addressed by responses
        - Determine whether responses introduce new problems
        - Provide an overall evaluation of the response strength

        Based on the challenges and opposing viewpoints, evaluate potential responses.
        
        Format your response as a JSON object with the following structure:
        {
            "response_evaluation": {
                "summary": "Brief summary of your response evaluation",
                "challenge_response_assessments": [
                    {
                        "challenge": "The challenge being addressed",
                        "response": "The response to this challenge",
                        "effectiveness": "Assessment of response effectiveness",
                        "completeness": "Assessment of response completeness",
                        "robustness": "Assessment of response robustness",
                        "new_issues_introduced": ["issue 1", "issue 2", ...],
                        "overall_rating": "High/Medium/Low rating of this response"
                    },
                    ...
                ],
                "unaddressed_vulnerabilities": [
                    {
                        "vulnerability": "Description of the unaddressed vulnerability",
                        "importance": "Assessment of the importance of this vulnerability",
                        "suggested_response": "Suggested response to this vulnerability"
                    },
                    ...
                ],
                "response_pattern_analysis": {
                    "defensive_patterns": ["pattern 1", "pattern 2", ...],
                    "creative_patterns": ["pattern 1", "pattern 2", ...],
                    "evasive_patterns": ["pattern 1", "pattern 2", ...],
                    "pattern_implications": "Implications of these response patterns"
                },
                "response_effectiveness_matrix": [
                    {
                        "challenge_type": "Type of challenge",
                        "response_effectiveness": "High/Medium/Low",
                        "explanation": "Explanation of this effectiveness rating"
                    },
                    ...
                ],
                "overall_response_evaluation": "Overall evaluation of response effectiveness"
            }
        }
        """
        
    def _get_robust_strategy_synthesizer_prompt(self) -> str:
        """Get the prompt for the Robust Strategy Synthesizer agent."""
        return """
        You are a robust strategy synthesizer who creates resilient plans. Your role is to:
        - Synthesize insights from all challenges and responses
        - Develop a more robust strategy that addresses key vulnerabilities
        - Incorporate contingency plans for identified failure modes
        - Build flexibility and adaptability into the approach
        - Create a strategy that maintains effectiveness across different scenarios

        Based on all previous analyses, synthesize a robust strategy.
        
        Format your response as a JSON object with the following structure:
        {
            "Executive Summary": "Brief executive summary of the robust strategy",
            "Key Insights": ["insight 1", "insight 2", ...],
            "Robust Strategy": {
                "core_approach": "Description of the core approach",
                "key_modifications": [
                    {
                        "original_element": "Original element of the strategy",
                        "modification": "Modification to make it more robust",
                        "rationale": "Rationale for this modification",
                        "expected_impact": "Expected impact of this modification"
                    },
                    ...
                ],
                "vulnerability_mitigations": [
                    {
                        "vulnerability": "The vulnerability being mitigated",
                        "mitigation_approach": "Approach to mitigate this vulnerability",
                        "residual_risk": "Any residual risk after mitigation"
                    },
                    ...
                ],
                "contingency_plans": [
                    {
                        "trigger_condition": "Condition that triggers this contingency",
                        "contingency_action": "The contingency action to take",
                        "resource_requirements": "Resources required for this contingency",
                        "implementation_approach": "How to implement this contingency"
                    },
                    ...
                ],
                "adaptability_mechanisms": [
                    {
                        "adaptation_point": "Point in the strategy where adaptation may be needed",
                        "adaptation_options": ["option 1", "option 2", ...],
                        "decision_criteria": "Criteria for choosing among options",
                        "implementation_approach": "How to implement this adaptation"
                    },
                    ...
                ],
                "cross_scenario_effectiveness": [
                    {
                        "scenario": "Description of the scenario",
                        "strategy_effectiveness": "Assessment of strategy effectiveness in this scenario",
                        "key_adjustments": "Key adjustments for this scenario"
                    },
                    ...
                ]
            },
            "Implementation Considerations": [
                {
                    "consideration": "Implementation consideration",
                    "importance": "Importance of this consideration",
                    "approach": "Approach to address this consideration"
                },
                ...
            ],
            "Success Metrics": ["metric 1", "metric 2", ...],
            "Risk Management": {
                "key_risks": ["risk 1", "risk 2", ...],
                "monitoring_approach": "Approach to monitor for these risks",
                "response_strategies": "Strategies to respond if risks materialize"
            }
        }
        """
        
    def _build_graph(self) -> StateGraph:
        """Build the LangGraph workflow for the Contrarian Challenge System panel."""
        # Define the state schema
        class State(TypedDict):
            query: str
            context: Dict
            problem_analysis: Optional[Dict]
            assumption_challenges: Optional[Dict]
            alternative_viewpoints: Optional[Dict]
            logical_fallacy_analysis: Optional[Dict]
            devils_advocate_critique: Optional[Dict]
            response_evaluation: Optional[Dict]
            robust_strategy: Optional[Dict]
        
        # Create the graph
        graph = StateGraph(State)
        
        # Define the nodes
        
        # Problem Analyzer node
        def problem_analyzer(state):
            if self.visualizer:
                self.visualizer.update_agent_status("Problem Analyzer", "processing")
                
            query = state["query"]
            context = state["context"]
            
            prompt = self.agent_prompts["problem_analyzer"]
            
            response = self.client.messages.create(
                model=self.model,
                max_tokens=2000,
                temperature=0.7,
                system=prompt,
                messages=[
                    {"role": "user", "content": f"Query: {query}\n\nContext: {json.dumps(context)}"}
                ]
            )
            
            try:
                content = response.content[0].text
                # Extract JSON from the response
                import re
                json_match = re.search(r'```json\n(.*?)\n```', content, re.DOTALL)
                if json_match:
                    json_str = json_match.group(1)
                else:
                    json_str = content
                
                problem_analysis = json.loads(json_str)
                
                if self.visualizer:
                    self.visualizer.update_agent_status("Problem Analyzer", "Complete")
                    
                return {"problem_analysis": problem_analysis}
            except Exception as e:
                logger.error(f"Error parsing Problem Analyzer response: {e}")
                if self.visualizer:
                    self.visualizer.update_agent_status("Problem Analyzer", "Error")
                return {"problem_analysis": {"error": str(e), "raw_response": content}}
        
        # Assumption Challenger node
        def assumption_challenger(state):
            if self.visualizer:
                self.visualizer.update_agent_status("Assumption Challenger", "processing")
                
            query = state["query"]
            context = state["context"]
            problem_analysis = state["problem_analysis"]
            
            prompt = self.agent_prompts["assumption_challenger"]
            
            response = self.client.messages.create(
                model=self.model,
                max_tokens=2000,
                temperature=0.7,
                system=prompt,
                messages=[
                    {"role": "user", "content": f"Query: {query}\n\nContext: {json.dumps(context)}\n\nProblem Analysis: {json.dumps(problem_analysis)}"}
                ]
            )
            
            try:
                content = response.content[0].text
                # Extract JSON from the response
                import re
                json_match = re.search(r'```json\n(.*?)\n```', content, re.DOTALL)
                if json_match:
                    json_str = json_match.group(1)
                else:
                    json_str = content
                
                assumption_challenges = json.loads(json_str)
                
                if self.visualizer:
                    self.visualizer.update_agent_status("Assumption Challenger", "Complete")
                    
                return {"assumption_challenges": assumption_challenges}
            except Exception as e:
                logger.error(f"Error parsing Assumption Challenger response: {e}")
                if self.visualizer:
                    self.visualizer.update_agent_status("Assumption Challenger", "Error")
                return {"assumption_challenges": {"error": str(e), "raw_response": content}}
        
        # Alternative Viewpoint Generator node
        def alternative_viewpoint_generator(state):
            if self.visualizer:
                self.visualizer.update_agent_status("Alternative Viewpoint Generator", "processing")
                
            query = state["query"]
            context = state["context"]
            problem_analysis = state["problem_analysis"]
            
            prompt = self.agent_prompts["alternative_viewpoint_generator"]
            
            response = self.client.messages.create(
                model=self.model,
                max_tokens=2000,
                temperature=0.7,
                system=prompt,
                messages=[
                    {"role": "user", "content": f"Query: {query}\n\nContext: {json.dumps(context)}\n\nProblem Analysis: {json.dumps(problem_analysis)}"}
                ]
            )
            
            try:
                content = response.content[0].text
                # Extract JSON from the response
                import re
                json_match = re.search(r'```json\n(.*?)\n```', content, re.DOTALL)
                if json_match:
                    json_str = json_match.group(1)
                else:
                    json_str = content
                
                alternative_viewpoints = json.loads(json_str)
                
                if self.visualizer:
                    self.visualizer.update_agent_status("Alternative Viewpoint Generator", "Complete")
                    
                return {"alternative_viewpoints": alternative_viewpoints}
            except Exception as e:
                logger.error(f"Error parsing Alternative Viewpoint Generator response: {e}")
                if self.visualizer:
                    self.visualizer.update_agent_status("Alternative Viewpoint Generator", "Error")
                return {"alternative_viewpoints": {"error": str(e), "raw_response": content}}
        
        # Logical Fallacy Detector node
        def logical_fallacy_detector(state):
            if self.visualizer:
                self.visualizer.update_agent_status("Logical Fallacy Detector", "processing")
                
            query = state["query"]
            context = state["context"]
            problem_analysis = state["problem_analysis"]
            assumption_challenges = state["assumption_challenges"]
            
            prompt = self.agent_prompts["logical_fallacy_detector"]
            
            response = self.client.messages.create(
                model=self.model,
                max_tokens=2000,
                temperature=0.7,
                system=prompt,
                messages=[
                    {"role": "user", "content": f"""
                    Query: {query}
                    
                    Context: {json.dumps(context)}
                    
                    Problem Analysis: {json.dumps(problem_analysis)}
                    
                    Assumption Challenges: {json.dumps(assumption_challenges)}
                    """}
                ]
            )
            
            try:
                content = response.content[0].text
                # Extract JSON from the response
                import re
                json_match = re.search(r'```json\n(.*?)\n```', content, re.DOTALL)
                if json_match:
                    json_str = json_match.group(1)
                else:
                    json_str = content
                
                logical_fallacy_analysis = json.loads(json_str)
                
                if self.visualizer:
                    self.visualizer.update_agent_status("Logical Fallacy Detector", "Complete")
                    
                return {"logical_fallacy_analysis": logical_fallacy_analysis}
            except Exception as e:
                logger.error(f"Error parsing Logical Fallacy Detector response: {e}")
                if self.visualizer:
                    self.visualizer.update_agent_status("Logical Fallacy Detector", "Error")
                return {"logical_fallacy_analysis": {"error": str(e), "raw_response": content}}
        
        # Devil's Advocate node
        def devils_advocate(state):
            if self.visualizer:
                self.visualizer.update_agent_status("Devil's Advocate", "processing")
                
            query = state["query"]
            context = state["context"]
            problem_analysis = state["problem_analysis"]
            assumption_challenges = state["assumption_challenges"]
            alternative_viewpoints = state["alternative_viewpoints"]
            logical_fallacy_analysis = state["logical_fallacy_analysis"]
            
            prompt = self.agent_prompts["devils_advocate"]
            
            response = self.client.messages.create(
                model=self.model,
                max_tokens=2000,
                temperature=0.7,
                system=prompt,
                messages=[
                    {"role": "user", "content": f"""
                    Query: {query}
                    
                    Context: {json.dumps(context)}
                    
                    Problem Analysis: {json.dumps(problem_analysis)}
                    
                    Assumption Challenges: {json.dumps(assumption_challenges)}
                    
                    Alternative Viewpoints: {json.dumps(alternative_viewpoints)}
                    
                    Logical Fallacy Analysis: {json.dumps(logical_fallacy_analysis)}
                    """}
                ]
            )
            
            try:
                content = response.content[0].text
                # Extract JSON from the response
                import re
                json_match = re.search(r'```json\n(.*?)\n```', content, re.DOTALL)
                if json_match:
                    json_str = json_match.group(1)
                else:
                    json_str = content
                
                devils_advocate_critique = json.loads(json_str)
                
                if self.visualizer:
                    self.visualizer.update_agent_status("Devil's Advocate", "Complete")
                    
                return {"devils_advocate_critique": devils_advocate_critique}
            except Exception as e:
                logger.error(f"Error parsing Devil's Advocate response: {e}")
                if self.visualizer:
                    self.visualizer.update_agent_status("Devil's Advocate", "Error")
                return {"devils_advocate_critique": {"error": str(e), "raw_response": content}}
        
        # Response Evaluator node
        def response_evaluator(state):
            if self.visualizer:
                self.visualizer.update_agent_status("Response Evaluator", "processing")
                
            query = state["query"]
            context = state["context"]
            assumption_challenges = state["assumption_challenges"]
            alternative_viewpoints = state["alternative_viewpoints"]
            logical_fallacy_analysis = state["logical_fallacy_analysis"]
            devils_advocate_critique = state["devils_advocate_critique"]
            
            prompt = self.agent_prompts["response_evaluator"]
            
            response = self.client.messages.create(
                model=self.model,
                max_tokens=2000,
                temperature=0.7,
                system=prompt,
                messages=[
                    {"role": "user", "content": f"""
                    Query: {query}
                    
                    Context: {json.dumps(context)}
                    
                    Assumption Challenges: {json.dumps(assumption_challenges)}
                    
                    Alternative Viewpoints: {json.dumps(alternative_viewpoints)}
                    
                    Logical Fallacy Analysis: {json.dumps(logical_fallacy_analysis)}
                    
                    Devil's Advocate Critique: {json.dumps(devils_advocate_critique)}
                    """}
                ]
            )
            
            try:
                content = response.content[0].text
                # Extract JSON from the response
                import re
                json_match = re.search(r'```json\n(.*?)\n```', content, re.DOTALL)
                if json_match:
                    json_str = json_match.group(1)
                else:
                    json_str = content
                
                response_evaluation = json.loads(json_str)
                
                if self.visualizer:
                    self.visualizer.update_agent_status("Response Evaluator", "Complete")
                    
                return {"response_evaluation": response_evaluation}
            except Exception as e:
                logger.error(f"Error parsing Response Evaluator response: {e}")
                if self.visualizer:
                    self.visualizer.update_agent_status("Response Evaluator", "Error")
                return {"response_evaluation": {"error": str(e), "raw_response": content}}
        
        # Robust Strategy Synthesizer node
        def robust_strategy_synthesizer(state):
            if self.visualizer:
                self.visualizer.update_agent_status("Robust Strategy Synthesizer", "processing")
                
            query = state["query"]
            context = state["context"]
            problem_analysis = state["problem_analysis"]
            assumption_challenges = state["assumption_challenges"]
            alternative_viewpoints = state["alternative_viewpoints"]
            logical_fallacy_analysis = state["logical_fallacy_analysis"]
            devils_advocate_critique = state["devils_advocate_critique"]
            response_evaluation = state["response_evaluation"]
            
            prompt = self.agent_prompts["robust_strategy_synthesizer"]
            
            response = self.client.messages.create(
                model=self.model,
                max_tokens=3000,
                temperature=0.7,
                system=prompt,
                messages=[
                    {"role": "user", "content": f"""
                    Query: {query}
                    
                    Context: {json.dumps(context)}
                    
                    Problem Analysis: {json.dumps(problem_analysis)}
                    
                    Assumption Challenges: {json.dumps(assumption_challenges)}
                    
                    Alternative Viewpoints: {json.dumps(alternative_viewpoints)}
                    
                    Logical Fallacy Analysis: {json.dumps(logical_fallacy_analysis)}
                    
                    Devil's Advocate Critique: {json.dumps(devils_advocate_critique)}
                    
                    Response Evaluation: {json.dumps(response_evaluation)}
                    """}
                ]
            )
            
            try:
                content = response.content[0].text
                # Extract JSON from the response
                import re
                json_match = re.search(r'```json\n(.*?)\n```', content, re.DOTALL)
                if json_match:
                    json_str = json_match.group(1)
                else:
                    json_str = content
                
                robust_strategy = json.loads(json_str)
                
                if self.visualizer:
                    self.visualizer.update_agent_status("Robust Strategy Synthesizer", "Complete")
                    
                return {"robust_strategy": robust_strategy}
            except Exception as e:
                logger.error(f"Error parsing Robust Strategy Synthesizer response: {e}")
                if self.visualizer:
                    self.visualizer.update_agent_status("Robust Strategy Synthesizer", "Error")
                return {"robust_strategy": {"error": str(e), "raw_response": content}}
        
        # Add nodes to the graph
        graph.add_node("problem_analyzer", problem_analyzer)
        graph.add_node("assumption_challenger", assumption_challenger)
        graph.add_node("alternative_viewpoint_generator", alternative_viewpoint_generator)
        graph.add_node("logical_fallacy_detector", logical_fallacy_detector)
        graph.add_node("devils_advocate", devils_advocate)
        graph.add_node("response_evaluator", response_evaluator)
        graph.add_node("robust_strategy_synthesizer", robust_strategy_synthesizer)
        
        # Define the edges
        graph.add_edge("problem_analyzer", "assumption_challenger")
        graph.add_edge("problem_analyzer", "alternative_viewpoint_generator")
        graph.add_edge("assumption_challenger", "logical_fallacy_detector")
        graph.add_edge("alternative_viewpoint_generator", "logical_fallacy_detector")
        graph.add_edge("logical_fallacy_detector", "devils_advocate")
        graph.add_edge("devils_advocate", "response_evaluator")
        graph.add_edge("response_evaluator", "robust_strategy_synthesizer")
        graph.add_edge("robust_strategy_synthesizer", END)
        
        # Set the entry point
        graph.set_entry_point("problem_analyzer")
        
        # Return the compiled graph
        return graph.compile()
        
    def run(self, query: str, context: str = "") -> Dict[str, Any]:
        """Run the Contrarian Challenge System panel on the given query.
        
        Args:
            query: The query to run the panel on
            context: Context information
            
        Returns:
            The panel's output
        """
        if self.visualizer:
            self.visualizer.display_welcome("Contrarian Challenge System")
            self.visualizer.display_query(query)
            self.visualizer.update_status("Running Contrarian Challenge System panel")
        
        # Parse context if it's a string
        if isinstance(context, str):
            try:
                context_dict = json.loads(context)
            except:
                context_dict = {"raw_context": context}
        else:
            context_dict = context
        
        # Initialize the state
        initial_state = {
            "query": query,
            "context": context_dict,
            "problem_analysis": {},
            "assumption_challenges": {},
            "alternative_viewpoints": {},
            "logical_fallacy_analysis": {},
            "devils_advocate_critique": {},
            "response_evaluation": {},
            "robust_strategy": {}
        }
        
        # Run the graph
        try:
            result = self.graph.invoke(initial_state)
            
            if self.visualizer:
                self.visualizer.display_success("Contrarian Challenge System panel completed successfully")
                self.visualizer.display_plan(result["robust_strategy"])
            
            return result["robust_strategy"]
        except Exception as e:
            logger.error(f"Error running Contrarian Challenge System panel: {e}")
            if self.visualizer:
                self.visualizer.display_error(f"Error running Contrarian Challenge System panel: {e}")
            return {
                "error": str(e),
                "Executive Summary": "An error occurred while running the Contrarian Challenge System panel.",
                "Key Insights": ["Error in panel execution"],
                "Robust Strategy": {"core_approach": "Please try again or contact support"}
            } 