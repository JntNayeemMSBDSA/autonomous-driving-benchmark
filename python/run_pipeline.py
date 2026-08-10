"""Execute the reproducible analytical pipeline.

Network acquisition is optional. The default run uses bundled evidence and
the verified NHTSA schema excerpt.
"""
from __future__ import annotations
import subprocess
import sys
from pathlib import Path

HERE=Path(__file__).resolve().parent
STEPS=[
    ("acquire_data.py",["--skip-downloads"]),
    ("clean_data.py",[]),
    ("analyze_incidents.py",[]),
    ("analyze_deployment.py",[]),
    ("gpu_cost_model.py",[]),
    ("scalability_model.py",[]),
    ("export_powerbi_tables.py",[]),
    ("build_database.py",[]),
    ("validate_data.py",[]),
]
def main() -> int:
    for script,args in STEPS:
        command=[sys.executable,str(HERE/script),*args]
        print(f"\n=== Running {script} ===")
        result=subprocess.run(command,cwd=HERE.parent,check=False)
        if result.returncode:
            print(f"FAILED: {script} returned {result.returncode}")
            return result.returncode
    print("\nPipeline completed successfully.")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
