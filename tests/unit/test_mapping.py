import pytest
from pydantic import ValidationError
from gdc2fhir.schema import Schema, Source, Destination, Map, Metadata, Version


@pytest.fixture
def example_schema():
    # schema for testing
    source_obj = Source(
        name="case",
        description="The collection of all data related to a specific subject in the context of a specific project.",
        type="object"
    )

    destination_obj = Destination(
        name="Patient",
        description="This is a patient",
        module="Administration",
        title="Patient",
        type="object"
    )

    map_obj = Map(source=source_obj, destination=destination_obj)

    source_a = Source(
        name="case_id",
        description="UUID",
        type="object"
    )

    destination_a = Destination(
        name="Patient.identifier",
        description="some description",
        module="Administration",
        title="Patient.identifier",
        type="object"
    )

    map1 = Map(source=source_a, destination=destination_a)

    source_b = Source(
        name="sample_id",
        description="A 128-bit identifier.",
        type="object"
    )

    destination_b = Destination(
        name="Specimen.identifier",
        description="Id for specimen.",
        module="AnotherModule",
        title="AnotherTitle",
        type="object"
    )

    map2 = Map(source=source_b, destination=destination_b)

    gdc_version = Version(
        source_version="1",
        data_release="Data Release 39.0 - December 04, 2023",
        commit="023da73eee3c17608db1a9903c82852428327b88",
        status="OK",
        tag="5.0.6",
    )
    fhir_version = Version(
        destination_version="5.0.0"
    )

    metadata = Metadata(
        title="Case",
        category="case",
        type="obj",
        description="",
        downloadable=False,
        versions=[gdc_version, fhir_version]
    )

    return Schema(
        version="1.0.0",
        metadata=metadata,
        obj_mapping=map_obj,
        obj_keys=["case_id", "sample_id"],
        mappings=[map1, map2]
    )


def test_find_source(example_schema):
    found_source = example_schema.find_map_by_source(source_name="case_id").source
    assert found_source is not None
    assert found_source.name == "case_id"


def test_has_map_for_source(example_schema):
    assert example_schema.has_map_for_source("case_id")
    assert not example_schema.has_map_for_source("NonExistentDestination")


def test_find_destination(example_schema):
    found_map = example_schema.find_map_by_destination(destination_name="Patient.identifier")
    assert found_map is not None
    assert found_map.destination.name == "Patient.identifier"


def test_has_map_for_destination(example_schema):
    assert example_schema.has_map_for_destination("Patient.identifier")
    assert not example_schema.has_map_for_destination("NonExistentDestination")


def test_find_and_update_values(example_schema):
    source_name = "case_id"
    source_values = {"description": "Unique key of entity"}

    # Find map by source name
    map_instance = example_schema.find_map_by_source(source_name=source_name)
    assert map_instance is not None

    # Update its values
    # map_instance.update_values(source_name=source_name, source_values=source_values)

    # Check updates
    # updated_source = map_instance.find_source(source_name=source_name)
    # assert updated_source is not None
    # assert updated_source.description == "Unique key of entity"


@pytest.mark.xfail
def test_invalid_map(example_schema):
    # can't have map without name - expected to fail
    with pytest.raises(ValidationError, match="can't have map without name - none not allowed"):
        Map.model_validate(Map(
            source=Source(name=None, description="invalid Source", type="object"),
            destination=example_schema.obj_mapping.destination
        ))


@pytest.mark.xfail
def test_invalid_schema():
    # can't have schema without obj_kye - expected to fail
    with pytest.raises(ValidationError, match="obj_key required"):
        Schema.model_validate(Schema(metadata={'title': 'Case', 'downloadable': False},
                                     obj_mapping=Map(source=Source(name="case_id", description='UUID', type='object'))
                                     )
                              )
