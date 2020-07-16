import os
import pathlib

from setuptools import setup, Extension
from setuptools.command.build_ext import build_ext as build_ext_orig

class CMakeExtension(Extension):
    def __init__(self, name):
        super().__init__(name, sources=[])


class build_ext(build_ext_orig):

    def run(self):
        for ext in self.extensions:
            self.build_cmake(ext)
        super().run()

    def build_cmake(self, ext):
        cwd = pathlib.Path().absolute()
        build_temp = pathlib.Path(self.build_temp)
        build_temp.mkdir(parents=True, exist_ok=True)
        extdir = pathlib.Path(self.get_ext_fullpath(ext.name))
        extdir.mkdir(parents=True, exist_ok=True)
        libpath = extdir.parent.joinpath("flame").absolute()
        config = 'Debug' if self.debug else 'Release'
        pyexe = '/opt/rh/rh-python38/root/usr/bin/python3.8'
        cmake = '/opt/rh/rh-python38/root/usr/local/bin/cmake'
        cmake_args = [
            '-DCMAKE_LIBRARY_OUTPUT_DIRECTORY=' + str(libpath),
            '-DCMAKE_BUILD_TYPE=' + config,
            '-DPYTHON_EXECUTABLE=' + pyexe,
            '-DNEED_PYTHON=ON',
            '-DNEED_DEMOIOC=OFF',
            '-DNEED_EPICS=OFF',
            '-DUSE_HDF5=OFF',
            '-DDEF_PATH=/etc/flame/cavity_data',
        ]
        build_args = [
            "--config", config,
            "--", '-j4'
        ]
        os.chdir(str(build_temp))
        self.spawn([cmake, str(cwd)] + cmake_args)
        if not self.dry_run:
            self.spawn([cmake, '--build', '.'] + build_args)
        os.chdir(str(cwd))


setup(
    name='flame',
    version='1.8.6',
    package_dir={'flame': 'python/flame'},
    packages=['flame'],
    ext_modules=[CMakeExtension('flame_core')],
    cmdclass={
        'build_ext': build_ext,
    }
)
