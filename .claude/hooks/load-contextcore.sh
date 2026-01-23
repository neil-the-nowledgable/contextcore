#!/bin/bash
# SessionStart hook: Load ContextCore project metadata into Claude's context

CONTEXTCORE_FILE="$CLAUDE_PROJECT_DIR/.contextcore.yaml"

# Exit silently if no context file exists
if [ ! -f "$CONTEXTCORE_FILE" ]; then
  exit 0
fi

# Output context header and file contents
cat << 'HEADER'
==============================================
PROJECT CONTEXT (from .contextcore.yaml)
==============================================

HEADER

cat "$CONTEXTCORE_FILE"

cat << 'FOOTER'

==============================================
Use /project-context for detailed context query
==============================================
FOOTER

exit 0
