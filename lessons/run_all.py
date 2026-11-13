"""Run every lesson in order (01 -> 07)."""
import runpy
import sys
from pathlib import Path

here = Path(__file__).parent
sys.path.insert(0, str(here))
for lesson in sorted(here.glob("0*.py")):
    print(f"\n\n######## {lesson.name} ########")
    runpy.run_path(str(lesson), run_name="__main__")
