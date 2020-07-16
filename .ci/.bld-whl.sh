#!/bin/bash
set -e -x

function repair_wheel {
    wheel="$1"
    if ! auditwheel show "$wheel"; then
        echo "Skipping non-platform wheel $wheel"
    else
        auditwheel repair "$wheel" --plat "$PLAT" -w /io/wheelhouse/
    fi
}

yum install -y rh-python38-python-devel \
            rh-python38-python-pip \
            boost-devel flex bison doxygen
. /opt/rh/rh-python38/enable
pip3.8 install cmake numpy nose wheel
python_exe=`which python3.8`
cmake_exe=`which cmake`
pip3.8 wheel /io/ --no-deps -w wheelhouse/
unzip wheelhouse/*.whl -d flame0
mv flame0/flame/*.so* /usr/lib

for whl in wheelhouse/*.whl; do
    repair_wheel "$whl"
done
