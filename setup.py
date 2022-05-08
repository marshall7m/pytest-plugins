import sys
import os
from setuptools import setup, find_packages
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

classifiers = [
    'License :: OSI Approved :: MIT License',
    'Programming Language :: Python :: 3.7',
    "Framework :: Pytest"
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
        version='0.1.0',
        platforms=['unix', 'linux'],
        author='Marshall Mamiya',
        url='https://github.com/marshall7m/pytest-terra-fixt',
        classifiers=classifiers,
        install_requires=install_requires,
        entry_points=entry_points,
        py_modules=['terra_fixt']
    )
    kwargs.update()
    setup(**kwargs)