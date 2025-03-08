"""Client for interacting with the Perplexity API."""

import logging
import time
import json
import re
from typing import Dict, List, Any, Optional, Union
import requests
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
import tiktoken
import os

logger = logging.getLogger(__name__)


class PerplexityAPIError(Exception):
    """Exception raised for Perplexity API errors."""
    pass


class PerplexityRateLimitError(PerplexityAPIError):
    """Exception raised for Perplexity API rate limit errors."""
    pass


class PerplexityClient:
    """Client for interacting with the Perplexity API."""
    
    DEFAULT_API_URL = "https://api.perplexity.ai"
    
    def __init__(
        self, 
        api_key: str, 
        model: str = "sonar",
        temperature: float = 0.2,
        max_retries: int = 3
    ):
        """Initialize the Perplexity API client.
        
        Args:
            api_key: Perplexity API key
            model: Model to use for queries (default: sonar)
            temperature: Temperature for generation (0.0-1.0)
            max_retries: Maximum number of retries for API calls
        """
        self.api_key = api_key
        self.model = model
        self.temperature = temperature
        self.max_retries = max_retries
        self.api_url = self.DEFAULT_API_URL
        
        # Cost constants
        self.cost_per_1k_tokens = 0.001  # $1 per 1M tokens
        self.cost_per_search = 0.005  # $5 per 1000 searches
        
        # API costs dictionary for easier access
        self.API_COSTS = {
            'token': self.cost_per_1k_tokens,
            'search': self.cost_per_search
        }
        
        # Log the model being used
        logger.info(f"Initialized PerplexityClient with model: {self.model}")
        
        # Check if model is overridden by environment variable
        env_model = os.environ.get("PERPLEXITY_MODEL")
        if env_model and env_model != self.model:
            logger.info(f"Overriding model from config with environment variable: {env_model}")
            self.model = env_model
        
        self.encoder = tiktoken.get_encoding("cl100k_base")  # Using this as an estimate
    
    def count_tokens(self, text: str) -> int:
        """Count tokens in text.
        
        Args:
            text: Text to count tokens for
            
        Returns:
            Number of tokens
        """
        return len(self.encoder.encode(text))
    
    def estimate_cost(self, query: str, expected_response_tokens: int = 2000) -> float:
        """Estimate cost of a Perplexity API call.
        
        Args:
            query: Query text
            expected_response_tokens: Expected number of tokens in response
            
        Returns:
            Estimated cost in USD
        """
        # For the chat completions format, we need to count tokens for the system message + user message
        system_message = "You are a research assistant."
        user_message = query
        
        # Count tokens in the messages
        system_tokens = self.count_tokens(system_message)
        query_tokens = self.count_tokens(user_message)
        total_tokens = system_tokens + query_tokens + expected_response_tokens
        
        # Calculate token cost
        token_cost = (total_tokens / 1000) * self.cost_per_1k_tokens
        
        # Add search cost (each API call counts as 1 search)
        search_cost = self.cost_per_search
        
        # Return total cost
        return token_cost + search_cost
    
    def _get_headers(self) -> Dict[str, str]:
        """Get headers for API requests.
        
        Returns:
            Headers dictionary
        """
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=60),
        retry=retry_if_exception_type((PerplexityRateLimitError, requests.exceptions.ConnectionError)),
        reraise=True
    )
    def search(self, query: str, mode: str = "search") -> Dict[str, Any]:
        """Perform a standard search query with Perplexity.
        
        Args:
            query: Search query
            mode: Search mode parameter (typically "search")
            
        Returns:
            Dictionary with 'text', 'sources', and 'usage' keys
        """
        logger.debug(f"Calling Perplexity API for search with model {self.model}")
        
        # Create system message based on mode
        system_message = "You are a helpful search assistant. Provide concise, factual information for the query."
        
        # Construct the payload using the new chat completions format
        payload = {
            "model": self.model,
            "messages": [
                {
                    "role": "system",
                    "content": system_message
                },
                {
                    "role": "user",
                    "content": query
                }
            ],
            "temperature": self.temperature,
            "max_tokens": 2000,  # Standard response length
            "top_p": 0.9,
        }
        
        # Use the new chat/completions endpoint
        endpoint = f"{self.api_url}/chat/completions"
        
        try:
            response = requests.post(
                endpoint,
                headers=self._get_headers(),
                json=payload,
                timeout=60
            )
            
            # Handle rate limiting
            if response.status_code == 429:
                retry_after = int(response.headers.get("Retry-After", "60"))
                logger.warning(f"Perplexity API rate limit exceeded. Retry after {retry_after} seconds.")
                raise PerplexityRateLimitError(f"Rate limit exceeded. Retry after {retry_after} seconds.")
            
            # Handle other errors
            if response.status_code != 200:
                error_msg = f"Perplexity API error: {response.status_code} - {response.text}"
                logger.error(error_msg)
                raise PerplexityAPIError(error_msg)
            
            # Parse response
            data = response.json()
            
            # Extract results from the chat completions format
            content = ""
            citations = []
            
            if "choices" in data and len(data["choices"]) > 0:
                content = data["choices"][0]["message"]["content"]
            
            if "citations" in data:
                citations = [{"url": url, "title": "Source", "snippet": ""} for url in data["citations"]]
            
            # Construct the result
            result = {
                'text': content,
                'sources': self._process_sources(citations),
                'usage': data.get('usage', {})
            }
            
            return result
            
        except requests.exceptions.ConnectionError as e:
            logger.warning(f"Connection error when calling Perplexity API: {e}")
            raise
        except requests.exceptions.Timeout as e:
            logger.error(f"Timeout when calling Perplexity API: {e}")
            raise PerplexityAPIError(f"Request timed out: {e}")
        except requests.exceptions.RequestException as e:
            logger.error(f"Error when calling Perplexity API: {e}")
            raise PerplexityAPIError(f"Request failed: {e}")
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse Perplexity API response: {e}")
            raise PerplexityAPIError(f"Invalid JSON response: {e}")
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=60),
        retry=retry_if_exception_type((PerplexityRateLimitError, requests.exceptions.ConnectionError)),
        reraise=True
    )
    def deep_research(self, query: str, max_retries: int = None) -> dict:
        """Perform deep research on a query using the Perplexity API.
        
        Args:
            query: The query to research
            max_retries: Maximum number of retries (overrides instance setting)
            
        Returns:
            Dictionary containing the research results with 'text', 'sources', and 'usage' keys
        """
        # Enhance the query with specific instructions to stay on topic
        enhanced_query = f"""
IMPORTANT: Your task is to research the following topic EXACTLY as stated. 
DO NOT change the topic or drift to other subjects.
STRICTLY focus on this specific topic and nothing else: 

{query}

Provide comprehensive, factual information ONLY about this exact topic.
"""
        
        logger.debug(f"Calling Perplexity API for deep research with model {self.model}")
        
        # Prepare the API request
        payload = {
            "model": self.model,
            "messages": [
                {
                    "role": "user", 
                    "content": enhanced_query
                }
            ],
            "temperature": self.temperature
        }
        
        # Make the API call with retries
        max_retries = max_retries or self.max_retries
        response = self._make_api_call_with_retries(payload, max_retries)
        logger.debug(f"Got response from _make_api_call_with_retries with keys: {list(response.keys())}")
        
        # Calculate token usage and costs
        input_tokens = self._count_tokens(enhanced_query)
        output_tokens = self._count_tokens(response["text"])
        
        # Log token usage and costs
        token_cost = (input_tokens + output_tokens) * self.cost_per_1k_tokens / 1000
        search_cost = self.cost_per_search  # Each deep research call counts as one search
        total_cost = token_cost + search_cost
        
        logger.debug(f"Perplexity deep research API call: {input_tokens + output_tokens} tokens, ${token_cost:.4f} cost")
        
        # Add cost information to the response
        response["usage"] = {
            'total_tokens': input_tokens + output_tokens,
            'input_tokens': input_tokens,
            'output_tokens': output_tokens,
            'token_cost': token_cost,
            'search_cost': search_cost,
            'total_cost': total_cost
        }
        
        logger.debug(f"Final response from deep_research has keys: {list(response.keys())}")
        return response
    
    def batch_deep_research(self, queries: List[Dict[str, Any]], max_concurrent: int = 3) -> List[Dict[str, Any]]:
        """Run multiple deep research queries in batch.
        
        Args:
            queries: List of query objects with parameters
            max_concurrent: Maximum number of concurrent requests
            
        Returns:
            List of result dictionaries
        """
        logger.info(f"Running batch of {len(queries)} deep research queries")
        
        results = []
        for i in range(0, len(queries), max_concurrent):
            # Process queries in batches of max_concurrent
            batch = queries[i:i+max_concurrent]
            batch_results = []
            
            for query_obj in batch:
                query_text = query_obj.get("query_text", "")
                context = query_obj.get("context", None)
                
                # Process additional parameters
                params = query_obj.get("parameters", {})
                
                # Set model parameters based on the query
                depth = params.get("depth", "detailed")
                if depth == "exhaustive":
                    # For exhaustive searches, use longer timeout and more sources
                    timeout = 180
                else:
                    timeout = 120
                
                try:
                    logger.info(f"Processing query: {query_text[:50]}...")
                    result = self.deep_research(query_text, context)
                    
                    # Add query info to result
                    result["original_query"] = query_obj
                    batch_results.append(result)
                    
                except Exception as e:
                    logger.error(f"Error processing query '{query_text[:50]}...': {e}")
                    # Add error info to results
                    batch_results.append({
                        "error": str(e),
                        "original_query": query_obj,
                        "text": "",
                        "sources": []
                    })
                
                # Rate limiting sleep between queries
                time.sleep(2)
            
            # Add batch results to overall results
            results.extend(batch_results)
        
        logger.info(f"Completed batch of {len(queries)} queries with {len(results)} results")
        return results
    
    def run_optimized_queries(self, structured_queries: str) -> Dict[str, Any]:
        """Run optimized queries from Claude's output.
        
        Args:
            structured_queries: JSON string with optimized queries
            
        Returns:
            Combined results from all queries
        """
        logger.info("Processing optimized queries from Claude")
        
        # Extract JSON data from the string
        queries_data = self._extract_queries_from_text(structured_queries)
        
        if not queries_data or "queries" not in queries_data:
            logger.warning("No valid queries found in Claude's output")
            return {"text": "No valid queries were found", "sources": []}
        
        # Get the list of query objects
        queries = queries_data["queries"]
        
        # Sort queries by priority if available
        if all("priority" in q for q in queries):
            queries.sort(key=lambda q: q.get("priority", 5))
        
        # Convert to the format expected by batch_deep_research
        formatted_queries = []
        for query in queries:
            formatted_query = {
                "query_text": query.get("query_text", ""),
                "context": query.get("original_question", ""),
                "parameters": query.get("parameters", {})
            }
            formatted_queries.append(formatted_query)
        
        # Run the batch research
        batch_results = self.batch_deep_research(formatted_queries)
        
        # Combine results
        combined_text = "# Combined Research Results\n\n"
        all_sources = []
        
        for i, result in enumerate(batch_results):
            original_query = result.get("original_query", {})
            query_text = original_query.get("query_text", f"Query {i+1}")
            
            combined_text += f"## Research: {query_text}\n\n"
            combined_text += result.get("text", "No results available") + "\n\n"
            
            # Track sources
            sources = result.get("sources", [])
            for source in sources:
                if source not in all_sources:  # Avoid duplicates
                    all_sources.append(source)
        
        return {
            "text": combined_text,
            "sources": all_sources
        }
    
    def _extract_queries_from_text(self, text: str) -> Optional[Dict[str, Any]]:
        """Extract structured queries from Claude's response text.
        
        Args:
            text: Text response from Claude
            
        Returns:
            Dictionary with query data, or None if extraction failed
        """
        # Log the extraction process and input length
        logger.debug(f"Extracting queries from text (length: {len(text)})")
        
        # Handle empty or invalid text
        if not text or len(text.strip()) < 10:
            logger.warning("Empty or very short text provided for query extraction")
            return None
            
        # Log a preview of the text for debugging
        preview = text[:200] + "..." if len(text) > 200 else text
        logger.debug(f"Text preview: {preview}")
        
        # Try to extract JSON from triple backticks first (```json ... ```)
        json_regex = r"```(?:json)?\s*([\s\S]*?)```"
        json_matches = re.findall(json_regex, text)
        
        if json_matches:
            logger.debug(f"Found {len(json_matches)} JSON blocks in backticks")
            for idx, json_str in enumerate(json_matches):
                try:
                    # Try to parse the JSON
                    logger.debug(f"Attempting to parse JSON block {idx+1}")
                    data = json.loads(json_str)
                    
                    # Check if it has the expected structure
                    if isinstance(data, dict) and ("queries" in data or "query_text" in data):
                        logger.info(f"Successfully extracted query data from JSON block {idx+1}")
                        return data
                    elif isinstance(data, list) and all(isinstance(q, dict) and "query_text" in q for q in data):
                        logger.info(f"Successfully extracted list of query objects, converting to expected format")
                        return {"queries": data}
                except json.JSONDecodeError as e:
                    logger.warning(f"Failed to parse JSON block {idx+1}: {e}")
        
        # If no valid JSON in backticks, try to find raw JSON in the text
        try:
            # Look for JSON array pattern [{ ... }] or object pattern { ... }
            array_pattern = r"\[\s*{[\s\S]*}\s*\]"
            object_pattern = r"{[\s\S]*\"queries\"[\s\S]*}"
            
            # Try array pattern first
            array_match = re.search(array_pattern, text)
            if array_match:
                json_str = array_match.group(0)
                logger.debug(f"Found potential JSON array: {json_str[:100]}...")
                try:
                    data = json.loads(json_str)
                    if isinstance(data, list) and all(isinstance(q, dict) and "query_text" in q for q in data):
                        logger.info("Successfully extracted query list from raw JSON array")
                        return {"queries": data}
                except json.JSONDecodeError:
                    logger.warning("Failed to parse raw JSON array")
            
            # Try object pattern
            object_match = re.search(object_pattern, text)
            if object_match:
                json_str = object_match.group(0)
                logger.debug(f"Found potential JSON object: {json_str[:100]}...")
                try:
                    data = json.loads(json_str)
                    if isinstance(data, dict) and "queries" in data:
                        logger.info("Successfully extracted query data from raw JSON object")
                        return data
                except json.JSONDecodeError:
                    logger.warning("Failed to parse raw JSON object")
        
        except Exception as e:
            logger.warning(f"Error during raw JSON extraction: {e}")
        
        # Fallback: try to extract information directly from text if JSON parsing failed
        logger.info("Using fallback query extraction method")
        
        # Look for query patterns in text
        query_pattern = r"(?:query|query_text|search)(?:\s*:\s*|\s*=\s*|\s*is\s*)[\"']([^\"']+)[\"']"
        depth_pattern = r"(?:depth|level)(?:\s*:\s*|\s*=\s*|\s*is\s*)[\"']([^\"']+)[\"']"
        focus_pattern = r"(?:focus|topic)(?:\s*:\s*|\s*=\s*|\s*is\s*)[\"']([^\"']+)[\"']"
        source_pattern = r"(?:source|preference|sources)(?:\s*:\s*|\s*=\s*|\s*is\s*)[\"']([^\"']+)[\"']"
        
        # Extract queries
        query_matches = re.findall(query_pattern, text, re.IGNORECASE)
        
        if query_matches:
            logger.info(f"Extracted {len(query_matches)} queries using pattern matching")
            queries = []
            
            for query_text in query_matches:
                # Find the context around this query
                query_context = text[max(0, text.find(query_text) - 200):min(len(text), text.find(query_text) + 500)]
                
                # Extract parameters if available
                depth_match = re.search(depth_pattern, query_context, re.IGNORECASE)
                focus_match = re.search(focus_pattern, query_context, re.IGNORECASE)
                source_match = re.search(source_pattern, query_context, re.IGNORECASE)
                
                query = {
                    "query_text": query_text,
                    "depth": depth_match.group(1) if depth_match else "detailed",
                    "focus": focus_match.group(1) if focus_match else "current",
                    "source_preference": source_match.group(1) if source_match else "academic"
                }
                
                queries.append(query)
            
            if queries:
                return {"queries": queries}
        
        # If all extraction methods failed
        logger.error("No JSON or query data found in text")
        return None
    
    def _process_sources(self, sources: List[Dict]) -> List[Dict]:
        """Process and validate sources from Perplexity API response.
        
        Args:
            sources: List of source dictionaries
            
        Returns:
            Processed sources with consistent format
        """
        logger.debug(f"Processing sources: {sources}")
        
        if not sources:
            return []
        
        # Check if sources is just a list of URLs (common in newer API versions)
        if isinstance(sources, list) and all(isinstance(s, str) for s in sources):
            logger.debug("Sources are URLs, converting to standard format")
            processed_sources = []
            for url in sources:
                processed_sources.append({
                    'url': url,
                    'title': 'Source',
                    'snippet': '',
                    'reliability': 0.8  # Default reliability score
                })
            return processed_sources
            
        # Otherwise, expect a list of dictionaries with url, title, etc.
        processed_sources = []
        for source in sources:
            if isinstance(source, dict):
                logger.debug(f"Processing dictionary source: {source}")
                processed_source = {
                    'url': source.get('url', ''),
                    'title': source.get('title', 'Source'),
                    'snippet': source.get('snippet', ''),
                    'reliability': source.get('reliability', 0.8)
                }
                processed_sources.append(processed_source)
            elif isinstance(source, str):
                logger.debug(f"Processing string source: {source}")
                processed_sources.append({
                    'url': source,
                    'title': 'Source',
                    'snippet': '',
                    'reliability': 0.8
                })
            else:
                logger.warning(f"Unexpected source format: {type(source)}")
        
        logger.debug(f"Processed sources: {processed_sources}")
        return processed_sources
    
    def _make_api_call_with_retries(self, payload: dict, max_retries: int) -> dict:
        """Make an API call with retries.
        
        Args:
            payload: The API request payload
            max_retries: Maximum number of retries
            
        Returns:
            API response as a dictionary
            
        Raises:
            PerplexityAPIError: If the API call fails after all retries
        """
        endpoint = f"{self.api_url}/chat/completions"
        
        for attempt in range(max_retries + 1):
            try:
                response = requests.post(
                    endpoint,
                    headers=self._get_headers(),
                    json=payload,
                    timeout=120  # Longer timeout for deep research
                )
                
                # Log response for debugging
                logger.debug(f"Raw API response status: {response.status_code}")
                logger.debug(f"Raw API response headers: {response.headers}")
                
                # Handle rate limiting
                if response.status_code == 429:
                    retry_after = int(response.headers.get("Retry-After", "60"))
                    logger.warning(f"Perplexity API rate limit exceeded. Retry after {retry_after} seconds.")
                    if attempt < max_retries:
                        time.sleep(retry_after)
                        continue
                    else:
                        raise PerplexityRateLimitError(f"Rate limit exceeded. Retry after {retry_after} seconds.")
                
                # Handle other errors
                if response.status_code != 200:
                    error_msg = f"Perplexity API error: {response.status_code} - {response.text}"
                    logger.error(error_msg)
                    if attempt < max_retries:
                        time.sleep(2 ** attempt)  # Exponential backoff
                        continue
                    else:
                        raise PerplexityAPIError(error_msg)
                
                # Parse response
                data = response.json()
                logger.debug(f"Parsed API response data: {json.dumps(data, indent=2)[:500]}...")
                
                # Extract results from the chat completions format
                content = ""
                citations = []
                
                if "choices" in data and len(data["choices"]) > 0:
                    content = data["choices"][0]["message"]["content"]
                    logger.debug(f"Extracted content preview: {content[:100]}...")
                
                if "citations" in data:
                    citations = data["citations"]
                    logger.debug(f"Found {len(citations)} citations")
                
                # Construct the result
                result = {
                    'text': content,
                    'sources': self._process_sources(citations),
                }
                logger.debug(f"Returning result with keys: {list(result.keys())}")
                
                return result
                
            except requests.exceptions.ConnectionError as e:
                logger.warning(f"Connection error when calling Perplexity API: {e}")
                if attempt < max_retries:
                    time.sleep(2 ** attempt)  # Exponential backoff
                    continue
                else:
                    raise PerplexityAPIError(f"Connection error: {e}")
            except requests.exceptions.Timeout as e:
                logger.error(f"Timeout when calling Perplexity API: {e}")
                if attempt < max_retries:
                    time.sleep(2 ** attempt)  # Exponential backoff
                    continue
                else:
                    raise PerplexityAPIError(f"Request timed out: {e}")
            except requests.exceptions.RequestException as e:
                logger.error(f"Error when calling Perplexity API: {e}")
                if attempt < max_retries:
                    time.sleep(2 ** attempt)  # Exponential backoff
                    continue
                else:
                    raise PerplexityAPIError(f"Request failed: {e}")
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse Perplexity API response: {e}")
                if attempt < max_retries:
                    time.sleep(2 ** attempt)  # Exponential backoff
                    continue
                else:
                    raise PerplexityAPIError(f"Invalid JSON response: {e}")
        
        # If we get here, all retries failed
        raise PerplexityAPIError("API call failed after all retries")
    
    def _count_tokens(self, text: str) -> int:
        """Count the number of tokens in a text string.
        
        Args:
            text: The text to count tokens for
            
        Returns:
            Number of tokens
        """
        if not text:
            return 0
            
        try:
            return len(self.encoder.encode(text))
        except Exception as e:
            logger.warning(f"Error counting tokens: {e}")
            # Fallback: estimate 4 characters per token
            return len(text) // 4 