import subprocess
import importlib.resources
from pathlib import Path


def test_group_member():
    group_path = str(Path(importlib.resources.files(
        'fhirizer').parent / 'tests' / 'fixtures' / 'file' / 'META' / 'Group.ndjson'))
    command = f"cat {group_path} | grep -v '\"member\":' | wc -l"

    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True, check=True)
        line_count = int(result.stdout.strip())
        assert line_count == 0, f"Missing Group member reference in: {line_count} Groups."
    except subprocess.CalledProcessError as e:
        print(f"Subprocess error: {e}")
    except Exception as e:
        print(f"An error occurred: {e}")


def test_document_reference_subject():
    document_reference_path = str(Path(importlib.resources.files(
        'fhirizer').parent / 'tests' / 'fixtures' / 'file' / 'META' / 'DocumentReference.ndjson'))
    command = f"cat {document_reference_path} | grep -v '\"subject\":' | wc -l"

    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True, check=True)
        line_count = int(result.stdout.strip())
        assert line_count == 0, f"Missing DocumentReference subject reference in: {line_count} DocumentReferences."
    except subprocess.CalledProcessError as e:
        print(f"Subprocess error: {e}")
    except Exception as e:
        print(f"An error occurred: {e}")
