"""
Assignment 06 — Zero-shot Chain-of-Thought Prompting Solution
Task: Solve a logic problem using step-by-step thinking without examples
"""

import sys
from pathlib import Path

# allow importing from project root
sys.path.append(str(Path(__file__).resolve().parent.parent.parent))

from helper import get_completion

prompt = """
A store is having a sale. If you buy 2 shirts, you get 1 free. Each shirt normally costs $25. If you buy 6 shirts during this sale, how much money do you save compared to buying 6 shirts at the regular price?

Think step by step to solve this problem.
"""

response = get_completion(prompt)

print("Prompt:")
print("-" * 50)
print(prompt)

print("\nResponse:")
print("-" * 50)
print(response)
