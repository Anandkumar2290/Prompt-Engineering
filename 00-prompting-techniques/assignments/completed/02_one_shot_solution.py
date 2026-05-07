"""
Assignment 02 — One-shot Prompting Solution
Task: Convert informal text to professional business tone using one example
"""

import sys
from pathlib import Path

# allow importing from project root
sys.path.append(str(Path(__file__).resolve().parent.parent.parent))

from helper import get_completion

prompt = """
Convert the informal sentence into a professional business tone.

Example:
Input: hey can u send me the report asap pls
Output: Could you please send me the report at your earliest convenience?

Now do the same for:
Input: i need the meeting notes from yesterday thx
Output:
"""

response = get_completion(prompt)

print("Prompt:")
print("-" * 50)
print(prompt)

print("\nResponse:")
print("-" * 50)
print(response)
