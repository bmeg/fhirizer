from fhirizer import utils, mapping, entity2fhir, icgc2fhir, htan2fhir
import click
from pathlib import Path


class NotRequiredIf(click.Option):
    def __init__(self, *args, **kwargs):
        self.not_required_if = kwargs.pop('not_required_if')
        assert self.not_required_if, "'not_required_if' parameter required"
        if isinstance(self.not_required_if, str):
            self.not_required_if = [self.not_required_if]
        kwargs['help'] = (kwargs.get('help', '') +
                          ' NOTE: This argument is mutually exclusive with %s' %
                          ', '.join(self.not_required_if)
                          ).strip()
        super(NotRequiredIf, self).__init__(*args, **kwargs)

    def handle_parse_result(self, ctx, opts, args):
        we_are_present = self.name in opts
        others_present = [opt for opt in self.not_required_if if opt in opts]

        if others_present:
            if we_are_present:
                raise click.UsageError(
                    "Illegal usage: `%s` is mutually exclusive with `%s`" % (
                        self.name, ', '.join(others_present)))
            else:
                self.prompt = None

        return super(NotRequiredIf, self).handle_parse_result(
            ctx, opts, args)



@click.group()
def cli():
    """GDC, Cellosaurus, ICGC to FHIR schema Key and Content Mapping"""
    pass


@cli.command('fields')
@click.option('--input_path', required=True,
              default='./resources/gdc_resources/fields/case_fields.json',
              show_default=True,
              help='Path to available GDC field json files in this repo')
def field_keys(input_path):
    assert Path(input_path).is_file(), f"Path {input_path} is not a valid file path."

    case_fields = utils._read_json(input_path)
    print("reading from input_path: ", input_path)
    print("case fields: ", case_fields)


@cli.command('project_init')
@click.option('--field_path', required=True,
              default=utils.FIELDS_PATH,
              show_default=True,
              help='Path to GDC fields')
@click.option('--out_path', required=True,
              default='./mapping/project_test.json',
              show_default=True,
              help='Path to GDC project json schema')
def project_init(field_path, out_path):
    assert Path(field_path).is_file(), f"Path {field_path} is not a valid file path."

    mapping.initialize_project(field_path, out_path)


@cli.command('case_init')
@click.option('--field_path', required=True,
              default=utils.FIELDS_PATH,
              show_default=True,
              help='Path to GDC fields')
@click.option('--out_path', required=True,
              default='./mapping/case_test.json',
              show_default=True,
              help='Path to GDC case json schema')
def case_init(field_path, out_path):
    assert Path(field_path).is_file(), f"Path {field_path} is not a valid file path."

    mapping.initialize_case(field_path, out_path)


@cli.command('file_init')
@click.option('--field_path', required=True,
              default=utils.FIELDS_PATH,
              show_default=True,
              help='Path to GDC fields')
@click.option('--out_path', required=True,
              default='./mapping/file_test.json',
              show_default=True,
              help='Path to GDC file json schema')
def file_init(field_path, out_path):
    assert Path(field_path).is_file(), f"Path {field_path} is not a valid file path."

    mapping.initialize_file(field_path, out_path)


@cli.command('resource')
@click.option('--name', required=True,
              default='cellosaurus',
              show_default=True,
              help='Name of resource')
@click.option('--path', required=True,
              show_default=True,
              help='Path to cell-lines ndjson file')
@click.option('--out_dir', required=False,
              show_default=True,
              help='Directory path to save generated resources')
def resource(name, path, out_dir):
    assert Path(path).is_file(), f"Path {path} is not a valid file path."
    assert Path(out_dir).is_dir(), f"Path {out_dir} is not a valid directory path."

    if name in 'cellosaurus':
        entity2fhir.cellosaurus_resource(path=path, out_dir=out_dir)


@cli.command('convert')
@click.option('--name', required=True,
              default='project',
              show_default=True,
              help='project, case, or file GDC entity name to map')
@click.option('--in_path', required=True,
              show_default=True,
              help='Path to GDC data to be mapped')
@click.option('--out_path', required=False,
              show_default=True,
              help='Path to save mapped result')
@click.option('--verbose', is_flag=True, required=False,
              default=False,
              show_default=True)
def convert(name, in_path, out_path, verbose):
    name_list = ['project', 'case', 'file', 'cellosaurus', 'icgc']
    assert name in ['project', 'case', 'file', 'cellosaurus', 'icgc'], f'--name is not in {name_list}.'
    assert Path(in_path).is_file(), f"Path {in_path} is not a valid file path."

    mapping.convert_maps(name=name, in_path=in_path, out_path=out_path, verbose=verbose)


@cli.command('generate')
@click.option('--name', required=True,
              default='project',
              show_default=True,
              help='entity name to map - project, case, file of GDC or cellosaurus')
@click.option('--out_dir', cls=NotRequiredIf,
              not_required_if=['htan', 'icgc'],
              help='Directory path to save mapped FHIR ndjson files.')
@click.option('--entity_path', cls=NotRequiredIf,
              not_required_if=['htan', 'icgc'],
              help='Path to GDC entity with mapped FHIR like keys (converted file via convert) or Cellosaurus ndjson '
                   'file of human cell-lines of interest.')
@click.option('--atlas', required=False,
              default=['OHSU'],
              show_default=True,
              help='List of atlas project(s) name to FHIRize. ex. ["OHSU", "DFCI", "WUSTL", "BU", "CHOP", "Duke", "HMS", "HTAPP", "MSK", "Stanford"]')
@click.option('--icgc', help='Name of the ICGC project to FHIRize.')
@click.option('--has_files', is_flag=True, help='Boolean indicating file metatda via new argo site is available @ '
                                                'ICGC/{project}/data directory to FHIRize.')
@click.option('--convert', is_flag=True, help='Boolean indicating to write converted keys to directory')
@click.option('--verbose', is_flag=True)
def generate(name, out_dir, entity_path, icgc, has_files, atlas, convert, verbose):
    name_list = ['project', 'case', 'file', 'cellosaurus', 'icgc', 'htan']
    assert name in name_list, f'--name is not in {name_list}.'
    if name != 'htan':
        assert Path(out_dir).is_dir(), f"Path {out_dir} is not a valid directory path."
        assert Path(entity_path).is_file(), f"Path {entity_path} is not a valid file path."
    else:
        assert Path("./projects/HTAN").is_dir()

    if name in 'project':
        entity2fhir.project_gdc_to_fhir_ndjson(out_dir=out_dir, projects_path=entity_path, convert=convert, verbose=verbose)
    if name in 'case':
        entity2fhir.case_gdc_to_fhir_ndjson(out_dir=out_dir, name=name, cases_path=entity_path, convert=convert, verbose=verbose)
    if name in 'file':
        entity2fhir.file_gdc_to_fhir_ndjson(out_dir=out_dir, name=name, files_path=entity_path, convert=convert, verbose=verbose)
    if name in 'cellosaurus':
        entity2fhir.cellosaurus2fhir(out_dir=out_dir, path=entity_path)
    if name in 'icgc' and icgc:
        icgc2fhir.icgc2fhir(project_name=icgc, has_files=has_files)
    if name in 'htan':
        if isinstance(atlas, str):
            if "," in atlas:
                atlas = atlas.split(",")
                atlas = [a.strip() for a in atlas]
            else:
                atlas = [atlas]

        htan2fhir.htan2fhir(entity_atlas_name=atlas, verbose=verbose)


if __name__ == '__main__':
    cli()
