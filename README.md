![Doxygen](https://github.com/zhangt58/flame/actions/workflows/gh-pages.yml/badge.svg)
![Wheels](https://github.com/zhangt58/flame/actions/workflows/build.yml/badge.svg)
![Static Badge](https://img.shields.io/badge/Python-3.6%7C3.7%7C3.8%7C3.9%7C3.10%7C3.11%7C3.12-blue)
![PyPI - Version](https://img.shields.io/pypi/v/flame-code)

## Installation
Install via pip: `pip install flame-code [-U]`, see [PyPI project](https://pypi.org/project/flame-code/).

The dynamic library of Python `libpython3.so` is required,
- Install `libpython<python-version>` on Debian (and its derivatives, e.g. `libpython3.11`)
- Or, `python<python-version>-libs` on RPM-based OS, e.g. `python3.11-libs`.
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
apt-get install libboost-dev libboost-system-dev \
 libboost-thread-dev libboost-filesystem-dev \
 libboost-regex-dev libboost-program-options-dev \
 libboost-test-dev \
 build-essential cmake bison flex cppcheck git libhdf5-dev \
 python-numpy python-nose python3-numpy python3-nose
```
Supports Python 3.6+

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
cmake .. -DPYTHON_EXECUTABLE=/usr/bin/python3.11
```

### Running tests

```sh
make test
```

Please attach ```Testing/Temporary/LastTest.log``` when reporting test failures.
