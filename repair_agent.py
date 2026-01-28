"""
Repair Agent — Claude-Powered Code Fixer

This module uses Claude to generate repair patches
that conform to repair_schema.py format.
"""

import os
import json
from anthropic import Anthropic
from repair_schema import validate_patch


# Initialize Claude client
client = Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))


def build_repair_prompt(code: str, failures: str, profile: str) -> str:
    """Build the repair agent prompt."""
    return f"""You are a precise code repair agent. Your job is to fix ONLY the specific failures provided.

CRITICAL RULES:
1. Generate ONLY valid JSON - no markdown, no explanations, no preamble
2. Fix ONLY the failures listed - do not refactor or improve other code
3. Make MINIMAL edits - change only what's necessary
4. Preserve all original formatting, indentation, and style except for the specific fix
5. Each patch must have: line, old, new, reason, category, blocking

OUTPUT FORMAT (JSON only):
{{
  "patches": [
    {{
      "line": <line_number>,
      "old": "<exact original line>",
      "new": "<fixed line>",
      "reason": "<why this fix is needed>",
      "category": "<spacing|docstring|naming|style>",
      "blocking": <true|false>
    }}
  ]
}}

CODE TO FIX:
```python
{code}
```

FAILURES TO ADDRESS:
{failures}

PROFILE: {profile}

Generate repair patches as JSON only. No other text."""


def generate_repairs(
    code: str,
    failures: list,
    profile: str = "strict"
) -> list[dict]:
    """
    Use Claude to generate repair patches for code failures.
    
    Args:
        code: Original Python code
        failures: List of failure descriptions from judge
        profile: Strictness level
    
    Returns:
        List of RepairPatch dictionaries
    """
    
    if not failures:
        return []
    
    # Format failures as numbered list
    failures_text = "\n".join(f"{i+1}. {f}" for i, f in enumerate(failures))
    
    # Build prompt
    prompt = build_repair_prompt(code, failures_text, profile)
    
    # Call Claude
    try:
        message = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=4000,
            messages=[{
                "role": "user",
                "content": prompt
            }]
        )
        
        # Extract response
        response_text = message.content[0].text.strip()
        
        # Remove markdown code blocks if present
        if response_text.startswith("```"):
            lines = response_text.split('\n')
            response_text = '\n'.join(lines[1:-1])
        
        # Parse JSON
        result = json.loads(response_text)
        patches = result.get("patches", [])
        
        # Validate all patches
        valid_patches = []
        for patch in patches:
            if validate_patch(patch):
                valid_patches.append(patch)
            else:
                print(f"WARNING: Invalid patch skipped: {patch}")
        
        return valid_patches
        
    except json.JSONDecodeError as e:
        print(f"ERROR: Claude returned invalid JSON: {e}")
        print(f"Response was: {response_text[:500]}")
        return []
    except Exception as e:
        print(f"ERROR: Failed to generate repairs: {e}")
        return []


# Test function
if __name__ == "__main__":
    test_code = """def add(x,y):
    return x+y

result=add(1,2)
print(result)"""
    
    test_failures = [
        "Line 1: Missing space after comma in function parameters",
        "Line 4: Missing spaces around assignment operator"
    ]
    
    print("Generating repairs...")
    patches = generate_repairs(test_code, test_failures, "strict")
    
    print(f"\nGenerated {len(patches)} patches:")
    for patch in patches:
        print(json.dumps(patch, indent=2))
