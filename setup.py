# -*- coding: utf-8 -*-
from setuptools import find_packages, setup


setup(
    name='wagtail_video',
    version='1.0.1',
    packages=find_packages(),
    include_package_data=True,
    license='BSD License',
    description='Wagtail images but for video.',
    long_description='',
    url='https://github.com/l1f7/wagtail_video',
    author='Lift Interactive',
    author_email='dev@liftinteractive.com',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Framework :: Django',
        'Framework :: Django :: 1.8',
        'Framework :: Django :: 1.9',
        'Topic :: Internet :: WWW/HTTP :: Site Management',
    ],
    install_requires=[
        'wagtail>=2.7',
        'Django>=2.1'
    ]
)
