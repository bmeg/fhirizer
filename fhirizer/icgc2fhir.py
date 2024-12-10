import os
import re
import glob
import pathlib
import inflection
import itertools
import pandas as pd
import uuid
import json
import orjson
import copy
from fhir.resources.identifier import Identifier
from fhir.resources.researchstudy import ResearchStudy
from fhir.resources.codeableconcept import CodeableConcept
from fhir.resources.encounter import Encounter
from fhir.resources.reference import Reference
from fhir.resources.condition import Condition, ConditionStage
from fhir.resources.observation import Observation
from fhir.resources.specimen import Specimen, SpecimenProcessing, SpecimenCollection
from fhir.resources.patient import Patient
from fhir.resources.researchsubject import ResearchSubject
from fhir.resources.duration import Duration
from fhir.resources.procedure import Procedure
from fhir.resources.bodystructure import BodyStructure, BodyStructureIncludedStructure
from fhir.resources.documentreference import DocumentReference, DocumentReferenceContent
from fhir.resources.attachment import Attachment
from fhirizer import utils
import importlib.resources
from pathlib import Path
from uuid import uuid3, NAMESPACE_DNS

smoking_obs = utils._read_json(
    str(Path(importlib.resources.files('fhirizer').parent / 'resources' / 'icgc' / 'observations' / 'smoking.json')))
alcohol_obs = utils._read_json(
    str(Path(importlib.resources.files('fhirizer').parent / 'resources' / 'icgc' / 'observations' / 'alcohol.json')))
biospecimen_observation = utils._read_json(str(Path(importlib.resources.files(
    'fhirizer').parent / 'resources' / 'gdc_resources' / 'content_annotations' / 'biospecimen' / 'biospecimen_observation.json')))

# smoking_obs = utils._read_json("resources/icgc/observations/smoking.json")
# alcohol_obs = utils._read_json("resources/icgc/observations/alcohol.json")
# NOTE: all url's are based on current site that will be-updated https://platform.icgc-argo.org/

# project_id = "ICGC"
# NAMESPACE_GDC = uuid3(NAMESPACE_DNS, 'icgc-argo.org')

project_id = "cbds"
NAMESPACE_GDC = uuid3(NAMESPACE_DNS, 'evotypes_labkey_demo')

conditionoccurredFollowing = {
    "extension": [
        {
            "url": "https://dcc.icgc.org",
            "valueCoding": {
                "system": "http://snomed.info/sct",
                "code": "",
                "display": ""
            }
        }
    ],
    "url": "http://hl7.org/fhir/StructureDefinition/condition-occurredFollowing",
    "valueString": ""
},

conditionoccurredFollowing_snomed_code = {"disease progression": "246450006", "stable disease": "58158008",
                                          "unknown": "261665006", "partial response": "399204005"}

# ResearchStudy condition codes
SC = [{
    "system": "http://snomed.info/sct",
    "code": "118286007",
    "display": "Squamous Cell Neoplasms"
},
    {
        "system": "http://snomed.info/sct",
        "code": "115215004",
        "display": "Adenomas and Adenocarcinomas"
    }]

ES = [{
    "system": "http://snomed.info/sct",
    "code": "276803003",
    "display": "Adenocarcinoma of esophagus"},
    {
        "system": "http://snomed.info/sct",
        "code": "115215004",
        "display": "Adenomas and Adenocarcinomas"
    }]

relapse_type_snomed = {"Local recurrence of malignant tumor of esophagus": "314960002",
                       "Distant metastasis present": "399409002"}

smoking_snomed_codes = [
    {
        "snomed_code": "77176002",
        "snomed_display": "Current smoker",
        "text": "Current smoker",
        "note_text": "Current smoker"
    },
    {
        "snomed_code": "8392000",
        "snomed_display": "Non-smoker",
        "text": "Non-smoker",
        "note_text": "Lifelong non-smoker (<100 cigarettes smoked in lifetime)"
    }
]

alcohol_snomed_codes = [
    {
        "snomed_code": "228276006",
        "snomed_display": "Occasional drinker",
        "text": "Occasional drinker",
        "note_text": "Occasional Drinker (< once a month)"
    },
    {
        "snomed_code": "28127009",
        "snomed_display": "Social drinker",
        "text": "Social drinker",
        "note_text": "Social Drinker (> once a month, < once a week)"
    },
    {
        "snomed_code": "225769003",
        "snomed_display": "Once a week",
        "text": "Once a week",
        "note_text": "Weekly Drinker (>=1x a week)"
    },
    {
        "snomed_code": "69620002",
        "snomed_display": "Daily",
        "text": "Daily",
        "note_text": "Daily Drinker"
    }
]

exam = {
    "resourceType": "Observation",
    "id": "f026c5e8-d485-593f-af5c-38080d0ea4f9",
    "status": "final",
    "category": [
        {
            "coding": [
                {
                    "system": "http://terminology.hl7.org/CodeSystem/observation-category",
                    "code": "exam",
                    "display": "exam"
                }
            ]
        }
    ],
    "code": {
        "coding": [
            {
                "system": "https://terminology.hl7.org/5.1.0/NamingSystem-icd10CM.html",
                "code": "C34.1",
                "display": "Malignant neoplasm of upper lobe, bronchus or lung"
            }
        ]
    }
}

relapse_type = ["distant recurrence/metastasis",
                "local recurrence",
                "local recurrence and distant metastasis",
                "progression (liquid tumours)"]

# for each patient create bodyStructure with either of these general bodySites
body_site_snomed_code = {"Esophagus": "32849002", "Bronchus and lung": "110736001"}
snomed_system = "http://snomed.info/sct"

dictionary_cols = ['csv_column_name',
                   'csv_description',
                   'csv_type',
                   'csv_type_notes',
                   'fhir_resource_type',
                   'coding_system',
                   'coding_code',
                   'coding_display',
                   'coding_version',
                   'observation_subject',
                   'uom_system',
                   'uom_code',
                   'uom_unit']


def project_files(path, project):
    dir_path = "".join([path, project, "/*.tsv.gz"])
    all_paths = glob.glob(dir_path)
    return all_paths


def fetch_paths(path):
    all_paths = glob.glob(path)
    return all_paths


def get_df(file_path):
    df = pd.read_csv(file_path, compression='gzip', sep="\t")
    df = df.fillna('')
    return df


def simplify_data_types(data_type):
    if data_type in ['int64', 'int32', 'int16']:
        return 'integer'
    elif data_type in ['float64', 'float32', 'float16']:
        return 'float'
    elif data_type in ['object', 'string']:
        return 'string'
    elif data_type == 'bool':
        return 'boolean'
    elif data_type in ['datetime64[ns]', 'timedelta64[ns]', 'period']:
        return 'date'
    else:
        print(f"New Data type: {data_type}.")
        return data_type


def reform(df, out_path, project_name=None, df_type=None, file_name="data-dictionary-original"):
    df.columns = df.columns.to_series().apply(lambda x: inflection.underscore(inflection.parameterize(x)))

    data_type_list = []
    [data_type_list.append(simplify_data_types(str(pd_dat_type.name))) for pd_dat_type in list(df.dtypes)]

    df_dictionary = pd.DataFrame(columns=dictionary_cols)
    df_dictionary['csv_column_name'] = list(df.columns)

    df_dictionary['csv_type'] = data_type_list
    df_dictionary = df_dictionary.fillna('')

    if project_name:
        file_name = "-".join([df_type, project_name, file_name])

    df_dictionary.to_excel(pathlib.Path(out_path) / f"{file_name}.xlsx", index=False)
    df.to_csv(pathlib.Path(out_path) / f"{file_name}.csv", index=False)


def init_mappings(project_name, paths, out_path):
    # caution this re-writes mappings
    for path in paths:
        if "donor_therapy" in path:
            donor_therapy_df = get_df(path)
            reform(donor_therapy_df, out_path, project_name=project_name, df_type="donor_therapy",
                   file_name="data-dictionary-original")
        elif "donor_exposure" in path:
            donor_exposure_df = get_df(path)
            reform(donor_exposure_df, out_path, project_name=project_name, df_type="donor_exposure",
                   file_name="data-dictionary-original")
        elif "donor_surgery" in path:
            donor_surgery_df = get_df(path)
            reform(donor_surgery_df, out_path, project_name=project_name, df_type="donor_surgery",
                   file_name="data-dictionary-original")
        elif "donor_family" in path:
            donor_family_df = get_df(path)
            reform(donor_family_df, out_path, project_name=project_name, df_type="donor_family",
                   file_name="data-dictionary-original")
        elif "donor." in path:
            donor_df = get_df(path)
            reform(donor_df, out_path, project_name=project_name, df_type="donor",
                   file_name="data-dictionary-original")
        elif "sample" in path:
            sample_df = get_df(path)
            reform(sample_df, out_path, project_name=project_name, df_type="sample",
                   file_name="data-dictionary-original")
        elif "specimen" in path:
            specimen_df = get_df(path)
            reform(specimen_df, out_path, project_name=project_name, df_type="specimen",
                   file_name="data-dictionary-original")
        elif "simple_somatic_mutation.open" in path:
            ssm_df = get_df(path)
            reform(ssm_df, out_path, project_name=project_name, df_type="simple_somatic_mutation",
                   file_name="data-dictionary-original")
        # elif "copy_number_somatic_mutation" in path:
        #    cnsm_df = get_df(path)
        #    reform(cnsm_df, out_path, project_name=project_name, df_type="copy_number_somatic_mutation",
        #           file_name="data-dictionary-original")


def fetch_mappings(file_paths, project_name='ESAD-UK'):
    df_dict = {}
    for file_path in file_paths:
        file_name = os.path.basename(file_path)
        key = file_name.split("-" + project_name)[0]

        df = pd.read_excel(file_path)
        df_subset = df[['csv_column_name', 'csv_type', 'fhir_resource_type']]
        df_subset = df_subset.fillna('')
        df_dict[key] = df_subset
    return df_dict


def fetch_data(file_paths, project_name):
    df_dict = {}
    for file_path in file_paths:
        file_name = os.path.basename(file_path)
        key = file_name.split("-" + project_name)[0]

        df = pd.read_csv(file_path)
        df = df.fillna('')
        df_dict[key] = df
    return df_dict


def fhir_research_study(df):
    research_study_list = []
    name = df["project_code"].unique()[0]
    rs_name = "icgc_project"

    condition = None
    if name in ["ESAD-UK", "ESCA-CN"]:
        rs_name = "Esophageal Adenocarcinoma"
        condition = CodeableConcept(**{"coding": ES})
    elif name in ["LUSC-KR", "LUSC-CN"]:
        rs_name = "Lung Squamous cell carcinoma"
        condition = CodeableConcept(**{"coding": SC})

    research_study_parent_ident = Identifier(**{"system": "".join(["https://platform.icgc-argo.org/", "program"]),
                                                "value": "ICGC"})

    research_study_parent_id = utils.mint_id(
        identifier=research_study_parent_ident,
        resource_type="ResearchStudy",
        project_id=project_id,
        namespace=NAMESPACE_GDC)

    icgc_program = ResearchStudy(**{"id": research_study_parent_id,
                                    "identifier": [research_study_parent_ident], "status": "active"})
    research_study_list.append(icgc_program)

    if name != "ICGC":
        research_study_ident = Identifier(
            **{"system": "".join(["https://platform.icgc-argo.org/", "project"]), "value": name})

        research_study_id = utils.mint_id(
            identifier=research_study_ident,
            resource_type="ResearchStudy",
            project_id=project_id,
            namespace=NAMESPACE_GDC)

        icgc_project = ResearchStudy(**{"id": research_study_id,
                                        "identifier": [research_study_ident],
                                        "name": rs_name, "status": "active", "partOf": [
                Reference(**{"reference": "/".join(["ResearchStudy", icgc_program.id])})],
                                        "condition": [condition]})
        research_study_list.append(icgc_project)

    studies = [value for value in df['study_donor_involved_in'].unique() if value]

    if studies:
        for study in studies:
            if study not in [name]:
                research_ident = Identifier(
                    **{"system": "".join(["https://platform.icgc-argo.org/", "project"]), "value": study})

                research_id = utils.mint_id(
                    identifier=research_ident,
                    resource_type="ResearchStudy",
                    project_id=project_id,
                    namespace=NAMESPACE_GDC)

                icgc_study = ResearchStudy(**{"id": research_id,
                                              "identifier": [research_ident],
                                              "name": rs_name, "status": "active", "partOf": [
                        Reference(**{"reference": "/".join(["ResearchStudy", icgc_program.id])}),
                        Reference(**{"reference": "/".join(["ResearchStudy", icgc_project.id])})]})
                research_study_list.append(icgc_study)
    return research_study_list


def exposure_observation(obs, row, snomed, smoking):
    patient_ident = Identifier(**{"system": "".join(["https://platform.icgc-argo.org/", "donor_id"]),
                                  "value": row['icgc_donor_id']})

    patient_id = utils.mint_id(
        identifier=patient_ident,
        resource_type="Patient",
        project_id=project_id,
        namespace=NAMESPACE_GDC)

    if smoking:
        obs["note"][0]["text"] = row['tobacco_smoking_history_indicator']
    else:
        obs["note"][0]["text"] = row['alcohol_history_intensity']

    obs["subject"] = {"reference": "".join(["Patient/", patient_id])}
    obs["focus"] = [{"reference": "".join(["Patient/", patient_id])}]
    obs_ident = Identifier(**{"system": "".join(["https://platform.icgc-argo.org/", "donor_id"]),
                              "value": "/".join([row['icgc_donor_id'], "social-history"])})
    obs["id"] = utils.mint_id(
        identifier=[obs_ident, patient_ident],
        resource_type="Observation",
        project_id=project_id,
        namespace=NAMESPACE_GDC)

    if snomed:
        obs["valueCodeableConcept"]["coding"][0]["code"] = snomed["snomed_code"]
        obs["valueCodeableConcept"]["coding"][0]["display"] = snomed["snomed_display"]
        obs["valueCodeableConcept"]["text"] = snomed["text"]
    return obs


def fhir_smoking_exposure_observations(row):
    obs = None
    if 'tobacco_smoking_history_indicator' in row.keys() and pd.notna(
            row['tobacco_smoking_history_indicator']) and isinstance(row['tobacco_smoking_history_indicator'], str):
        if row['tobacco_smoking_history_indicator'] in ['Current reformed smoker for > 15 years',
                                                        'Current reformed smoker for <= 15 years',
                                                        'Current reformed smoker, duration not specified']:
            obs = exposure_observation(obs=copy.deepcopy(smoking_obs), row=row, snomed=None, smoking=True)
        elif "Current smoker" in row['tobacco_smoking_history_indicator']:
            snomed = next((code for code in smoking_snomed_codes if
                           code['note_text'] == "Lifelong non-smoker (<100 cigarettes smoked in lifetime)"), None)
            if snomed:
                obs = exposure_observation(obs=copy.deepcopy(smoking_obs), row=row, snomed=snomed, smoking=True)
        elif "Lifelong non-smoker" in row['tobacco_smoking_history_indicator']:
            snomed = next((code for code in smoking_snomed_codes if
                           code['note_text'] == "Lifelong non-smoker (<100 cigarettes smoked in lifetime)"), None)
            if snomed:
                obs = exposure_observation(obs=copy.deepcopy(smoking_obs), row=row, snomed=snomed, smoking=True)
    if obs:
        return obs


def fhir_alcohol_exposure_observations(row):
    obs = None
    if 'alcohol_history_intensity' in row.keys() and pd.notna(row['alcohol_history_intensity']) and isinstance(
            row['alcohol_history_intensity'], str):
        if 'Daily Drinker' in row['alcohol_history_intensity'] and row['alcohol_history_intensity']:
            snomed = [code for code in alcohol_snomed_codes if code['note_text'] == 'Daily Drinker'][0]
            obs = exposure_observation(obs=copy.deepcopy(alcohol_obs), row=row, snomed=snomed, smoking=False)
        elif 'Social Drinker' in row['alcohol_history_intensity']:
            snomed = [code for code in alcohol_snomed_codes if
                      code['note_text'] == 'Social Drinker (> once a month, < once a week)'][0]
            obs = exposure_observation(obs=copy.deepcopy(alcohol_obs), row=row, snomed=snomed, smoking=False)
        elif 'Weekly Drinker' in row['alcohol_history_intensity']:
            snomed = [code for code in alcohol_snomed_codes if code['note_text'] == 'Weekly Drinker (>=1x a week)'][0]
            obs = exposure_observation(obs=copy.deepcopy(alcohol_obs), row=row, snomed=snomed, smoking=False)
        elif 'Occasional Drinker' in row['alcohol_history_intensity']:
            snomed = \
                [code for code in alcohol_snomed_codes if code['note_text'] == 'Occasional Drinker (< once a month)'][0]
            obs = exposure_observation(obs=copy.deepcopy(alcohol_obs), row=row, snomed=snomed, smoking=False)
    if obs:
        return obs


def fhir_patient(row):
    sex_code = None
    if row['donor_sex'] == "male":
        sex_code = "M"
    elif row['donor_sex'] == "female":
        sex_code = "F"
    patient_gender = None
    if row['donor_sex']:
        patient_gender = row['donor_sex']

    patient_ident = Identifier(**{"system": "".join(["https://platform.icgc-argo.org/", "donor_id"]),
                                  "value": row['icgc_donor_id']})

    patient_id = utils.mint_id(
        identifier=patient_ident,
        resource_type="Patient",
        project_id=project_id,
        namespace=NAMESPACE_GDC)

    patient = Patient(
        **{"id": patient_id,
           "identifier": [patient_ident],
           "gender": patient_gender,
           "extension": [
               {
                   "url": "http://hl7.org/fhir/us/core/StructureDefinition/us-core-birthsex",
                   "valueCode": sex_code
               }]
           })
    return patient


def fhir_research_subject(row):
    patient_ident = Identifier(**{"system": "".join(["https://platform.icgc-argo.org/", "donor_id"]),
                                  "value": row['icgc_donor_id']})

    patient_id = utils.mint_id(
        identifier=patient_ident,
        resource_type="Patient",
        project_id=project_id,
        namespace=NAMESPACE_GDC)

    research_study_ident = Identifier(**{"system": "".join(["https://platform.icgc-argo.org/", "project"]),
                                         "value": row['project_code']})

    research_study_id = utils.mint_id(
        identifier=research_study_ident,
        resource_type="ResearchStudy",
        project_id=project_id,
        namespace=NAMESPACE_GDC)

    research_subject_id = utils.mint_id(
        identifier=patient_ident,
        resource_type="ResearchSubject",
        project_id=project_id,
        namespace=NAMESPACE_GDC)

    return ResearchSubject(
        **{"id": research_subject_id, "status": "active",
           "study": Reference(**{"reference": "/".join(["ResearchStudy", research_study_id])}),
           "subject": Reference(**{"reference": "/".join(["Patient", patient_id])})})


def fhir_body_structure(row):
    # patient_id = str(uuid.uuid3(uuid.NAMESPACE_DNS, "".join([row['icgc_donor_id'], row['project_code']])))
    patient_ident = Identifier(**{"system": "".join(["https://platform.icgc-argo.org/", "donor_id"]),
                                  "value": row['icgc_donor_id']})

    patient_id = utils.mint_id(
        identifier=patient_ident,
        resource_type="Patient",
        project_id=project_id,
        namespace=NAMESPACE_GDC)

    body_site = None
    if row['project_code'] in ["ESAD-UK", "ESCA-CN"]:
        body_site = {
            "system": "http://snomed.info/sct",
            "code": "32849002",
            "display": "Esophagus"
        }
    elif row['project_code'] in ["LUSC-KR", "LUSC-CN"]:
        body_site = {
            "system": "http://snomed.info/sct",
            "code": "110736001",
            "display": "Bronchus and lung"
        }

    body_structure_ident = Identifier(**{"system": "".join(["https://platform.icgc-argo.org/", "body_site"]),
                                         "value": body_site["display"]})

    body_structure_id = utils.mint_id(
        identifier=[patient_ident, body_structure_ident],
        resource_type="BodyStructure",
        project_id=project_id,
        namespace=NAMESPACE_GDC)

    body_structure = BodyStructure(
        **{"id": body_structure_id,
           "includedStructure": [BodyStructureIncludedStructure(**{"structure": {"coding": [body_site]}})],
           "patient": Reference(**{"reference": "/".join(["Patient", patient_id])})
           })
    return body_structure


def fhir_condition(row):
    # condition, condition observation, encounter
    project_id = "ICGC"
    icd10 = None
    if row['icgc_donor_id']:
        icd10 = row['donor_diagnosis_icd10'].upper()

    patient_ident = Identifier(**{"system": "".join(["https://platform.icgc-argo.org/", "donor_id"]),
                                  "value": row['icgc_donor_id']})

    patient_id = utils.mint_id(
        identifier=patient_ident,
        resource_type="Patient",
        project_id=project_id,
        namespace=NAMESPACE_GDC)

    # https://docs.icgc.org/submission/projects/
    condition_discription = None
    if row['project_code'] in ["ESAD-UK", "ESCA-CN"]:
        condition_discription = 'Esophageal Adenocarcinoma'
    elif row['project_code'] in ["LUSC-KR", "LUSC-CN"]:
        condition_discription = 'Lung Squamous Cell Carcinoma'

    condition_ident = Identifier(**{"system": "".join(["https://platform.icgc-argo.org/", "project"]),
                                    "value": condition_discription})

    condition_id = utils.mint_id(
        identifier=[condition_ident, patient_ident],
        resource_type="Condition",
        project_id=project_id,
        namespace=NAMESPACE_GDC)

    clinicalStatus = None
    if 'donor_relapse_type' in row.keys() and pd.notna(row['donor_relapse_type']) and row[
        'donor_relapse_type'] in relapse_type:
        clinicalStatus_code = {
            "system": "http://terminology.hl7.org/CodeSystem/condition-clinical",
            "code": "relapse",
            "display": "Relapse"
        }
        clinicalStatus = CodeableConcept(**{"coding": [clinicalStatus_code], "text": row['donor_relapse_type']})

    elif pd.notna(row['disease_status_last_followup']) and row['disease_status_last_followup'] in [
        'no evidence of disease', 'stable']:
        clinicalStatus_code = {
            "system": "http://terminology.hl7.org/CodeSystem/condition-clinical",
            "code": "remission",
            "display": "Remission"
        }
        clinicalStatus = CodeableConcept(**{"coding": [clinicalStatus_code], "text": "".join(
            ["Since last follow-up: ", row['disease_status_last_followup']])})

    else:
        clinicalStatus = CodeableConcept(**{"coding": [{
            "system": "http://terminology.hl7.org/CodeSystem/condition-clinical",
            "code": "active",
            "display": "Active"
        }]})

    body_site = None
    if row['project_code'] in ["ESAD-UK", "ESCA-CN"]:
        body_site = CodeableConcept(**{"coding": [{
            "system": "http://snomed.info/sct",
            "code": "32849002",
            "display": "Esophagus"
        }]})
    elif row['project_code'] in ["LUSC-KR", "LUSC-CN"]:
        body_site = CodeableConcept(**{"coding": [{
            "system": "http://snomed.info/sct",
            "code": "110736001",
            "display": "Bronchus and lung"
        }]})

    condition_code = None
    encounter = None
    obs_exam = None
    if 'donor_diagnosis_icd10' in row.keys() and pd.notna(row['donor_diagnosis_icd10']) and re.match(
            r"^[A-Za-z0-9\-.]+$",
            row['donor_diagnosis_icd10']):
        condition_code = CodeableConcept(**{"coding": [{
            "system": "https://terminology.hl7.org/5.1.0/NamingSystem-icd10CM.html",
            "code": str(icd10),
            "display": str(icd10)
        }]})

        encounter = Encounter.model_construct()
        encounter.status = 'completed'
        encounter.id = utils.mint_id(
            identifier=patient_ident,
            resource_type="Encounter",
            project_id=project_id,
            namespace=NAMESPACE_GDC)

        encounter.subject = Reference(**{"reference": "/".join(["Patient", patient_id])})

        obs_ident = Identifier(**{"system": "".join(["https://platform.icgc-argo.org/", "donor_id"]),
                                  "value": "/".join([row['icgc_donor_id'], "exam"])})

        obs_exam = copy.deepcopy(exam)
        obs_exam["id"] = utils.mint_id(
            identifier=[obs_ident, patient_ident],
            resource_type="Observation",
            project_id=project_id,
            namespace=NAMESPACE_GDC)

        obs_exam["subject"] = {"reference": "/".join(["Patient", patient_id])}
        obs_exam["focus"] = [{"reference": "/".join(["Patient", patient_id])},
                             {"reference": "/".join(["Condition", condition_id])}]

        comp = []
        if row['donor_survival_time'] and isinstance(row['donor_survival_time'], float):
            a_comp = utils.get_component('donor_survival_time', value=row['donor_survival_time'],
                                         component_type='float')
            comp.append(a_comp)
        if row['donor_interval_of_last_followup'] and isinstance(row['donor_interval_of_last_followup'], float):
            b_comp = utils.get_component('donor_interval_of_last_followup',
                                         value=row['donor_interval_of_last_followup'],
                                         component_type='float')
            comp.append(b_comp)
        if comp:
            obs_exam["component"] = comp

        if encounter:
            obs_exam["encounter"] = {"reference": "/".join(["Encounter", encounter.id])}

    age_string = None
    if row['donor_age_at_diagnosis'] and isinstance(row['donor_age_at_diagnosis'], float):
        age_string = str(int(row['donor_age_at_diagnosis']))

    condition = Condition(**{"id": condition_id,
                             "clinicalStatus": clinicalStatus,
                             "subject": Reference(**{"reference": "/".join(["Patient", patient_id])}),
                             "bodySite": [body_site], "code": condition_code, "onsetString": age_string})

    return {"condition": condition, "encounter": encounter, "observation": obs_exam}


def fhir_specimen(row):
    # specimen, specimen Observation
    # SpecimenContainer() # don't have device info/schema atm -> observation component
    # https://terminology.hl7.org/5.5.0/ValueSet-v2-0493.html

    observations = []
    # parent sample
    sample_identifier_0 = Identifier(**{"system": "".join(["https://platform.icgc-argo.org/", "icgc_sample_id"]),
                                        "value": row['icgc_sample_id']})

    sample_id = utils.mint_id(
        identifier=sample_identifier_0,
        resource_type="Specimen",
        project_id=project_id,
        namespace=NAMESPACE_GDC)

    patient_ident_sample = Identifier(**{"system": "".join(["https://platform.icgc-argo.org/", "donor_id"]),
                                         "value": row['icgc_donor_id_sample']})

    sample_patient = utils.mint_id(
        identifier=patient_ident_sample,
        resource_type="Patient",
        project_id=project_id,
        namespace=NAMESPACE_GDC)

    sample_identifier_1 = Identifier(**{"system": "".join(["https://platform.icgc-argo.org/", "submitted_sample_id"]),
                                        "value": row['submitted_sample_id']})
    sample = Specimen(**{"id": sample_id, "identifier": [sample_identifier_0, sample_identifier_1],
                         "subject": Reference(**{"reference": "/".join(["Patient", sample_patient])})})

    sample_components = []
    if 'percentage_cellularity' in row.keys() and pd.notna(row['percentage_cellularity']) and isinstance(
            row['percentage_cellularity'], str):
        cpc = utils.get_component('percentage_cellularity', value=row['percentage_cellularity'],
                                  component_type='string')
        sample_components.append(cpc)
    if 'level_of_cellularity' in row.keys() and pd.notna(row['level_of_cellularity']) and isinstance(
            row['level_of_cellularity'], float):
        # if not isinstance(row['level_of_cellularity'], float):
        # float(row['level_of_cellularity'])
        cpc = utils.get_component('level_of_cellularity', value=row['level_of_cellularity'],
                                  component_type='float')
        sample_components.append(cpc)

    if 'analyzed_sample_interval' in row.keys() and pd.notna(row['analyzed_sample_interval']) and isinstance(
            row['analyzed_sample_interval'], float):
        cpc = utils.get_component('analyzed_sample_interval', value=row['analyzed_sample_interval'],
                                  component_type='float')
        sample_components.append(cpc)

    if sample_components:
        sample_observation = copy.deepcopy(biospecimen_observation)
        # print(sample_components)

        sample_observation['id'] = utils.mint_id(
            identifier=sample_identifier_0,
            resource_type="Observation",
            project_id=project_id,
            namespace=NAMESPACE_GDC)

        sample_observation['component'] = sample_components

        sample_observation['subject'] = {
            "reference": "/".join(["Patient", sample_patient])}
        sample_observation['specimen'] = {
            "reference": "/".join(["Specimen", sample_id])}
        sample_observation['focus'][0] = {
            "reference": "/".join(["Specimen", sample_id])}
        observations.append(copy.deepcopy(sample_observation))

    # child specimen

    specimen_identifier_0 = Identifier(**{"system": "".join(["https://platform.icgc-argo.org/", "icgc_sample_id"]),
                                          "value": row['icgc_specimen_id']})

    specimen_id = utils.mint_id(
        identifier=specimen_identifier_0,
        resource_type="Specimen",
        project_id=project_id,
        namespace=NAMESPACE_GDC)

    patient_ident_specimen = Identifier(**{"system": "".join(["https://platform.icgc-argo.org/", "donor_id"]),
                                           "value": row['icgc_donor_id_specimen']})

    specimen_patient = utils.mint_id(
        identifier=patient_ident_specimen,
        resource_type="Patient",
        project_id=project_id,
        namespace=NAMESPACE_GDC)

    specimen_identifier_1 = Identifier(
        **{"system": "".join(["https://platform.icgc-argo.org/", "submitted_specimen_id"]),
           "value": row['submitted_specimen_id_specimen']})

    sc = None
    if row['specimen_interval'] and pd.notna(row['specimen_interval']) and isinstance(row['specimen_interval'], float):
        sc = SpecimenCollection(**{"duration": Duration(**{"value": row['specimen_interval']})})

    processing_list = []
    sp = []
    if 'specimen_processing' in row.keys() and pd.notna(row['specimen_processing']) and re.match(r"^[A-Za-z0-9\-.]+$",
                                                                                                 row[
                                                                                                     'specimen_processing']):
        processing_list.append({
            'system': "https://dcc.icgc.org/processing_method",
            'display': row['specimen_processing'],
            'code': row['specimen_processing']})
    if 'specimen_processing_other' in row.keys() and pd.notna(row['specimen_processing_other']) and re.match(
            r"^[A-Za-z0-9\-.]+$", row['specimen_processing']):
        processing_list.append({
            'system': "https://dcc.icgc.org/processing_method",
            'display': row['specimen_processing_other'],
            'code': row['specimen_processing_other']})

    if processing_list:
        sp = [SpecimenProcessing(**{"method": CodeableConcept(**{"coding": processing_list})})]

    parent = None
    if sample_id:
        parent = [Reference(**{"reference": "/".join(["Specimen", sample_id])})]

    st = None
    if 'specimen_type' in row.keys() and pd.notna(row['specimen_type']):
        st = CodeableConcept(**{"coding": [
            {"code": row['specimen_type'], "system": "https://dcc.icgc.org/specimen_type",
             "display": row['specimen_type']}]})

    specimen_components = []
    if 'specimen_storage' in row.keys() and pd.notna(row['specimen_storage']) and isinstance(row['specimen_storage'],
                                                                                             str):
        if "," in row['specimen_storage']:
            row['specimen_storage'] = row['specimen_storage'].replace(",", "")

        if re.match(r"[ \r\n\t\S]+", row['specimen_storage']):
            cpc = utils.get_component('specimen_storage', value=row['specimen_storage'],
                                      component_type='string')
            specimen_components.append(cpc)

    if specimen_components:
        specimen_observation = copy.deepcopy(biospecimen_observation)
        specimen_observation['id'] = utils.mint_id(
            identifier=specimen_identifier_0,
            resource_type="Observation",
            project_id=project_id,
            namespace=NAMESPACE_GDC)
        specimen_observation['component'] = specimen_components

        specimen_observation['subject'] = {
            "reference": "/".join(["Patient", specimen_patient])}
        specimen_observation['specimen'] = {
            "reference": "/".join(["Specimen", specimen_id])}
        specimen_observation['focus'][0] = {
            "reference": "/".join(["Specimen", specimen_id])}

        if specimen_observation:
            observations.append(copy.deepcopy(specimen_observation))

    specimen = Specimen(
        **{"id": specimen_id, "identifier": [sample_identifier_0, specimen_identifier_1], "parent": parent,
           "type": st, "processing": sp, "collection": sc,
           "subject": Reference(**{"reference": "/".join(["Patient", specimen_patient])})})

    return {"samples": [specimen, sample], "observations": observations}


def fhir_document_reference(row):
    # ICGC website in midst of data transition.
    # files via https://platform.icgc-argo.org/ site
    # associated clinical data via https://dcc.icgc.org/ (deprecated)

    file_ident = Identifier(**{"system": "".join(["https://platform.icgc-argo.org/", "file"]),
                               "value": row['File ID']})

    dr_id = utils.mint_id(
        identifier=file_ident,
        resource_type="DocumentReference",
        project_id=project_id,
        namespace=NAMESPACE_GDC)

    # Data Type & Experimental Strategy
    category_list = []
    if "Data Type" in row.keys() and pd.notna(row['Data Type']):
        category_list.append(CodeableConcept(**{"coding": [{"code": row['Data Type'], "display": row['Data Type'],
                                                            "system": "https://platform.icgc-argo.org/data_type"}]}))
    if "Experimental Strategy" in row.keys() and pd.notna(row['Experimental Strategy']):
        category_list.append(CodeableConcept(
            **{"coding": [{"code": row['Experimental Strategy'], "display": row['Experimental Strategy'],
                           "system": "https://platform.icgc-argo.org/experimental_strategy"}]}))

    dr = DocumentReference(**{"id": dr_id, "identifier": [
        Identifier(**{"system": "https://platform.icgc-argo.org/file_id", "value": row['File ID']})],
                              "status": "current",
                              "basedOn": [{"reference": "/".join(["Specimen", row["sample_mintid"]])}],
                              "content": [DocumentReferenceContent(**{"attachment": Attachment(
                                  **{"title": row["file_name"],
                                     "url": "".join(["https://platform.icgc-argo.org/file/", row['File ID']]),
                                     "size": str(row["file_size"]), "hash": str(row["md5sum"])})})],
                              "subject": {"reference": "/".join(["Patient", row["patient_mintid"]])},
                              "category": category_list,
                              "type": CodeableConcept(**{"coding": [
                                  {"code": row["file_type"], "display": row["file_type"],
                                   "system": "https://platform.icgc-argo.org/file_type"}]})
                              })
    return dr


def patient_id(row):
    patient_ident = Identifier(**{"system": "".join(["https://platform.icgc-argo.org/", "donor_id"]),
                                  "value": row['icgc_donor_id']})

    patient_id = utils.mint_id(
        identifier=patient_ident,
        resource_type="Patient",
        project_id=project_id,
        namespace=NAMESPACE_GDC)

    return patient_id


def sample_id(row):
    # only applies to new data file and sample relations on argo site (sample vs. specimen where specimen is the child sample that is sequenced)
    specimen_identifier_0 = Identifier(**{"system": "".join(["https://platform.icgc-argo.org/", "icgc_sample_id"]),
                                          "value": row['icgc_sample_id']})

    specimen_id = utils.mint_id(
        identifier=specimen_identifier_0,
        resource_type="Specimen",
        project_id=project_id,
        namespace=NAMESPACE_GDC)
    return specimen_id


def icgc2fhir(project_name, has_files):
    # project_name = "ESCA-UK"
    # has_files = True
    file_name = "score-manifest.tsv"
    file_table_name = "file-table.tsv"

    this_project_path = "../ICGC/"
    map_path = f"./projects/ICGC/{project_name}/data/*.xlsx"
    dat_path = f"./projects/ICGC/{project_name}/data/*.csv"
    file_path = f"./projects/ICGC/{project_name}/data/{file_name}"
    file_table_path = f"./projects/ICGC/{project_name}/data/{file_table_name}"
    out_path = f"./projects/ICGC/{project_name}"

    # -------------------------------------------------------------------
    paths = project_files(path=this_project_path, project=project_name)
    # init_mappings(project_name, paths, out_path)

    mp = fetch_paths(map_path)
    mp_dict = fetch_mappings(mp)

    dat_paths = fetch_paths(dat_path)
    dat_paths = [path for path in dat_paths if
                 "simple_somatic_mutation" not in path and "copy_number_somatic_mutation" not in path]

    dat_dict = fetch_data(dat_paths, project_name=project_name)

    # combine sample and specimen relations
    df_specimen = pd.merge(dat_dict['specimen'], dat_dict['sample'], on='icgc_specimen_id', how='left',
                           suffixes=('_specimen', '_sample'))

    # combine patient and exposure observations
    # https://loinc.org/LG41856-2
    if 'donor_exposure' in dat_dict.keys():
        df_patient = pd.merge(dat_dict['donor'], dat_dict['donor_exposure'], on='icgc_donor_id', how='left',
                              suffixes=('', '_donor_exposure'))
        df_patient.fillna('')
    else:
        df_patient = dat_dict['donor']

    # TODO: family cancer history observation link confirmation
    # df_patient_exposure_family = pd.merge(dat_dict['donor'], dat_dict['donor_family'], on='icgc_donor_id', how='left',
    #                        suffixes=('', '_donor_family'))
    # df_patient_exposure_family = df_patient_exposure_family.fillna('')
    # -------------------------------------------------------------------
    # row = dat_dict['donor'].iloc[0]

    patients = [orjson.loads(p.model_dump_json()) for p in list(df_patient.apply(fhir_patient, axis=1)) if p]
    obs_smoking = [os for os in list(df_patient.apply(fhir_smoking_exposure_observations, axis=1)) if os]
    obs_alc = [ol for ol in list(df_patient.apply(fhir_alcohol_exposure_observations, axis=1)) if ol]

    rsub = [orjson.loads(rs.model_dump_json()) for rs in list(df_patient.apply(fhir_research_subject, axis=1)) if rs]
    rs = [orjson.loads(r.model_dump_json()) for r in fhir_research_study(df=dat_dict['donor'])]

    cond_obs_encont = df_patient.apply(fhir_condition, axis=1)
    conditions = [orjson.loads(c['condition'].model_dump_json()) for c in cond_obs_encont if c['condition']]
    encounters = [orjson.loads(c['encounter'].model_dump_json()) for c in cond_obs_encont if c['encounter']]
    obs_exam = [c['observation'] for c in cond_obs_encont if c['observation']]

    body_structures = [orjson.loads(b.model_dump_json()) for b in list(df_patient.apply(fhir_body_structure, axis=1)) if b]
    body_structures = list({v['id']: v for v in body_structures}.values())

    sample_observations_nested_list = [s["observations"] for s in list(df_specimen.apply(fhir_specimen, axis=1)) if
                                       s["observations"]]
    sample_observations_list = list(itertools.chain.from_iterable(sample_observations_nested_list))
    sample_observations = list({v['id']: v for v in sample_observations_list}.values())

    samples_nested_list = [s["samples"] for s in list(df_specimen.apply(fhir_specimen, axis=1)) if s["samples"]]
    samples_list = list(itertools.chain.from_iterable(samples_nested_list))
    samples_list_json = [orjson.loads(s.model_dump_json()) for s in samples_list]
    samples = list({v['id']: v for v in samples_list_json}.values())

    observations = obs_alc + obs_smoking + obs_exam + sample_observations
    observations = list({v['id']: v for v in observations}.values())

    # url https://platform.icgc-argo.org/file/FL37616
    document_references = None
    if has_files:
        file_metadata = pd.read_csv(file_path, sep="\t")
        file_metadata = file_metadata.fillna('')
        file_metadata.rename(
            columns={"donor_id": "icgc_donor_id", "program_id": "project_code", "sample_id(s)": "icgc_sample_id"},
            inplace=True)

        file_table = pd.read_csv(file_table_path, sep="\t")
        file_table = file_table.fillna('')
        file_table.rename(columns={"Object ID": "object_id"}, inplace=True)
        file_metadata = file_metadata.merge(file_table, on='object_id', how="left")
        file_metadata = file_metadata.fillna('')

        df_patient["patient_mintid"] = df_patient.apply(patient_id, axis=1)
        file_metadata_patient_info = file_metadata.merge(df_patient, on="icgc_donor_id", how="left",
                                                         suffixes=["", "_p"])

        df_specimen["sample_mintid"] = df_specimen.apply(sample_id, axis=1)
        file_metadata_patient_specimen_info = file_metadata_patient_info.merge(df_specimen, on='icgc_sample_id',
                                                                               how="left")

        document_references = [orjson.loads(f.model_dump_json()) for f in
                               list(file_metadata_patient_specimen_info.apply(fhir_document_reference, axis=1)) if
                               f]
    import os
    out_dir = os.path.join(out_path, "META")
    if not os.path.exists(out_dir):
        os.makedirs(out_dir)

    if patients:
        utils.fhir_ndjson(patients, "/".join([out_dir, "Patient.ndjson"]))
        print("Successfully converted GDC case info to FHIR's Patient ndjson file!")
    if rs:
        utils.fhir_ndjson(rs, "/".join([out_dir, "ResearchStudy.ndjson"]))
        print("Successfully converted GDC case info to FHIR's ResearchStudy ndjson file!")
    if rsub:
        utils.fhir_ndjson(rsub, "/".join([out_dir, "ResearchSubject.ndjson"]))
        print("Successfully converted GDC case info to FHIR's ResearchSubject ndjson file!")
    if observations:
        utils.fhir_ndjson(observations, "/".join([out_dir, "Observation.ndjson"]))
        print("Successfully converted GDC case info to FHIR's Observation ndjson file!")
    if conditions:
        utils.fhir_ndjson(conditions, "/".join([out_dir, "Condition.ndjson"]))
        print("Successfully converted GDC case info to FHIR's Condition ndjson file!")
    if body_structures:
        utils.fhir_ndjson(body_structures, "/".join([out_dir, "BodyStructure.ndjson"]))
        print("Successfully converted GDC case info to FHIR's body_structures ndjson file!")
    if encounters:
        utils.fhir_ndjson(encounters, "/".join([out_dir, "Encounter.ndjson"]))
        print("Successfully converted GDC case info to FHIR's Encounter ndjson file!")
    if samples:
        utils.fhir_ndjson(samples, "/".join([out_dir, "Specimen.ndjson"]))
        print("Successfully converted GDC case info to FHIR's Specimen ndjson file!")
    if document_references:
        utils.fhir_ndjson(document_references, "/".join([out_dir, "DocumentReference.ndjson"]))
        print("Successfully converted GDC case info to FHIR's DocumentReference ndjson file!")
