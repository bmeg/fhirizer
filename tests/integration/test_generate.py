import pytest
from fhirizer import entity2fhir, utils


@pytest.fixture
def research_study():
    return utils.load_ndjson("./tests/fixtures/case/META/ResearchStudy.ndjson")


@pytest.fixture
def research_subject():
    return utils.load_ndjson("./tests/fixtures/case/META/ResearchSubject.ndjson")


@pytest.fixture
def patient():
    return utils.load_ndjson("./tests/fixtures/case/META/Patient.ndjson")


@pytest.fixture
def condition():
    return utils.load_ndjson("./tests/fixtures/case/META/Condition.ndjson")


@pytest.fixture
def observation():
    return utils.load_ndjson("./tests/fixtures/case/META/Observation.ndjson")


@pytest.fixture
def specimen():
    return utils.load_ndjson("./tests/fixtures/case/META/Specimen.ndjson")


@pytest.fixture
def body_structure():
    return utils.load_ndjson("./tests/fixtures/case/META/BodyStructure.ndjson")


@pytest.fixture
def medication():
    return utils.load_ndjson("./tests/fixtures/case/META/Medication.ndjson")


@pytest.fixture
def medication_administration():
    return utils.load_ndjson("./tests/fixtures/case/META/MedicationAdministration.ndjson")


def test_case_gdc_to_fhir(patient, condition, research_study, research_subject, observation, specimen,
                          medication, medication_administration, body_structure, name='case', out_dir='./tests/fixtures/case/META',
                          cases_path="./tests/fixtures/case/cases.ndjson", spinner=None):
    entity2fhir.case_gdc_to_fhir_ndjson(out_dir=out_dir, name=name, cases_path=cases_path, convert=False, verbose=False, spinner=spinner)
    assert patient == utils.load_ndjson("./tests/fixtures/case/META/Patient.ndjson")
    assert condition == utils.load_ndjson("./tests/fixtures/case/META/Condition.ndjson")
    assert research_study == utils.load_ndjson("./tests/fixtures/case/META/ResearchStudy.ndjson")
    assert research_subject == utils.load_ndjson("./tests/fixtures/case/META/ResearchSubject.ndjson")
    assert observation == utils.load_ndjson("./tests/fixtures/case/META/Observation.ndjson")
    assert specimen == utils.load_ndjson("./tests/fixtures/case/META/Specimen.ndjson")
    assert body_structure == utils.load_ndjson("./tests/fixtures/case/META/BodyStructure.ndjson")
    assert medication == utils.load_ndjson("./tests/fixtures/case/META/Medication.ndjson")
    assert medication_administration == utils.load_ndjson("./tests/fixtures/case/META/MedicationAdministration.ndjson")

