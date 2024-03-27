#!/bin/bash
# example run :
# (cd /fhir/objects/dir/META/; ./count_gender.sh TCGA-ACC)

research_subjects_file="ResearchSubject.ndjson"
patient_file="Patient.ndjson"
study_name="$1"

patient_ids=$(jq -r 'select(.study.reference == "ResearchStudy/$study_name") | .subject.reference' ResearchSubject.ndjson | sed 's/^.*[/]//')

female_count=0
male_count=0

for patient_id in $patient_ids; do
    echo "$patient_id"
    female=$(grep -c "$patient_id.*female" Patient.ndjson)
    male=$(grep -c "$patient_id.*male" Patient.ndjson)
    if [ $female == 1 ]; then
        ((female_count++))
    elif [ $male == 1 ]; then
        ((male_count++))
    fi
done

echo "Female count in the $study_name study: $female_count"
echo "Male count in the $study_name study: $male_count"

