#!/bin/bash
set -ex

PYBIN=/opt/python/${PY_NAME}/bin
PIP=${PYBIN}/pip

yum install -y boost-devel flex bison doxygen cppcheck graphviz
${PIP} install -r /io/requirements/${PY_NAME}.txt

cmake /io -DPYTHON_EXECUTABLE=/opt/python/${PY_NAME}/bin/python
cmake --build . --target doc

mv documentation /io/doc-built
mv /io/sphinx_doc/_build/html /io/doc-built/pyapi/

