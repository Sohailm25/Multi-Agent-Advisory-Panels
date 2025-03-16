#!/usr/bin/env python3
"""Direct test for LLM caching in the Strategic Advisor Swarm."""

import os
import json
import time
import hashlib
from dotenv import load_dotenv

# Import necessary modules
from anthropic import Anthropic

def test_caching():
    """Test LLM caching with a simple implementation."""
    # Load environment variables
    load_dotenv()
    
    # Get the API key
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        print("Error: No API key found for Anthropic.")
        print("Please set ANTHROPIC_API_KEY environment variable.")
        return 1
    
    # Create an Anthropic client
    client = Anthropic(api_key=api_key)
    
    # Test prompt
    test_prompt = """
    Analyze the following business scenario and provide strategic advice:
    
    A medium-sized software company is experiencing high employee turnover, especially among senior developers.
    The company has competitive salaries but struggles with maintaining a positive work culture.
    What strategic changes should the company implement to improve retention?
    """
    
    # Initialize a simple cache
    cache = {}
    cache_hits = 0
    cache_misses = 0
    
    def get_cache_key(prompt, model):
        """Generate a unique cache key for the prompt and model."""
        combined = f"{prompt}:{model}"
        return hashlib.md5(combined.encode()).hexdigest()
    
    def call_llm_with_cache(prompt, model="claude-3-opus-20240229", use_cache=True):
        """Call the LLM with optional caching."""
        # Check if we should use the cache
        if use_cache:
            cache_key = get_cache_key(prompt, model)
            
            # Check if the prompt is in the cache
            if cache_key in cache:
                nonlocal cache_hits
                cache_hits += 1
                print(f"Cache hit! Key: {cache_key[:8]}...")
                return cache[cache_key]
            
            # Cache miss
            nonlocal cache_misses
            cache_misses += 1
            print(f"Cache miss. Key: {cache_key[:8]}...")
        
        # Make the API call
        print("Calling Anthropic API...")
        start_time = time.time()
        response = client.messages.create(
            model=model,
            max_tokens=500,
            messages=[{"role": "user", "content": prompt}]
        )
        api_time = time.time() - start_time
        print(f"API call took {api_time:.2f} seconds")
        
        # Get the response text
        result = response.content[0].text
        
        # Store in cache if needed
        if use_cache:
            cache_key = get_cache_key(prompt, model)
            cache[cache_key] = result
            print(f"Stored in cache with key: {cache_key[:8]}...")
        
        return result
    
    # Run tests with caching
    print("\n===== TESTING WITH CACHING ENABLED =====")
    
    # First call - should be a cache miss
    print("\nFirst call (expecting cache miss):")
    start_time = time.time()
    response1 = call_llm_with_cache(test_prompt)
    total_time1 = time.time() - start_time
    print(f"Call took {total_time1:.2f} seconds")
    print(f"Response length: {len(response1)} chars")
    
    # Second call - should be a cache hit
    print("\nSecond call (expecting cache hit):")
    start_time = time.time()
    response2 = call_llm_with_cache(test_prompt)
    total_time2 = time.time() - start_time
    print(f"Call took {total_time2:.2f} seconds")
    print(f"Response length: {len(response2)} chars")
    
    # Third call - should be a cache hit
    print("\nThird call (expecting cache hit):")
    start_time = time.time()
    response3 = call_llm_with_cache(test_prompt)
    total_time3 = time.time() - start_time
    print(f"Call took {total_time3:.2f} seconds")
    print(f"Response length: {len(response3)} chars")
    
    # Compare response times
    print("\n===== RESULTS =====")
    print(f"First call (cache miss): {total_time1:.2f} seconds")
    print(f"Second call (cache hit): {total_time2:.2f} seconds")
    print(f"Third call (cache hit): {total_time3:.2f} seconds")
    print(f"Speed improvement: {total_time1/total_time2:.2f}x faster with cache")
    print(f"Cache hits: {cache_hits}")
    print(f"Cache misses: {cache_misses}")
    
    # Test with a slightly different prompt
    print("\n===== TESTING WITH A DIFFERENT PROMPT =====")
    different_prompt = test_prompt + "\nPlease provide 3 specific examples."
    
    print("Call with different prompt (expecting cache miss):")
    start_time = time.time()
    response4 = call_llm_with_cache(different_prompt)
    total_time4 = time.time() - start_time
    print(f"Call took {total_time4:.2f} seconds")
    print(f"Response length: {len(response4)} chars")
    
    # Final cache statistics
    print("\n===== FINAL CACHE STATISTICS =====")
    print(f"Cache size: {len(cache)} entries")
    print(f"Cache hits: {cache_hits}")
    print(f"Cache misses: {cache_misses}")
    hit_rate = cache_hits / (cache_hits + cache_misses) if (cache_hits + cache_misses) > 0 else 0
    print(f"Hit rate: {hit_rate:.2f}")
    
    return 0

if __name__ == "__main__":
    exit(test_caching()) 