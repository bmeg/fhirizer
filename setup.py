from setuptools import setup, find_packages

__version__ = '1.0.0'

setup(
    name='fhirizer',
    version=__version__,
    description="Mapping GDC's and Cellosaurus schema to FHIR schema.",
    long_description=open('README.md').read(),
    url='https://github.com/bmeg/fhirizer',
    author='https://ellrottlab.org/',
    packages=find_packages(),
    entry_points={
        'console_scripts': ['fhirizer = fhirizer.cli:cli']
    },
    install_requires=[
        'charset_normalizer',
        'idna',
        'certifi',
        'requests',
        'pydantic',
        'pytest',
        'click',
        'pathlib',
        'orjson',
        'tqdm',
        'iteration_utilities',
        'icd10-cm',
        'beautifulsoup4',
        'fhir.resources>=7.1.0'  # FHIR® (Release R5, version 5.0.0)
    ],
    package_data={
        'gdc2fhir': [
            '../resources/gdc_resources/content_annotations/**/*.json',
            '../resources/gdc_resources/data_dictionary/**/*.json',
            '../resources/gdc_resources/fields/*.json',
            '../resources/*.json.gz',
            '../mapping/*.json'
        ]
    },
    tests_require=['pytest'],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'License :: OSI Approved :: MIT License',
        'Intended Audience :: Developers',
        'Intended Audience :: Science/Research',
        'Topic :: Scientific/Engineering',
        'Topic :: Scientific/Engineering :: Bio-Informatics'
    ],
    platforms=['any'],
    python_requires='>=3.9, <4.0',
)

