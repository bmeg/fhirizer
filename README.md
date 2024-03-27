# fhirizer
![Status](https://img.shields.io/badge/Status-Build%20Passing-lgreen)

### Project overview: 
Mapping GDC (Genomic Data Commons) schema or Cellosaurus cell-lines to FHIR (Fast Healthcare Interoperability Resources).

- #### GDC study simplified FHIR graph 
![mapping](./imgs/gdc_tcga_study_example_fhir_graph.png)


### fhirizer structure:

Data directories included in package data:
- **resources**: data resources generated or used in mappings
- **mapping**: json data maps produced by fhirizer pydantic schema maps
****
```
fhirizer/
|-- fhirizer/
|   |-- __init__.py
|   |-- labels/
|   |   |-- __init__.py
|   |   |-- files.py
|   |   |-- case.py
|   |   └── project.py
|   |   
|   |-- schema.py
|   |-- entity2fhir.py
|   |-- mapping.py
|   |-- utils.py
|   └── cli.py
|   
|-- mapping/
|   |-- project.json
|   |-- case.json
|   └── file.json
|  
|-- resources/
|   |-- gdc_resources/
|   |   |-- content_annotations/
|   |   |-- data_dictionary/
|   |   └── fields/
|   └── fhir_resources/
| 
|-- tests/
|   |-- __init__.py
|   |-- unit/
|   |   |-- __init__.py
|   |   └── test_mapping.py
|   |-- integration/
|   |   |-- __init__.py
|   |   |-- test_generate.py
|   |   └── test_convert.py
|   └── fixtures/
|   
|--README.md
└── setup.py
```

### Installation

- from source 
```
git clone repo
cd fhirizer
# create virtual env ex. 
# NOTE: package_data folders must be in python path in virtual envs 
python -m venv venv-fhirizer
source venv-fhirizer/bin/activate
pip install . 
```

- Dockerfile

```
(sudo) docker build -t <tag-name>:latest .
(sudo) docker run -it  --mount type=bind,source=<path-to-input-ndjson>,target=/opt/data --rm <tag-name>:latest
```

- Singularity 
```
singularity build fhirizer.sif docker://quay.io/ohsu-comp-bio/fhirizer
singularity shell fhirizer.sif
```

### Convert and Generate

- GDC 
  - convert GDC schema keys to fhir mapping
  - generate fhir object models ndjson files in directory

    Example run for patient - replace path's to ndjson files or directories. 
 
  ```
  fhirizer convert --name case --in_path cases.ndjson --out_path cases_key.ndjson --verbose True
  
  fhirizer generate --name case --out_dir ./data --entity_path cases_key.ndjson
  ``` 

  - to generate document reference for the patients
  ```
  fhirizer convert --name file --in_path files.ndjson --out_path files_key.ndjson --verbose True
  
  fhirizer generate --name file --out_dir ./data --entity_path files_key.ndjson
  ``` 

- Cellosaurus 

  - Cellosaurus ndjson follows [Cellosaurus GET API](https://api.cellosaurus.org/)  json format
  ```
  generate --name cellosaurus --out_dir ./data --entity_path <path-to-cellosaurus-celllines-ndjson>
  ```

### Constructing GDC maps cli cmds 

initialize initial structure of project, case, or file to add Maps

```
fhirizer project_init 
# to update Mappings run associated labels script ex ./labels/project.py 

fhirizer case_init 
fhirizer file_init 
```


### Testing 
```
pytest -cov 
```
