from setuptools import setup, find_packages
import ella_hub

install_requires = [
    'ella>=3.0.5,<4',
    'django-tastypie',
    'django-object-permissions',
    'django-jsonfield',
]

tests_require = [
    'nose',
    'coverage',
]

long_description = open('README.rst').read()

setup(
    name='Ella-Hub',
    version=ella_hub.__versionstr__,
    description='Ella Hub - Api',
    long_description=long_description,
    author='Sanoma Media Praha',
    author_email='online-dev@sanomamedia.cz',
    license='BSD',
    url='https://github.com/SanomaCZ/ella-hub',

    packages=find_packages(
        where='.',
        exclude=('doc', 'tests',)
    ),

    include_package_data=True,

    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: BSD License",
        "Operating System :: OS Independent",
        "Framework :: Django",
        "Programming Language :: Python :: 2.5",
        "Programming Language :: Python :: 2.6",
        "Programming Language :: Python :: 2.7",
        "Operating System :: OS Independent",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    install_requires=install_requires,
    dependency_links=[
        'http://github.com/toastdriven/django-tastypie/tarball/master#egg=django-tastypie'
    ],
    test_suite='tests.run_tests.run_all',
    tests_require=tests_require,
)
