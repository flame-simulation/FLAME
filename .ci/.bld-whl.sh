#!/bin/bash
set -ex

function repair_wheel {
    wheel="$1"
    if ! auditwheel show "$wheel"; then
        echo "Skipping non-platform wheel $wheel"
    else
        auditwheel repair "$wheel" --plat "$PLAT" -w /io/wheelhouse/
    fi
}

PYBIN=/opt/python/${PY_NAME}/bin
PIP=${PYBIN}/pip

yum install -y boost-devel flex bison doxygen cppcheck
${PIP} install -r /io/requirements/${PY_NAME}.txt

${PIP} wheel /io/ --no-deps -w wheelhouse

unzip wheelhouse/*.whl -d flame0
mv flame0/flame/*.so* /usr/local/lib64

for whl in wheelhouse/*$PY_MAJOR$PY_MINOR*.whl; do
    repair_wheel "$whl"
done
