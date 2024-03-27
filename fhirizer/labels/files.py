import os
from fhirizer import utils
from fhirizer.schema import Map, Source, Destination, Reference

package_dir = utils.package_dir
file_schema = utils.load_schema_from_json(path=os.path.join(package_dir, 'mapping', 'file.json'))
keys_to_label_fields = [key for key in file_schema.obj_keys if
                        key not in [x.source.name for x in file_schema.mappings]]
data_dict = utils.load_data_dictionary(
    path=os.path.join(package_dir, 'resources', 'gdc_resources', 'data_dictionary', ''))

file_maps = [
    Map(
        source=Source(
            name='id',
        ),
        destination=Destination(
            name='DocumentReference.id',
        )
    ),

    Map(
        source=Source(
            name='data_category',
        ),
        destination=Destination(
            name='DocumentReference.category.data_category',
        )
    ),

    Map(
        source=Source(
            name='platform',
        ),
        destination=Destination(
            name='DocumentReference.category.platform',
        )
    ),

    Map(
        source=Source(
            name='data_type',
        ),
        destination=Destination(
            name='DocumentReference.type',
        )
    ),

    Map(
        source=Source(
            name='experimental_strategy',
        ),
        destination=Destination(
            name='DocumentReference.category.experimental_strategy',
        )
    ),

    Map(
        source=Source(
            name='version',
        ),
        destination=Destination(
            name='DocumentReference.version',
        )
    ),

    Map(
        source=Source(
            name='file_name',
        ),
        destination=Destination(
            name='DocumentReference.Identifier.file_name',
        )
    ),

    Map(
        source=Source(
            name='submitter_id',
        ),
        destination=Destination(
            name='DocumentReference.Identifier',
        )
    ),

    Map(
        source=Source(
            name='cases.case_id',
        ),
        destination=Destination(
            name='Patient.id',
        )
    ),

    Map(
        source=Source(
            name='data_format',
        ),
        destination=Destination(
            name='DocumentReference.content.profile',
        )
    )
]

# out_path = os.path.join(package_dir, 'mapping', 'case.json')
out_path = '../../mapping/file.json'
valid_file_maps = [Map.model_validate(f) for f in file_maps]
[file_schema.mappings.append(i) for i in valid_file_maps]
utils.validate_and_write(file_schema, out_path=out_path, update=True, generate=False)

# dict_keys(['id', 'data_format', 'cases', 'access', 'file_name', 'wgs_coverage', 'submitter_id', 'data_category', 'acl', 'type', 'platform', 'file_size', 'created_datetime', 'index_files', 'md5sum', 'updated_datetime', 'file_id', 'data_type', 'state', 'experimental_strategy', 'version', 'data_release'])
