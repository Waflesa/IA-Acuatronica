import os
import subprocess
import sys
import tempfile

ROOT = os.path.dirname(os.path.abspath(__file__))
HOB = os.path.join(tempfile.gettempdir(), "h2ob")


def main():
    os.chdir(ROOT)
    work = os.path.join(HOB, "build")
    dist = os.path.join(HOB, "dist")

    data = [
        ("resources", "resources"),
        ("styles_dark.qss", "."),
        ("styles_light.qss", "."),
        ("logo.ico", "."),
    ]

    args = [
        sys.executable, "-m", "PyInstaller",
        "--noconfirm",
        "--distpath", dist,
        "--workpath", work,
        "--windowed",
        "--name", "H2-OBSERVER",
        "--icon", "logo.ico",
    ]
    for src, dst in data:
        args += ["--add-data", f"{src}{os.pathsep}{dst}"]
    args += ["main.py"]

    subprocess.check_call(args)
    out = os.path.join(dist, "H2-OBSERVER")
    print(f"\nPyInstaller OK -> {out}")


if __name__ == "__main__":
    main()
