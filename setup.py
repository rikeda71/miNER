from setuptools import setup


with open('README.md', 'r', encoding='utf-8') as f:
    readme = f.read()

setup(
    name='mi-ner',
    version='0.0.2',
    description='A python library for named entity recognition evaluation',
    long_description=readme,
    long_description_content_type='text/markdown',
    author='Ryuya Ikeda',
    author_email='rikeda71@gmail.com',
    url='https://github.com/Andolab/miNER',
    license='MIT',
    keywords=['named entity recognition', 'nlp',
              'natural language processing'],
    classifiers=[
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Topic :: Text Processing',
    ],
    packages=['miner'],
    test_suite='tests',
)
