import json
import orjson
from fhirizer import utils

out_dir = "projects/All_HTAN/META"
path = "projects/All_HTAN/META/MedicationAdministration.ndjson"
med_admin_data = utils.read_ndjson(path)
resource_type = "MedicationAdministration"

for item in med_admin_data:
    medication = item.get('medication')
    if medication and isinstance(medication, dict) and 'reference' in medication:
        del medication['reference']

utils.fhir_ndjson(med_admin_data, "".join([out_dir, "/", resource_type, "_2",".ndjson"]))
