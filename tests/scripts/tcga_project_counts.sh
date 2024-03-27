#!/bin/bash
# chmod to make executable chmod +x tcga_project_counts.sh
# Example run:
# ./tests/scripts/tcga_project_counts.sh ../META/ResearchStudy.ndjson

if [ "$#" -ne 1 ]; then
  echo "Usage: $0 <file_pathname>"
  exit 1
fi

file_pathname="$1"


patterns=("TCGA-BRCA" "TCGA-ACC" "TCGA-KIRP" "TCGA-KIRC" "TCGA-KICH" "TCGA-HNSC" "TCGA-GBM" "TCGA-ESCA" "TCGA-DLBC" "TCGA-COAD" "TCGA-CHOL" "TCGA-CESC" "TCGA-BLCA" "TCGA-UVM" "TCGA-UCS" "TCGA-UCEC" "TCGA-THYM" "TCGA-THCA" "TCGA-TGCT" "TCGA-STAD" "TCGA-SKCM" "TCGA-SARC" "TCGA-READ" "TCGA-PRAD" "TCGA-PCPG" "TCGA-PAAD" "TCGA-OV" "TCGA-MESO" "TCGA-LUSC" "TCGA-LUAD" "TCGA-LIHC" "TCGA-LGG" "TCGA-LAML")

for pattern in "${patterns[@]}"; do
    count=$(grep -c "\"id\": \"$pattern\"" "$file_pathname")
    echo "$pattern: $count"
done