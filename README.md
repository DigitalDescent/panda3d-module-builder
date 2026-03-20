Panda3D Module Builder
===========================

<img src="https://avatars2.githubusercontent.com/u/590956?v=3&s=500" align="right" width="200" />

This tool allows you to seamlessly mix your C++ and Python code for the 
<a href="http://github.com/panda3d/panda3d">Panda3D Game Engine</a>.

It generates Python bindings for your C++ code and packages the result as an installable Python wheel.


### Features
 - Automatic Python bindings using `interrogate`
 - Builds as a standard Python wheel via `pip` / `python -m build`
 - Works on Windows, Linux and Mac
 - Python 10 – 3.14

## Getting started


#### 1. Clone this repository

You can use the download-zip button, or clone this repository. 

Typically it is recommended you create a new repository using this one as the template.
This ensures you immediately have access to the CI workflows for automating your wheel builds and publishing to pypi.

#### 2. Configure `config.ini`

Set `module_name` to the name you want for your module (e.g. `TestModule`).
You can also set a `description`.

#### 3. Write your source code

You can now start to write your C++ code and store it in the `source/` directory.
Here's a simple example you can start with (save it as `source/example.h` for example):

```cpp
#ifndef EXAMPLE_H
#define EXAMPLE_H

#include "pandabase.h"


BEGIN_PUBLISH // This exposes all functions in this block to python

inline int multiply(int a, int b) {
    return a * b;
}

END_PUBLISH


class ExampleClass {
    PUBLISHED: // Exposes all functions in this scope, use instead of "public:"
        inline int get_answer() {
            return 42;
        };
};


#endif EXAMPLE_H
```

#### 4. Build the module

Build and install directly into your environment:

```bash
pip install .
```

Or build a distributable wheel:

```bash
pip install build
python -m build --wheel
```

The wheel will be placed in the `dist/` directory.

#### 5. Use your module

Using your compiled module is straightforward:

```python
import panda3d.core  # Make sure you import this first before importing your module

import TestModule

print(TestModule.multiply(3, 4)) # prints 12

example = TestModule.ExampleClass()
print(example.get_answer()) # prints 42

```


## Requirements

- Python 3.10+
- The [Panda3D](https://www.panda3d.org/) SDK (not the pip package — the SDK headers are needed for compilation)
- [CMake](https://cmake.org/download/) 3.16 or higher
- A C++ compiler matching your Panda3D build:

| Platform | Compiler |
|---|---|
| Windows | Visual Studio 2015 – 2022 (must match the Panda3D SDK) |
| Linux | GCC / Clang |
| macOS | Xcode / Clang |


## Advanced configuration

**After changing the configuration, delete the build output directory so that
CMake picks up the new settings on the next build.**

### config.ini

All build options are set in `config.ini`:

- `module_name` — Name of the compiled module (required).
- `description` — Short description included in the wheel metadata.
- `optimize` — Optimization level (default `3`). Should match the `--optimize=` level your Panda3D was built with.
- `generate_pdb` — Set to `1` to generate a `.pdb` debug-info file (Windows only).
- `require_lib_eigen` — Set to `1` to require the Eigen 3 library.
- `require_lib_bullet` — Set to `1` to require the Bullet physics library.
- `require_lib_freetype` — Set to `1` to require the FreeType library.
- `verbose_igate` — Set to `1` or `2` for detailed interrogate output (1 = verbose, 2 = very verbose).

### Additional libaries

If you want to include additional (external) libraries, you can create a
cmake file named `additional_libs.cmake` in the folder of the module builder,
which will then get included during the build.

If you would like to include the protobuf library for example, your cmake file could look like this:

```cmake
find_package(Protobuf REQUIRED)
include_directories(${PROTOBUF_INCLUDE_DIRS})
set(LIBRARIES "${LIBRARIES};${PROTOBUF_LIBRARIES}")

```

## License

This project is licensed under the [MIT License](LICENSE).