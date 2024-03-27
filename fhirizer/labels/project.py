import os
from typing import List
from fhirizer import utils
from fhirizer.schema import Map, Source, Destination, Reference
from fhir.resources.researchstudy import ResearchStudy, ResearchStudyProgressStatus, ResearchStudyRecruitment
from fhir.resources.codeableconcept import CodeableConcept
from fhir.resources.codeablereference import CodeableReference
from fhir.resources.condition import Condition
from fhir.resources.extension import Extension

package_dir = utils.package_dir
project_schema = utils.load_schema_from_json(path=os.path.join(package_dir, 'mapping', 'project.json'))
keys_to_label_fields = [key for key in project_schema.obj_keys if
                        key not in [x.source.name for x in project_schema.mappings]]
data_dict = utils.load_data_dictionary(
    path=os.path.join(package_dir, 'resources', 'gdc_resources', 'data_dictionary', ''))

"""
Field labels mapped semi-computationally 
"""

project_maps = [
    Map(
        source=Source(
            name='program',
            description=data_dict['administrative']['program']['description'],
            category=data_dict['administrative']['program']['category'],
            type=data_dict['administrative']['program']['type']
        ),
        destination=Destination(
            name='ResearchStudy',
            description=utils.clean_description(ResearchStudy.schema()['description']),
            module='Administration',
            title=ResearchStudy.schema()['title'],
            type=ResearchStudy.schema()['type']
        )
    ),

    Map(
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
            reference=[Reference(reference_type=str(ResearchStudy))]
        )
    ),

    Map(
        source=Source(
            name='project_id',
            description=data_dict['administrative']['project']['properties']['id']['common']['description'],
            category=data_dict['administrative']['project']['category'],
            type=data_dict['administrative']['project']['properties']['id']['common']['termDef']['term']
        ),
        destination=Destination(
            name='ResearchStudy.id',
            description=ResearchStudy.schema()['properties']['id']['description'],
            module='Administration',
            title=ResearchStudy.schema()['properties']['id']['title'],
            type=ResearchStudy.schema()['properties']['id']['type']
        )
    ),

    Map(
        source=Source(
            name='dbgap_accession_number',
            description=data_dict['administrative']['project']['properties']['dbgap_accession_number']['description'],
            category=data_dict['administrative']['project']['category'],
            type=data_dict['administrative']['project']['properties']['dbgap_accession_number']['type']
        ),
        destination=Destination(
            name="ResearchStudy.identifier",
            description=ResearchStudy.schema()['properties']['identifier']['description'],
            module='Administration',
            title=ResearchStudy.schema()['properties']['identifier']['title'],
            type=ResearchStudy.schema()['properties']['identifier']['type']
        )
    ),

    Map(
        source=Source(
            name='disease_type',
            description=data_dict['administrative']['project']['properties']['disease_type']['description'],
            category=data_dict['administrative']['project']['category'],
            type=data_dict['administrative']['project']['properties']['disease_type']['type'],
            content_annotation='@content_annotations/case/disease_types.json'
        ),
        destination=Destination(
            name='ResearchStudy.condition',
            description=ResearchStudy.schema()['properties']['condition']['description'],
            module='Administration',
            title=ResearchStudy.schema()['properties']['condition']['title'],
            type=ResearchStudy.schema()['properties']['condition']['type'],
            format=str(List[CodeableConcept])
        )
    ),

    Map(
        source=Source(
            name='primary_site',
            description=data_dict['administrative']['project']['properties']['primary_site']['description'],
            category=data_dict['administrative']['project']['category'],
            type=data_dict['administrative']['project']['properties']['primary_site']['type'],
            content_annotation='@content_annotations/case/primary_site.json'
        ),
        destination=Destination(
            name='Condition.bodySite',
            description=Condition.schema()['properties']['bodySite']['description'],
            module='Clinical Summary',
            title=Condition.schema()['properties']['bodySite']['title'],
            type=Condition.schema()['properties']['bodySite']['type'],
            format=str(List[CodeableConcept])
        )
    ),

    Map(
        source=Source(
            name='released',
            description=data_dict['administrative']['project']['properties']['released']['description'],
            category=data_dict['administrative']['project']['category'],
            type=data_dict['administrative']['project']['properties']['released']['type']
        ),
        destination=Destination(
            name='ResearchStudyProgressStatus.actual',  # TODO will be part of ResearchStudy.status
            description=ResearchStudyProgressStatus.schema()['properties']['actual']['description'],
            module='Administration',
            title=ResearchStudyProgressStatus.schema()['properties']['actual']['title'],
            type=ResearchStudyProgressStatus.schema()['properties']['actual']['type']
        )
    ),

    Map(
        source=Source(
            name='state',
            description=data_dict['administrative']['project']['properties']['state']['description'],
            category=data_dict['administrative']['project']['category'],
            type='string',
            enums=[{'enum': data_dict['administrative']['project']['properties']['state']['enum']}]
        ),
        destination=Destination(
            name='ResearchStudy.status',
            description=ResearchStudy.schema()['properties']['status']['description'],
            module='Administration',
            title=ResearchStudy.schema()['properties']['status']['title'],
            type=ResearchStudy.schema()['properties']['status']['type']
        )
    ),

    Map(
        source=Source(
            name='program.dbgap_accession_number',
            description=data_dict['administrative']['program']['properties']['dbgap_accession_number']['description'],
            category=data_dict['administrative']['program']['category'],
            type=data_dict['administrative']['program']['properties']['dbgap_accession_number']['type']
        ),
        destination=Destination(
            name="ResearchStudy.identifier",
            description=ResearchStudy.schema()['properties']['identifier']['description'],
            module='Administration',
            title=ResearchStudy.schema()['properties']['identifier']['title'],
            type=ResearchStudy.schema()['properties']['identifier']['type']
        )
    ),

    Map(
        source=Source(
            name='program.name',
            description=data_dict['administrative']['program']['properties']['name']['description'],
            category=data_dict['administrative']['program']['category'],
            type=data_dict['administrative']['program']['properties']['name']['type']
        ),
        destination=Destination(
            name='ResearchStudy.name',
            description=ResearchStudy.schema()['properties']['name']['title'],
            module='Administration',
            title=ResearchStudy.schema()['properties']['name']['title'],
            type=ResearchStudy.schema()['properties']['name']['type']
        )
    ),

    Map(
        source=Source(
            name='program.program_id',
            description=data_dict['administrative']['program']['properties']['id']['common']['description'],
            category=data_dict['administrative']['program']['category'],
            type=data_dict['administrative']['program']['properties']['id']['common']['termDef']['term']
        ),
        destination=Destination(
            name='ResearchStudy.id',
            description=ResearchStudy.schema()['properties']['id']['description'],
            module='Administration',
            title=ResearchStudy.schema()['properties']['id']['title'],
            type=ResearchStudy.schema()['properties']['id']['type']
        )
    ),

    Map(
        source=Source(
            name='summary.case_count',
            description='The number of cases in the project',
            description_url='https://docs.gdc.cancer.gov/Data_Portal/Users_Guide/Projects/',
            category='administrative',
            type='integer'
        ),
        destination=Destination(
            name='ResearchStudyRecruitment.actualNumber',
            description=ResearchStudyRecruitment.schema()['properties']['actualNumber']['title'],
            module='Administration',
            title=ResearchStudyRecruitment.schema()['properties']['actualNumber']['title'],
            type=ResearchStudyRecruitment.schema()['properties']['actualNumber']['type']
        )
    ),

    Map(
        source=Source(
            name='summary.file_count',
            description='The number of files of the project.',
            description_url='https://docs.gdc.cancer.gov/Data_Portal/Users_Guide/Projects/',
            category='administrative',
            type='integer'
        ),
        destination=Destination(
            name='Extension.valueUnsignedInt',
            description=Extension.schema()['properties']['valueUnsignedInt']['description'],
            module='Foundation',
            title=Extension.schema()['properties']['valueUnsignedInt']['title'],
            type=Extension.schema()['properties']['valueUnsignedInt']['type']
        )
    ),

    Map(
        source=Source(
            name='summary.file_size',
            description="".join(
                [data_dict['file']['file']['properties']['file_size']['common']['description'], '(summary)']),
            category='administrative',
            type='integer'
        ),
        destination=Destination(
            name='Extension.valueUnsignedInt',
            description=Extension.schema()['properties']['valueUnsignedInt']['description'],
            module='Foundation',
            title=Extension.schema()['properties']['valueUnsignedInt']['title'],
            type=Extension.schema()['properties']['valueUnsignedInt']['type']
        )
    ),

    Map(
        source=Source(
            name='summary.data_categories.case_count',
            description_url='https://docs.gdc.cancer.gov/Data_Portal/Users_Guide/Projects/',
            description="Total number of case(s) within the type(s) of data available in the project.",
            category='administrative',
            type='integer'
        ),
        destination=Destination(
            name='Extension.valueUnsignedInt',
            description=Extension.schema()['properties']['valueUnsignedInt']['description'],
            module='Foundation',
            title=Extension.schema()['properties']['valueUnsignedInt']['title'],
            type=Extension.schema()['properties']['valueUnsignedInt']['type']
        )
    ),

    Map(
        source=Source(
            name='summary.experimental_strategies.case_count',
            description_url='https://docs.gdc.cancer.gov/Data_Portal/Users_Guide/Projects/',
            description="Total number of case(s) within the genomic analysis type(s) available in the project.",
            category='administrative',
            type='integer'
        ),
        destination=Destination(
            name='Extension.valueUnsignedInt',
            description=Extension.schema()['properties']['valueUnsignedInt']['description'],
            module='Foundation',
            title=Extension.schema()['properties']['valueUnsignedInt']['title'],
            type=Extension.schema()['properties']['valueUnsignedInt']['type']
        )
    ),

    Map(
        source=Source(
            name='summary.data_categories.data_category',
            description_url='https://docs.gdc.cancer.gov/Data_Portal/Users_Guide/Projects/',
            description="Types of data available in the project.",
            category='administrative',
            enums=[{'enums': ['Sequencing Reads',
                              'Structural Variation',
                              'Transcriptome Profiling',
                              'Simple Nucleotide Variation',
                              'Clinical',
                              'Biospecimen',
                              'Copy Number Variation',
                              'Dna Methylation',
                              'Somatic Structural Variation',
                              'Proteome Profiling',
                              'Combined Nucleotide Variation']
                    }],
            type='string'
        ),
        destination=Destination(
            name='Extension.valueString',
            description=Extension.schema()['properties']['valueString']['description'],
            module='Foundation',
            title=Extension.schema()['properties']['valueString']['title'],
            type=Extension.schema()['properties']['valueString']['type']
        )
    ),

    Map(
        source=Source(
            name='summary.data_categories.file_count',
            description_url='https://docs.gdc.cancer.gov/Data_Portal/Users_Guide/Projects/',
            description="Total number of files within the type(s) of data available in the project.",
            category='administrative',
            type='integer'
        ),
        destination=Destination(
            name='Extension.valueUnsignedInt',
            description=Extension.schema()['properties']['valueUnsignedInt']['description'],
            module='Foundation',
            title=Extension.schema()['properties']['valueUnsignedInt']['title'],
            type=Extension.schema()['properties']['valueUnsignedInt']['type']
        )
    ),

    Map(
        source=Source(
            name='summary.experimental_strategies.experimental_strategy',
            description_url='https://docs.gdc.cancer.gov/Data_Portal/Users_Guide/Projects/',
            description="All unique experimental strategies used for molecular characterization of the cancer in the project.",
            category='administrative',
            type='string',
            enums=[{'enum': ['RNA-Seq',
                             'WXS',
                             'WGS',
                             'miRNA-Seq',
                             'Methylation Array',
                             'Genotyping Array',
                             'Tissue Slide',
                             'Diagnostic Slide',
                             'Reverse Phase Protein Array',
                             'ATAC-Seq',
                             'Targeted Sequencing',
                             'scRNA-Seq']}]
        ),
        destination=Destination(
            name='ResearchStudy.focus',
            description=ResearchStudy.schema()['properties']['focus']['description'],
            module='Administration',
            title=ResearchStudy.schema()['properties']['focus']['title'],
            type=ResearchStudy.schema()['properties']['focus']['type'],
            format=str(List[CodeableReference])
        )
    ),

    Map(
        source=Source(
            name='summary.experimental_strategies.file_count',
            description='Total number of files within the experimental strategies used for molecular characterization of the cancer in the project.',
            description_url='https://docs.gdc.cancer.gov/Data_Portal/Users_Guide/Projects/',
            category='administrative',
            type='integer'
        ),
        destination=Destination(
            name='Extension.valueUnsignedInt',
            description=Extension.schema()['properties']['valueUnsignedInt']['description'],
            module='Foundation',
            title=Extension.schema()['properties']['valueUnsignedInt']['title'],
            type=Extension.schema()['properties']['valueUnsignedInt']['type']
        )
    )]
"""
proceed with caution this code changes the state of current files under mapping
"""

# out_path = os.path.join(package_dir, 'mapping', 'project.json')
out_path = '../../mapping/project.json'
valid_project_maps = [Map.model_validate(p) for p in project_maps]
[project_schema.mappings.append(i) for i in valid_project_maps]
utils.validate_and_write(project_schema, out_path=out_path, update=True, generate=False)
