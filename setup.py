"""
setuptools entry-point that drives the existing CMake / interrogate build
and packages the resulting extension module into a wheel.

The package name and build options are read from config.ini (module_name).
Set the SETUPTOOLS_SCM_PRETEND_VERSION environment variable to control the
wheel version (the CI workflow does this automatically).
"""

import os
import platform
import shutil
import sys
from pathlib import Path
from types import SimpleNamespace

from setuptools import Extension, setup
from setuptools.command.build_ext import build_ext


def _read_config():
    """Read the simple key=value config.ini next to this file."""
    config = {}
    config_path = Path(__file__).resolve().parent / "config.ini"
    if config_path.exists():
        for line in config_path.read_text().splitlines():
            line = line.strip()
            if line and "=" in line:
                key, value = line.split("=", 1)
                config[key.strip()] = value.strip()
    return config


_CONFIG = _read_config()
MODULE_NAME = _CONFIG.get("module_name", "p3d_module")
DESCRIPTION = _CONFIG.get("description", "Panda3D C++ extension module")

# ---------------------------------------------------------------------------
# CMake-backed extension
# ---------------------------------------------------------------------------

class CMakeExtension(Extension):
    """Marker extension — no real source list; CMake handles everything."""

    def __init__(self, name: str):
        super().__init__(name, sources=[])


class CMakeBuild(build_ext):
    """build_ext that delegates to the existing scripts/ CMake pipeline."""

    def build_extension(self, ext: Extension):
        project_dir = Path(__file__).resolve().parent

        # panda3d must be importable before we touch the scripts package.
        import panda3d.core  # noqa

        # Ensure the project root is on sys.path so the scripts package
        # resolves correctly regardless of cwd.
        root_str = str(project_dir)
        if root_str not in sys.path:
            sys.path.insert(0, root_str)

        # Change into the project directory (scripts expect it).
        orig_cwd = os.getcwd()
        os.chdir(root_str)

        try:
            from scripts.common import get_ini_conf
            from scripts.setup import make_output_dir, run_cmake, run_cmake_build

            config = get_ini_conf(str(project_dir / "config.ini"))
            args = SimpleNamespace(optimize=None, clean=False)

            make_output_dir(clean=False)
            run_cmake(config, args)
            run_cmake_build(config, args)
        finally:
            os.chdir(orig_cwd)

        # build.py / finalize.py copy the binary to the project root.
        if platform.system().lower() == "windows":
            built = project_dir / f"{ext.name}.pyd"
        else:
            built = project_dir / f"{ext.name}.so"

        if not built.exists():
            raise FileNotFoundError(
                f"Build did not produce expected binary: {built}"
            )

        # Place the binary where setuptools expects it for the wheel.
        dest = Path(self.get_ext_fullpath(ext.name))
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(str(built), str(dest))


setup(
    name=MODULE_NAME,
    version=os.environ.get("SETUPTOOLS_SCM_PRETEND_VERSION", "0.0.0"),
    description=DESCRIPTION,
    ext_modules=[CMakeExtension(MODULE_NAME)],
    cmdclass={"build_ext": CMakeBuild},
)
