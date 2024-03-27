import json
from pathlib import Path
import importlib.resources
from fhirizer import utils
from fhirizer.schema import Schema, Map, Metadata, Version, Source, Destination, Reference
from fhir.resources.researchstudy import ResearchStudy
from fhir.resources.patient import Patient
from fhir.resources.documentreference import DocumentReference

data_dict = utils.load_data_dictionary(path=utils.DATA_DICT_PATH)


def initialize_project(field_path=utils.FIELDS_PATH,
                       out_path=str(Path(importlib.resources.files('fhirizer').parent / 'mapping' / 'project_test.json'))):

    """
    initial Schema structure of GDC project

    :param field_path: Path to GDC fields json files
    :param out_path: Path to project json schema
    :return: saves initial json schema of GDC object to mapping
    """
    fields = utils.load_fields(field_path)

    metadata = Metadata(
        title="Project",
        category="project",
        type="object",
        downloadable=False,
        description="Mapping GDC project entities, properties, and relations to FHIR. GDC project is any specifically defined piece of work that is undertaken or attempted to meet a single requirement. (NCIt C47885)",
        versions=[
            Version(
                source_version="1",
                data_release="Data Release 39.0 - December 04, 2023",
                commit="023da73eee3c17608db1a9903c82852428327b88",
                status="OK",
                tag="5.0.6"

            ),
            Version(
                destination_version="5.0.0"
            )
        ],
        resource_links=["https://gdc.cancer.gov/about-gdc/gdc-overview", "https://www.hl7.org/fhir/overview.html"]
    )

    source_ref = Reference(
        reference_type=data_dict['administrative']['project']['links'][0]['target_type']
    )

    destination_ref = Reference(
        reference_type=ResearchStudy.schema()['properties']['partOf']['enum_reference_types'][0]
    )

    source = Source(
        name=data_dict['administrative']['project']['id'],
        description=data_dict['administrative']['project']['description'],
        category=data_dict['administrative']['project']['category'],
        type=data_dict['administrative']['project']['type'],
        reference=[source_ref]
    )

    destination = Destination(
        name=ResearchStudy.schema()['title'],
        description=utils.clean_description(ResearchStudy.schema()['description']),
        module='Administration',
        title=ResearchStudy.schema()['title'],
        type=ResearchStudy.schema()['type'],
        reference=[destination_ref]
    )

    obj_map = Map(
        source=source,
        destination=destination
    )

    project_schema = Schema(
        version="1",
        metadata=metadata,
        obj_mapping=obj_map,
        obj_keys=fields['project_fields'],
        source_key_required=[],
        destination_key_required=[],
        unique_keys=[],
        source_key_aliases={},
        destination_key_aliases={},
        mappings=[]
    )

    utils.validate_and_write(project_schema, out_path=out_path, update=False, generate=True)


def initialize_case(field_path=utils.FIELDS_PATH,
                    out_path=str(Path(importlib.resources.files('fhirizer').parent / 'mapping' / 'case_test.json'))):
    """
    initial Schema structure of GDC Case

    :param field_path: Path to GDC fields json files
    :param out_path: Path to case json schema
    :return: saves initial json schema of GDC object for mapping
    """
    fields = utils.load_fields(field_path)

    metadata = Metadata(
        title="Case",
        category="case",
        type="object",
        downloadable=False,
        description="Mapping GDC case entities, properties, and relations to FHIR. GDC case is the collection of all data related to a specific subject in the context of a specific project.",
        versions=[
            Version(
                source_version="1",
                data_release="Data Release 39.0 - December 04, 2023",
                commit="023da73eee3c17608db1a9903c82852428327b88",
                status="OK",
                tag="5.0.6"

            ),
            Version(
                destination_version="5.0.0"
            )
        ],
        resource_links=["https://gdc.cancer.gov/about-gdc/gdc-overview", "https://www.hl7.org/fhir/overview.html"]
    )

    references = [data_dict['case']['case']['links'][i]['target_type'] for i in
                  range(0, len(data_dict['case']['case']['links']))]
    source_refs = []
    for r in references:
        source_refs.append(Reference(
            reference_type=r
        ))

    source = Source(
        name=data_dict['case']['case']['id'],
        description=data_dict['case']['case']['description'],
        category=data_dict['case']['case']['category'],
        type=data_dict['case']['case']['type'],
        reference=source_refs
    )

    destination = Destination(
        name=Patient.schema()['title'],
        description=utils.clean_description(Patient.schema()['description']),
        module='Administration',
        title=Patient.schema()['title'],
        type=Patient.schema()['type']
    )

    obj_map = Map(
        source=source,
        destination=destination
    )

    case_schema = Schema(
        version="1",
        metadata=metadata,
        obj_mapping=obj_map,
        obj_keys=fields['case_fields'],
        source_key_required=[],
        destination_key_required=[],
        unique_keys=[],
        source_key_aliases={},
        destination_key_aliases={},
        mappings=[]
    )

    utils.validate_and_write(case_schema, out_path=out_path, update=False, generate=True)


def initialize_file(field_path=utils.FIELDS_PATH, out_path=str(Path(importlib.resources.files('fhirizer').parent / 'mapping' / 'file_test.json'))):
    """
    initial Schema structure of GDC File

    :param field_path: Path to GDC fields json files
    :param out_path: Path to file json schema
    :return: saves initial json schema of GDC object for mapping
    """
    fields = utils.load_fields(field_path)

    metadata = Metadata(
        title="File",
        category="data_file",
        type="object",
        downloadable=True,
        description="Mapping GDC file to FHIR. GDC file is a set of related records (either written or electronic) kept together. (NCIt C42883)",
        versions=[
            Version(
                source_version="1",
                data_release="Data Release 39.0 - December 04, 2023",
                commit="023da73eee3c17608db1a9903c82852428327b88",
                status="OK",
                tag="5.0.6"

            ),
            Version(
                destination_version="5.0.0"
            )
        ],
        resource_links=["https://gdc.cancer.gov/about-gdc/gdc-overview", "https://www.hl7.org/fhir/overview.html"]
    )

    references = [i['target_type'] if 'subgroup' not in i
                  else [subgroup['target_type'] for subgroup in i['subgroup']]
                  for i in data_dict['file']['file']['links']]

    source_refs = []
    for r in references[0]:
        source_refs.append(Reference(
            reference_type=r
        ))

    source = Source(
        name=data_dict['file']['file']['id'],
        description=data_dict['file']['file']['description'],
        category=data_dict['file']['file']['category'],
        type=data_dict['file']['file']['type'],
        reference=source_refs
    )

    destination = Destination(
        name=DocumentReference.schema()['title'],
        description=utils.clean_description(DocumentReference.schema()['description']),
        module='Diagnostics',
        title=DocumentReference.schema()['title'],
        type=DocumentReference.schema()['type']
    )

    obj_map = Map(
        source=source,
        destination=destination
    )

    file_schema = Schema(
        version="1",
        metadata=metadata,
        obj_mapping=obj_map,
        obj_keys=fields['file_fields'],
        source_key_required=[],
        destination_key_required=[],
        unique_keys=[],
        source_key_aliases={},
        destination_key_aliases={},
        mappings=[]
    )

    utils.validate_and_write(file_schema, out_path=out_path, update=False, generate=True)


def add_some_maps(out_path=str(Path(importlib.resources.files('fhirizer').parent / 'mapping' / 'project_test.json'))):
    """
    # add name and project_id for testing

    :param out_path:
    :return:
    """
    project_schema = utils.load_schema_from_json(path=out_path)

    m = [Map(
        source=Source(
            name='name',
            description='Display name for the project.',
            category=data_dict['administrative']['project']['category'],
            type='string'
        ),
        destination=Destination(
            name='ResearchStudy.name',
            description=ResearchStudy.schema()['properties']['name']['title'],
            module='Administration',
            title=ResearchStudy.schema()['properties']['name']['title'],
            type=ResearchStudy.schema()['properties']['name']['type'],
        )
    ), Map(
        source=Source(
            name='project_id',
            description=data_dict['administrative']['project']['properties']['id']['common']['description'],
            category=data_dict['administrative']['project']['category'],
            type=data_dict['administrative']['project']['properties']['id']['common']['termDef']['term']
        ),
        destination=Destination(
            name='ResearchStudy.identifier',
            description=ResearchStudy.schema()['properties']['identifier']['description'],
            module='Administration',
            title=ResearchStudy.schema()['properties']['identifier']['title'],
            type=ResearchStudy.schema()['properties']['identifier']['items']['type'],
            format=ResearchStudy.schema()['properties']['identifier']['type']
        )
    )]

    [project_schema.mappings.append(i) for i in m]
    utils.validate_and_write(project_schema, out_path=out_path, update=True, generate=False)


def convert_maps(in_path, out_path, name, verbose):
    """
    - load updated schema
    - load GDC bmeg script json file
    - extract gdc key hierarchy
    - check available Map sources
    - map destination keys

    fhirizer convert --in_path "/Users/sanati/KCRB/fhir/cases.ndjson" --out_path "/Users/sanati/KCRB/fhir/case_key.ndjson" --verbose True

    :param name: project, case GDC entity
    :param in_path: ndjson path of data scripted from GDC ex bmeg-etl script
    :param out_path:
    :param verbose:
    :return:
    """

    mapped_entity_list = []
    schema = None

    if name in 'project':
        schema = utils.load_schema_from_json(path=str(Path(importlib.resources.files('fhirizer').parent / 'mapping' / 'project.json')))
    elif name in 'case':
        schema = utils.load_schema_from_json(path=str(Path(importlib.resources.files('fhirizer').parent / 'mapping' / 'case.json')))
    elif name in 'file':
        schema = utils.load_schema_from_json(path=str(Path(importlib.resources.files('fhirizer').parent / 'mapping' / 'file.json')))
    if schema:
        entities = utils.load_ndjson(path=in_path)

        all_keys = [list(utils.extract_keys(e)) for e in entities]
        keys = list(set().union(*all_keys))  # union of all keys

        available_maps = [schema.find_map_by_source(k) for k in keys]
        available_maps.append(schema.obj_mapping)

        profile = Map(
            source=Source(name='data_format', description=None, description_url=None, category=None, type=None,
                          format=None, enums=None, content_annotation=None, reference=None),
            destination=Destination(name='DocumentReference.content.profile', description=None, description_url=None,
                                    module=None, title=None, type=None, format=None, reference=None))
        if name in 'file' and profile not in available_maps:
            available_maps.append(profile)

        if verbose:
            print("available_maps: ", available_maps)

        mapped_entity_list = [utils.map_data(e, available_maps, verbose=verbose)['mapped_data'] for e in entities]

        if out_path:
            with open(out_path, 'w') as file:
                file.write('\n'.join(map(json.dumps, mapped_entity_list)))

    return mapped_entity_list

