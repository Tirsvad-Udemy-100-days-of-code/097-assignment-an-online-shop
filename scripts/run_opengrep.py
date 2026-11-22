"""@brief Run opengrep over src and tests; fail on any error-severity finding.

Run it before every push. It uses the rules in .opengrep/rules.yml and the
opengrep binary of the current user. It needs no network access.
"""

import subprocess
import sys
from pathlib import Path

DEFAULT_BINARY = Path.home() / ".opengrep" / "cli" / "latest" / "opengrep.exe"
RULES = Path(".opengrep") / "rules.yml"
TARGETS = ("src", "tests", "scripts", "tools")


def main() -> int:
    """@brief Run the scan.

    @return The exit code: 0 for no finding, 1 for findings, 2 when opengrep is missing.
    """
    binary = DEFAULT_BINARY
    if not binary.exists():
        print(f"opengrep not found at {binary}", file=sys.stderr)
        return 2
    targets = [target for target in TARGETS if Path(target).exists()]
    command = [
        str(binary),
        "scan",
        "--config",
        str(RULES),
        "--severity",
        "ERROR",
        "--error",
        "--disable-version-check",
        *targets,
    ]
    # The command holds only fixed paths and options, no user input.
    return subprocess.run(command, check=False).returncode  # nosemgrep


if __name__ == "__main__":
    sys.exit(main())
