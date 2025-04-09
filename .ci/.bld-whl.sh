#!/bin/bash
set -ex

# Fix yum repo: CentOS 7
# https://www.veeble.com/kb/centos-repo-list-working-urls/
rm -rf /etc/yum.repos.d/*
cat << EOF > /etc/yum.repos.d/CentOS-Base.repo
[base]
name=CentOS-$releasever - Base
baseurl=https://vault.centos.org/7.9.2009/os/$basearch/
gpgcheck=1
gpgkey=file:///etc/pki/rpm-gpg/RPM-GPG-KEY-CentOS-7
enabled=1

[updates]
name=CentOS-$releasever - Updates
baseurl=https://vault.centos.org/7.9.2009/updates/$basearch/
gpgcheck=1
gpgkey=file:///etc/pki/rpm-gpg/RPM-GPG-KEY-CentOS-7
enabled=1

[extras]
name=CentOS-$releasever - Extras
baseurl=https://vault.centos.org/7.9.2009/extras/$basearch/
gpgcheck=1
gpgkey=file:///etc/pki/rpm-gpg/RPM-GPG-KEY-CentOS-7
enabled=1

[centosplus]
name=CentOS-$releasever - CentOSPlus
baseurl=https://vault.centos.org/7.9.2009/centosplus/$basearch/
gpgcheck=1
gpgkey=file:///etc/pki/rpm-gpg/RPM-GPG-KEY-CentOS-7
enabled=0
EOF

cat /etc/yum.repos.d/CentOS-Base.repo

yum clean all
yum makecache


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
