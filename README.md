![Doxygen](https://github.com/zhangt58/flame/actions/workflows/gh-pages.yml/badge.svg)
![Wheels](https://github.com/zhangt58/flame/actions/workflows/build.yml/badge.svg)
![Static Badge](https://img.shields.io/badge/Python-3.6%7C3.7%7C3.8%7C3.9%7C3.10%7C3.11%7C3.12%7C3.13-blue)
![PyPI - Version](https://img.shields.io/pypi/v/flame-code)

## Installation
Install via pip: `pip install flame-code [-U]`, see [PyPI project](https://pypi.org/project/flame-code/).

The Python extension obtains the Python C API from the interpreter and does
not require a separate dynamic `libpython` library.  This supports Python
interpreters with libpython built in statically, including manylinux Python.
See the following sections for developers' guide.

## Documentation

* [C++ documentation](https://flame-simulation.github.io/FLAME)
* [Getting started](https://flame-simulation.github.io/FLAME/gettingstarted.html)
* [Python Sphinx doc](https://flame-simulation.github.io/FLAME/sphinx/)
* Report [bugs through ISSUES](https://github.com/flame-simulation/FLAME/issues)

## Development

### Pre-requisites

Needs boost headers.  Also the boost-system and boost-python libraries.
Also python and numpy headers.
The nosetests test runner is used for 'make test' if present.

```sh
apt-get install libboost-dev libboost-filesystem-dev \
 libboost-program-options-dev libboost-test-dev \
 build-essential cmake bison flex cppcheck git libhdf5-dev \
 python-numpy python-nose python3-numpy python3-nose
```
Supports Python 3.6+. Windows wheels are built for CPython 3.11 through 3.13.

### Building

```sh
git clone https://github.com/flame-simulation/FLAME.git flame
mkdir flame/build
cd flame/build
cmake ..
make
```

To build with a specific python version, change the cmake invokation to:

```sh
cmake .. -DPython3_EXECUTABLE=/usr/bin/python3.11
```

### Windows x64

Use a native x64 Developer PowerShell for Visual Studio 2022. Install CMake,
Git, Python 3.11 or newer, WinFlexBison, and
[vcpkg](https://learn.microsoft.com/en-us/vcpkg/get_started/get-started), then
set `VCPKG_ROOT` to the vcpkg directory. The `x64-windows-static-md` triplet
links FLAME and Boost statically while retaining the dynamic MSVC runtime used
by CPython.

```powershell
choco install winflexbison3 --yes
& "$env:VCPKG_ROOT/vcpkg.exe" install --triplet x64-windows-static-md

cmake -S . -B build-win64 -A x64 `
  -DCMAKE_TOOLCHAIN_FILE="$env:VCPKG_ROOT/scripts/buildsystems/vcpkg.cmake" `
  -DVCPKG_TARGET_TRIPLET=x64-windows-static-md `
  -DPython3_EXECUTABLE="$(Get-Command python | Select-Object -ExpandProperty Source)" `
  -DUSE_PYTHON=ON -DUSE_HDF5=OFF -DUSE_EPICS=OFF

cmake --build build-win64 --config Release --parallel
build-win64/tools/Release/flame.exe --help
```

To produce a Windows x64 wheel for the active CPython interpreter:

```powershell
$env:CMAKE_ARGS = "-DCMAKE_TOOLCHAIN_FILE=$env:VCPKG_ROOT/scripts/buildsystems/vcpkg.cmake -DVCPKG_TARGET_TRIPLET=x64-windows-static-md"
python -m pip install build
python -m build --wheel
python -m pip install (Get-ChildItem dist/flame_code-*.whl)
python -c "import flame; print(flame.__version__)"
```

### Running tests

```sh
make test
```

Please attach ```Testing/Temporary/LastTest.log``` when reporting test failures.
