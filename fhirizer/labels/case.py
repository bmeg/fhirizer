import os
from typing import List, LiteralString
from fhirizer import utils
from fhirizer.schema import Map, Source, Destination, Reference
from fhir.resources.patient import Patient
from fhir.resources.extension import Extension
from fhir.resources.researchstudy import ResearchStudy, ResearchStudyProgressStatus
from fhir.resources.researchsubject import ResearchSubject
from fhir.resources.specimen import Specimen
from fhir.resources.imagingstudy import ImagingStudy
from fhir.resources.condition import Condition
from fhir.resources.diagnosticreport import DiagnosticReport
from fhir.resources.codeableconcept import CodeableConcept
from fhir.resources.codeablereference import CodeableReference
from fhir.resources.genomicstudy import GenomicStudy
from fhir.resources.encounter import Encounter

package_dir = utils.package_dir
case_schema = utils.load_schema_from_json(path=os.path.join(package_dir, 'mapping', 'case.json'))
keys_to_label_fields = [key for key in case_schema.obj_keys if
                        key not in [x.source.name for x in case_schema.mappings]]
data_dict = utils.load_data_dictionary(path=os.path.join(package_dir, 'resources', 'gdc_resources', 'data_dictionary',  ''))

"""
Field labels mapped semi-computationally 

Map(
    source=Source(
        name='',
        description='',
        description_url='',
        category='',
        type='',
        enums=[],
        content_annotation=[],
        reference=[]

    ),
    destination=Destination(
        name='',
        description='',
        description_url='',
        module='',
        title='',
        type='',
        format='',
        reference=''
    )
)
"""

case_maps = [Map(
    source=Source(
        name='aliquot_ids',
        description=data_dict["biospecimen"]["aliquot"]["properties"]["id"]["common"]["description"],
        category=data_dict["biospecimen"]["aliquot"]["category"],
        type=data_dict["biospecimen"]["aliquot"]["properties"]["id"]["type"],
        reference=[
            Reference(reference_type=data_dict["biospecimen"]["aliquot"]["links"][0]["subgroup"][0]["target_type"]),
            Reference(reference_type=data_dict["biospecimen"]["aliquot"]["links"][0]["subgroup"][1]["target_type"])]
    ),
    destination=Destination(
        name='Specimen.id.aliquot',
        description=Specimen.schema()["properties"]["id"]["description"],
        module='Diagnostics',
        title=Specimen.schema()["properties"]["id"]["title"],
        type=Specimen.schema()["properties"]["id"]["type"]
    )
),

    Map(
        source=Source(
            name='analyte_ids',
            description=data_dict["biospecimen"]["analyte"]["properties"]["id"]["common"]["description"],
            category=data_dict["biospecimen"]["analyte"]["category"],
            type=data_dict["biospecimen"]["analyte"]["properties"]["id"]["type"],
            reference=[
                Reference(reference_type=data_dict["biospecimen"]["analyte"]["links"][0]["subgroup"][0]["target_type"]),
                Reference(reference_type=data_dict["biospecimen"]["analyte"]["links"][0]["subgroup"][1]["target_type"])]
        ),
        destination=Destination(
            name='Specimen.ids.analyte',
            description=Specimen.schema()["properties"]["id"]["description"],
            module='Diagnostics',
            title=Specimen.schema()["properties"]["id"]["title"],
            type=Specimen.schema()["properties"]["id"]["type"]
        )
    ),

    Map(
        source=Source(
            name='case_id',
            description=data_dict["case"]["case"]["properties"]["id"]["common"]["description"],
            category=data_dict["case"]["case"]["category"],
            type=data_dict["case"]["case"]["properties"]["id"]["common"]["termDef"]["term"],
            reference=[Reference(reference_type=data_dict["case"]["case"]["links"][0]["target_type"]),
                       Reference(reference_type=data_dict["case"]["case"]["links"][1]["target_type"])]
        ),
        destination=Destination(
            name='Patient.id',
            description=Patient.schema()["properties"]['id']["title"],
            module='Administration',
            title=Patient.schema()["properties"]['id']["title"],
            type=Patient.schema()["properties"]['id']["type"]
        )
    ),

    Map(
        source=Source(
            name='created_datetime',
            description=data_dict["clinical"]["diagnosis"]["properties"]["created_datetime"]["common"]["description"],
            category=data_dict["clinical"]["diagnosis"]["category"],
            format=data_dict["clinical"]["diagnosis"]["properties"]["created_datetime"]["oneOf"][0]["format"],
            type=data_dict["clinical"]["diagnosis"]["properties"]["created_datetime"]["oneOf"][0]["type"]
        ),
        destination=Destination(
            name='DiagnosticReport.issued',
            description=DiagnosticReport.schema()["properties"]["issued"]["description"],
            module='Diagnostics',
            title=DiagnosticReport.schema()["properties"]["issued"]["title"],
            type=DiagnosticReport.schema()["properties"]["issued"]["type"]
        )
    ),

    Map(
        source=Source(
            name='portion_ids',
            description=data_dict["biospecimen"]["portion"]["properties"]["id"]["common"]["description"],
            category=data_dict["biospecimen"]["portion"]["category"],
            type=data_dict["biospecimen"]["portion"]["properties"]["id"]["type"]
        ),
        destination=Destination(
            name='Specimen.id.portion',
            description=Specimen.schema()["properties"]["id"]["description"],
            module='Diagnostics',
            title=Specimen.schema()["properties"]["id"]["title"],
            type=Specimen.schema()["properties"]["id"]["type"]
        )
    ),

    Map(
        source=Source(
            name='sample_ids',
            description=data_dict["biospecimen"]["sample"]["properties"]["id"]["common"]["description"],
            category=data_dict["biospecimen"]["sample"]["category"],
            type=data_dict["biospecimen"]["sample"]["properties"]["id"]["common"]["termDef"]["term"],
            reference=[Reference(reference_type=data_dict["biospecimen"]["sample"]["links"][0]["target_type"]),
                       Reference(reference_type=data_dict["biospecimen"]["sample"]["links"][1]["target_type"]),
                       Reference(reference_type=data_dict["biospecimen"]["sample"]["links"][2]["target_type"]),
                       Reference(reference_type=data_dict["biospecimen"]["sample"]["links"][3]["target_type"])]
        ),
        destination=Destination(
            name='Specimen.id',
            description=Specimen.schema()["properties"]["id"]["description"],
            module='Diagnostics',
            title=Specimen.schema()["properties"]["id"]["title"],
            type=Specimen.schema()["properties"]["id"]["type"]
        )
    ),

    Map(
        source=Source(
            name='slide_ids',
            description=data_dict["biospecimen"]["slide"]["properties"]["id"]["common"]["description"],
            category=data_dict["biospecimen"]["slide"]["category"],
            type=data_dict["biospecimen"]["slide"]["properties"]["id"]["type"]
        ),
        destination=Destination(
            name='ImagingStudy.id',
            description=ImagingStudy.schema()["properties"]["id"]["description"],
            module='',
            title=ImagingStudy.schema()["properties"]["id"]["title"],
            type=ImagingStudy.schema()["properties"]["id"]["type"]
        )
    ),

    Map(
        source=Source(
            name='state',
            description=data_dict["case"]["case"]["properties"]["state"]["common"]["description"],
            category=data_dict["case"]["case"]["category"],
            type='string'
        ),
        destination=Destination(
            name='ResearchSubject.status',
            description=ResearchSubject.schema()["properties"]["status"]["description"],
            module='',
            title=ResearchSubject.schema()["properties"]["status"]["title"],
            type=ResearchSubject.schema()["properties"]["status"]["type"]
        )
    ),

    Map(
        source=Source(
            name='submitter_aliquot_ids',
            description=data_dict["biospecimen"]["aliquot"]["properties"]["submitter_id"]["description"],
            category=data_dict["biospecimen"]["aliquot"]["category"],
            type=data_dict["biospecimen"]["aliquot"]["properties"]["submitter_id"]["type"]
        ),
        destination=Destination(
            name='Specimen.identifier.aliquot',
            description=Specimen.schema()["properties"]["identifier"]["description"],
            module='Diagnostics',
            title=Specimen.schema()["properties"]["identifier"]["title"],
            type=Specimen.schema()["properties"]["identifier"]["type"]
        )
    ),

    Map(
        source=Source(
            name='submitter_analyte_ids',
            description=data_dict["biospecimen"]["analyte"]["properties"]["submitter_id"]["description"],
            category=data_dict["biospecimen"]["analyte"]["category"],
            type=data_dict["biospecimen"]["analyte"]["properties"]["submitter_id"]["type"]
        ),
        destination=Destination(
            name='Specimen.identifier.analyte',
            description=Specimen.schema()["properties"]["identifier"]["description"],
            module='Diagnostics',
            title=Specimen.schema()["properties"]["identifier"]["title"],
            type=Specimen.schema()["properties"]["identifier"]["type"]
        )
    ),

    Map(
        source=Source(
            name='submitter_id',
            description=data_dict["case"]["case"]["properties"]["submitter_id"]["description"],
            category=data_dict["case"]["case"]["category"],
            type=data_dict["case"]["case"]["properties"]["submitter_id"]["type"]

        ),
        destination=Destination(
            name='Patient.identifier',
            description=Patient.schema()["properties"]['identifier']["title"],
            module='Administration',
            title=Patient.schema()["properties"]['identifier']["title"],
            type=Patient.schema()["properties"]['identifier']["type"]
        )
    ),

    Map(
        source=Source(
            name='submitter_portion_ids',
            description=data_dict["biospecimen"]["portion"]["properties"]["submitter_id"]["description"],
            category=data_dict["biospecimen"]["portion"]["category"],
            type=data_dict["biospecimen"]["portion"]["properties"]["submitter_id"]["type"]
        ),
        destination=Destination(
            name='Specimen.identifier.portion',
            description=Specimen.schema()["properties"]["identifier"]["title"],
            module='Diagnostics',
            title=Specimen.schema()["properties"]["identifier"]["title"],
            type=Specimen.schema()["properties"]["identifier"]["type"]
        )
    ),

    Map(
        source=Source(
            name='submitter_sample_ids',
            description=data_dict["biospecimen"]["sample"]["properties"]["submitter_id"]["description"],
            category=data_dict["biospecimen"]["sample"]["category"],
            type=data_dict["biospecimen"]["sample"]["properties"]["submitter_id"]["type"]
        ),
        destination=Destination(
            name='Specimen.identifier',
            description=Specimen.schema()["properties"]["identifier"]["title"],
            module='Diagnostics',
            title=Specimen.schema()["properties"]["identifier"]["title"],
            type=Specimen.schema()["properties"]["identifier"]["type"]
        )
    ),

    Map(
        source=Source(
            name='submitter_slide_ids',
            description=data_dict["biospecimen"]["slide"]["properties"]["submitter_id"]["description"],
            category=data_dict["biospecimen"]["slide"]["category"],
            type=data_dict["biospecimen"]["slide"]["properties"]["submitter_id"]["type"]
        ),
        destination=Destination(
            name='ImagingStudy.identifier',
            description=ImagingStudy.schema()["properties"]["identifier"]["title"],
            module='Diagnostics',
            title=ImagingStudy.schema()["properties"]["identifier"]["title"],
            type=ImagingStudy.schema()["properties"]["identifier"]["type"]
        )
    ),

    Map(
        source=Source(
            name='updated_datetime',
            description=data_dict["case"]["case"]["properties"]["updated_datetime"]["common"]["description"],
            category=data_dict["case"]["case"]["category"],
            type=data_dict["case"]["case"]["properties"]["updated_datetime"]["oneOf"][0]["type"],
            format=data_dict["case"]["case"]["properties"]["updated_datetime"]["oneOf"][0]["format"]

        ),
        destination=Destination(
            name='Extension.valueDateTime',
            description=Extension.schema()["properties"]["valueDateTime"]["description"],
            description_url='https://build.fhir.org/datatypes.html#dateTime',
            module='Extensibility',
            title=Extension.schema()["properties"]["valueDateTime"]["title"],
            type=Extension.schema()["properties"]["valueDateTime"]["type"]
        )
    ),

    Map(
        source=Source(
            name='demographic.created_datetime',
            description=data_dict["clinical"]["demographic"]["properties"]["created_datetime"]["common"]["description"],
            description_url='https://docs.gdc.cancer.gov/Data_Dictionary/viewer/#?view=table-definition-view&id=demographic',
            category=data_dict["clinical"]["demographic"]["category"],
            type=data_dict["clinical"]["demographic"]["properties"]["created_datetime"]["oneOf"][0]["type"],
            format=data_dict["clinical"]["demographic"]["properties"]["created_datetime"]["oneOf"][0]["format"]
        ),
        destination=Destination(
            name='Extension.valueDateTime',
            description=Extension.schema()["properties"]["valueDateTime"]["description"],
            description_url='https://build.fhir.org/datatypes.html#dateTime',
            module='Foundation',
            title=Extension.schema()["properties"]["valueDateTime"]["title"],
            type=Extension.schema()["properties"]["valueDateTime"]["type"],
            format=Extension.schema()["properties"]["valueDateTime"]["format"]
        )
    ),

    Map(
        source=Source(
            name='demographic.demographic_id',
            description=data_dict["clinical"]["demographic"]["properties"]["id"]["common"]["description"],
            category=data_dict["clinical"]["demographic"]["category"],
            type=data_dict["clinical"]["demographic"]["properties"]["id"]["common"]["termDef"]["term"]
        ),
        destination=Destination(
            name='Patient.id',
            description=Patient.schema()["properties"]['id']["description"],
            module='Administration',
            title=Patient.schema()["properties"]['id']["title"],
            type=Patient.schema()["properties"]['id']["type"]
        )
    ),

    Map(
        source=Source(
            name='demographic.ethnicity',
            description=data_dict["clinical"]["demographic"]["properties"]["ethnicity"]["description"],
            category=data_dict["clinical"]["demographic"]["category"],
            type=data_dict["clinical"]["demographic"]["properties"]["ethnicity"]["termDef"]["term"],
            enums=[{'enum': ['hispanic or latino',
                             'not hispanic or latino',
                             'Unknown',
                             'unknown',
                             'not reported',
                             'not allowed to collect']}],
            content_annotation="@fhirizer/resources/gdc_resources/content_annotations/demographic/ethnicity.json"
        ),
        destination=Destination(
            name='Extension:extension.USCoreEthnicity',
            description='Concepts classifying the person into a named category of humans sharing common history, traits, '
                        'geographical origin or nationality. The race codes used to represent these concepts are based '
                        'upon the CDC Race and Ethnicity Code Set Version 1.0 which includes over 900 concepts for '
                        'representing race and ethnicity of which 921 reference race. The race concepts are grouped by '
                        'and pre-mapped to the 5 OMB race categories.',
            description_url='https://build.fhir.org/ig/HL7/US-Core/StructureDefinition-us-core-ethnicity.profile.json.html',
            module='Foundation',
            title=Extension.schema()["properties"]["extension"]["title"],
            type=Extension.schema()["properties"]["extension"]["type"]
        )
    ),

    Map(
        source=Source(
            name='demographic.gender',
            description=data_dict["clinical"]["demographic"]["properties"]["gender"]["description"],
            category=data_dict["clinical"]["demographic"]["category"],
            type=data_dict["clinical"]["demographic"]["properties"]["gender"]["termDef"]["term"],
            enums=[{'enum': ['female', 'male', 'unspecified', 'unknown', 'not reported']}],
            content_annotation="@fhirizer/resources/gdc_resources/content_annotations/demographic/gender.json"
        ),
        destination=Destination(
            name='Patient.gender',
            description=Patient.schema()["properties"]['gender']["description"],
            module='Administration',
            title=Patient.schema()["properties"]['gender']["title"],
            type=Patient.schema()["properties"]['gender']["type"]
        )
    ),

    Map(
        source=Source(
            name='demographic.vital_status'
        ),
        destination=Destination(
            name='Patient.deceasedBoolean'
        )
    ),

    Map(
        source=Source(
            name='demographic.age_at_index'
        ),
        destination=Destination(
            name='Patient.extension.age'
        )
    ),

    Map(
        source=Source(
            name='demographic.race',
            description=data_dict["clinical"]["demographic"]["properties"]["race"]["description"],
            category=data_dict["clinical"]["demographic"]["category"],
            type=data_dict["clinical"]["demographic"]["properties"]["race"]["termDef"]["term"],
            enums=[{'enum': ['american indian or alaska native',
                             'asian',
                             'black or african american',
                             'native hawaiian or other pacific islander',
                             'white',
                             'other',
                             'Unknown',
                             'unknown',
                             'not reported',
                             'not allowed to collect']}],
            content_annotation="@fhirizer/resources/gdc_resources/content_annotations/demographic/race.json"
        ),
        destination=Destination(
            name='Extension.extension:USCoreRaceExtension',
            description='Concepts classifying the person into a named category of humans sharing common history, traits, '
                        'geographical origin or nationality. The race codes used to represent these concepts are based '
                        'upon the CDC Race and Ethnicity Code Set Version 1.0 which includes over 900 concepts for '
                        'representing race and ethnicity of which 921 reference race. The race concepts are grouped by '
                        'and pre-mapped to the 5 OMB race categories.',
            description_url='http://hl7.org/fhir/us/core/STU6.1/StructureDefinition-us-core-race.profile.json.html',
            module='Foundation',
            title=Extension.schema()["properties"]["extension"]["title"],
            type=Extension.schema()["properties"]["extension"]["type"]
        )
    ),

    Map(
        source=Source(
            name='demographic.state',
            description=data_dict["clinical"]["demographic"]["properties"]["state"]["common"]["description"],
            category=data_dict["clinical"]["demographic"]["category"],
            type='string',
            enums=[{'enum': ['uploading',
                             'uploaded',
                             'md5summing',
                             'md5summed',
                             'validating',
                             'error',
                             'invalid',
                             'suppressed',
                             'redacted',
                             'live']},
                   {'enum': ['validated', 'submitted', 'released']}]

        ),
        destination=Destination(
            name='Extension.valueString',
            description=Extension.schema()["properties"]["valueString"]["description"],
            description_url='',
            module='Foundation',
            title=Extension.schema()["properties"]["extension"]["title"],
            type=Extension.schema()["properties"]["valueString"]["title"]
        )
    ),

    Map(
        source=Source(
            name='demographic.submitter_id',
            description=data_dict["clinical"]["demographic"]["properties"]["submitter_id"]["description"],
            category=data_dict["clinical"]["demographic"]["category"],
            type=data_dict["clinical"]["demographic"]["properties"]["submitter_id"]["type"]
        ),
        destination=Destination(
            name='Patient.identifier',
            description=Patient.schema()["properties"]["identifier"]["title"],
            module='Administration',
            title=Patient.schema()["properties"]["identifier"]["title"],
            type=Patient.schema()["properties"]["identifier"]["type"]
        )
    ),

    Map(
        source=Source(
            name='demographic.updated_datetime',
            description=data_dict["clinical"]["demographic"]["properties"]["updated_datetime"]["common"]["description"],
            category=data_dict["clinical"]["demographic"]["category"],
            type=data_dict["clinical"]["demographic"]["properties"]["updated_datetime"]["oneOf"][0]["type"]
        ),
        destination=Destination(
            name='Extension.valueDateTime',
            description=Extension.schema()["properties"]["valueDateTime"]["description"],
            description_url='https://build.fhir.org/datatypes.html#dateTime',
            module='Extensibility',
            title=Extension.schema()["properties"]["valueDateTime"]["title"],
            type=Extension.schema()["properties"]["valueDateTime"]["type"]
        )
    ),

    Map(
        source=Source(
            name='demographic.year_of_birth',
            description=data_dict["clinical"]["demographic"]["properties"]["year_of_birth"]["description"],
            category=data_dict["clinical"]["demographic"]["category"],
            type=data_dict["clinical"]["demographic"]["properties"]["year_of_birth"]["oneOf"][0]["type"]

        ),
        destination=Destination(
            name='Patient.birthDate',
            description=Patient.schema()["properties"]["birthDate"]["title"],
            module='Administration',
            title=Patient.schema()["properties"]["birthDate"]["title"],
            type=Patient.schema()["properties"]["birthDate"]["type"],
            format=str(LiteralString)
        )
    ),

    Map(
        source=Source(
            name='demographic.year_of_death',
            description=data_dict["clinical"]["demographic"]["properties"]["year_of_death"]["description"],
            category=data_dict["clinical"]["demographic"]["category"],
            type=data_dict["clinical"]["demographic"]["properties"]["year_of_death"]["type"]
        ),
        destination=Destination(
            name='Patient.deceasedDateTime',
            description=Patient.schema()["properties"]["deceasedDateTime"]["title"],
            module='Administration',
            title=Patient.schema()["properties"]["deceasedDateTime"]["title"],
            type=Patient.schema()["properties"]["deceasedDateTime"]["type"],
            format=str(LiteralString)
        )
    ),

    Map(
        source=Source(
            name='diagnoses.age_at_diagnosis',
            description=data_dict["clinical"]["diagnosis"]["properties"]["age_at_diagnosis"]["description"],
            category=data_dict["clinical"]["diagnosis"]["category"],
            type=data_dict["clinical"]["diagnosis"]["properties"]["age_at_diagnosis"]["oneOf"][0]["type"]
        ),
        destination=Destination(
            name='Condition.onsetAge',
            description=Condition.schema()["properties"]["onsetAge"]["title"],
            module='Clinical Summary',
            title=Condition.schema()["properties"]["onsetAge"]["title"],
            type=Condition.schema()["properties"]["onsetAge"]["type"],
            format=''
        )
    ),

    Map(
        source=Source(
            name='tissue_source_site.tissue_source_site_id'
        ),
        destination=Destination(
            name='Encounter.id'
        )
    ),

    Map(
        source=Source(
            name='exposures.pack_years_smoked'
        ),
        destination=Destination(
            name='Observation.patient.pack_years_smoked'
        )
    ),

    Map(
        source=Source(
            name='exposures.cigarettes_per_day'
        ),
        destination=Destination(
            name='Observation.patient.cigarettes_per_day'
        )
    ),

    Map(
        source=Source(
            name='exposures.years_smoked'
        ),
        destination=Destination(
            name='Observation.patient.years_smoked'
        )
    ),

    Map(
        source=Source(
            name='exposures.exposure_id'
        ),
        destination=Destination(
            name='Observation.patient.exposure_id'
        )
    ),

    Map(
        source=Source(
            name='exposures.alcohol_history'
        ),
        destination=Destination(
            name='Observation.patient.alcohol_history'
        )
    ),

    Map(
        source=Source(
            name='exposures.alcohol_intensity'
        ),
        destination=Destination(
            name='Observation.patient.alcohol_intensity'
        )
    ),

    Map(
        source=Source(
            name='samples.sample_id'
        ),
        destination=Destination(
            name='Specimen.id.sample'
        )
    ),

    Map(
        source=Source(
            name='samples.composition'
        ),
        destination=Destination(
            name='Observation.sample.composition'
        )
    ),

    Map(
        source=Source(
            name='samples.updated_datetime'
        ),
        destination=Destination(
            name='Observation.sample.updated_datetime'
        )
    ),

    Map(
        source=Source(
            name='samples.is_ffpe'
        ),
        destination=Destination(
            name='Observation.sample.is_ffpe'
        )
    ),

    Map(
        source=Source(
            name='samples.preservation_method'
        ),
        destination=Destination(
            name='Observation.sample.preservation_method'
        )
    ),

    Map(
        source=Source(
            name='samples.portions.portion_id'
        ),
        destination=Destination(
            name='Specimen.id.portion'
        )
    ),

    Map(
        source=Source(
            name='samples.portions.is_ffpe'
        ),
        destination=Destination(
            name='Observation.portions.is_ffpe'
        )
    ),

    Map(
        source=Source(
            name='samples.portions.weight'
        ),
        destination=Destination(
            name='Observation.portions.weight'
        )
    ),

    Map(
        source=Source(
            name='samples.portions.updated_datetime'
        ),
        destination=Destination(
            name='Observation.portion.updated_datetime'
        )
    ),

    Map(
        source=Source(
            name='samples.days_to_collection'
        ),
        destination=Destination(
            name='Specimen.combined.time_indicator_for_sample_pairs'
        )
    ),

    Map(
        source=Source(
            name='samples.portions.analytes.experimental_protocol_type'
        ),
        destination=Destination(
            name='Specimen.processing.method.analyte'
        )
    ),

    Map(
        source=Source(
            name='samples.portions.analytes.analyte_id'
        ),
        destination=Destination(
            name='Specimen.id.analyte'
        )
    ),

    Map(
        source=Source(
            name='samples.portions.analytes.analyte_type'
        ),
        destination=Destination(
            name='Specimen.type.analyte'
        )
    ),

    Map(
        source=Source(
            name='samples.portions.analytes.concentration'
        ),
        destination=Destination(
            name='Observation.analyte.concentration'
        )
    ),

    Map(
        source=Source(
            name='samples.portions.analytes.experimental_protocol_type'
        ),
        destination=Destination(
            name='Observation.analyte.experimental_protocol_type'
        )
    ),

    Map(
        source=Source(
            name='samples.portions.analytes.updated_datetime'
        ),
        destination=Destination(
            name='Observation.analyte.updated_datetime'
        )
    ),

    Map(
        source=Source(
            name='samples.portions.analytes.normal_tumor_genotype_snp_match'
        ),
        destination=Destination(
            name='Observation.analyte.normal_tumor_genotype_snp_match'
        )
    ),

    Map(
        source=Source(
            name='samples.portions.analytes.ribosomal_rna_28s_16s_ratio'
        ),
        destination=Destination(
            name='Observation.analyte.ribosomal_rna_28s_16s_ratio'
        )
    ),

    Map(
        source=Source(
            name='samples.portions.analytes.rna_integrity_number'
        ),
        destination=Destination(
            name='Observation.analyte.rna_integrity_number'
        )
    ),

    Map(
        source=Source(
            name='samples.portions.analytes.spectrophotometer_method'
        ),
        destination=Destination(
            name='Observation.analyte.spectrophotometer_method'
        )
    ),

    Map(
        source=Source(
            name='samples.portions.analytes.a260_a280_ratio'
        ),
        destination=Destination(
            name='Observation.analyte.a260_a280_ratio'
        )
    ),

    Map(
        source=Source(
            name='samples.portions.analytes.aliquots.analyte_type'
        ),
        destination=Destination(
            name='Observation.aliquot.analyte_type'
        )
    ),

    Map(
        source=Source(
            name='samples.portions.analytes.aliquots.center.name'
        ),
        destination=Destination(
            name='Specimen.aliquot.center_name'
        )
    ),

    Map(
        source=Source(
            name='samples.portions.analytes.aliquots.center.short_name'
        ),
        destination=Destination(
            name='Specimen.aliquot.short_name'
        )
    ),

    Map(
        source=Source(
            name='samples.portions.analytes.aliquots.center.namespace'
        ),
        destination=Destination(
            name='Specimen.aliquot.namespace'
        )
    ),

    Map(
        source=Source(
            name='samples.portions.analytes.aliquots.center.id'
        ),
        destination=Destination(
            name='Specimen.aliquot.center_id'
        )
    ),

    Map(
        source=Source(
            name='samples.portions.analytes.aliquots.no_matched_normal_wgs'
        ),
        destination=Destination(
            name='Observation.aliquot.no_matched_normal_wgs'
        )
    ),

    Map(
        source=Source(
            name='samples.portions.analytes.aliquots.no_matched_normal_wxs'
        ),
        destination=Destination(
            name='Observation.aliquot.no_matched_normal_wxs'
        )
    ),

    Map(
        source=Source(
            name='samples.portions.analytes.aliquots.no_matched_normal_low_pass_wgs'
        ),
        destination=Destination(
            name='Observation.aliquot.no_matched_normal_low_pass_wgs'
        )
    ),

    Map(
        source=Source(
            name='samples.portions.analytes.aliquots.no_matched_normal_targeted_sequencing'
        ),
        destination=Destination(
            name='Observation.aliquot.no_matched_normal_targeted_sequencing'
        )
    ),

    Map(
        source=Source(
            name='samples.portions.analytes.aliquots.selected_normal_low_pass_wgs'
        ),
        destination=Destination(
            name='Observation.aliquot.selected_normal_low_pass_wgs'
        )
    ),

    Map(
        source=Source(
            name='samples.portions.analytes.aliquots.selected_normal_targeted_sequencing'
        ),
        destination=Destination(
            name='Observation.aliquot.selected_normal_targeted_sequencing'
        )
    ),

    Map(
        source=Source(
            name='samples.portions.analytes.aliquots.selected_normal_wgs'
        ),
        destination=Destination(
            name='Observation.aliquot.selected_normal_wgs'
        )
    ),

    Map(
        source=Source(
            name='samples.portions.analytes.aliquots.selected_normal_wxs'
        ),
        destination=Destination(
            name='Observation.aliquot.selected_normal_wxs'
        )
    ),

    Map(
        source=Source(
            name='samples.portions.analytes.aliquots.concentration'
        ),
        destination=Destination(
            name='Observation.aliquot.concentration'
        )
    ),

    Map(
        source=Source(
            name='samples.portions.analytes.aliquots.aliquot_volume'
        ),
        destination=Destination(
            name='Observation.aliquot.aliquot_volume'
        )
    ),

    Map(
        source=Source(
            name='samples.portions.analytes.aliquots.aliquot_quantity'
        ),
        destination=Destination(
            name='Observation.aliquot.aliquot_quantity'
        )
    ),

    Map(
        source=Source(
            name='samples.portions.analytes.aliquots.no_matched_normal_low_pass_wgs'
        ),
        destination=Destination(
            name='Observation.aliquot.no_matched_normal_low_pass_wgs'
        )
    ),

    Map(
        source=Source(
            name='samples.portions.analytes.aliquots.no_matched_normal_wgs'
        ),
        destination=Destination(
            name='Observation.aliquot.no_matched_normal_wgs'
        )
    ),

    Map(
        source=Source(
            name='samples.portions.analytes.aliquots.no_matched_normal_targeted_sequencing'
        ),
        destination=Destination(
            name='Observation.aliquot.no_matched_normal_targeted_sequencing'
        )
    ),

    Map(
        source=Source(
            name='samples.portions.analytes.aliquots.no_matched_normal_wxs'
        ),
        destination=Destination(
            name='Observation.aliquot.no_matched_normal_wxs'
        )
    ),

    Map(
        source=Source(
            name='samples.portions.analytes.aliquots.updated_datetime'
        ),
        destination=Destination(
            name='Observation.aliquot.updated_datetime'
        )
    ),

    Map(
        source=Source(
            name='samples.portions.analytes.aliquots.aliquot_id'
        ),
        destination=Destination(
            name='Specimen.id.aliquot'
        )
    ),

    Map(
        source=Source(
            name='samples.portions.slides.slide_id'
        ),
        destination=Destination(
            name='ImagingStudy.id'
        )
    ),

    Map(
        source=Source(
            name='samples.portions.slides.section_location'
        ),
        destination=Destination(
            name='Observation.slides.section_location'
        )
    ),

    Map(
        source=Source(
            name='samples.sample_type'
        ),
        destination=Destination(
            name='Specimen.type.sample'
        )
    ),

    Map(
        source=Source(
            name='samples.preservation_method'
        ),
        destination=Destination(
            name='Specimen.processing.method'
        )
    ),

    Map(
        source=Source(
            name='diagnoses.ajcc_pathologic_stage'
        ),
        destination=Destination(
            name='Condition.stage_ajcc_pathologic_stage'
        )
    ),

    Map(
        source=Source(
            name='diagnoses.ajcc_pathologic_t'
        ),
        destination=Destination(
            name='Condition.stage_ajcc_pathologic_t'
        )
    ),

    Map(
        source=Source(
            name='diagnoses.ajcc_pathologic_n'
        ),
        destination=Destination(
            name='Condition.stage_ajcc_pathologic_n'
        )
    ),

    Map(
        source=Source(
            name='diagnoses.ajcc_pathologic_m'
        ),
        destination=Destination(
            name='Condition.stage_ajcc_pathologic_m'
        )
    ),

    Map(
        source=Source(
            name='diagnoses.ajcc_clinical_t'
        ),
        destination=Destination(
            name='Condition.stage_ajcc_clinical_t'
        )
    ),

    Map(
        source=Source(
            name='diagnoses.ajcc_clinical_n'
        ),
        destination=Destination(
            name='Condition.stage_ajcc_clinical_n'
        )
    ),

    Map(
        source=Source(
            name='diagnoses.ajcc_clinical_m'
        ),
        destination=Destination(
            name='Condition.stage_ajcc_clinical_m'
        )
    ),

    Map(
        source=Source(
            name='diagnoses.tumor_grade'
        ),
        destination=Destination(
            name='Observation.code.nci_tumor_grade'
        )
    ),

    Map(
        source=Source(
            name='diagnoses.treatments.treatment_id'
        ),
        destination=Destination(
            name='MedicationAdministration.id'
        )
    ),

    Map(
        source=Source(
            name='diagnoses.treatments.submitter_id'
        ),
        destination=Destination(
            name='MedicationAdministration.identifier'
        )
    ),

    Map(
        source=Source(
            name='diagnoses.treatments.treatment_or_therapy'
        ),
        destination=Destination(
            name='MedicationAdministration.status'
        )
    ),

    Map(
        source=Source(
            name='diagnoses.treatments.treatment_type'
        ),
        destination=Destination(
            name='MedicationAdministration.treatment_type'
        )
    ),

    Map(
        source=Source(
            name='diagnoses.treatments.therapeutic_agents'
        ),
        destination=Destination(
            name='Medication.code'
        )
    ),

    Map(
        source=Source(
            name='diagnoses.diagnosis_id'
        ),
        destination=Destination(
            name='Condition.id'
        )
    ),

    Map(
        source=Source(
            name='diagnosis.tissue_or_organ_of_origin'
        ),
        destination=Destination(
            name='Condition.bodySite'
        )
    ),

    Map(
        source=Source(
            name='diagnoses.primary_diagnosis'
        ),
        destination=Destination(
            name='Condition.code_primary_diagnosis'
        )
    ),

    Map(
        source=Source(
            name='diagnoses.prior_treatment'
        ),
        destination=Destination(
            name='Condition.prior_treatment'
        )
    ),

    Map(
        source=Source(
            name='diagnoses.icd_10_code'
        ),
        destination=Destination(
            name='Condition.coding_icd_10_code'
        )
    ),

    Map(
        source=Source(
            name='diagnoses.primary_diagnoses'
        ),
        destination=Destination(
            name='Condition.display'
        )
    ),

    Map(
        source=Source(
            name='diagnoses.days_to_death'
        ),
        destination=Destination(
            name='Observation.survey.days_to_death'
        )
    ),

    Map(
        source=Source(
            name='diagnoses.days_to_last_follow_up'
        ),
        destination=Destination(
            name='Observation.survey.days_to_last_follow_up'
        )
    ),

    Map(
        source=Source(
            name='diagnoses.updated_datetime'
        ),
        destination=Destination(
            name='Observation.survey.updated_datetime'
        )
    ),

    Map(
        source=Source(
            name='submitter_diagnosis_ids'
        ),
        destination=Destination(
            name='Condition.identifier'
        )
    ),

    # project Maps -----------------------------------------------------
    Map(
        source=Source(
            name='project',
            description=data_dict['administrative']['project']['description'],
            category=data_dict['administrative']['project']['category'],
            type=data_dict['administrative']['project']['type']
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
            name='project.program',
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
            name='project.name',
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
            name='project.project_id',
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
            name='project.dbgap_accession_number',
            description=data_dict['administrative']['project']['properties']['dbgap_accession_number']['description'],
            category=data_dict['administrative']['project']['category'],
            type=data_dict['administrative']['project']['properties']['dbgap_accession_number']['type']
        ),
        destination=Destination(
            name="ResearchStudy.identifier",
            description=ResearchStudy.schema()['properties']['identifier']['description'],
            module='Administration',
            title=ResearchStudy.schema()['properties']['identifier']['title'],
            type=ResearchStudy.schema()['properties']['identifier']['items']['type']
        )
    ),

    Map(
        source=Source(
            name='project.disease_type',
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
            name='project.primary_site',
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
            name='project.released',
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
            name='project.state',
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
            name='project.program.dbgap_accession_number',
            description=data_dict['administrative']['program']['properties']['dbgap_accession_number']['description'],
            category=data_dict['administrative']['program']['category'],
            type=data_dict['administrative']['program']['properties']['dbgap_accession_number']['type']
        ),
        destination=Destination(
            name="ResearchStudy.identifier",
            description=ResearchStudy.schema()['properties']['identifier']['description'],
            module='Administration',
            title=ResearchStudy.schema()['properties']['identifier']['title'],
            type=ResearchStudy.schema()['properties']['identifier']['items']['type'],
            reference=[Reference(reference_type=str(ResearchStudy))]
        )
    ),

    Map(
        source=Source(
            name='project.program.name',
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
            name='project.program.program_id',
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
    )
]

"""
proceed with caution this code changes the state of current files under mapping
"""

# out_path = os.path.join(package_dir, 'mapping', 'case.json')
out_path = '../../mapping/case.json'
valid_case_maps = [Map.model_validate(c) for c in case_maps]
[case_schema.mappings.append(i) for i in valid_case_maps]
utils.validate_and_write(case_schema, out_path=out_path, update=True, generate=False)
