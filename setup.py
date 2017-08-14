#!/usr/bin/env python

from setuptools import setup, find_packages

setup(
    name='optimize-later',
    version='0.1.1',
    description='Mark potentially slow blocks for notifications when it actually turns out too slow, '
                'so you can optimize it.',
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
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Software Development',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
    zip_safe=False,
)
