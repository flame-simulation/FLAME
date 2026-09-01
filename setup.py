import os
import sys
import shutil
import pathlib
import sysconfig
import shlex

from setuptools import setup, Extension
from setuptools.command.build_ext import build_ext as build_ext_orig


class CMakeExtension(Extension):
    def __init__(self, name):
        super().__init__(name, sources=[])


class build_ext(build_ext_orig):

    def run(self):
        for ext in self.extensions:
            self.build_cmake(ext)

    def build_cmake(self, ext):
        source_dir = pathlib.Path(__file__).resolve().parent
        build_temp = pathlib.Path(self.build_temp).resolve()
        build_temp.mkdir(parents=True, exist_ok=True)
        extpath = pathlib.Path(self.get_ext_fullpath(ext.name)).resolve()
        extdir = extpath.parent
        extdir.mkdir(parents=True, exist_ok=True)
        config = 'Debug' if self.debug else 'Release'
        pyexe = pathlib.Path(sys.executable).resolve()
        cmake = shutil.which('cmake')
        if not cmake:
            raise RuntimeError('CMake 3.18 or newer is required')

        cmake_args = [
            '-DCMAKE_LIBRARY_OUTPUT_DIRECTORY=' + str(extdir),
            '-DCMAKE_RUNTIME_OUTPUT_DIRECTORY=' + str(extdir),
            '-DCMAKE_LIBRARY_OUTPUT_DIRECTORY_' + config.upper() + '=' + str(extdir),
            '-DCMAKE_RUNTIME_OUTPUT_DIRECTORY_' + config.upper() + '=' + str(extdir),
            '-DCMAKE_BUILD_TYPE=' + config,
            '-DPython3_EXECUTABLE=' + str(pyexe),
            '-DFLAME_PYTHON_EXTENSION_SUFFIX=' + (sysconfig.get_config_var('EXT_SUFFIX') or extpath.suffix),
            '-DBUILD_TESTING=OFF',
            '-DUSE_PYTHON=ON',
            '-DNEED_PYTHON=ON',
            '-DNEED_DEMOIOC=OFF',
            '-DUSE_EPICS=OFF',
            '-DNEED_EPICS=OFF',
            '-DUSE_HDF5=OFF',
        ]
        cmake_args.extend(shlex.split(os.environ.get('CMAKE_ARGS', '')))
        build_args = [
            '--config', config,
            '--target', '_internal',
            '--parallel', os.environ.get('CMAKE_BUILD_PARALLEL_LEVEL', '4'),
        ]
        self.spawn([cmake, '-S', str(source_dir), '-B', str(build_temp)] + cmake_args)
        if not self.dry_run:
            self.spawn([cmake, '--build', str(build_temp)] + build_args)

        if not extpath.exists():
            raise RuntimeError('CMake did not produce the expected extension: ' + str(extpath))


setup(
    name='flame-code',
    version='1.9.3',
    package_dir={'flame': 'python/flame'},
    packages=['flame'],
    ext_modules=[CMakeExtension('flame._internal')],
    cmdclass={
        'build_ext': build_ext,
    },
    install_requires = [
        'numpy>=1.23.5',
    ],
    python_requires='>=3.11',
)
