#!/bin/bash

if [ "$#" -ne 3 ]; then
    echo "Usage: $0 <Patient.ndjson> <ResearchSubject.ndjson> <Observation.ndjson> "
    exit 1
fi

patients=$1
research_subjects=$2
observations=$3

patient_ids_tmp=$(mktemp)
patients_with_obs_tmp=$(mktemp)
patients_without_obs_tmp=$(mktemp)
research_studies_tmp=$(mktemp)

jq -r '.id' "$patients" > "$patient_ids_tmp"

jq -r '
  select(.subject.reference != null) |
  if (.subject.reference | type) == "string" then
    select(.subject.reference | test("^Patient/")) | .subject.reference | split("/")[1]
  else
    empty
  end
' "$observations" | sort | uniq > "$patients_with_obs_tmp"

grep -vFf "$patients_with_obs_tmp" "$patient_ids_tmp" > "$patients_without_obs_tmp"

echo "Patients without observations:"
cat "$patients_without_obs_tmp"

echo "Associated research studies for patients without observations:"
while IFS= read -r patient_id; do
    jq -r --arg patient_id "$patient_id" 'select(.subject.reference == "Patient/" + $patient_id) | .study.reference' "$research_subjects"
done < "$patients_without_obs_tmp" | sort | uniq > "$research_studies_tmp"

cat "$research_studies_tmp"

rm "$patient_ids_tmp" "$patients_with_obs_tmp" "$patients_without_obs_tmp" "$research_studies_tmp"
