#!/usr/bin/env python
import os

from setuptools import setup, find_packages

with open(os.path.join(os.path.dirname(__file__), 'README.md')) as f:
    long_description = f.read()

setup(
    name='optimize-later',
    version='0.3',
    description='Mark potentially slow blocks for notifications when it actually turns out too slow, '
                'so you can optimize it.',
    long_description=long_description,
    long_description_content_type='text/markdown',
    author='Quantum',
    author_email='quantum@dmoj.ca',
    url='https://github.com/quantum5/optimize-later',
    keywords='optimize profiler speed',
    packages=find_packages(),
    include_package_data=True,
    license='MIT',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Web Environment',
        'Framework :: Django',
        'Framework :: Django :: 1.11',
        'Framework :: Django :: 2.0',
        'Framework :: Django :: 2.1',
        'Framework :: Django :: 2.2',
        'Framework :: Django :: 3.0',
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3 :: Only',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Software Development',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
    zip_safe=False,
)
