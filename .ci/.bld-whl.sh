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

function install {
    major=$1
    minor=$2
    if [[ $major$minor == "35" || $major$minor == "36" ]]; then
        yum install -y \
            rh-python${PY_MAJOR}${PY_MINOR}-numpy
    elif [[ $major$minor == "38" ]]; then
        yum install -y \
            rh-python${PY_MAJOR}${PY_MINOR}-python-numpy
    fi
}

yum install -y rh-python${PY_MAJOR}${PY_MINOR}-python-devel \
               rh-python${PY_MAJOR}${PY_MINOR}-python-pip \
               boost-devel flex bison doxygen

install ${PY_MAJOR} ${PY_MINOR}

. /opt/rh/rh-python${PY_MAJOR}${PY_MINOR}/enable

pip${PY_MAJOR}.${PY_MINOR} install pip --upgrade
pip${PY_MAJOR} install cmake wheel nose

python_exe=`which python${PY_MAJOR}.${PY_MINOR}`
cmake_exe=`which cmake`

pip${PY_MAJOR} wheel /io/ --no-deps -w wheelhouse$PLAT$PY_MAJOR_$PY_MINOR

unzip wheelhouse$PLAT$PY_MAJOR_$PY_MINOR/*.whl -d flame0
mv flame0/flame/*.so* /usr/lib

for whl in wheelhouse$PLAT$PY_MAJOR_$PY_MINOR/*.whl; do
    repair_wheel "$whl"
done
