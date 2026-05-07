"""
Assignment 08 — Prompt Structuring Basics Solution
Task: Create a well-structured prompt for content generation
"""

import sys
from pathlib import Path

# allow importing from project root
sys.path.append(str(Path(__file__).resolve().parent.parent.parent))

from helper import get_completion

prompt = """
# TASK
Write a blog post about the benefits of remote work.

# CONTEXT
- Target audience: HR managers and business leaders
- Company: TechCorp (fictitious tech company)
- Purpose: To convince leadership to adopt hybrid work policy

# REQUIREMENTS
- Length: 500-600 words
- Include 3 main benefits with specific examples
- Professional but engaging tone
- Include a call-to-action at the end

# STRUCTURE
1. Engaging introduction
2. Benefit 1: Increased productivity with data
3. Benefit 2: Cost savings with calculations
4. Benefit 3: Talent attraction with statistics
5. Conclusion with CTA

# CONSTRAINTS
- Avoid overly technical jargon
- Focus on business outcomes
- Include at least one statistic from a reputable source
"""

response = get_completion(prompt)

print("Structured Prompt:")
print("-" * 50)
print(prompt)

print("\nResponse:")
print("-" * 50)
print(response)
