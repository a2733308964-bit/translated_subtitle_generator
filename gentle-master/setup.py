from setuptools import setup
from gentle import __version__

setup(
    name='gentle',
    version=__version__,
    description='Robust yet lenient forced-aligner built on Kaldi.',
    url='http://lowerquality.com/gentle',
    author='Robert M Ochshorn',
    license='MIT',
    packages=['gentle'],
    install_requires=['twisted'],
    # 移除 app 和 test_suite 兼容新 setuptools
    # data_files 和 options 可以在使用 py2app 时再单独配置
)
