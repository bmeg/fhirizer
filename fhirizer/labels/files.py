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
            name='DocumentReference.category.data_type',
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
            name='wgs_coverage',
        ),
        destination=Destination(
            name='DocumentReference.category.wgs_coverage',
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
            name='cases.samples.portions.analytes.aliquots.aliquot_id',
        ),
        destination=Destination(
            name='Specimen.id',
        )
    ),

    Map(
        source=Source(
            name='data_format',
        ),
        destination=Destination(
            name='DocumentReference.content.profile',
        )
    ),

    Map(
        source=Source(
            name='file_name',
        ),
        destination=Destination(
            name='Attachment.title',
        )
    ),

    Map(
        source=Source(
            name='md5sum',
        ),
        destination=Destination(
            name='Attachment.hash',
        )
    ),

    Map(
        source=Source(
            name='file_size',
        ),
        destination=Destination(
            name='Attachment.size',
        )
    ),

    Map(
        source=Source(
            name='created_datetime',
        ),
        destination=Destination(
            name='DocumentReference.date',
        )
    ),

    Map(
        source=Source(
            name='analysis.metadata.read_groups.adapter_name',
        ),
        destination=Destination(
            name='Observation.DocumentReference.adapter_name',
        )
    ),

    Map(
        source=Source(
            name='analysis.metadata.read_groups.adapter_sequence',
        ),
        destination=Destination(
            name='Observation.DocumentReference.adapter_sequence',
        )
    ),

    Map(
        source=Source(
            name='analysis.metadata.read_groups.base_caller_name',
        ),
        destination=Destination(
            name='Observation.DocumentReference.base_caller_name',
        )
    ),

    Map(
        source=Source(
            name='analysis.metadata.read_groups.base_caller_version',
        ),
        destination=Destination(
            name='Observation.DocumentReference.base_caller_version',
        )
    ),

    Map(
        source=Source(
            name='analysis.metadata.read_groups.created_datetime',
        ),
        destination=Destination(
            name='Observation.DocumentReference.created_datetime',
        )
    ),

    Map(
        source=Source(
            name='analysis.metadata.read_groups.experiment_name',
        ),
        destination=Destination(
            name='Observation.DocumentReference.experiment_name',
        )
    ),

    Map(
        source=Source(
            name='analysis.metadata.read_groups.flow_cell_barcode',
        ),
        destination=Destination(
            name='Observation.DocumentReference.flow_cell_barcode',
        )
    ),

    Map(
        source=Source(
            name='analysis.metadata.read_groups.includes_spike_ins',
        ),
        destination=Destination(
            name='Observation.DocumentReference.includes_spike_ins',
        )
    ),

    Map(
        source=Source(
            name='analysis.metadata.read_groups.instrument_model',
        ),
        destination=Destination(
            name='Observation.DocumentReference.instrument_model',
        )
    ),

    Map(
        source=Source(
            name='analysis.metadata.read_groups.is_paired_end',
        ),
        destination=Destination(
            name='Observation.DocumentReference.is_paired_end',
        )
    ),

    Map(
        source=Source(
            name='analysis.metadata.read_groups.library_name',
        ),
        destination=Destination(
            name='Observation.DocumentReference.library_name',
        )
    ),

    Map(
        source=Source(
            name='analysis.metadata.read_groups.library_preparation_kit_catalog_number',
        ),
        destination=Destination(
            name='Observation.DocumentReference.library_preparation_kit_catalog_number',
        )
    ),

    Map(
        source=Source(
            name='analysis.metadata.read_groups.library_preparation_kit_name',
        ),
        destination=Destination(
            name='Observation.DocumentReference.library_preparation_kit_name',
        )
    ),

    Map(
        source=Source(
            name='analysis.metadata.read_groups.library_preparation_kit_vendor',
        ),
        destination=Destination(
            name='Observation.DocumentReference.library_preparation_kit_vendor',
        )
    ),

    Map(
        source=Source(
            name='analysis.metadata.read_groups.library_preparation_kit_version',
        ),
        destination=Destination(
            name='Observation.DocumentReference.library_preparation_kit_version',
        )
    ),

    Map(
        source=Source(
            name='analysis.metadata.read_groups.library_selection',
        ),
        destination=Destination(
            name='Observation.DocumentReference.library_selection',
        )
    ),

    Map(
        source=Source(
            name='analysis.metadata.read_groups.library_strand',
        ),
        destination=Destination(
            name='Observation.DocumentReference.library_strand',
        )
    ),

    Map(
        source=Source(
            name='analysis.metadata.read_groups.library_strategy',
        ),
        destination=Destination(
            name='Observation.DocumentReference.library_strategy',
        )
    ),

    Map(
        source=Source(
            name='analysis.metadata.read_groups.platform',
        ),
        destination=Destination(
            name='Observation.DocumentReference.platform',
        )
    ),

    Map(
        source=Source(
            name='analysis.metadata.read_groups.read_group_id',
        ),
        destination=Destination(
            name='Observation.DocumentReference.read_group_id',
        )
    ),

    Map(
        source=Source(
            name='analysis.metadata.read_groups.read_group_name',
        ),
        destination=Destination(
            name='Observation.DocumentReference.read_group_name',
        )
    ),

    Map(
        source=Source(
            name='analysis.metadata.read_groups.read_length',
        ),
        destination=Destination(
            name='Observation.DocumentReference.read_length',
        )
    ),

    Map(
        source=Source(
            name='analysis.metadata.read_groups.RIN',
        ),
        destination=Destination(
            name='Observation.DocumentReference.RIN',
        )
    ),

    Map(
        source=Source(
            name='analysis.metadata.read_groups.sequencing_center',
        ),
        destination=Destination(
            name='Observation.DocumentReference.sequencing_center',
        )
    ),

    Map(
        source=Source(
            name='analysis.metadata.read_groups.sequencing_date',
        ),
        destination=Destination(
            name='Observation.DocumentReference.sequencing_date',
        )
    ),

    Map(
        source=Source(
            name='analysis.metadata.read_groups.size_selection_range',
        ),
        destination=Destination(
            name='Observation.DocumentReference.size_selection_range',
        )
    ),

    Map(
        source=Source(
            name='analysis.metadata.read_groups.spike_ins_concentration',
        ),
        destination=Destination(
            name='Observation.DocumentReference.spike_ins_concentration',
        )
    ),

    Map(
        source=Source(
            name='analysis.metadata.read_groups.spike_ins_fasta',
        ),
        destination=Destination(
            name='Observation.DocumentReference.spike_ins_fasta',
        )
    ),

    Map(
        source=Source(
            name='analysis.metadata.read_groups.state',
        ),
        destination=Destination(
            name='Observation.DocumentReference.state',
        )
    ),

    Map(
        source=Source(
            name='analysis.metadata.read_groups.submitter_id',
        ),
        destination=Destination(
            name='Observation.DocumentReference.submitter_id',
        )
    ),

    Map(
        source=Source(
            name='analysis.metadata.read_groups.target_capture_kit_catalog_number',
        ),
        destination=Destination(
            name='Observation.DocumentReference.target_capture_kit_catalog_number',
        )
    ),

    Map(
        source=Source(
            name='analysis.metadata.read_groups.target_capture_kit_name',
        ),
        destination=Destination(
            name='Observation.DocumentReference.target_capture_kit_name',
        )
    ),

    Map(
        source=Source(
            name='analysis.metadata.read_groups.target_capture_kit_target_region',
        ),
        destination=Destination(
            name='Observation.DocumentReference.target_capture_kit_target_region',
        )
    ),

    Map(
        source=Source(
            name='analysis.metadata.read_groups.target_capture_kit_vendor',
        ),
        destination=Destination(
            name='Observation.DocumentReference.target_capture_kit_vendor',
        )
    ),

    Map(
        source=Source(
            name='analysis.metadata.read_groups.target_capture_kit_version',
        ),
        destination=Destination(
            name='Observation.DocumentReference.target_capture_kit_version',
        )
    ),

    Map(
        source=Source(
            name='analysis.metadata.read_groups.to_trim_adapter_sequence',
        ),
        destination=Destination(
            name='Observation.DocumentReference.to_trim_adapter_sequence',
        )
    ),

    Map(
        source=Source(
            name='analysis.metadata.read_groups.updated_datetime',
        ),
        destination=Destination(
            name='Observation.DocumentReference.updated_datetime',
        )
    ),

    Map(
        source=Source(
            name='analysis.metadata.read_groups.days_to_sequencing',
        ),
        destination=Destination(
            name='Observation.DocumentReference.days_to_sequencing',
        )
    ),

    Map(
        source=Source(
            name='analysis.metadata.read_groups.single_cell_library',
        ),
        destination=Destination(
            name='Observation.DocumentReference.single_cell_library',
        )
    ),

    Map(
        source=Source(
            name='analysis.metadata.read_groups.multiplex_barcode',
        ),
        destination=Destination(
            name='Observation.DocumentReference.multiplex_barcode',
        )
    ),

    Map(
        source=Source(
            name='analysis.metadata.read_groups.target_capture_kit',
        ),
        destination=Destination(
            name='Observation.DocumentReference.target_capture_kit',
        )
    ),

    Map(
        source=Source(
            name='analysis.metadata.read_groups.lane_number',
        ),
        destination=Destination(
            name='Observation.DocumentReference.lane_number',
        )
    ),

    Map(
        source=Source(
            name='analysis.metadata.read_groups.fragment_standard_deviation_length',
        ),
        destination=Destination(
            name='Observation.DocumentReference.fragment_standard_deviation_length',
        )
    ),

    Map(
        source=Source(
            name='analysis.metadata.read_groups.fragment_minimum_length',
        ),
        destination=Destination(
            name='Observation.DocumentReference.fragment_minimum_length',
        )
    ),

    Map(
        source=Source(
            name='analysis.metadata.read_groups.number_expect_cells',
        ),
        destination=Destination(
            name='Observation.DocumentReference.number_expect_cells',
        )
    ),

    Map(
        source=Source(
            name='analysis.metadata.read_groups.fragment_mean_length',
        ),
        destination=Destination(
            name='Observation.DocumentReference.fragment_mean_length',
        )
    ),

    Map(
        source=Source(
            name='analysis.metadata.read_groups.fragment_maximum_length',
        ),
        destination=Destination(
            name='Observation.DocumentReference.fragment_maximum_length',
        )
    )
]

# out_path = os.path.join(package_dir, 'mapping', 'case.json')
out_path = '../../mapping/file.json'
valid_file_maps = [Map.model_validate(f) for f in file_maps]
[file_schema.mappings.append(i) for i in valid_file_maps]
utils.validate_and_write(file_schema, out_path=out_path, update=True, generate=False)

# dict_keys(['id', 'data_format', 'cases', 'access', 'file_name', 'wgs_coverage', 'submitter_id', 'data_category', 'acl', 'type', 'platform', 'file_size', 'created_datetime', 'index_files', 'md5sum', 'updated_datetime', 'file_id', 'data_type', 'state', 'experimental_strategy', 'version', 'data_release'])
