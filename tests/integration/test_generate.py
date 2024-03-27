import pytest
from gdc2fhir import entity2fhir, utils


@pytest.fixture
def research_study():
    return utils.load_ndjson("./tests/fixtures/project/ResearchStudy.ndjson")


@pytest.fixture
def patient():
    return utils.load_ndjson("./tests/fixtures/case/Patient.ndjson")


@pytest.fixture
def condition():
    return utils.load_ndjson("./tests/fixtures/case/Condition.ndjson")


def test_project_gdc_to_fhir(research_study, out_dir='./tests/fixtures/project',
                             projects_path="./tests/fixtures/project/project_key.ndjson"):
    entity2fhir.project_gdc_to_fhir_ndjson(out_dir, projects_path)
    assert research_study == utils.load_ndjson("./tests/fixtures/project/ResearchStudy.ndjson")


def test_case_gdc_to_fhir(patient, condition, out_dir='./tests/fixtures/case',
                          cases_path="./tests/fixtures/case/case_key.ndjson"):
    entity2fhir.case_gdc_to_fhir_ndjson(out_dir, cases_path)
    assert patient == utils.load_ndjson("./tests/fixtures/case/Patient.ndjson")
    assert condition == utils.load_ndjson("./tests/fixtures/case/Condition.ndjson")


