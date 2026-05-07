"""
Assignment 05 — Chain-of-Thought Prompting Solution
Task: Solve a word problem using step-by-step reasoning
"""

import sys
from pathlib import Path

# allow importing from project root
sys.path.append(str(Path(__file__).resolve().parent.parent.parent))

from helper import get_completion

prompt = """
Solve this problem step by step, showing your reasoning:

A company has 120 employees. 40% work in sales, 25% work in engineering, 20% work in marketing, and the rest work in administration. If the company needs to reduce the workforce by 15% and decides to lay off employees proportionally from each department, how many employees will remain in the sales department?

Think through this step by step:
1. Calculate how many employees are in each department initially
2. Calculate the total number of layoffs needed
3. Calculate how many layoffs per department
4. Calculate the remaining sales employees
"""

response = get_completion(prompt)

print("Prompt:")
print("-" * 50)
print(prompt)

print("\nResponse:")
print("-" * 50)
print(response)
