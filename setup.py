import os
import sys
import shutil
import pathlib
import subprocess
import sysconfig
import shlex

from setuptools import setup, Extension
from setuptools.command.build_ext import build_ext as build_ext_orig


class CMakeExtension(Extension):
    def __init__(self, name):
        super().__init__(name, sources=[])


class build_ext(build_ext_orig):

    def run(self):
        if os.name != 'nt':
            for ext in self.extensions:
                self.build_cmake_unix(ext)
            super().run()
            return

        for ext in self.extensions:
            self.build_cmake_windows(ext)

    def build_cmake_unix(self, ext):
        cwd = pathlib.Path().absolute()
        build_temp = pathlib.Path(self.build_temp)
        build_temp.mkdir(parents=True, exist_ok=True)
        extdir = pathlib.Path(self.get_ext_fullpath(ext.name))
        extdir.mkdir(parents=True, exist_ok=True)
        libpath = extdir.parent.joinpath("flame").absolute()
        config = 'Debug' if self.debug else 'Release'
        cmake = shutil.which('cmake')
        cmake_args = [
            '-DCMAKE_LIBRARY_OUTPUT_DIRECTORY=' + str(libpath),
            '-DCMAKE_BUILD_TYPE=' + config,
            '-DPYTHON_EXECUTABLE=' + sys.executable,
            '-DNEED_PYTHON=ON',
            '-DNEED_DEMOIOC=OFF',
            '-DNEED_EPICS=OFF',
            '-DUSE_HDF5=OFF',
            '-DDEF_PATH=/etc/flame/cavity_data',
        ]
        build_args = [
            '--config', config,
            '--', '-j4',
        ]
        os.chdir(str(build_temp))
        try:
            self.spawn([cmake, str(cwd)] + cmake_args)
            env = os.environ.copy()
            env['LD_LIBRARY_PATH'] = env.get('LD_LIBRARY_PATH', '') + ':' + str(libpath)
            if not self.dry_run:
                self.spawn([cmake, '--build', '.'] + build_args)
                subprocess.run([shutil.which('ctest'), '--output-on-failure'], env=env)
        finally:
            os.chdir(str(cwd))

    def build_cmake_windows(self, ext):
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


setup_options = {}
if os.name == 'nt':
    setup_options['python_requires'] = '>=3.11'


setup(
    name='flame-code',
    version='1.9.3',
    package_dir={'flame': 'python/flame'},
    packages=['flame'],
    ext_modules=[CMakeExtension(
        'flame._internal' if os.name == 'nt' else 'flame_core'
    )],
    cmdclass={
        'build_ext': build_ext,
    },
    install_requires = [
        'numpy>1.21',
    ],
    **setup_options
)
