from gdc2fhir import utils, mapping
import click


@click.group()
def cli():
    """GDC to FHIR Key and Content Mapping"""
    pass


@cli.command('fields')
@click.option('--input_path', required=True,
              default='./resources/gdc_resources/fields/case_fields.json',
              show_default=True,
              help='Path to available GDC field json files in this repo')
def field_keys(input_path):
    case_fields = utils.read_json(input_path)
    print("reading from input_path: ", input_path)
    print("case fields: ", case_fields)


@cli.command('project_init')
@click.option('--field_path', required=True,
              default='./resources/gdc_resources/fields/',
              show_default=True,
              help='Path to GDC fields')
@click.option('--out_path', required=True,
              default='./mapping/project_test.json',
              show_default=True,
              help='Path to GDC project json schema')
def project_init(field_path, out_path):
    mapping.initialize_project(field_path, out_path)


@cli.command('case_init')
@click.option('--field_path', required=True,
              default='./resources/gdc_resources/fields/',
              show_default=True,
              help='Path to GDC fields')
@click.option('--out_path', required=True,
              default='./mapping/case_test.json',
              show_default=True,
              help='Path to GDC case json schema')
def case_init(field_path, out_path):
    mapping.initialize_case(field_path, out_path)


@cli.command('file_init')
@click.option('--field_path', required=True,
              default='./resources/gdc_resources/fields/',
              show_default=True,
              help='Path to GDC fields')
@click.option('--out_path', required=True,
              default='./mapping/file_test.json',
              show_default=True,
              help='Path to GDC file json schema')
def file_init(field_path, out_path):
    mapping.initialize_file(field_path, out_path)


@cli.command('convert')
@click.option('--name', required=True,
              default='project',
              show_default=True,
              help='Name of GDC entity to map')
@click.option('--in_path', required=True,
              show_default=True,
              help='Path to GDC data to be mapped')
@click.option('--out_path', required=False,
              show_default=True,
              help='Path to save mapped result')
@click.option('--verbose', required=False,
              default=True,
              show_default=True,
              help='Print the count metric statements')
def convert(name, in_path, out_path, verbose):
    mapping.convert_maps(name=name, in_path=in_path, out_path=out_path, verbose=verbose)


if __name__ == '__main__':
    cli()
