#!/usr/bin/env python3
"""Install the LaunchAgent plist for this checkout and user."""
import argparse
from pathlib import Path
import plistlib
from tempfile import TemporaryDirectory


def install(destination: Path, project: Path, home: Path) -> None:
    template = Path(__file__).with_name("com.vladilen.brain-sync.plist")
    with template.open("rb") as file:
        agent = plistlib.load(file)
    agent["Label"] = destination.stem
    agent["ProgramArguments"][0] = str(project / "bin" / "brain")
    log = str(home / "Library" / "Logs" / "brain-sync.log")
    agent["StandardOutPath"] = log
    agent["StandardErrorPath"] = log

    with TemporaryDirectory(dir=destination.parent) as directory:
        staged = Path(directory) / destination.name
        staged.write_bytes(plistlib.dumps(agent, sort_keys=False))
        staged.replace(destination)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("destination", type=Path, help="installed plist named <LaunchAgent label>.plist")
    args = parser.parse_args()
    install(args.destination, Path(__file__).resolve().parents[1], Path.home())
