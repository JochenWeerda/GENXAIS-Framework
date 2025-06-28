# Cursor Rules for GENXAIS Framework

This directory contains the rules for the different modes of the GENXAIS Framework.

## Modes

The GENXAIS Framework supports the following modes:

1. **VAN Mode** (Vision, Analysis, Navigation)
   - Understanding requirements
   - Analyzing context
   - Asking clarifying questions

2. **PLAN Mode** (Project Planning)
   - Project planning
   - Solution concept
   - Task distribution
   - Next steps

3. **CREATE Mode** (Code Generation)
   - Code generation
   - Resource provisioning
   - Design patterns
   - Architecture principles
   - Tests

4. **IMPLEMENT Mode** (Implementation)
   - Integration
   - Deployment
   - Documentation
   - Validation

5. **REFLECT Mode** (Reflection)
   - Reflection on the process
   - Documentation of lessons learned
   - Knowledge transfer

6. **ARCHIVE** (Archiving)
   - Archiving the current state
   - Creating a snapshot

## Mode Commands

To switch between modes, use the following commands in the command line:

```bash
python scripts/mode_commands.py VAN-mode
python scripts/mode_commands.py PLAN-mode
python scripts/mode_commands.py CREATE-mode
python scripts/mode_commands.py IMPLEMENT-mode
python scripts/mode_commands.py REFLECT-mode
python scripts/mode_commands.py ARCHIVE NOW
```

These commands will activate the corresponding mode and load the appropriate rules.

## Mode Rules

Each mode has its own set of rules that define how the AI assistant should behave in that mode. The rules are stored in JSON files in this directory.

- `van_mode_rules.json`: Rules for the VAN mode
- `plan_mode_rules.json`: Rules for the PLAN mode
- `creative_mode_rules.json`: Rules for the CREATE mode
- `implement_mode_rules.json`: Rules for the IMPLEMENT mode
- `reflect_archive_rules.json`: Rules for the REFLECT and ARCHIVE modes

## SDK Integration

The mode commands are integrated with the GENXAIS SDK. When you run a mode command, it will:

1. Initialize the GENXAIS Framework
2. Set the current mode
3. Load the appropriate rules
4. Update the current mode in the `.genxais/current_mode.txt` file

You can also programmatically switch modes using the SDK:

```python
from genxais_sdk import GENXAISFramework

framework = GENXAISFramework()
framework.set_mode("VAN")  # Switch to VAN mode
current_mode = framework.get_mode()  # Get the current mode
```

## Custom Rules

You can create custom rules for your project by creating new JSON files in this directory. The rules should follow the same structure as the existing rules.

## Integration with the Memory Bank

The rules are closely integrated with the project's memory bank structure:

`
memory-bank/
   activeContext.md           # Active context
   validation/                # VAN mode documents
      validation-template.md # Template for validation reports
   planning/                  # PLAN mode documents
      implementation-plan-template.md # Template for implementation plans
   creative/                  # CREATE mode documents
   handover/                  # Handover documents
      handover-template.md   # Template for handover documents
      handover-history/      # Historical handover documents
   reflection/                # REFLECT mode documents
   archive/                   # Archived documents
`

## Handover Protocol

The handover protocol enables seamless transitions between different work sessions or agents:

1. The departing agent creates a handover document based on handover-template.md
2. The document is saved in memory-bank/handover/
3. A copy is archived in memory-bank/handover/handover-history/
4. The receiving agent can read the handover document to understand the context

## Customizing the Rules

The rules can be customized as needed to meet specific project requirements. Follow these guidelines:

1. Maintain the basic structure of the modes
2. Ensure that new rules are compatible with the memory bank structure
3. Document all changes in this README file

## Further Information

For more information about the APM Framework and its concepts, see:
- The project documentation in the docs/ directory
- docs/handover_system.md for details on the handover system
- docs/architecture/development_flow.md for the development flow in the project
