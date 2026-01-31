# Deprecated Code Archive

This directory contains code that has been archived during the codebase cleanup on January 31, 2026.

## Contents

### clinical-ops-rt/
The original clinical operations runtime package (29 files). This was an early attempt at building a clinical operations system but was never integrated with the main Streamlit application. All functionality has been consolidated into the `src/` directory.

**Reason for archival**: Zero imports from main application, completely unused.

### fix_dataframe.py
A standalone utility script for DataFrame fixes.

**Reason for archival**: One-time utility script, not part of core application.

## Restoration

If you need to restore any of these files:
```powershell
# Example: Restore clinical-ops-rt
Move-Item deprecated\clinical-ops-rt clinical-ops-rt
```

## Safe to Delete?

Yes, after verifying the application works correctly without these files, this entire directory can be safely deleted.
