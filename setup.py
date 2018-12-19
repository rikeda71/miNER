from setuptools import setup, find_packages


with open('README.md') as f:
    readme = f.read()

with open('LICENSE') as f:
    license = f.read()

setup(
    name='miNER',
    version='1.0.0',
    description='A python library for named entity recognition evaluation',
    long_description=readme,
    author='AndoLab',
    author_email='ando.laboratory@gmail.com',
    url='https://github.com/Andolab/miNER',
    license=license,
    packages=['miner'],
    python_requires='>=3.5',
    classifiers=[
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'License :: OSI Approved :: MIT License',
    ],
    test_suite='tests',
)
