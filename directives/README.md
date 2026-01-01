# Directives Directory

This directory contains natural language SOPs (Standard Operating Procedures) that define what the agent should do.

## Directive Format

Each directive should include:

### 1. Goal
What is this directive trying to accomplish?

### 2. Inputs
What information/data does this need to work?
- Parameter 1: Description
- Parameter 2: Description

### 3. Tools/Scripts
Which execution scripts should be used?
- `execution/script_name.py` - What it does

### 4. Outputs
What should this produce?
- Deliverable 1: Description
- Deliverable 2: Description

### 5. Edge Cases
What could go wrong and how to handle it?
- Edge case 1: Solution
- Edge case 2: Solution

## Example Directive Template

```markdown
# Directive Name

## Goal
Clear statement of what this accomplishes

## Inputs
- input_1: Description
- input_2: Description

## Tools/Scripts
- execution/tool_name.py: What it does

## Outputs
- Cloud deliverable (Google Sheet/Slides)
- Any temporary files in .tmp/

## Edge Cases
- What if X happens? Do Y
- What if Z happens? Do A

## Notes
- Any additional context
- API limits or constraints
- Timing expectations
```

## Best Practices

1. Be specific about inputs and outputs
2. Document API constraints and limits
3. Update directives as you learn
4. Reference specific execution scripts
5. Include error handling instructions
