import sys
import os
from setuptools import setup, find_packages
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

classifiers = [
    'License :: OSI Approved :: MIT License',
    'Programming Language :: Python :: 3.7'
]

install_requires = ['pytest']

entry_points = {
    'pytest11': [
        'terra_fixt = terra_fixt'
    ]
}
if __name__ == '__main__':
    kwargs = dict(
        name='pytest-terra-fixt',
        description='Terraform fixtures for pytest',
        platforms=['unix', 'linux'],
        author='Marshall Mamiya',
        classifiers=classifiers,
        install_requires=install_requires,
        py_modules=['pytest_terra_fixt'],
        entry_points=entry_points,
        packages=find_packages()
    )
    kwargs.update()
    setup(**kwargs)