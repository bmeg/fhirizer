from __future__ import annotations
from typing import List, Optional, Union, Dict
from pydantic import BaseModel, Field


class Reference(BaseModel):
    reference_type: str = Field(None, description='Reference type of data resource.')
    parent: Optional[str] = Field(None, description='Parent identifier.')


class Source(BaseModel):
    # map types via this standard: https://docs.pydantic.dev/latest/concepts/types/
    name: str = Field(..., description='GDC available field name hierarchy dot notation.')
    description: Optional[str] = Field(None, description='Description of the last GDC element for mapping.')
    description_url: Optional[str] = Field(None, description='Description source url.')
    category: Optional[str] = Field(None, description='GDC data dictionary category: case | clinical | biospecimen | '
                                                      'files | anntations | analysis | notation | index | data')
    type: Optional[str] = Field(None, description='GDC type of the last element.')
    format: Optional[str] = Field(None, description='GDC format of the type of the last element ex. date-time.')
    enums: Optional[List[dict]] = Field(None, description='Enum string values of the last GDC element.')
    content_annotation: Optional[Union[List[dict], str]] = Field(None, description='Content annotations with definitions.')
    reference: Optional[List[Reference]] = Field(None, description='Reference to parent type and id.')


class Destination(BaseModel):
    name: str = Field(..., description='FHIR resources matching the source hierarchy.')
    description: Optional[str] = Field(None, description='Description of the final FHIR mapping element.')
    description_url: Optional[str] = Field(None, description='Description source url.')
    module: Optional[str] = Field(None, description='Name of the parent module of final mapping element.')
    title: Optional[str] = Field(None, description='Field title of the FHIR mapping element.')
    type: Optional[str] = Field(None, description='type of the final FHIR mapping element.')
    format: Optional[str] = Field(None, description='Format required for mapping ex. a pydantic list[str]')
    reference: Optional[List[Reference]] = Field(None, description='Reference to parent type and id.')


class Map(BaseModel):
    source: Source
    destination: Destination

    # store maps internally with source name as key to access faster
    _map_dict: Dict[str, Map] = {}

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._map_dict[self.source.name] = self

    @staticmethod
    def update_fields(model: BaseModel, values: Dict):
        for field, value in values.items():
            setattr(model, field, value)

    @staticmethod
    def update_values(source_name: str, source_values: Optional[Dict] = None,
                      destination_values: Optional[Dict] = None):
        map_instance = Map._map_dict.get(source_name)
        if map_instance:
            if source_values:
                Map.update_fields(map_instance.source, source_values)
            if destination_values:
                Map.update_fields(map_instance.destination, destination_values)

    @classmethod
    def find_source(cls, source_name: str) -> Optional[Source]:
        map_instance = cls._map_dict.get(source_name)
        if map_instance:
            return map_instance.source


class Version(BaseModel):
    source_version: Optional[str] = Field(None, description='GDC data dictionary version.')
    data_release: Optional[str] = Field(None, description='GDC data dictionary release.')
    commit: Optional[str] = Field(None, description='GDC data dictionary commit.')
    status: Optional[str] = Field(None, description='GDC data dictionary status.')
    tag: Optional[str] = Field(None, description='GDC data dictionary tag.')
    destination_version: Optional[str] = Field(None, description='FHIR published data release version.')


class Metadata(BaseModel):
    title: str = Field(..., description='GDC object name for this schema.')
    category: str = Field(None, description='GDC object category ex. case | file | project.')
    type: str = Field(..., description='GDC object type.')
    downloadable: bool = Field(None, description='Downloadable content available.')
    description: str = Field(..., description='GDC description of this schema object.')
    versions: List[Version] = Field(..., description='Source and destination data versions being mapped.')
    resource_links: Optional[List[str]] = Field(None, description='Resource links to GDC and FHIR overviews.')


class Schema(BaseModel):
    version: str = Field(..., description='Semantic versioning of the mappings schema.')
    metadata: Metadata = Field(..., description='Metadata on GDC object and FHIR resources.')
    obj_mapping: Map = Field(..., description="The GDC object being mapped.")
    obj_keys: List[str] = Field(..., description='List of GDC available fields hierarchy to be mapped.')
    mappings: List[Map] = Field(..., description='List of Map(s) describing the source -> destination Maps.')
    source_key_required: Optional[List[str]] = Field(None,
                                                     description='Required key elements defined by GDC in this schema.')
    destination_key_required: Optional[List[str]] = Field(None,
                                                          description='Required key elements defined by FHIR in this schema.')
    unique_keys: Optional[List[List[str]]] = Field(None,
                                                   description='Unique keys that identify this GDC based schema model.')
    source_key_aliases: Optional[Dict[str, Union[str, List[str]]]] = Field(None, description='GDC key aliases in this schema.')
    destination_key_aliases: Optional[Dict[str, Union[str, List[str]]]] = Field(None,
                                                                                description='FHIR key aliases in this schema.')

    # TODO: replace Config
    # https://docs.pydantic.dev/latest/concepts/json_schema/
    class Config:
        json_schema_extra = {
            '$schema': 'http://json-schema.org/draft-07/schema#'
        }

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    @property
    def source_map_dict(self):
        return {mapping.source.name: mapping for mapping in self.mappings}

    @property
    def destination_map_dict(self):
        return {mapping.destination.name: mapping for mapping in self.mappings}

    def find_map_by_source(self, source_name: str) -> Optional[Map]:
        return self.source_map_dict.get(source_name)

    def find_map_by_destination(self, destination_name: str) -> Optional[Map]:
        return self.destination_map_dict.get(destination_name)

    def has_map_for_source(self, source_key: str) -> bool:
        return any(mapping.source.name == source_key for mapping in self.mappings)

    def has_map_for_destination(self, destination_key: str) -> bool:
        return any(mapping.destination.name == destination_key for mapping in self.mappings)
