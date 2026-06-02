# Document Feature Implementation

Generate comprehensive documentation for a feature or code flow, suitable for newcomers.

## Input

Feature or component to document: $ARGUMENTS

## Parameters

Parse the arguments for optional flags:
- `--ascii` or `-a`: Use ASCII diagrams (simple ASCII characters, no rendering needed)
- Default: Use Mermaid diagram syntax (renders in GitHub/GitLab)

Example usage:
- `/doc-feature PricingModelResult population` (Mermaid diagrams)
- `/doc-feature --ascii PricingModelResult population` (ASCII diagrams)

## Instructions

1. **Explore the codebase** to understand the feature:
   - Find the main entry points and key functions
   - Trace the data flow from input to output
   - Identify related files, types, and dependencies
   - Look for existing tests that demonstrate usage

2. **Create documentation** in `docs/` with the following structure:

### Required Sections

#### Overview
- What the feature does (1-2 paragraphs)
- High-level transformation/process steps (numbered list)

#### Architecture
- Diagram showing the data flow or component relationships (see Diagram Style below)
- Table of key source files with their purpose
- Navigation tip with search terms to find main entry points

##### Diagram Style

**Default (Mermaid):** Use Mermaid syntax for GitHub/GitLab rendering:
```mermaid
flowchart LR
    A[Model Execution] --> B[Features Map]
    B --> C[Converter]
    C --> D[Result]
```

Rules for Mermaid diagrams:
- Use `flowchart LR` for left-to-right, `flowchart TD` for top-down
- Keep node labels concise
- Use subgraphs for grouping related components

**With `--ascii` flag:** Use simple ASCII characters for maximum compatibility:
```
+------------------+     +------------------+     +------------------+
|                  |     |                  |     |                  |
|      Model       |---->|   Features Map   |---->|     Converter    |
|    Execution     |     |  Map[String,Val] |     |                  |
|                  |     |                  |     |                  |
+------------------+     +------------------+     +------------------+
                                                          |
                                                          v
                                                  +------------------+
                                                  |      Result      |
                                                  +------------------+
```

Rules for ASCII diagrams:
- Use `+`, `-`, `|` for boxes (not Unicode box-drawing characters)
- Use `---->` for horizontal arrows, `v` for downward arrows
- Keep diagrams narrow (max 80 characters wide)
- Align right edges by counting characters carefully

#### Data Flow
- Step-by-step breakdown of how data moves through the system
- Code snippets for each step with search hints (e.g., "Search for `def functionName`")
- Example inputs/outputs at each stage

#### Key Components
- Important types, constants, and helper functions
- Tables for mappings (e.g., field mappings, enum conversions)

#### Code Examples
- 2-3 practical examples showing common usage patterns
- Include both success and error/edge cases

#### Troubleshooting
- Common issues with symptoms, causes, and solutions
- Debugging tips

#### Testing
- How to run relevant tests
- Search terms to find test files

#### Related Documentation
- Links to related docs in the project

### Formatting Guidelines

- Use GitHub-flavored markdown
- Use tables for structured data (field mappings, conversions, etc.)
- Use code blocks with `scala` syntax highlighting
- **Never use line numbers** in code references - use searchable terms instead:
  - Good: "Search for `def getMultiPricingModelResults`"
  - Bad: "See PricingModelResultConversions.scala:16-43"
- Use shortened paths in tables (e.g., `src/.../converters/` instead of full paths)
- Include navigation tips as blockquotes

### Output

Save the documentation to `docs/<feature-name>.md` where `<feature-name>` is a kebab-case version of the feature name.
