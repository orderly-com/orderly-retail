import os
from setuptools import setup, find_packages

setup(
    name='retail-ext',
    version='1.0.0',
    url='https://github.com/orderly-com/retail-ext',
    license='BSD',
    description='Orderly extension for retail industry',
    author='RayYang',
    author_email='ray.yang@ezorderly.com',

    packages=find_packages('src'),
    package_dir={'': 'src'},

    install_requires=['setuptools', 'requests', 'django'],

    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3.5',
        'Topic :: Internet :: WWW/HTTP',
    ]
)