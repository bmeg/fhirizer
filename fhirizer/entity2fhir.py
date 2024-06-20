import os
import re
import uuid
import json
import copy
import orjson
from iteration_utilities import unique_everseen
from fhir.resources.identifier import Identifier
from fhir.resources.researchstudy import ResearchStudy
from fhir.resources.codeableconcept import CodeableConcept
from fhir.resources.researchstudy import ResearchStudyRecruitment
from fhir.resources.extension import Extension
from fhir.resources.reference import Reference
from fhir.resources.condition import Condition, ConditionStage
from fhir.resources.observation import Observation
from fhir.resources.encounter import Encounter
from fhir.resources.specimen import Specimen, SpecimenProcessing, SpecimenCollection
from fhir.resources.patient import Patient
from fhir.resources.researchsubject import ResearchSubject
from fhir.resources.imagingstudy import ImagingStudy, ImagingStudySeries
from fhir.resources.procedure import Procedure
from fhir.resources.medicationadministration import MedicationAdministration
from fhir.resources.bodystructure import BodyStructure, BodyStructureIncludedStructure
from fhir.resources.medication import Medication
from fhir.resources.codeablereference import CodeableReference
from fhir.resources.documentreference import DocumentReference, DocumentReferenceContent, \
    DocumentReferenceContentProfile
from fhir.resources.attachment import Attachment
from fhir.resources.age import Age
from fhirizer import utils
from datetime import datetime
import icd10
import importlib.resources
from pathlib import Path
from uuid import uuid3, NAMESPACE_DNS

disease_types = utils._read_json(str(Path(importlib.resources.files(
    'fhirizer').parent / 'resources' / 'gdc_resources' / 'content_annotations' / 'case' / 'disease_types.json')))
primary_sites = utils._read_json(str(Path(importlib.resources.files(
    'fhirizer').parent / 'resources' / 'gdc_resources' / 'content_annotations' / 'case' / 'primary_sites.json')))
race = utils._read_json(str(Path(importlib.resources.files(
    'fhirizer').parent / 'resources' / 'gdc_resources' / 'content_annotations' / 'demographic' / 'race.json')))
ethnicity = utils._read_json(str(Path(importlib.resources.files(
    'fhirizer').parent / 'resources' / 'gdc_resources' / 'content_annotations' / 'demographic' / 'ethnicity.json')))
gender = utils._read_json(str(Path(importlib.resources.files(
    'fhirizer').parent / 'resources' / 'gdc_resources' / 'content_annotations' / 'demographic' / 'gender.json')))
data_dict = utils.load_data_dictionary(path=utils.DATA_DICT_PATH)
cancer_pathological_staging = utils._read_json(str(Path(importlib.resources.files(
    'fhirizer').parent / 'resources' / 'gdc_resources' / 'content_annotations' / 'diagnosis' / 'cancer_pathological_staging.json')))
ncit2mondo = utils.ncit2mondo(
    str(Path(importlib.resources.files('fhirizer').parent / 'resources' / 'ncit2mondo.json.gz')))
biospecimen_observation = utils._read_json(str(Path(importlib.resources.files(
    'fhirizer').parent / 'resources' / 'gdc_resources' / 'content_annotations' / 'biospecimen' / 'biospecimen_observation.json')))
biospecimen_imaging_observation = utils._read_json(str(Path(importlib.resources.files(
    'fhirizer').parent / 'resources' / 'gdc_resources' / 'content_annotations' / 'biospecimen' / 'biospecimen_imaging_observation.json')))
social_histody_smoking_observation = utils._read_json(str(Path(importlib.resources.files(
    'fhirizer').parent / 'resources' / 'gdc_resources' / 'content_annotations' / 'case' / 'social_history_smoking_observations.json')))
social_histody_alcohol_observation = utils._read_json(str(Path(importlib.resources.files(
    'fhirizer').parent / 'resources' / 'gdc_resources' / 'content_annotations' / 'case' / 'social_history_alcohol_observations.json')))
aliquot = utils._read_json(str(Path(importlib.resources.files(
    'fhirizer').parent / 'resources' / 'gdc_resources' / 'content_annotations' / 'biospecimen' / 'aliquot.json')))


def assign_fhir_for_project(project, disease_types=disease_types):
    project_id = "GDC"
    NAMESPACE_GDC = uuid3(NAMESPACE_DNS, 'gdc.cancer.gov')

    # create ResearchStudy
    rs = ResearchStudy.construct()
    """
    if 'ResearchStudyProgressStatus.actual' in project.keys() and project['ResearchStudyProgressStatus.actual']:
        rs.status = "-".join([project['ResearchStudy.status'], "released"])
    else:
        rs.status = project['ResearchStudy.status']
    """
    rs.status = "active"  # temp harmonization
    pl = []
    if 'ResearchStudy.id' in project.keys() and project['ResearchStudy.id'] in ["EXCEPTIONAL_RESPONDERS-ER",
                                                                                "CDDP_EAGLE-1"]:
        pr_ident = Identifier(**{"system": "".join(["https://gdc.cancer.gov/", "program_id"]),
                                 "value": project['ResearchStudy']['ResearchStudy.id']})
        pl.append(pr_ident)

        rs.id = utils.mint_id(
            identifier=pr_ident,
            resource_type="ResearchStudy",
            project_id=project_id,
            namespace=NAMESPACE_GDC)

    else:
        p_ident = Identifier(**{"system": "".join(["https://gdc.cancer.gov/", "project_id"]),
                                "value": project['ResearchStudy.id']})
        rs.id = utils.mint_id(
            identifier=p_ident,
            resource_type="ResearchStudy",
            project_id=project_id,
            namespace=NAMESPACE_GDC)
        pl.append(p_ident)

    rs.name = project['ResearchStudy.name']

    if 'ResearchStudy.identifier' in project.keys() and project['ResearchStudy.identifier']:
        ident = Identifier.construct()
        ident.value = project['ResearchStudy.identifier']
        ident.system = "".join(["https://gdc.cancer.gov/", "project"])
        pl.append(ident)
        rs.identifier = pl

    l = []
    for c in project['ResearchStudy.condition']:
        for d in disease_types:
            if c in d['value']:
                if d['sctid']:
                    l.append({'system': "http://snomed.info/sct", 'display': d['value'], 'code': d['sctid']})

    if l:
        cc = CodeableConcept.construct()
        # syntax
        # cc.coding = [{'system': "http://snomed.info/sct", 'code': "115219005", 'display': "Acinar Cell Neoplasms"}]
        cc.coding = l
        rs.condition = [cc]

    # create ResearchStudy -- partOf --> ResearchStudy
    rs_parent = ResearchStudy.construct()

    # assign required fields first
    rs_parent.status = project['ResearchStudy.status']  # child's status?
    rs_parent.id = utils.mint_id(
        identifier=Identifier(**{"system": "".join(["https://gdc.cancer.gov/", "program_id"]),
                                 "value": project['ResearchStudy']['ResearchStudy.id']}),
        resource_type="ResearchStudy",
        project_id=project_id,
        namespace=NAMESPACE_GDC)

    rs_parent.name = project['ResearchStudy']['ResearchStudy.name']

    if 'ResearchStudy.identifier' in project['ResearchStudy'].keys() and project['ResearchStudy'][
        'ResearchStudy.identifier']:
        ident_parent = Identifier.construct()
        ident_parent.value = project['ResearchStudy']['ResearchStudy.identifier']
        ident_parent.system = "".join(["https://gdc.cancer.gov/", "project"])
        rs_parent.identifier = [ident_parent]

    if 'summary' in project.keys():
        rsr = ResearchStudyRecruitment.construct()
        rsr.actualNumber = project['summary']['ResearchStudyRecruitment.actualNumber']
        rs.recruitment = rsr

        e = Extension.construct()
        e.valueUnsignedInt = project['summary'][
            'Extension.valueUnsignedInt']  # total documentReference Count - better association?
        rs.extension = [e]

    ref = Reference(**{"reference": "/".join(["ResearchStudy", rs_parent.id])})
    rs.partOf = [ref]
    #  condition -- subject --> patient <--subject-- researchsubject -- study --> researchstudy -- partOf --> researchstudy

    return {'ResearchStudy': rs.json(), "ResearchStudy.partOf": rs_parent.json(), 'ResearchStudy_obj': rs,
            "ResearchStudy.partOf_obj": rs_parent}


# projects_path="./tests/fixtures/project/project_key.ndjson"


def create_imaging_study(slide, patient, sample):
    project_id = "GDC"
    NAMESPACE_GDC = uuid3(NAMESPACE_DNS, 'gdc.cancer.gov')

    img = ImagingStudy.construct()
    img.status = "available"

    img_identifier = Identifier(
        **{"system": "".join(["https://gdc.cancer.gov/", "slide_id"]),
           "value": slide["ImagingStudy.id"]})
    img.id = utils.mint_id(identifier=img_identifier, resource_type="ImagingStudy",
                           project_id=project_id,
                           namespace=NAMESPACE_GDC)

    img.subject = Reference(**{"reference": "/".join(["Patient", patient.id])})

    img_series = ImagingStudySeries.construct()
    img_series.uid = sample.id

    # https://hl7.org/fhir/R4/codesystem-dicom-dcim.html#dicom-dcim-SM
    # https://dicom.nema.org/medical/dicom/current/output/chtml/part16/chapter_D.html
    modality = CodeableConcept.construct()
    modality.coding = [
        {"system": " http://dicom.nema.org/resources/ontology/DCM", "display": "Slide Microscopy", "code": "SM"}]
    img_series.modality = modality

    img_series.specimen = [Reference(**{"reference": "/".join(["Specimen", sample.id])})]
    img.series = [img_series]

    return img


def specimen_exists(specimen_id, specimen_list):
    return any(specimen.id == specimen_id for specimen in specimen_list)


def add_specimen(dat, name, id_key, has_parent, parent, patient, all_fhir_specimens):
    if name in dat.keys():
        for sample in dat[name]:
            if id_key in sample.keys():
                fhir_specimen = Specimen.construct()
                fhir_specimen.id = sample[id_key]
                fhir_specimen.subject = Reference(**{"reference": "/".join(["Patient", patient.id])})
                if has_parent:
                    fhir_specimen.parent = [Reference(**{"reference": "/".join(["Specimen", parent.id])})]
                if fhir_specimen not in all_fhir_specimens:
                    all_fhir_specimens.append(fhir_specimen)


def project_gdc_to_fhir_ndjson(out_dir, projects_path):
    projects = utils.load_ndjson(projects_path)
    all_rs = [assign_fhir_for_project(project=p, disease_types=disease_types) for p in projects]
    research_study = [orjson.loads(rs['ResearchStudy_obj'].json()) for rs in all_rs]
    research_study_parent = [orjson.loads(rs['ResearchStudy.partOf_obj'].json()) for rs in all_rs]
    rs_e2f = research_study + list(
        unique_everseen(research_study_parent))  # ResearchStudy -- *...1  partOf -> ResearchStudy

    with open("".join([out_dir, "/ResearchStudy.ndjson"]), 'w') as file:
        file.write('\n'.join(map(json.dumps, rs_e2f)))
    print("Successfully converted GDC projetcs/programs to FHIR's models ndjson file!")


# Case ---------------------------------------------------------------
# load case mapped key values
# cases = utils.load_ndjson("./tests/fixtures/case/case_key.ndjson")
# case = cases[0]

def assign_fhir_for_case(case, disease_types=disease_types, primary_sites=primary_sites, data_dict=data_dict,
                         race=race, ethnicity=ethnicity):
    # create patient **
    project_id = "GDC"
    NAMESPACE_GDC = uuid3(NAMESPACE_DNS, 'gdc.cancer.gov')

    patient = Patient.construct()

    patient_id_identifier = Identifier.construct()
    patient_id_identifier.value = case['Patient.id']
    patient_id_identifier.system = "".join(["https://gdc.cancer.gov/", "case_id"])

    patient.id = utils.mint_id(identifier=patient_id_identifier, resource_type="Patient", project_id=project_id,
                               namespace=NAMESPACE_GDC)

    treatments_med = []
    treatments_medadmin = []
    procedure = None
    observations = []
    condition_observations = []

    if 'Patient.identifier' in case.keys() and case['Patient.identifier'] and re.match(r"^[A-Za-z0-9\-.]+$",
                                                                                       case['Patient.identifier']):
        patient_submitter_id_identifier = Identifier.construct()
        patient_submitter_id_identifier.value = case['Patient.identifier']
        patient_submitter_id_identifier.system = "".join(["https://gdc.cancer.gov/", "case_submitter_id"])

        patient.identifier = [patient_submitter_id_identifier, patient_id_identifier]
    else:
        patient.identifier = [patient_id_identifier]

    if 'demographic' in case.keys() and 'Patient.birthDate' in case['demographic']:
        # converted to https://build.fhir.org/datatypes.html#date / NOTE: month and day missing in GDC
        if case['demographic']['Patient.birthDate']:
            patient.birthDate = datetime(int(case['demographic']['Patient.birthDate']), 1, 1)

    patient_gender = None
    if 'demographic' in case.keys() and 'Patient.gender' in case['demographic']:
        for g in gender:
            if g['value'] == case['demographic']['Patient.gender']:
                patient_gender = g['fhir_display']

    patient.gender = patient_gender

    race_ethnicity_sex = []
    if patient_gender:
        female = {"url": "http://hl7.org/fhir/us/core/StructureDefinition/us-core-birthsex", "valueCode": "F"}
        male = {"url": "http://hl7.org/fhir/us/core/StructureDefinition/us-core-birthsex", "valueCode": "M"}

        if patient_gender == 'female':
            race_ethnicity_sex.append(female)
        elif patient_gender == 'male':
            race_ethnicity_sex.append(male)

    if 'demographic' in case.keys() and 'Patient.deceasedDateTime' in case['demographic']:
        patient.deceasedDateTime = case['demographic']['Patient.deceasedDateTime']
    else:
        if 'demographic' in case.keys() and 'Patient.deceasedBoolean' in case['demographic']:
            if case['demographic']['Patient.deceasedBoolean'] == "Alive":
                patient.deceasedBoolean = False
            elif case['demographic']['Patient.deceasedBoolean'] == "Dead":
                patient.deceasedBoolean = True

    if 'demographic' in case.keys() and 'Extension.extension:USCoreRaceExtension' in case['demographic'].keys():
        #  race and ethnicity
        # https://build.fhir.org/ig/HL7/US-Core/ValueSet-omb-race-category.html
        # https://build.fhir.org/ig/HL7/US-Core/ValueSet-omb-ethnicity-category.html

        race_ext = Extension.construct()
        race_ext.url = "http://hl7.org/fhir/us/core/StructureDefinition/us-core-race"

        race_code = ""
        race_display = ""
        race_system = ""
        for r in race:
            if r['value'] in case['demographic']['Extension.extension:USCoreRaceExtension'] and re.match(
                    r"[ \r\n\t\S]+", r['ombCategory-code']):
                race_code = r['ombCategory-code']
                race_system = r['ombCategory-system']
                race_display = r['ombCategory-display']
                gdc_race_code = r['term_id']
                gdc_race_system = r['description_url']
                gdc_race_display = r['value']
                race_ext.valueString = r['ombCategory-display']

        if race_code:
            race_ext.extension = [{"url": "ombCategory",
                                   "valueCoding": {
                                       "system": race_system,
                                       "code": race_code,
                                       "display": race_display
                                   }},
                                  {"url": "https://ncit.nci.nih.gov",
                                   "valueCoding": {
                                       "system": gdc_race_system,
                                       "code": gdc_race_code,
                                       "display": gdc_race_display
                                   }}]
        race_ethnicity_sex.append(race_ext)

    if 'demographic' in case.keys() and 'Extension:extension.USCoreEthnicity' in case['demographic'].keys():
        ethnicity_ext = Extension.construct()
        ethnicity_ext.url = "http://hl7.org/fhir/us/core/StructureDefinition/us-core-ethnicity"

        ethnicity_code = ""
        ethnicity_display = ""
        ethnicity_system = ""
        for e in ethnicity:
            if e['value'] in case['demographic']['Extension:extension.USCoreEthnicity']:
                ethnicity_code = e['ombCategory-code']
                ethnicity_system = e['ombCategory-system']
                ethnicity_display = e['ombCategory-display']
                gdc_ethnicity_code = e['term_id']
                gdc_ethnicity_system = e['description_url']
                gdc_ethnicity_display = e['value']
                ethnicity_ext.valueString = e['ombCategory-display']
                ethnicity_ext.valueString = e['value']

        if ethnicity_code:
            ethnicity_ext.extension = [{"url": "ombCategory",
                                        "valueCoding": {
                                            "system": ethnicity_system,
                                            "code": ethnicity_code,
                                            "display": ethnicity_display
                                        }},
                                       {"url": "https://ncit.nci.nih.gov",
                                        "valueCoding": {
                                            "system": gdc_ethnicity_system,
                                            "code": gdc_ethnicity_code,
                                            "display": gdc_ethnicity_display
                                        }}]

            race_ethnicity_sex.append(ethnicity_ext)

    if 'demographic' in case.keys() and 'Patient.extension.age' in case['demographic'].keys():
        # alternative way(s) of defining age vs birthDate in patient field
        # "url": "http://hl7.org/fhir/us/icsr-ae-reporting/StructureDefinition/icsr-ext-ageattimeofonset"
        if case['demographic']['Patient.extension.age']:
            age_at_index = case['demographic']['Patient.extension.age']
            age = {"url": "http://hl7.org/fhir/SearchParameter/patient-extensions-Patient-age",
                   'valueQuantity': {"value": age_at_index}}
            race_ethnicity_sex.append(age)

    if race_ethnicity_sex:
        patient.extension = race_ethnicity_sex

    # gdc project for patient
    project_relations = assign_fhir_for_project(project=case['ResearchStudy'], disease_types=disease_types)
    study_ref = Reference(**{"reference": "/".join(["ResearchStudy", project_relations['ResearchStudy_obj'].id])})
    subject_ref = Reference(**{"reference": "/".join(["Patient", patient.id])})

    # create researchSubject to link Patient --> ResearchStudy
    research_subject = ResearchSubject.construct()
    # research_subject.status = "".join(['unknown-', case['ResearchSubject.status']])
    research_subject.status = "active"
    research_subject.study = study_ref
    research_subject.subject = subject_ref
    research_subject.id = utils.mint_id(
        identifier=patient_id_identifier,
        resource_type="ResearchSubject",
        project_id=project_id,
        namespace=NAMESPACE_GDC)

    # create Encounter **
    encounter = None
    encounter_ref = None
    if 'tissue_source_site' in case.keys():
        encounter_tss_id = case['tissue_source_site']['Encounter.id']

        encounter = Encounter.construct()
        encounter.status = 'completed'

        encounter.id = utils.mint_id(
            identifier=Identifier(**{"system": "".join(["https://gdc.cancer.gov/", "tissue_source_site"]),
                                     "value": case['tissue_source_site']['Encounter.id']}),
            resource_type="Encounter",
            project_id=project_id,
            namespace=NAMESPACE_GDC)

        encounter.subject = subject_ref
        encounter_ref = Reference(**{"reference": "/".join(["Encounter", encounter.id])})

    observation = None
    observation_ref = None
    gdc_condition_annotation = None
    condition_codes_list = []
    if 'diagnoses' in case.keys() and isinstance(case['diagnoses'], list):
        case['diagnoses'] = {k: v for d in case['diagnoses'] for k, v in d.items()}

    if 'diagnoses' in case.keys() and 'Condition.id' in case['diagnoses'].keys():
        # create Observation **
        observation = Observation.construct()
        observation.status = 'final'

        observation_identifier = Identifier(**{"system": "".join(["https://gdc.cancer.gov/", "diagnosis_id"]),
                                               "value": case['diagnoses']['Condition.id']})
        observation.id = utils.mint_id(identifier=[observation_identifier, patient_id_identifier],
                                       resource_type="Observation",
                                       project_id=project_id,
                                       namespace=NAMESPACE_GDC)

        observation.subject = subject_ref
        observation.category = [{
            "coding": [
                {
                    "system": "http://terminology.hl7.org/CodeSystem/observation-category",
                    "code": "exam",
                    "display": "exam"
                }
            ]
        }]

        if encounter_ref:
            observation.encounter = encounter_ref

        observation_code = CodeableConcept.construct()
        if 'Condition.coding_icd_10_code' in case['diagnoses']:
            system = "https://terminology.hl7.org/5.1.0/NamingSystem-icd10CM.html"
            code = case['diagnoses']['Condition.coding_icd_10_code']
            icd10code = icd10.find(case['diagnoses']['Condition.coding_icd_10_code'])
            if icd10code:
                display = icd10code.description
                icd10_annotation = {'system': system, 'display': display, 'code': code}
                condition_codes_list.append(icd10_annotation)

        # not all conditions of GDC have enumDef for it's resource code/system in data dictionary
        if 'Condition.code_primary_diagnosis' in case['diagnoses'].keys() and case['diagnoses'][
            'Condition.code_primary_diagnosis']:
            if case['diagnoses']['Condition.code_primary_diagnosis'] in \
                    data_dict["clinical"]["diagnosis"]["properties"]["primary_diagnosis"]["enumDef"].keys():
                diagnosis_display = case['diagnoses']['Condition.code_primary_diagnosis']
                ncit_condition_display = \
                    data_dict["clinical"]["diagnosis"]["properties"]["primary_diagnosis"]["enumDef"][diagnosis_display][
                        "termDef"]["term"]
                ncit_condition_code = \
                    data_dict["clinical"]["diagnosis"]["properties"]["primary_diagnosis"]["enumDef"][diagnosis_display][
                        "termDef"]["term_id"]
                ncit_condition = {"system": "https://ncit.nci.nih.gov", "display": ncit_condition_display,
                                  "code": ncit_condition_code}
                condition_codes_list.append(ncit_condition)

                mondo = [d["mondo_id"] for d in ncit2mondo if d["ncit_id"] == ncit_condition_code]
                if mondo:
                    mondo_code = mondo[0]
                    mondo_display = ncit_condition_display
                    mondo_coding = {'system': "https://www.ebi.ac.uk/ols4/ontologies/mondo", 'display': mondo_display,
                                    'code': mondo_code}
                    condition_codes_list.append(mondo_coding)

        # required placeholder
        if not condition_codes_list:
            loinc_annotation = {'system': "https://loinc.org/", 'display': "replace-me", 'code': "000000"}
            condition_codes_list.append(loinc_annotation)

        observation_code.coding = condition_codes_list
        observation.code = observation_code
        observation_ref = Reference(**{"reference": "/".join(["Observation", observation.id])})

    survey_updated_datetime_component = None
    if 'diagnoses' in case.keys() and "Observation.survey.updated_datetime" in case['diagnoses'].keys() and \
            case['diagnoses'][
                "Observation.survey.updated_datetime"]:
        survey_updated_datetime_component = utils.get_component('updated_datetime', value=case['diagnoses'][
            "Observation.survey.updated_datetime"],
                                                                component_type='dateTime',
                                                                system="https://gdc.cancer.gov/demographic")

    obs_survey = []
    if 'diagnoses' in case.keys() and 'Observation.survey.days_to_death' in case['diagnoses'].keys() and \
            case['diagnoses'][
                'Observation.survey.days_to_death']:

        observation_days_to_death_identifier = Identifier(
            **{"system": "".join(["https://gdc.cancer.gov/", "days_to_death"]),
               "value": case['diagnoses']['Observation.survey.days_to_death']})
        observation_days_to_death_id = utils.mint_id(
            identifier=[observation_days_to_death_identifier, patient_id_identifier], resource_type="Observation",
            project_id=project_id,
            namespace=NAMESPACE_GDC)

        days_to_death = {
            "resourceType": "Observation",
            "id": observation_days_to_death_id,
            "status": "final",
            "category": [
                {
                    "coding": [
                        {
                            "system": "http://terminology.hl7.org/CodeSystem/observation-category",
                            "code": "survey",
                            "display": "survey"
                        }
                    ]
                }
            ],
            "code": {
                "coding": [
                    {
                        "system": "https://ontobee.org/",
                        "code": "NCIT_C156419",
                        "display": "Days between Diagnosis and Death"
                    }
                ]
            },
            "subject": {
                "reference": "/".join(["Patient", patient.id])
            },
            "focus": [{
                "reference": "/".join(["Patient", patient.id])
            }],
            "valueQuantity": {
                "value": int(case['diagnoses'][
                                 'Observation.survey.days_to_death']),
                "unit": "days",
                "system": "http://unitsofmeasure.org",
                "code": "d"
            }
        }
        if survey_updated_datetime_component:
            days_to_death['component'] = [survey_updated_datetime_component]
        obs_survey.append(days_to_death)

    if 'diagnoses' in case.keys() and 'Observation.survey.days_to_last_follow_up' in case['diagnoses'].keys() and \
            case['diagnoses'][
                'Observation.survey.days_to_last_follow_up']:

        observation_days_to_last_follow_up_identifier = Identifier(
            **{"system": "".join(["https://gdc.cancer.gov/", "days_to_last_follow_up"]),
               "value": case['diagnoses']['Observation.survey.days_to_last_follow_up']})
        observation_days_to_last_follow_up_id = utils.mint_id(
            identifier=[observation_days_to_last_follow_up_identifier, patient_id_identifier],
            resource_type="Observation",
            project_id=project_id,
            namespace=NAMESPACE_GDC)
        days_to_last_follow_up = {
            "resourceType": "Observation",
            "id": observation_days_to_last_follow_up_id,
            "status": "final",
            "category": [
                {
                    "coding": [
                        {
                            "system": "http://terminology.hl7.org/CodeSystem/observation-category",
                            "code": "survey",
                            "display": "survey"
                        }
                    ]
                }
            ],
            "code": {
                "coding": [
                    {
                        "system": "https://ontobee.org/",
                        "code": "NCIT_C181065",
                        "display": "Number of Days Between Index Date and Last Follow Up"
                    }
                ]
            },
            "subject": {
                "reference": "/".join(["Patient", patient.id])
            },
            "focus": [{
                "reference": "/".join(["Patient", patient.id])
            }],
            "valueQuantity": {
                "value": int(case['diagnoses']['Observation.survey.days_to_last_follow_up']),
                "unit": "days",
                "system": "http://unitsofmeasure.org",
                "code": "d"
            }
        }
        if survey_updated_datetime_component:
            days_to_last_follow_up['component'] = [survey_updated_datetime_component]
        obs_survey.append(days_to_last_follow_up)

    condition = None  # normal tissue don't/shouldn't  have diagnoses or condition
    body_structure = None
    if 'diagnoses' in case.keys() and 'Condition.id' in case['diagnoses'].keys():
        # create Condition - for each diagnosis_id there is. relation: condition -- assessment --> observation
        condition = Condition.construct()
        condition_identifier = Identifier(**{"system": "".join(["https://gdc.cancer.gov/", "diagnosis_id"]),
                                             "value": case['diagnoses']['Condition.id']})
        condition.id = utils.mint_id(identifier=condition_identifier, resource_type="Condition", project_id=project_id,
                                     namespace=NAMESPACE_GDC)

        condition.category = [CodeableConcept(**{"coding": [{
            "system": "http://terminology.hl7.org/CodeSystem/condition-category",
            "code": "encounter-diagnosis",
            "display": "Encounter Diagnosis"
            },
            {
                "system": "http://snomed.info/sct",
                "code": "439401001",
                "display": "Diagnosis"
            }]})]

        if 'Condition.identifier' in case.keys() and case['Condition.identifier']:
            condition.identifier = [Identifier(**{"value": case['Condition.identifier'][0], "system": "".join(
                ["https://gdc.cancer.gov/", "submitter_diagnosis_ids"])})]

        if gdc_condition_annotation:
            cc = CodeableConcept.construct()
            cc.coding = [gdc_condition_annotation]
            condition.code = cc

        condition_clinicalstatus_code = CodeableConcept.construct()
        condition_clinicalstatus_code.coding = [
            {"system": "http://terminology.hl7.org/CodeSystem/condition-clinical", "display": "unknown",
             "code": "unknown"}]
        condition.clinicalStatus = condition_clinicalstatus_code

        condition.subject = subject_ref
        condition.encounter = encounter_ref

        if 'diagnoses' in case.keys() and 'Condition.onsetAge' in case['diagnoses'].keys() and case['diagnoses'][
            'Condition.onsetAge']:
            # https://build.fhir.org/valueset-age-units.html
            condition.onsetAge = {
                "value": case['diagnoses']['Condition.onsetAge'],
                "unit": "days",
                "system": "http://unitsofmeasure.org",
                "code": "d"
            }

        # condition.bodySite <-- primary_site snomed
        l_body_site = []
        bd_coding = []
        body_struct = None
        for body_site in case['ResearchStudy']['Condition.bodySite']:
            # print("body_site", body_site)
            for p in primary_sites:
                if not 'sctid' in p.keys():
                    code = "0000"
                elif not p['sctid']:
                    code = "0000"
                else:
                    code = p['sctid']
                if body_site in p['value'] and 'sctid' in p.keys():
                    if code == "0000":
                        print(f"Condition body-site code for {body_site} for patient-id: {patient.id} not found.")
                    l_body_site.append({'system': "http://snomed.info/sct", 'display': p['value'], 'code': code})
                    body_struct = {'system': "http://snomed.info/sct", 'display': p['value'], 'code': code}
                    bd_coding.append(body_struct)

        body_struct_ident = None
        if body_struct['display']:
            body_struct_ident = Identifier(
                **{"value": body_struct['display'], "system": "".join(["https://gdc.cancer.gov/", "primary_site"])})
        body_structure = BodyStructure(
            **{"id": utils.mint_id(identifier=[patient_id_identifier, body_struct_ident], resource_type="BodyStructure",
                                   project_id=project_id,
                                   namespace=NAMESPACE_GDC),
               "includedStructure": [BodyStructureIncludedStructure(**{"structure": {"coding": bd_coding}})],
               "patient": subject_ref
               })

        cc_body_site = CodeableConcept.construct()
        cc_body_site.coding = l_body_site
        condition.bodySite = [cc_body_site]
        diagnosis_content_bool = False
        if 'diagnoses' in case.keys():
            # condition staging
            # staging grouping for observation.code https://build.fhir.org/ig/HL7/fhir-mCODE-ig/ValueSet-mcode-tnm-stage-group-staging-type-vs.html
            staging_list = []
            # print("case['diagnoses']", case['diagnoses'])
            for key, value in case['diagnoses'].items():
                if 'Condition.stage_' in key and value:
                    case_stage_display = value
                    # print("case_stage_display", case_stage_display)
                    staging_name = key.replace('Condition.stage_', '')

                    sctid_code = "0000"
                    stage_type_sctid_code = "0000"
                    for dict_item in cancer_pathological_staging:
                        if case['diagnoses'][key] == dict_item['value']:
                            sctid_code = dict_item['sctid']
                            stage_type_sctid_code = dict_item['stage_type_sctid']

                    cc_stage_type = CodeableConcept.construct()
                    cc_stage_type.coding = [{'system': "https://cadsr.cancer.gov/",
                                             'display': case['diagnoses'][key],
                                             'code': data_dict['clinical']['diagnosis']['properties'][staging_name][
                                                 'termDef'][
                                                 'cde_id']},
                                            {'system': "http://snomed.info/sct",
                                             'display': case['diagnoses'][key],
                                             'code': stage_type_sctid_code}
                                            ]
                    if sctid_code in "0000":
                        log_output_diag = f"Condition stage - sctid_code codeableConcept code in sctid_code for {case['diagnoses'][key]} not found! {case_stage_display}\n"
                        with open('output.log', 'a') as f:
                            f.write(log_output_diag)

                    if stage_type_sctid_code in "0000":
                        log_output_diag = f"Condition stage - stage_type_sctid_code codeableConcept code in stage_type_sctid_code for {case['diagnoses'][key]} not found! {case_stage_display}\n"
                        with open('output.log', 'a') as f:
                            f.write(log_output_diag)

                    # print("staging_name:", staging_name, "case_stage_display: ", case_stage_display)
                    if case_stage_display and case_stage_display in \
                            data_dict['clinical']['diagnosis']['properties'][staging_name]['enumDef'].keys():
                        code = \
                            data_dict['clinical']['diagnosis']['properties'][staging_name]['enumDef'][
                                case_stage_display][
                                'termDef']['cde_id']
                    else:
                        code = "0000"

                    if case['diagnoses'][key]:
                        display = case['diagnoses'][key]
                    else:
                        display = "replace-me"
                        diagnosis_content_bool = True

                    if not re.match("^[^\s]+(\s[^\s]+)*$", sctid_code):
                        sctid_code = "0000"

                    cc_stage = CodeableConcept.construct()
                    cc_stage.coding = [{'system': "https://ncit.nci.nih.gov",
                                        'display': display,
                                        'code': code
                                        }]

                    cc_stage_sctid = CodeableConcept.construct()
                    cc_stage_sctid.coding = [{'system': "http://snomed.info/sct",
                                              'display': display,
                                              'code': sctid_code}]

                    condition_stage = ConditionStage.construct()
                    condition_stage.summary = cc_stage
                    condition_stage.type = cc_stage_type
                    if observation_ref:
                        condition_stage.assessment = [observation_ref]
                    staging_list.append(condition_stage)

                if diagnosis_content_bool:
                    log_output_diag = f"Diagnosis codableConcept display of {key} for patient-id: {patient.id} doesn't exist or was not found!\n"
                    with open('output.log', 'a') as f:
                        f.write(log_output_diag)

            if "Observation.code.nci_tumor_grade" in case["diagnoses"].keys() and case["diagnoses"][
                "Observation.code.nci_tumor_grade"]:
                # temp fix for demo
                grade = ConditionStage(**{"type": CodeableConcept(**{"coding": [
                    {"code": "2785839", "system": "https://cadsr.cancer.gov",
                     "display": "neoplasm_histologic_grade"}]}),
                                          "summary": CodeableConcept(**{"coding": [
                                              {"code": "2785839", "system": "https://cadsr.cancer.gov",
                                               "display": case["diagnoses"]["Observation.code.nci_tumor_grade"]}]}),
                                          "assessment": [observation_ref]})
                staging_list.append(grade)

            condition.stage = staging_list
            observation.focus = [Reference(**{"reference": "/".join(["Condition", condition.id])}), subject_ref]
            condition_observations.append(orjson.loads(observation.json()))

            # create medication administration and medication
            treatment_content_bool = False
            if 'treatments' in case['diagnoses'].keys():

                for treatment in case['diagnoses']['treatments']:
                    # https://build.fhir.org/ig/HL7/fhir-mCODE-ig/artifacts.html
                    med = Medication.construct()
                    med_identifier = Identifier(
                        **{"system": "".join(["https://gdc.cancer.gov/", "treatment_id"]),
                           "value": treatment['MedicationAdministration.id']})
                    med.id = utils.mint_id(identifier=med_identifier, resource_type="Medication",
                                           project_id=project_id,
                                           namespace=NAMESPACE_GDC)

                    treatments_med.append(med)

                    if 'Medication.code' in treatment.keys() and treatment['Medication.code']:
                        display = treatment['Medication.code']
                    else:
                        display = "replace-me"
                        treatment_content_bool = True

                    med_code = CodeableConcept.construct()
                    med_code.coding = [{'system': "https://cadsr.cancer.gov/onedata/Home.jsp",
                                        'display': display,
                                        'code': '2975232'}]

                    med_cr = CodeableReference.construct()
                    med_cr.reference = Reference(**{"reference": "/".join(["Medication", med.id])})
                    med_cr.concept = med_code
                    med.code = med_code

                    if treatment_content_bool:
                        log_output = f"Medication codableConcept display for patient-id: {patient.id} doesn't exist or was not found!\n"
                        with open('output.log', 'a') as f:
                            f.write(log_output)

                    # if treatment['treatment_or_therapy'] == "yes" then completed, no "not-done"
                    status = "unknown"
                    if 'treatment_or_therapy' in treatment.keys() and treatment['treatment_or_therapy']:
                        if treatment['treatment_or_therapy'] == "yes":
                            status = "completed"
                        if treatment['treatment_or_therapy'] == "no":
                            status = "not-done"
                        if treatment['treatment_or_therapy'] in ["unknown", "not reported"]:
                            status = "unknown"

                    medadmin_category_code = None
                    if 'MedicationAdministration.treatment_type' in treatment.keys() and treatment[
                        'MedicationAdministration.treatment_type']:
                        medadmin_category_code = CodeableConcept.construct()
                        medadmin_category_code.coding = [{'system': "https://cadsr.cancer.gov/onedata/Home.jsp",
                                                          'display': treatment[
                                                              'MedicationAdministration.treatment_type'],
                                                          'code': '5102381'}]
                    if medadmin_category_code:
                        data = {"status": status,
                                "occurenceDateTime": "2019-07-31T21:32:54.724446-05:00",
                                "category": [medadmin_category_code],
                                # placeholder - required fhir field is not required in GDC
                                "medication": med_cr,
                                "subject": Reference(**{"reference": "/".join(["Patient", patient.id])}),
                                "id": treatment['MedicationAdministration.id']}
                    else:
                        data = {"status": status,
                                "occurenceDateTime": "2019-07-31T21:32:54.724446-05:00",
                                # placeholder - required fhir field is not required in GDC
                                "medication": med_cr,
                                "subject": Reference(**{"reference": "/".join(["Patient", patient.id])}),
                                "id": utils.mint_id(identifier=Identifier(
                                    **{"system": "".join(["https://gdc.cancer.gov/", "treatment_id"]),
                                       "value": treatment['MedicationAdministration.id']}),
                                    resource_type="MedicationAdministration",
                                    project_id=project_id,
                                    namespace=NAMESPACE_GDC)}

                    med_admin = MedicationAdministration(**data)
                    treatments_medadmin.append(med_admin)

    # if observation:
    #     condition_observations.append(orjson.loads(observation.json()))

    # exposures
    smoking_observation = []
    if 'exposures' in case.keys():
        if 'Observation.patient.pack_years_smoked' in case['exposures'][0] and case['exposures'][0][
            'Observation.patient.pack_years_smoked']:
            sm_obs = copy.deepcopy(social_histody_smoking_observation)
            # if 'valueQuantity' in sm_obs.keys():
            #    sm_obs.pop('valueQuantity', None)

            sm_ob_identifier = Identifier(
                **{"system": "".join(["https://gdc.cancer.gov/", "exposures.pack_years_smoked"]),
                   "value": case['exposures'][0]['Observation.patient.exposure_id']})
            sm_obs['id'] = utils.mint_id(identifier=sm_ob_identifier, resource_type="Observation",
                                         project_id=project_id,
                                         namespace=NAMESPACE_GDC)

            sm_obs['subject'] = {"reference": "".join(["Patient/", patient.id])}
            sm_obs['focus'] = [{"reference": "".join(["Patient/", patient.id])}]
            sm_obs['valueQuantity']['value'] = int(case['exposures'][0]['Observation.patient.pack_years_smoked'])
            smoking_observation.append(copy.deepcopy(sm_obs))

        if 'Observation.patient.cigarettes_per_day' in case['exposures'][0] and isinstance(
                case['exposures'][0]['Observation.patient.cigarettes_per_day'], float):
            sm_pd_obs = copy.deepcopy(social_histody_smoking_observation)
            if 'valueInteger' in sm_pd_obs.keys():
                sm_pd_obs.pop('valueInteger', None)
            sm_pd_obs_code = "".join([case['exposures'][0]['Observation.patient.exposure_id'], patient.id,
                                      orjson.loads(study_ref.json())['reference'],
                                      'Observation.patient.cigarettes_per_day'])

            sm_pd_obs['id'] = str(uuid.uuid3(uuid.NAMESPACE_DNS, sm_pd_obs_code))
            sm_pd_obs['subject'] = {"reference": "".join(["Patient/", patient.id])}
            sm_pd_obs['focus'] = [{"reference": "".join(["Patient/", patient.id])}]
            sm_pd_obs['valueQuantity'] = {
                "value": round(float(case['exposures'][0]['Observation.patient.cigarettes_per_day']), 2)}
            sm_pd_obs['code'] = {
                "coding": [
                    {
                        "system": "http://loinc.org",
                        "code": "64218-1",
                        "display": "How many cigarettes do you smoke per day now"
                    }
                ]
            }
            smoking_observation.append(copy.deepcopy(sm_pd_obs))

    # todo: change to alcohol intensity
    # https://docs.gdc.cancer.gov/Data_Dictionary/viewer/#?view=table-definition-view&id=exposure&anchor=alcohol_intensity
    alcohol_observation = []
    if 'exposures' in case.keys():
        if 'Observation.patient.alcohol_history' in case['exposures'][0] and case['exposures'][0][
            'Observation.patient.alcohol_history']:
            al_obs = copy.deepcopy(social_histody_alcohol_observation)
            al_ob_identifier = Identifier(
                **{"system": "".join(["https://gdc.cancer.gov/", "exposures.alcohol_history"]),
                   "value": case['exposures'][0]['Observation.patient.exposure_id']})
            al_obs['id'] = utils.mint_id(identifier=al_ob_identifier, resource_type="Observation",
                                         project_id=project_id,
                                         namespace=NAMESPACE_GDC)

            al_obs['subject'] = {"reference": "".join(["Patient/", patient.id])}
            al_obs['focus'] = [{"reference": "".join(["Patient/", patient.id])}]
            al_obs['valueString'] = case['exposures'][0]['Observation.patient.alcohol_history']
            alcohol_observation.append(al_obs)

    # create specimen
    specimen_observations = []
    sample_list = None
    slide_list = []
    procedures = []
    if "samples" in case.keys():
        samples = case["samples"]
        all_samples = []
        all_portions = []
        all_analytes = []
        all_aliquots = []

        sample_observations = []
        portion_observations = []
        analyte_observations = []
        aliquot_observations = []
        slides_observations = []

        for sample in samples:
            if 'Specimen.id.sample' in sample.keys():
                specimen = Specimen.construct()

                specimen_identifier = Identifier(
                    **{"system": "".join(["https://gdc.cancer.gov/", "sample_id"]),
                       "value": sample["Specimen.id.sample"]})
                specimen.id = utils.mint_id(identifier=specimen_identifier, resource_type="Specimen",
                                            project_id=project_id,
                                            namespace=NAMESPACE_GDC)

                specimen.identifier = [specimen_identifier]

                # add sample procedure
                procedure = Procedure.construct()
                procedure.status = "completed"

                procedure.id = utils.mint_id(identifier=specimen_identifier, resource_type="Procedure",
                                             project_id=project_id,
                                             namespace=NAMESPACE_GDC)

                procedure.status = "completed"
                procedure.subject = Reference(**{"reference": "/".join(["Patient", patient.id])})
                if encounter:
                    procedure.encounter = Reference(**{"reference": "/".join(["Encounter", encounter.id])})
                procedures.append(procedure)

                specimen.collection = SpecimenCollection(
                    **{"procedure": Reference(**{"reference": "/".join(["Procedure", procedure.id])}),
                       "collectedDateTime": "2018-08-23T16:32:20.747393-05:00"})

                if "Specimen.type.sample" in sample.keys():
                    sample_type = CodeableConcept.construct()
                    sample_type.coding = [{
                        'system': "https://cadsr.cancer.gov/sample_type",
                        'display': sample["Specimen.type.sample"],
                        'code': "3111302"}]
                    specimen.type = sample_type

                sp = None
                if "Specimen.processing.method" in sample.keys():
                    sample_processing = CodeableConcept.construct()
                    sp = SpecimenProcessing.construct()
                    sample_processing.coding = [{
                        'system': "https://cadsr.cancer.gov/preservation_method",
                        'display': sample["Specimen.processing.method"],
                        'code': "5432521"}]
                    sp.method = sample_processing
                    specimen.processing = [sp]

                sample_observation_components = []
                c = None
                if "Observation.sample.composition" in sample.keys() and sample["Observation.sample.composition"]:
                    c = utils.get_component('composition', value=sample["Observation.sample.composition"],
                                            component_type='string')
                    sample_observation_components.append(c)
                if "Observation.sample.is_ffpe" in sample.keys() and isinstance(sample["Observation.sample.is_ffpe"],
                                                                                bool):
                    c = utils.get_component('is_ffpe', value=sample["Observation.sample.is_ffpe"],
                                            component_type='bool')
                    sample_observation_components.append(c)

                if "Specimen.type.sample" in sample.keys() and sample["Specimen.type.sample"]:
                    c = utils.get_component('sample_type',
                                            value=sample["Specimen.type.sample"],
                                            component_type='string')
                    sample_observation_components.append(c)

                if "Observation.sample.updated_datetime" in sample.keys() and sample["Observation.sample.updated_datetime"]:
                    c = utils.get_component('updated_datetime',
                                            value=sample["Observation.sample.updated_datetime"],
                                            component_type='dateTime')
                    sample_observation_components.append(c)

                sample_observation = None
                if sample_observation_components:
                    sample_observation = copy.deepcopy(biospecimen_observation)
                    sample_observation['id'] = utils.mint_id(identifier=specimen_identifier,
                                                             resource_type="Observation",
                                                             project_id=project_id,
                                                             namespace=NAMESPACE_GDC)

                    sample_observation['component'] = sample_observation_components

                    sample_observation['subject'] = {"reference": "/".join(["Patient", patient.id])}
                    sample_observation['specimen'] = {"reference": "/".join(["Specimen", specimen.id])}
                    sample_observation['focus'][0] = {"reference": "/".join(["Specimen", specimen.id])}

                    if sample_observation not in sample_observations:
                        sample_observations.append(copy.deepcopy(sample_observation))

                specimen.subject = Reference(**{"reference": "/".join(["Patient", patient.id])})

                if not specimen_exists(specimen.id, all_samples):
                    all_samples.append(specimen)

                if "slides" in sample.keys():
                    for slide in sample["slides"]:
                        sample_img_study = create_imaging_study(slide=slide, patient=patient, sample=specimen)
                        slide_list.append(sample_img_study)
                """
                add_specimen(dat=sample, name="analytes", id_key="Specimen.id.analyte", has_parent=True,
                             parent=sample, patient=patient, all_fhir_specimens=all_analytes)

                add_specimen(dat=sample, name="aliquots", id_key="Specimen.id.aliquot", has_parent=True,
                             parent=sample, patient=patient, all_fhir_specimens=all_aliquots)
                """

                if "portions" in sample.keys():
                    for portion in sample['portions']:
                        if "Specimen.id.portion" in portion.keys():

                            portion_specimen = Specimen.construct()

                            portion_specimen_identifier = Identifier(
                                **{"system": "".join(["https://gdc.cancer.gov/", "portion_id"]),
                                   "value": portion["Specimen.id.portion"]})
                            portion_specimen.id = utils.mint_id(identifier=portion_specimen_identifier,
                                                                resource_type="Specimen",
                                                                project_id=project_id,
                                                                namespace=NAMESPACE_GDC)
                            portion_specimen.identifier = [portion_specimen_identifier]

                            portion_specimen.subject = Reference(**{"reference": "/".join(["Patient", patient.id])})
                            portion_specimen.parent = [Reference(**{"reference": "/".join(["Specimen", specimen.id])})]

                            portion_specimen.collection = SpecimenCollection(
                                **{"procedure": Reference(**{"reference": "/".join(["Procedure", procedure.id])}),
                                   "collectedDateTime": "2018-08-23T16:32:20.747393-05:00"})

                            portion_specimen.processing = [sp]

                            if not specimen_exists(portion_specimen.id, all_portions):
                                all_portions.append(portion_specimen)

                            portions_observation_components = []
                            if "Observation.portions.weight" in portion.keys() and portion[
                                "Observation.portions.weight"]:
                                c = utils.get_component('weight', value=portion["Observation.portions.weight"],
                                                        component_type='int')
                                portions_observation_components.append(c)
                            if "Observation.portions.is_ffpe" in portion.keys() and isinstance(
                                    portion["Observation.portions.is_ffpe"], bool):
                                c = utils.get_component('is_ffpe', value=portion["Observation.portions.is_ffpe"],
                                                        component_type='bool')
                                portions_observation_components.append(c)

                            if "Specimen.type.sample" in sample.keys() and sample["Specimen.type.sample"]:
                                c = utils.get_component('sample_type',
                                                        value=sample["Specimen.type.sample"],
                                                        component_type='string')
                                portions_observation_components.append(c)

                            if "Observation.portion.updated_datetime" in portion.keys() and portion[
                                "Observation.portion.updated_datetime"]:
                                c = utils.get_component('updated_datetime',
                                                        value=portion["Observation.portion.updated_datetime"],
                                                        component_type='dateTime')
                                portions_observation_components.append(c)

                            portions_observation = None
                            if portions_observation_components:
                                portions_observation = copy.deepcopy(biospecimen_observation)

                                portions_observation['id'] = utils.mint_id(identifier=portion_specimen_identifier,
                                                                           resource_type="Observation",
                                                                           project_id=project_id,
                                                                           namespace=NAMESPACE_GDC)

                                portions_observation['component'] = portions_observation_components

                                portions_observation['subject'] = {"reference": "/".join(["Patient", patient.id])}
                                portions_observation['specimen'] = {
                                    "reference": "/".join(["Specimen", portion_specimen.id])}
                                portions_observation['focus'][0] = {
                                    "reference": "/".join(["Specimen", portion_specimen.id])}

                                if portions_observation not in portion_observations:
                                    portion_observations.append(copy.deepcopy(portions_observation))

                            if "slides" in portion.keys():
                                for slide in portion["slides"]:
                                    portion_img_study = create_imaging_study(slide=slide, patient=patient,
                                                                             sample=portion_specimen)
                                    slide_list.append(portion_img_study)

                                    slides_observation_components = []
                                    if "Observation.slides.section_location" in slide.keys():
                                        c = utils.get_component('section_location',
                                                                value=slide["Observation.slides.section_location"],
                                                                component_type='string')
                                        slides_observation_components.append(c)

                                    slides_observation = None
                                    if slides_observation_components:
                                        slides_observation = copy.deepcopy(biospecimen_imaging_observation)

                                        slides_observation['id'] = utils.mint_id(identifier=Identifier(
                                            **{"system": "".join(["https://gdc.cancer.gov/", "slide_id"]),
                                               "value": slide["ImagingStudy.id"]}), resource_type="Observation",
                                            project_id=project_id,
                                            namespace=NAMESPACE_GDC)

                                        slides_observation['component'] = slides_observation_components

                                        slides_observation['subject'] = {
                                            "reference": "/".join(["Patient", patient.id])}
                                        slides_observation['specimen'] = {
                                            "reference": "/".join(["Specimen", portion_specimen.id])}
                                        slides_observation['focus'][0] = {
                                            "reference": "/".join(["ImagingStudy", portion_img_study.id])}

                                        if slides_observation not in slides_observations:
                                            slides_observations.append(copy.deepcopy(slides_observation))

                            if "analytes" in portion.keys():
                                for analyte in portion["analytes"]:
                                    if "Specimen.id.analyte" in analyte.keys():
                                        analyte_specimen = Specimen.construct()

                                        analyte_specimen_identifier = Identifier(
                                            **{"system": "".join(["https://gdc.cancer.gov/", "analyte_id"]),
                                               "value": analyte["Specimen.id.analyte"]})
                                        analyte_specimen.id = utils.mint_id(identifier=analyte_specimen_identifier,
                                                                            resource_type="Specimen",
                                                                            project_id=project_id,
                                                                            namespace=NAMESPACE_GDC)

                                        analyte_specimen.identifier = [analyte_specimen_identifier]

                                        analyte_specimen.subject = Reference(
                                            **{"reference": "/".join(["Patient", patient.id])})
                                        analyte_specimen.parent = [
                                            Reference(**{"reference": "/".join(["Specimen", portion_specimen.id])})]

                                        analyte_specimen.collection = SpecimenCollection(
                                            **{"procedure": Reference(
                                                **{"reference": "/".join(["Procedure", procedure.id])}),
                                                "collectedDateTime": "2018-08-23T16:32:20.747393-05:00"})

                                        analyte_specimen.processing = [sp]

                                        if "Specimen.type.analyte" in analyte.keys():
                                            analyte_type = CodeableConcept.construct()
                                            analyte_type.coding = [{
                                                'system': "https://cadsr.cancer.gov/experimental_protocol_type",
                                                'display': analyte["Specimen.type.analyte"],
                                                'code': "2513915"}]
                                            analyte_specimen.type = analyte_type

                                        if "slides" in analyte.keys():
                                            for slide in analyte["slides"]:
                                                analyte_img_study = create_imaging_study(slide=slide, patient=patient,
                                                                                         sample=analyte_specimen)
                                                slide_list.append(analyte_img_study)

                                        if not specimen_exists(analyte_specimen.id, all_analytes):
                                            all_analytes.append(analyte_specimen)

                                        analyte_observation_components = []
                                        if "Specimen.type.analyte" in analyte.keys() and analyte[
                                            "Specimen.type.analyte"]:
                                            c = utils.get_component('analyte_type',
                                                                    value=analyte["Specimen.type.analyte"],
                                                                    component_type='string')
                                            analyte_observation_components.append(c)

                                        if "Observation.analyte.concentration" in analyte.keys() and analyte[
                                            "Observation.analyte.concentration"]:
                                            c = utils.get_component('concentration',
                                                                    value=analyte[
                                                                        "Observation.analyte.concentration"],
                                                                    component_type='float')
                                            analyte_observation_components.append(c)

                                        if "Observation.analyte.experimental_protocol_type" in analyte.keys() and \
                                                analyte["Observation.analyte.experimental_protocol_type"]:
                                            c = utils.get_component('experimental_protocol_type',
                                                                    value=analyte[
                                                                        "Observation.analyte.experimental_protocol_type"],
                                                                    component_type='string')
                                            analyte_observation_components.append(c)

                                        if "Observation.analyte.normal_tumor_genotype_snp_match" in analyte.keys() and \
                                                analyte["Observation.analyte.normal_tumor_genotype_snp_match"]:
                                            c = utils.get_component('normal_tumor_genotype_snp_match',
                                                                    value=analyte[
                                                                        "Observation.analyte.normal_tumor_genotype_snp_match"],
                                                                    component_type='string')
                                            analyte_observation_components.append(c)

                                        if "Observation.analyte.ribosomal_rna_28s_16s_ratio" in analyte.keys() and \
                                                analyte["Observation.analyte.ribosomal_rna_28s_16s_ratio"]:
                                            c = utils.get_component('ribosomal_rna_28s_16s_ratio',
                                                                    value=analyte[
                                                                        "Observation.analyte.ribosomal_rna_28s_16s_ratio"],
                                                                    component_type='float')
                                            analyte_observation_components.append(c)

                                        if "Observation.analyte.rna_integrity_number" in analyte.keys() and analyte[
                                            "Observation.analyte.rna_integrity_number"]:
                                            c = utils.get_component('rna_integrity_number',
                                                                    value=analyte[
                                                                        "Observation.analyte.rna_integrity_number"],
                                                                    component_type='float')
                                            analyte_observation_components.append(c)

                                        if "Observation.analyte.spectrophotometer_method" in analyte.keys() and analyte[
                                            "Observation.analyte.spectrophotometer_method"]:
                                            c = utils.get_component('spectrophotometer_method',
                                                                    value=analyte[
                                                                        "Observation.analyte.spectrophotometer_method"],
                                                                    component_type='string')
                                            analyte_observation_components.append(c)

                                        if "Observation.analyte.updated_datetime" in analyte.keys() and analyte[
                                            "Observation.analyte.updated_datetime"]:
                                            c = utils.get_component('updated_datetime',
                                                                    value=analyte["Observation.analyte.updated_datetime"],
                                                                    component_type='dateTime')
                                            analyte_observation_components.append(c)

                                        if "Specimen.type.sample" in sample.keys() and sample["Specimen.type.sample"]:
                                            c = utils.get_component('sample_type',
                                                                    value=sample["Specimen.type.sample"],
                                                                    component_type='string')
                                            analyte_observation_components.append(c)

                                        analyte_observation = None
                                        if analyte_observation_components:
                                            analyte_observation = copy.deepcopy(biospecimen_observation)
                                            analyte_observation['id'] = utils.mint_id(
                                                identifier=analyte_specimen_identifier,
                                                resource_type="Observation",
                                                project_id=project_id,
                                                namespace=NAMESPACE_GDC)

                                            analyte_observation['component'] = analyte_observation_components

                                            analyte_observation['subject'] = {
                                                "reference": "/".join(["Patient", patient.id])}
                                            analyte_observation['specimen'] = {
                                                "reference": "/".join(["Specimen", analyte_specimen.id])}
                                            analyte_observation['focus'][0] = {
                                                "reference": "/".join(["Specimen", analyte_specimen.id])}

                                            if analyte_observation not in analyte_observations:
                                                analyte_observations.append(copy.deepcopy(analyte_observation))

                                        if "aliquots" in analyte.keys():
                                            for aliquot in analyte["aliquots"]:
                                                if "Specimen.id.aliquot" in aliquot.keys():
                                                    aliquot_specimen = Specimen.construct()

                                                    aliquot_specimen_identifier = Identifier(
                                                        **{"system": "".join(["https://gdc.cancer.gov/", "aliquot_id"]),
                                                           "value": aliquot["Specimen.id.aliquot"]})
                                                    aliquot_specimen.id = utils.mint_id(
                                                        identifier=aliquot_specimen_identifier,
                                                        resource_type="Specimen",
                                                        project_id=project_id,
                                                        namespace=NAMESPACE_GDC)

                                                    aliquot_specimen.identifier = [aliquot_specimen_identifier]

                                                    aliquot_specimen.collection = SpecimenCollection(
                                                        **{"procedure": Reference(
                                                            **{"reference": "/".join(["Procedure", procedure.id])}),
                                                            "collectedDateTime": "2018-08-23T16:32:20.747393-05:00"})

                                                    aliquot_specimen.processing = [sp]
                                                    # if aliquot_specimen.id == "3fc2bd45-8cf9-420d-b900-a0fee703731d":
                                                    # print("Patient", patient)

                                                    aliquot_specimen.subject = Reference(
                                                        **{"reference": "/".join(["Patient", patient.id])})
                                                    aliquot_specimen.parent = [Reference(
                                                        **{"reference": "/".join(["Specimen", analyte_specimen.id])})]

                                                    if not specimen_exists(aliquot_specimen.id, all_aliquots):
                                                        all_aliquots.append(aliquot_specimen)

                                                aliquot_observation_components = []
                                                if "Observation.aliquot.analyte_type" in aliquot.keys() and aliquot[
                                                    "Observation.aliquot.analyte_type"]:
                                                    c_aliquot_analyte_type = utils.get_component('aliquot.analyte_type',
                                                                                                 value=aliquot[
                                                                                                     "Observation.aliquot.analyte_type"],
                                                                                                 component_type='string')
                                                    aliquot_observation_components.append(c_aliquot_analyte_type)
                                                if "Observation.aliquot.concentration" in aliquot.keys() and aliquot[
                                                    "Observation.aliquot.concentration"]:
                                                    c = utils.get_component('concentration',
                                                                            value=aliquot[
                                                                                "Observation.aliquot.concentration"],
                                                                            component_type='float')
                                                    aliquot_observation_components.append(c)

                                                if "Observation.aliquot.aliquot_quantity" in aliquot.keys() and aliquot[
                                                    "Observation.aliquot.aliquot_quantity"]:
                                                    c = utils.get_component('aliquot_quantity',
                                                                            value=aliquot[
                                                                                "Observation.aliquot.aliquot_quantity"],
                                                                            component_type='float')
                                                    aliquot_observation_components.append(c)

                                                if "Observation.aliquot.aliquot_volume" in aliquot.keys() and aliquot[
                                                    "Observation.aliquot.aliquot_volume"]:
                                                    c = utils.get_component('aliquot_volume',
                                                                            value=aliquot[
                                                                                "Observation.aliquot.aliquot_volume"],
                                                                            component_type='float')
                                                    aliquot_observation_components.append(c)

                                                if "Observation.aliquot.no_matched_normal_wgs" in aliquot.keys() and isinstance(
                                                        aliquot[
                                                            "Observation.aliquot.no_matched_normal_wgs"], bool):
                                                    c = utils.get_component('no_matched_normal_wgs',
                                                                            value=aliquot[
                                                                                "Observation.aliquot.no_matched_normal_wgs"],
                                                                            component_type='bool')
                                                    aliquot_observation_components.append(c)

                                                if "Observation.aliquot.no_matched_normal_wxs" in aliquot.keys() and isinstance(
                                                        aliquot[
                                                            "Observation.aliquot.no_matched_normal_wxs"], bool):
                                                    c = utils.get_component('no_matched_normal_wxs',
                                                                            value=aliquot[
                                                                                "Observation.aliquot.no_matched_normal_wxs"],
                                                                            component_type='bool')
                                                    aliquot_observation_components.append(c)

                                                if "Observation.aliquot.no_matched_normal_low_pass_wgs" in aliquot.keys() and isinstance(
                                                        aliquot[
                                                            "Observation.aliquot.no_matched_normal_low_pass_wgs"],
                                                        bool):
                                                    c = utils.get_component('no_matched_normal_low_pass_wgs',
                                                                            value=aliquot[
                                                                                "Observation.aliquot.no_matched_normal_low_pass_wgs"],
                                                                            component_type='bool')
                                                    aliquot_observation_components.append(c)

                                                if "Observation.aliquot.no_matched_normal_targeted_sequencing" in aliquot.keys() and isinstance(
                                                        aliquot[
                                                            "Observation.aliquot.no_matched_normal_targeted_sequencing"],
                                                        bool):
                                                    c = utils.get_component('no_matched_normal_targeted_sequencing',
                                                                            value=aliquot[
                                                                                "Observation.aliquot.no_matched_normal_targeted_sequencing"],
                                                                            component_type='bool')
                                                    aliquot_observation_components.append(c)

                                                if "Observation.aliquot.selected_normal_low_pass_wgs" in aliquot.keys() and isinstance(
                                                        aliquot[
                                                            "Observation.aliquot.selected_normal_low_pass_wgs"], bool):
                                                    c = utils.get_component('selected_normal_low_pass_wgs',
                                                                            value=aliquot[
                                                                                "Observation.aliquot.selected_normal_low_pass_wgs"],
                                                                            component_type='bool')
                                                    aliquot_observation_components.append(c)

                                                if "Observation.aliquot.selected_normal_targeted_sequencing" in aliquot.keys() and isinstance(
                                                        aliquot[
                                                            "Observation.aliquot.selected_normal_targeted_sequencing"],
                                                        bool):
                                                    c = utils.get_component('selected_normal_targeted_sequencing',
                                                                            value=aliquot[
                                                                                "Observation.aliquot.selected_normal_targeted_sequencing"],
                                                                            component_type='bool')
                                                    aliquot_observation_components.append(c)

                                                if "Observation.aliquot.selected_normal_wgs" in aliquot.keys() and isinstance(
                                                        aliquot[
                                                            "Observation.aliquot.selected_normal_wgs"], bool):
                                                    c = utils.get_component('selected_normal_wgs',
                                                                            value=aliquot[
                                                                                "Observation.aliquot.selected_normal_wgs"],
                                                                            component_type='bool')
                                                    aliquot_observation_components.append(c)

                                                if "Specimen.type.sample" in sample.keys() and sample[
                                                    "Specimen.type.sample"]:
                                                    c = utils.get_component('sample_type',
                                                                            value=sample["Specimen.type.sample"],
                                                                            component_type='string')
                                                    aliquot_observation_components.append(c)

                                                if "Observation.aliquot.updated_datetime" in aliquot.keys() and aliquot[
                                                    "Observation.aliquot.updated_datetime"]:
                                                    c = utils.get_component('updated_datetime',
                                                                            value=aliquot[
                                                                                "Observation.aliquot.updated_datetime"],
                                                                            component_type='dateTime')
                                                    aliquot_observation_components.append(c)

                                                if "Observation.aliquot.selected_normal_wxs" in aliquot.keys() and isinstance(
                                                        aliquot[
                                                            "Observation.aliquot.selected_normal_wxs"], bool):
                                                    c = utils.get_component('selected_normal_wxs',
                                                                            value=aliquot[
                                                                                "Observation.aliquot.selected_normal_wxs"],
                                                                            component_type='bool')
                                                    aliquot_observation_components.append(c)

                                                aliquot_observation = None
                                                if aliquot_observation_components:
                                                    aliquot_observation = copy.deepcopy(biospecimen_observation)
                                                    aliquot_observation['id'] = utils.mint_id(
                                                        identifier=aliquot_specimen_identifier,
                                                        resource_type="Observation",
                                                        project_id=project_id,
                                                        namespace=NAMESPACE_GDC)

                                                    aliquot_observation['component'] = aliquot_observation_components

                                                    aliquot_observation['subject'] = {
                                                        "reference": "/".join(["Patient", patient.id])}
                                                    aliquot_observation['specimen'] = {
                                                        "reference": "/".join(["Specimen", aliquot_specimen.id])}
                                                    aliquot_observation['focus'][0] = {
                                                        "reference": "/".join(["Specimen", aliquot_specimen.id])}

                                                    if aliquot_observation not in aliquot_observations:
                                                        aliquot_observations.append(copy.deepcopy(aliquot_observation))

        sample_list = all_samples + all_portions + all_aliquots + all_analytes
        specimen_observations = sample_observations + portion_observations + slides_observations + analyte_observations + aliquot_observations

    all_observations = condition_observations + smoking_observation + alcohol_observation + obs_survey + specimen_observations

    return {'patient': patient, 'encounter': encounter, 'observations': all_observations, 'condition': condition,
            'project_relations': project_relations, 'research_subject': research_subject, 'specimens': sample_list,
            'imaging_study': slide_list, "procedures": procedures, "med_admin": treatments_medadmin,
            "med": treatments_med, "body_structure": body_structure}


def remove_duplicates(entities):
    seen = set()
    unique_entities = []
    for e in entities:
        if isinstance(e, dict):
            print(e)
            fhir_model = e
        else:
            fhir_model = json.dumps(e.json(), sort_keys=True)
        if fhir_model not in seen:
            seen.add(fhir_model)
            unique_entities.append(e)
    return unique_entities


def case_gdc_to_fhir_ndjson(out_dir, cases_path):
    cases = utils.load_ndjson(cases_path)
    all_fhir_case_obj = []
    [all_fhir_case_obj.append(assign_fhir_for_case(c)) for c in cases]

    patients = [orjson.loads(fhir_case['patient'].json()) for fhir_case in all_fhir_case_obj]
    encounters = [orjson.loads(fhir_case['encounter'].json()) for fhir_case in all_fhir_case_obj if
                  'encounter' in fhir_case.keys() and fhir_case['encounter']]
    encounters = list({v['id']: v for v in encounters}.values())
    #   observations = [orjson.loads(fhir_case['observations'].json()) for fhir_case in all_fhir_case_obj if
    #                    'observations' in fhir_case.keys() and fhir_case['observations']]
    conditions = [orjson.loads(fhir_case['condition'].json()) for fhir_case in all_fhir_case_obj if
                  'condition' in fhir_case.keys() and fhir_case['condition']]
    research_subjects = [orjson.loads(fhir_case['research_subject'].json()) for fhir_case in all_fhir_case_obj]
    projects = [orjson.loads(fhir_case['project_relations']["ResearchStudy_obj"].json()) for fhir_case in
                all_fhir_case_obj]
    programs = list(unique_everseen(
        [orjson.loads(fhir_case['project_relations']["ResearchStudy.partOf_obj"].json()) for fhir_case in
         all_fhir_case_obj]))

    body_structure = [orjson.loads(fhir_case['body_structure'].json()) for fhir_case in all_fhir_case_obj if
                      'body_structure' in fhir_case.keys() and fhir_case['body_structure']]

    specimens = []
    for fhir_case in all_fhir_case_obj:
        if fhir_case["specimens"]:
            for specimen in fhir_case["specimens"]:
                s = orjson.loads(specimen.json())
                # if 'parent' in s.keys():
                #     s['parent'] = s['parent'][0]
                specimens.append(s)

    observations = []
    for fhir_case in all_fhir_case_obj:
        if fhir_case["observations"]:
            for obs in fhir_case["observations"]:
                if isinstance(obs, dict):
                    observations.append(obs)
                else:
                    observations.append(orjson.loads(obs.json()))
    observations = list({v['id']: v for v in observations}.values())

    procedures = []
    for fhir_case in all_fhir_case_obj:
        if fhir_case["procedures"]:
            for procedure in fhir_case["procedures"]:
                procedures.append(orjson.loads(procedure.json()))

    imaging_study = []
    for fhir_case in all_fhir_case_obj:
        if fhir_case["imaging_study"]:
            for img in fhir_case["imaging_study"]:
                imaging_study.append(orjson.loads(img.json()))
    imaging_study = list({v['id']: v for v in imaging_study}.values())

    if "/" not in out_dir[-1]:
        out_dir = out_dir + "/"

    if specimens:
        utils.fhir_ndjson(specimens, "".join([out_dir, "Specimen.ndjson"]))
        print("Successfully converted GDC case sample to FHIR's Specimen ndjson file!")
    if patients:
        utils.fhir_ndjson(patients, "".join([out_dir, "Patient.ndjson"]))
        print("Successfully converted GDC case patient to FHIR's Patient ndjson file!")
    if encounters:
        utils.fhir_ndjson(encounters, "".join([out_dir, "Encounter.ndjson"]))
        print("Successfully converted GDC case info to FHIR's Encounter ndjson file!")
    if observations:
        utils.fhir_ndjson(observations, "".join([out_dir, "Observation.ndjson"]))
        print("Successfully converted GDC case info to FHIR's Observation ndjson file!")
    if conditions:
        utils.fhir_ndjson(conditions, "".join([out_dir, "Condition.ndjson"]))
        print("Successfully converted GDC case info to FHIR's Condition ndjson file!")
    if research_subjects:
        utils.fhir_ndjson(research_subjects, "".join([out_dir, "ResearchSubject.ndjson"]))
        print("Successfully converted GDC case info to FHIR's ResearchSubject ndjson file!")
    if projects:
        rs = projects + programs
        rs = list({v['id']: v for v in rs}.values())
        utils.fhir_ndjson(rs, "".join([out_dir, "ResearchStudy.ndjson"]))
        print("Successfully converted GDC case info to FHIR's ResearchStudy ndjson file!")
    if imaging_study:
        utils.fhir_ndjson(imaging_study, "".join([out_dir, "ImagingStudy.ndjson"]))
        print("Successfully converted GDC case info to FHIR's ImagingStudy ndjson file!")
    if procedures:
        utils.fhir_ndjson(procedures, "".join([out_dir, "Procedure.ndjson"]))
        print("Successfully converted GDC case info to FHIR's Procedure ndjson file!")
    if body_structure:
        utils.fhir_ndjson(body_structure, "".join([out_dir, "BodyStructure.ndjson"]))
        print("Successfully converted GDC case info to FHIR's BodyStructure ndjson file!")

    med_admins = []
    for fhir_case in all_fhir_case_obj:
        if fhir_case["med_admin"]:
            for med_admin in fhir_case["med_admin"]:
                med_admins.append(orjson.loads(med_admin.json()))
    if med_admins:
        utils.fhir_ndjson(med_admins, "".join([out_dir, "MedicationAdministration.ndjson"]))
        print("Successfully converted GDC case info to FHIR's MedicationAdministration ndjson file!")

    meds = []
    for fhir_case in all_fhir_case_obj:
        if fhir_case["med"]:
            for med in fhir_case["med"]:
                meds.append(orjson.loads(med.json()))
    if meds:
        utils.fhir_ndjson(meds, "".join([out_dir, "Medication.ndjson"]))
        print("Successfully converted GDC case info to FHIR's Medication ndjson file!")


# File ---------------------------------------------------------------
# load file mapped key values
# files = utils.load_ndjson("./tests/fixtures/file/file_key.ndjson")
# file = files[0]

def assign_fhir_for_file(file):
    project_id = "GDC"
    NAMESPACE_GDC = uuid3(NAMESPACE_DNS, 'gdc.cancer.gov')

    document = DocumentReference.construct()
    document.status = "current"

    ident = Identifier(
        **{"system": "".join(["https://gdc.cancer.gov/", "file_id"]), "value": file['DocumentReference.id']})

    document.id = utils.mint_id(
        identifier=ident,
        resource_type="DocumentReference",
        project_id=project_id,
        namespace=NAMESPACE_GDC)

    document.identifier = [ident]

    category = []
    if 'DocumentReference.category.data_category' in file.keys() and file['DocumentReference.category.data_category']:
        cc = CodeableConcept.construct()
        system = "".join(["https://gdc.cancer.gov/", "data_category"])
        cc.coding = [{'system': system,
                      'display': file['DocumentReference.category.data_category'],
                      'code': file['DocumentReference.category.data_category'], }]

        category.append(cc)

    if 'DocumentReference.category.platform' in file.keys() and file['DocumentReference.category.platform']:
        cc_plat = CodeableConcept.construct()
        system = "".join(["https://gdc.cancer.gov/", "platform"])
        cc_plat.coding = [{'system': system,
                           'display': file['DocumentReference.category.platform'],
                           'code': file['DocumentReference.category.platform']}]

        category.append(cc_plat)

    if 'DocumentReference.category.experimental_strategy' in file.keys() and file[
        'DocumentReference.category.experimental_strategy']:
        cc_es = CodeableConcept.construct()
        system = "".join(["https://gdc.cancer.gov/", "experimental_strategy"])
        cc_es.coding = [{'system': system,
                         'display': file['DocumentReference.category.experimental_strategy'],
                         'code': file['DocumentReference.category.experimental_strategy']}]

        category.append(cc_es)

    if 'DocumentReference.category.wgs_coverage' in file.keys() and file['DocumentReference.category.wgs_coverage']:
        cc_es = CodeableConcept.construct()
        system = "".join(["https://gdc.cancer.gov/", "wgs_coverage"])
        cc_es.coding = [{'system': system,
                         'display': file['DocumentReference.category.wgs_coverage'],
                         'code': file['DocumentReference.category.wgs_coverage']}]

        category.append(cc_es)

    if category:
        document.category = category

    if 'DocumentReference.version' in file.keys() and file['DocumentReference.version']:
        document.version = file['DocumentReference.version']

    if 'DocumentReference.date' in file.keys() and file['DocumentReference.date']:
        document.date = file['DocumentReference.date']

    patients = []
    sample_ref = []
    if 'cases' in file.keys() and file['cases']:
        for case in file['cases']:
            patient_id_identifier = Identifier.construct()
            patient_id_identifier.value = case['Patient.id']
            patient_id_identifier.system = "".join(["https://gdc.cancer.gov/", "case_id"])

            patient_id = utils.mint_id(identifier=patient_id_identifier, resource_type="Patient", project_id=project_id,
                                       namespace=NAMESPACE_GDC)

            patients.append(Reference(**{"reference": "/".join(["Patient", patient_id])}))

            if 'samples' in case.keys():
                for sample in case['samples']:
                    if 'Specimen.id' in sample['portions'][0]['analytes'][0]['aliquots'][0].keys() and \
                            sample['portions'][0]['analytes'][0]['aliquots'][0]['Specimen.id']:
                        specimen_identifier = Identifier(
                            **{"system": "".join(["https://gdc.cancer.gov/", "aliquot_id"]),
                               "value": sample['portions'][0]['analytes'][0]['aliquots'][0]['Specimen.id']})

                        specimen_id = utils.mint_id(identifier=specimen_identifier, resource_type="Specimen",
                                                    project_id=project_id,
                                                    namespace=NAMESPACE_GDC)

                        sample_ref.append(Reference(**{"reference": "/".join(["Specimen", specimen_id])}))

    if patients and len(patients) == 1:
        document.subject = patients[0]

    if sample_ref:
        document.basedOn = sample_ref

    attachment = Attachment.construct()
    attachment.url = "https://api.gdc.cancer.gov/data/{}".format(file['DocumentReference.id'])

    if 'Attachment.title' in file.keys() and file['Attachment.title']:
        attachment.title = file['Attachment.title']
    if 'Attachment.hash' in file.keys() and file['Attachment.hash']:
        attachment.hash = file['Attachment.hash']
    if 'Attachment.size' in file.keys() and file['Attachment.size']:
        attachment.size = file['Attachment.size']

    if 'DocumentReference.type' in file.keys() and file['DocumentReference.type']:
        """
        cc_type = CodeableConcept.construct()
        system = "".join(["https://gdc.cancer.gov/", "data_type"])
        cc_type.coding = [{'system': system,
                           'display': file['DocumentReference.type'],
                           'code': file['DocumentReference.type']}]

        document.type = cc_type
        """
        attachment.contentType = file['DocumentReference.type']

    profile = None
    if 'DocumentReference.content.profile' in file.keys() and file['DocumentReference.content.profile']:
        profile = DocumentReferenceContentProfile.construct()
        system = "".join(["https://gdc.cancer.gov/", "data_format"])
        profile.valueCoding = {"code": file['DocumentReference.content.profile'],
                               "display": file['DocumentReference.content.profile'],
                               "system": system}

        cc_type = CodeableConcept.construct()
        system = "".join(["https://gdc.cancer.gov/", "data_type"])
        cc_type.coding = [{'system': system,
                           'display': file['DocumentReference.content.profile'],
                           'code': file['DocumentReference.content.profile']}]

        document.type = cc_type

    if profile:
        data = {'attachment': attachment, "profile": [profile]}
    else:
        data = {'attachment': attachment}
    document.content = [DocumentReferenceContent(**data)]

    return document


def file_gdc_to_fhir_ndjson(out_dir, files_path):
    files = utils.load_ndjson(files_path)
    all_fhir_file_obj = []
    [all_fhir_file_obj.append(assign_fhir_for_file(f)) for f in files]

    doc_refs = [orjson.loads(fhir_file.json()) for fhir_file in all_fhir_file_obj]

    if "/" not in out_dir[-1]:
        out_dir = out_dir + "/"

    if doc_refs:
        utils.fhir_ndjson(doc_refs, "".join([out_dir, "DocumentReference.ndjson"]))
        print("Successfully converted GDC file info to FHIR's DocumentReference ndjson file!")


# Cellosaurus ---------------------------------------------------------------

def cellosaurus_resource(path, out_dir):
    out_dir = os.path.abspath(out_dir)
    out_dir = os.path.join(out_dir, "")

    ids = utils.cellosaurus_cancer_ids(path, os.path.join(out_dir, "ids.json"), save=True)  # filter step
    if ids:
        print("Successfully saved cellosaurus ids!")
    else:
        print("There aren't any cancer human cell-lines with sex annotation and depmap reference.")
        return

    cells_dir = os.path.join(out_dir, "cells")
    if not os.path.exists(cells_dir):
        os.makedirs(cells_dir)
    cells_dir = os.path.abspath(cells_dir)
    cells_dir = os.path.join(cells_dir, "")

    utils.fetch_cellines(ids, cells_dir)  # api call intensive - 1s per request + 0.5s delay
    cls = utils.cellosaurus_cancer_jsons(cells_dir)
    ndjson_path = os.path.join(out_dir, "cellosaurus_cellines.ndjson")
    utils.fhir_ndjson(cls, os.path.join(out_dir, "cellosaurus_cellines.ndjson"))

    if os.path.exists(ndjson_path):
        print("Successfully saved cell lines in cellosaurus_cellines.ndjson!")


def cellosaurus_fhir_mappping(cell_lines, verbose=False):
    project_id = "CELLOSAURUS"
    NAMESPACE_CELLOSAURUS = uuid3(NAMESPACE_DNS, 'cellosaurus.org')

    patients = []
    conditions = []
    samples = []
    for cell_line in cell_lines:
        for cl in cell_line["Cellosaurus"]["cell-line-list"]:
            patient = None
            patient_id = None
            ident_list = []
            for accession in cl["accession-list"]:
                if accession["type"] == "primary":
                    patient_identifier = Identifier(
                        **{"system": "https://www.cellosaurus.org/cell-line-primary-accession",
                           "value": accession["value"]})
                    patient_id = utils.mint_id(identifier=patient_identifier, resource_type="Patient",
                                               project_id=project_id,
                                               namespace=NAMESPACE_CELLOSAURUS)

                    ident_list.append(patient_identifier)
            if patient_id:
                for identifier in cl["name-list"]:
                    if identifier["type"] == "identifier":
                        patient_identifer = identifier["value"]
                        ident_identifier = Identifier.construct()
                        ident_identifier.value = patient_identifer
                        ident_identifier.system = "https://www.cellosaurus.org/name-list"
                        ident_list.append(ident_identifier)

                for xref in cl["xref-list"]:
                    if xref["database"] == "DepMap":
                        depmap_identifier = Identifier.construct()
                        depmap_identifier.value = xref["accession"]
                        # dep_map_url = xref["url"] # ex. https://depmap.org/portal/cell_line/ACH-000035"
                        depmap_identifier.system = "https://depmap.org/cell_line"
                        ident_list.append(depmap_identifier)

                    if xref["database"] == "Cosmic":
                        cosmic_identifier = Identifier.construct()
                        cosmic_identifier.value = xref["accession"]
                        cosmic_identifier.system = "https://cancer.sanger.ac.uk/cosmic/cell_line"
                        ident_list.append(cosmic_identifier)

                if "sex" in cl.keys() and cl["sex"]:
                    gender = cl["sex"].lower()
                    patient = Patient(
                        **{"id": patient_id, "gender": gender, "identifier": ident_list})
                    patients.append(patient)
                    patient_ref = Reference(**{"reference": "/".join(["Patient", patient_id])})

                if patient:
                    # add condition from disease-list
                    if "disease-list" in cl.keys():
                        for disease_annotation in cl["disease-list"]:
                            condition_identifier = Identifier(
                                **{"system": "https://www.cellosaurus.org/disease",
                                   "value": disease_annotation["accession"]})
                            condition_id = utils.mint_id(identifier=condition_identifier, resource_type="Condition",
                                                         project_id=project_id,
                                                         namespace=NAMESPACE_CELLOSAURUS)

                            if "terminology" in disease_annotation.keys() and disease_annotation[
                                "terminology"] == "NCIt":
                                condition_clinicalstatus_code = CodeableConcept.construct()
                                condition_clinicalstatus_code.coding = [
                                    {"system": "http://terminology.hl7.org/CodeSystem/condition-clinical",
                                     "display": "unknown", "code": "unknown"}]

                                disease_coding = []
                                code = disease_annotation["accession"]

                                if "value" in disease_annotation.keys():
                                    display = disease_annotation["value"]
                                elif "label" in disease_annotation.keys():
                                    display = disease_annotation["label"]
                                else:
                                    display = "place_holder"

                                coding = {'system': "https://ncit.nci.nih.gov/", 'display': display, 'code': code}

                                disease_coding.append(coding)

                                mondo = [d["mondo_id"] for d in ncit2mondo if
                                         d["ncit_id"] == disease_annotation["accession"]]
                                if mondo:
                                    mondo_code = mondo[0]
                                    mondo_display = display
                                    mondo_coding = {'system': "https://www.ebi.ac.uk/ols4/ontologies/mondo",
                                                    'display': mondo_display, 'code': mondo_code}
                                    disease_coding.append(mondo_coding)

                                cc = CodeableConcept.construct()
                                cc.coding = disease_coding

                                onset_age = None
                                if "age" in cl.keys() and cl["age"]:
                                    if "Y" not in cl["age"] and cl["age"][-1] == "M":
                                        age = round(int(cl["age"].split("M")[0]) / 12, 2)
                                        onset_age = Age(**{"value": age})
                                    elif "Y" in cl["age"]:
                                        age = cl["age"].split("Y")[0]
                                        if "-" in age:
                                            age = age.split("-")[0]
                                        if age.startswith(">"):
                                            age = age.replace(">", "")
                                        onset_age = Age(**{"value": age})
                                    else:
                                        if verbose:
                                            print("Age syntax doesn't match: ", cl["age"])

                                if onset_age:
                                    conditions.append(Condition(
                                        **{"id": condition_id, "identifier": [condition_identifier], "code": cc,
                                           "subject": patient_ref,
                                           "clinicalStatus": condition_clinicalstatus_code, "onsetAge": onset_age}))
                                else:
                                    conditions.append(Condition(
                                        **{"id": condition_id, "identifier": [condition_identifier], "code": cc,
                                           "subject": patient_ref,
                                           "clinicalStatus": condition_clinicalstatus_code}))

                    sample_parents_ref = []
                    # sample hierarchy
                    if "derived-from" in cl.keys() and cl["derived-from"]:
                        for parent_cell in cl["derived-from"]:
                            if "terminology" in parent_cell.keys() and parent_cell["terminology"] == "Cellosaurus":

                                parent_identifier = Identifier(
                                    **{"system": "https://www.cellosaurus.org/cell-line-primary-accession",
                                       "value": parent_cell["accession"]})
                                parent_id = utils.mint_id(identifier=parent_identifier, resource_type="Specimen",
                                                          project_id=project_id,
                                                          namespace=NAMESPACE_CELLOSAURUS)

                                parent_id_identifier = Identifier.construct()
                                parent_id_identifier.value = parent_cell["accession"]
                                parent_id_identifier.system = "https://www.cellosaurus.org/"

                                parent_identifier = Identifier.construct()
                                parent_identifier.value = parent_cell["value"]
                                parent_identifier.system = "https://www.cellosaurus.org/"

                                parent_sample = Specimen(
                                    **{"id": parent_id, "identifier": [parent_id_identifier, parent_identifier]})
                                if parent_sample not in samples:
                                    samples.append(parent_sample)
                                sample_parents_ref.append(Reference(**{"reference": "/".join(["Specimen", parent_id])}))

                    specimen_id = utils.mint_id(identifier=patient_identifier, resource_type="Specimen",
                                                project_id=project_id,
                                                namespace=NAMESPACE_CELLOSAURUS)

                    if sample_parents_ref:
                        samples.append(Specimen(
                            **{"id": specimen_id, "subject": patient_ref, "identifier": ident_list,
                               "parent": sample_parents_ref}))
                    else:
                        samples.append(Specimen(
                            **{"id": specimen_id, "subject": patient_ref, "identifier": ident_list}))

    return {"patients": patients, "conditions": conditions, "samples": samples}


def cellosaurus_to_fhir_ndjson(out_dir, obj):
    patients = [orjson.loads(patient.json()) for patient in obj["patients"]]
    samples = [orjson.loads(sample.json()) for sample in obj["samples"]]
    samples = list({v['id']: v for v in samples}.values())
    conditions = [orjson.loads(condition.json()) for condition in obj["conditions"]]
    conditions = list({v['id']: v for v in conditions}.values())

    if patients:
        utils.fhir_ndjson(patients, os.path.join(out_dir, "Patient.ndjson"))
        print("Successfully converted Cellosaurus info to FHIR's Patient ndjson file!")
    if samples:
        utils.fhir_ndjson(samples, os.path.join(out_dir, "Specimen.ndjson"))
        print("Successfully converted Cellosaurus info to FHIR's Specimen ndjson file!")
    if conditions:
        utils.fhir_ndjson(conditions, os.path.join(out_dir, "Condition.ndjson"))
        print("Successfully converted Cellosaurus info to FHIR's Condition ndjson file!")


def cellosaurus2fhir(path, out_dir):
    cell_lines = utils.load_ndjson(path=path)
    cellosaurus_fhir_objects = cellosaurus_fhir_mappping(cell_lines)
    cellosaurus_to_fhir_ndjson(out_dir=out_dir, obj=cellosaurus_fhir_objects)
