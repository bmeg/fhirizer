import os
import re
import json
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
from fhir.resources.specimen import Specimen, SpecimenProcessing
from fhir.resources.patient import Patient
from fhir.resources.researchsubject import ResearchSubject
from fhir.resources.imagingstudy import ImagingStudy, ImagingStudySeries
from fhir.resources.procedure import Procedure
from fhir.resources.medicationadministration import MedicationAdministration
from fhir.resources.medication import Medication
from gdc2fhir import utils
from datetime import datetime
import icd10
import importlib.resources
from pathlib import Path

disease_types = utils._read_json(str(Path(importlib.resources.files(
    'gdc2fhir').parent / 'resources' / 'gdc_resources' / 'content_annotations' / 'case' / 'disease_types.json')))
primary_sites = utils._read_json(str(Path(importlib.resources.files(
    'gdc2fhir').parent / 'resources' / 'gdc_resources' / 'content_annotations' / 'case' / 'primary_sites.json')))
race = utils._read_json(str(Path(importlib.resources.files(
    'gdc2fhir').parent / 'resources' / 'gdc_resources' / 'content_annotations' / 'demographic' / 'race.json')))
ethnicity = utils._read_json(str(Path(importlib.resources.files(
    'gdc2fhir').parent / 'resources' / 'gdc_resources' / 'content_annotations' / 'demographic' / 'ethnicity.json')))
gender = utils._read_json(str(Path(importlib.resources.files(
    'gdc2fhir').parent / 'resources' / 'gdc_resources' / 'content_annotations' / 'demographic' / 'gender.json')))
data_dict = utils.load_data_dictionary(path=utils.DATA_DICT_PATH)
cancer_pathological_staging = utils._read_json(str(Path(importlib.resources.files(
    'gdc2fhir').parent / 'resources' / 'gdc_resources' / 'content_annotations' / 'diagnosis' / 'cancer_pathological_staging.json')))


def assign_fhir_for_project(project, disease_types=disease_types):
    # create ResearchStudy
    rs = ResearchStudy.construct()
    if project['ResearchStudyProgressStatus.actual']:
        rs.status = "-".join([project['ResearchStudy.status'], "released"])
    else:
        rs.status = project['ResearchStudy.status']

    if project['ResearchStudy.id'] in ["EXCEPTIONAL_RESPONDERS-ER", "CDDP_EAGLE-1"]:
        rs.id = project['ResearchStudy']['ResearchStudy.id']
    else:
        rs.id = project['ResearchStudy.id']

    rs.name = project['ResearchStudy.name']

    if 'ResearchStudy.identifier' in project.keys() and project['ResearchStudy.identifier']:
        ident = Identifier.construct()
        ident.value = project['ResearchStudy.identifier']
        ident.system = "".join(["https://gdc.cancer.gov/", "project"])
        rs.identifier = [ident]

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
    # TODO: check 1..1 relation
    rs_parent = ResearchStudy.construct()

    # assign required fields first
    rs_parent.status = project['ResearchStudy.status']  # child's status?
    rs_parent.id = project['ResearchStudy']['ResearchStudy.id']
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

    ref = Reference(**{"reference": "/".join(["ResearchStudy", project['ResearchStudy']['ResearchStudy.id']])})
    rs.partOf = [ref]
    #  condition -- subject --> patient <--subject-- researchsubject -- study --> researchstudy -- partOf --> researchstudy

    return {'ResearchStudy': rs.json(), "ResearchStudy.partOf": rs_parent.json(), 'ResearchStudy_obj': rs,
            "ResearchStudy.partOf_obj": rs_parent}


# projects_path="./tests/fixtures/project/project_key.ndjson"

def project_gdc_to_fhir_ndjson(out_dir, projects_path):
    projects = utils.load_ndjson(projects_path)
    all_rs = [assign_fhir_for_project(project=p, disease_types=disease_types) for p in projects]
    research_study = [orjson.loads(rs['ResearchStudy_obj'].json()) for rs in all_rs]
    research_study_parent = [orjson.loads(rs['ResearchStudy.partOf_obj'].json()) for rs in all_rs]
    rs_e2f = research_study + list(
        unique_everseen(research_study_parent))  # ResearchStudy -- *...1  partOf -> ResearchStudy

    with open("".join([out_dir, "/ResearchStudy.ndjson"]), 'w') as file:
        file.write('\n'.join(map(json.dumps, rs_e2f)))


# Case ---------------------------------------------------------------
# load case mapped key values
# cases = utils.load_ndjson("./tests/fixtures/case/case_key.ndjson")
# case = cases[0]

def assign_fhir_for_case(case, disease_types=disease_types, primary_sites=primary_sites, data_dict=data_dict,
                         race=race, ethnicity=ethnicity):
    # create patient **
    patient = Patient.construct()
    patient.id = case['Patient.id']

    if 'Patient.identifier' in case.keys() and case['Patient.identifier'] and re.match(r"^[A-Za-z0-9\-.]+$",
                                                                                       case['Patient.identifier']):
        patient_identifier = Identifier.construct()
        patient_identifier.value = case['Patient.identifier']
        patient_identifier.system = "".join(["https://gdc.cancer.gov/", "case"])
        patient.identifier = [patient_identifier]

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

    if 'demographic' in case.keys() and 'Patient.deceasedDateTime' in case['demographic']:
        patient.deceasedDateTime = case['demographic']['Patient.deceasedDateTime']

    race_ethnicity = []
    if 'demographic' in case.keys() and 'Extension.extension:USCoreRaceExtension' in case['demographic'].keys():
        #  race and ethnicity
        race_ext = Extension.construct()
        race_ext.url = "https://hl7.org/fhir/us/core/STU6/StructureDefinition-us-core-race.json"

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
        race_ethnicity.append(race_ext)

    if 'demographic' in case.keys() and 'Extension:extension.USCoreEthnicity' in case['demographic'].keys():
        ethnicity_ext = Extension.construct()
        ethnicity_ext.url = "http://hl7.org/fhir/us/core/STU6/StructureDefinition-us-core-ethnicity.json"

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

            race_ethnicity.append(ethnicity_ext)

        if race_ethnicity:
            patient.extension = race_ethnicity

    # gdc project for patient
    project_relations = assign_fhir_for_project(project=case['ResearchStudy'], disease_types=disease_types)
    study_ref = Reference(**{"reference": "/".join(["ResearchStudy", project_relations['ResearchStudy_obj'].id])})
    subject_ref = Reference(**{"reference": "/".join(["Patient", case['Patient.id']])})

    # create researchSubject to link Patient --> ResearchStudy
    research_subject = ResearchSubject.construct()
    # research_subject.status = "".join(['unknown-', case['ResearchSubject.status']])
    research_subject.status = "active"
    research_subject.study = study_ref
    research_subject.subject = subject_ref

    # create Encounter **
    encounter = None
    encounter_ref = None
    if 'tissue_source_site' in case.keys():
        encounter_tss_id = case['tissue_source_site']['Encounter.id']

        encounter = Encounter.construct()
        encounter.status = 'completed'
        encounter.id = encounter_tss_id
        encounter.subject = subject_ref
        encounter_ref = Reference(**{"reference": "/".join(["Encounter", encounter_tss_id])})

    observation = None
    observation_ref = None
    gdc_condition_annotation = None
    condition_codes_list = []
    if 'diagnoses' in case.keys() and isinstance(case['diagnoses'], list):
        case['diagnoses'] = {k: v for d in case['diagnoses'] for k, v in d.items()}

    if 'diagnoses' in case.keys() and 'Condition.id' in case['diagnoses'].keys():

        obs_identifier = case['diagnoses']['Condition.id']

        # create Observation **
        observation = Observation.construct()
        observation.status = 'final'
        observation.subject = subject_ref
        if encounter_ref:
            observation.encounter = encounter_ref
        observation.id = obs_identifier

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
        """
        if ('Condition.code_primary_diagnosis' in case['diagnoses'].keys() and
                "Paget disease and infiltrating duct carcinoma of breast" not in case['diagnoses']['Condition.code_primary_diagnosis'])\
                and "Infiltrating lobular mixed with other types of carcinoma" not in case['diagnoses']['Condition.code_primary_diagnosis']:
            gdc_condition_display = data_dict['clinical']['diagnosis']['properties']['primary_diagnosis']["enumDef"][
                case['diagnoses']['Condition.code_primary_diagnosis']]['termDef']['term']
            gdc_condition_code = data_dict['clinical']['diagnosis']['properties']['primary_diagnosis']["enumDef"][
                case['diagnoses']['Condition.code_primary_diagnosis']]['termDef']['term_id']
            gdc_condition_system = data_dict['clinical']['diagnosis']['properties']['primary_diagnosis']["enumDef"][
                case['diagnoses']['Condition.code_primary_diagnosis']]['termDef']['term_url']
            gdc_condition_annotation = {"system": gdc_condition_system, "display": gdc_condition_display,
                                        "code": gdc_condition_code}
            condition_codes_list.append(gdc_condition_annotation)
        """

        loinc_annotation = {'system': "https://loinc.org/", 'display': "replace-me", 'code': "000000"}
        condition_codes_list.append(loinc_annotation)

        observation_code.coding = condition_codes_list
        # observation_code.coding = [loinc_annotation]
        observation.code = observation_code
        observation_ref = Reference(**{"reference": "/".join(["Observation", observation.id])})

    condition = None  # normal tissue don't/shouldn't  have diagnoses or condition
    if 'diagnoses' in case.keys() and 'Condition.id' in case['diagnoses'].keys():

        # create Condition - for each diagnosis_id there is. relation: condition -- assessment --> observation
        condition = Condition.construct()
        condition.id = case['diagnoses']['Condition.id']
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

        if 'diagnoses' in case.keys() and 'Condition.onsetAge' in case['diagnoses'].keys():
            condition.onsetString = str(case['diagnoses']['Condition.onsetAge'])

        # condition.bodySite <-- primary_site snomed
        l_body_site = []
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
                    l_body_site.append({'system': "http://snomed.info/sct", 'display': p['value'], 'code': code})

        cc_body_site = CodeableConcept.construct()
        cc_body_site.coding = l_body_site
        condition.bodySite = [cc_body_site]

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

            condition.stage = staging_list
            observation.focus = [Reference(**{"reference": "/".join(["Condition", condition.id])})]

            # create medication administration and medication
            # bug in MedicationAdministration.status
            """
            if 'treatments' in case['diagnoses'].keys():
                treatments_med = []
                treatments_medadmin = []

                for treatment in case['diagnoses']['treatments']:
                    # https://build.fhir.org/ig/HL7/fhir-mCODE-ig/artifacts.html
                    med = Medication.construct()
                    med.id = treatment['MedicationAdministration.id']  # confirm
                    # med.code = treatment['Medication.code']
                    # med.ingredient = treatment['Medication.active_agents']
                    treatments_med.append(med)

                    admin_status = CodeableConcept.construct()
                    admin_status.coding = [{'system': "	http://hl7.org/fhir/CodeSystem/medication-admin-status",
                                            'display': 'Completed',
                                            'code': 'completed'}]

                    med_admin = MedicationAdministration.construct()
                    med_admin.status = admin_status  # if treatment['treatment_or_therapy'] == "yes" then completed, no "not-done"
                    med_admin.occurenceDateTime = datetime.fromisoformat("2019-04-28T13:44:38.933790-05:00")
                    med_admin.id = treatment['MedicationAdministration.id']

                    med_admin.medication = Reference(**{"reference": "/".join(["Medication", med.id])})
                    med_admin.subject = Reference(**{"reference": "/".join(["Patient", patient.id])})
                    med_admin.encounter = Reference(**{"reference": "/".join(["Encounter", encounter.id])})
                    treatments_medadmin.append(med_admin)
            """

        # add procedure
        procedure = None
        if encounter:
            procedure = Procedure.construct()
            procedure.status = "completed"
            procedure.subject = Reference(**{"reference": "/".join(["Patient", patient.id])})
            procedure.encounter = Reference(**{"reference": "/".join(["Encounter", encounter.id])})

    # create specimen
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

    def add_imaging_study(slide, patient, sample):
        # SM	Slide Microscopy	Slide Microscopy
        img = ImagingStudy.construct()
        img.status = "available"
        img.id = slide["ImagingStudy.id"]
        img.subject = Reference(**{"reference": "/".join(["Patient", patient.id])})

        img_series = ImagingStudySeries.construct()
        img_series.uid = sample.id

        modality = CodeableConcept.construct()
        modality.coding = [{"system": " http://dicom.nema.org/resources/ontology/DCM", "display": "Slide Microscopy", "code": "SM"}]
        img_series.modality = modality

        img_series.specimen = [Reference(**{"reference": "/".join(["Specimen", sample.id])})]
        img.series = [img_series]

        return img

    sample_list = None
    slide_list = []
    if "samples" in case.keys():
        samples = case["samples"]
        all_samples = []
        all_portions = []
        all_analytes = []
        all_aliquots = []
        for sample in samples:
            if 'Specimen.id.sample' in sample.keys():
                specimen = Specimen.construct()
                specimen.id = sample["Specimen.id.sample"]
                if "Specimen.type.sample" in sample.keys():
                    sample_type = CodeableConcept.construct()
                    sample_type.coding = [{
                        'system': "https://cadsr.cancer.gov",
                        'display': sample["Specimen.type.sample"],
                        'code': "3111302"}]
                    specimen.type = sample_type
                if "Specimen.processing.method" in sample.keys():
                    sample_processing = CodeableConcept.construct()
                    sp = SpecimenProcessing.construct()
                    sample_processing.coding = [{
                        'system': "https://cadsr.cancer.gov",
                        'display': sample["Specimen.processing.method"],
                        'code': "5432521"}]
                    sp.method = sample_processing
                    specimen.processing = [sp]

                specimen.subject = Reference(**{"reference": "/".join(["Patient", patient.id])})
                if specimen not in all_samples:
                    all_samples.append(specimen)

                add_specimen(dat=sample, name="analytes", id_key="Specimen.id.analyte", has_parent=True,
                             parent=sample, patient=patient, all_fhir_specimens=all_analytes)

                add_specimen(dat=sample, name="aliquots", id_key="Specimen.id.aliquot", has_parent=True,
                             parent=sample, patient=patient, all_fhir_specimens=all_aliquots)

                if "portions" in sample.keys():
                    for portion in sample['portions']:
                        if "Specimen.id.portion" in portion.keys():
                            portion_specimen = Specimen.construct()
                            portion_specimen.id = portion["Specimen.id.portion"]
                            portion_specimen.subject = Reference(**{"reference": "/".join(["Patient", patient.id])})
                            portion_specimen.parent = [Reference(**{"reference": "/".join(["Specimen", specimen.id])})]
                            if portion_specimen not in all_portions:
                                all_portions.append(portion_specimen)

                            if "slides" in portion.keys():
                                for slide in portion["slides"]:
                                    slide_list.append(add_imaging_study(slide=slide, patient=patient, sample=portion_specimen))

                            if "analytes" in portion.keys():
                                for analyte in portion["analytes"]:
                                    if "Specimen.id.analyte" in analyte.keys():
                                        analyte_specimen = Specimen.construct()
                                        analyte_specimen.id = analyte["Specimen.id.analyte"]
                                        analyte_specimen.subject = Reference(
                                            **{"reference": "/".join(["Patient", patient.id])})
                                        analyte_specimen.parent = [
                                            Reference(**{"reference": "/".join(["Specimen", portion_specimen.id])})]

                                        if "Specimen.type.analyte" in analyte.keys():
                                            analyte_type = CodeableConcept.construct()
                                            analyte_type.coding = [{
                                                'system': "https://cadsr.cancer.gov",
                                                'display': analyte["Specimen.type.analyte"],
                                                'code': "2513915"}]
                                            analyte_specimen.type = analyte_type

                                        if "slides" in analyte.keys():
                                            for slide in analyte["slides"]:
                                                slide_list.append(
                                                    add_imaging_study(slide=slide, patient=patient, sample=analyte_specimen))

                                        if analyte_specimen not in all_analytes:
                                            all_analytes.append(analyte_specimen)

                                        if "aliquots" in analyte.keys():
                                            for aliquot in analyte["aliquots"]:
                                                if "Specimen.id.aliquot" in aliquot.keys():
                                                    aliquot_specimen = Specimen.construct()
                                                    aliquot_specimen.id = aliquot["Specimen.id.aliquot"]
                                                    aliquot_specimen.subject = Reference(
                                                        **{"reference": "/".join(["Patient", patient.id])})
                                                    aliquot_specimen.parent = [Reference(
                                                        **{"reference": "/".join(["Specimen", analyte_specimen.id])})]
                                                    if aliquot_specimen not in all_aliquots:
                                                        all_aliquots.append(aliquot_specimen)

        sample_list = all_samples + all_portions + all_aliquots + all_analytes

    return {'patient': patient, 'encounter': encounter, 'observation': observation, 'condition': condition,
            'project_relations': project_relations, 'research_subject': research_subject, 'specimens': sample_list,
            'imaging_study': slide_list, "procedure": procedure}


def fhir_ndjson(entity, out_path):
    if isinstance(entity, list):
        with open(out_path, 'w', encoding='utf8') as file:
            file.write('\n'.join(map(lambda e: json.dumps(e, ensure_ascii=False), entity)))
    else:
        with open(out_path, 'w', encoding='utf8') as file:
            file.write(json.dumps(entity, ensure_ascii=False))


def case_gdc_to_fhir_ndjson(out_dir, cases_path):
    cases = utils.load_ndjson(cases_path)
    all_fhir_case_obj = []
    [all_fhir_case_obj.append(assign_fhir_for_case(c)) for c in cases]

    patients = [orjson.loads(fhir_case['patient'].json()) for fhir_case in all_fhir_case_obj]
    encounters = [orjson.loads(fhir_case['encounter'].json()) for fhir_case in all_fhir_case_obj if
                  'encounter' in fhir_case.keys() and fhir_case['encounter']]
    procedures = [orjson.loads(fhir_case['procedure'].json()) for fhir_case in all_fhir_case_obj]
    observations = [orjson.loads(fhir_case['observation'].json()) for fhir_case in all_fhir_case_obj if
                    'observation' in fhir_case.keys() and fhir_case['observation']]
    conditions = [orjson.loads(fhir_case['condition'].json()) for fhir_case in all_fhir_case_obj if
                  'condition' in fhir_case.keys() and fhir_case['condition']]
    research_subjects = [orjson.loads(fhir_case['research_subject'].json()) for fhir_case in all_fhir_case_obj]
    projects = [orjson.loads(fhir_case['project_relations']["ResearchStudy_obj"].json()) for fhir_case in
                all_fhir_case_obj]
    programs = list(unique_everseen(
        [orjson.loads(fhir_case['project_relations']["ResearchStudy.partOf_obj"].json()) for fhir_case in
         all_fhir_case_obj]))

    specimens = []
    for fhir_case in all_fhir_case_obj:
        if fhir_case["specimens"]:
            for specimen in fhir_case["specimens"]:
                specimens.append(orjson.loads(specimen.json()))

    imaging_study = []
    for fhir_case in all_fhir_case_obj:
        if fhir_case["imaging_study"]:
            for img in fhir_case["imaging_study"]:
                imaging_study.append(orjson.loads(img.json()))

    if "/" not in out_dir[-1]:
        out_dir = out_dir + "/"

    if specimens:
        fhir_ndjson(specimens, "".join([out_dir, "Specimen.ndjson"]))
    if patients:
        fhir_ndjson(patients, "".join([out_dir, "Patient.ndjson"]))
    if encounters:
        fhir_ndjson(encounters, "".join([out_dir, "Encounter.ndjson"]))
    if observations:
        fhir_ndjson(observations, "".join([out_dir, "Observation.ndjson"]))
    if conditions:
        fhir_ndjson(conditions, "".join([out_dir, "Condition.ndjson"]))
    if research_subjects:
        fhir_ndjson(research_subjects, "".join([out_dir, "ResearchSubject.ndjson"]))
    if projects:
        fhir_ndjson(projects + programs, "".join([out_dir, "ResearchStudy.ndjson"]))
    if imaging_study:
        fhir_ndjson(imaging_study, "".join([out_dir, "ImagingStudy.ndjson"]))
    if procedures:
        fhir_ndjson(procedures, "".join([out_dir, "Procedure.ndjson"]))

    med_admin = []
    fhir_ndjson(med_admin, "".join([out_dir, "MedicationAdministration.ndjson"]))

    med = []
    fhir_ndjson(med, "".join([out_dir, "Medication.ndjson"]))





