#!/bin/bash

path="referential_data"
API_TOKEN=$(awk -F " = " '/API_TOKEN/ {print $2}' config.ini)

# List of URLs
urls=(
    "https://data.iledefrance-mobilites.fr/explore/dataset/arrets/download/?format=csv&timezone=Europe/Berlin&lang=fr&use_labels_for_header=true&csv_separator=%3B"
    "https://data.iledefrance-mobilites.fr/api/explore/v2.1/catalog/datasets/relations/exports/csv?lang=fr&timezone=Europe%2FBerlin&use_labels=true&delimiter=%3B"
    "https://data.iledefrance-mobilites.fr/explore/dataset/referentiel-des-lignes/download/?format=csv&timezone=Europe/Berlin&lang=fr&use_labels_for_header=true&csv_separator=%3B"
    "https://data.iledefrance-mobilites.fr/explore/dataset/perimetre-des-donnees-tr-disponibles-plateforme-idfm/download/?format=csv&timezone=Europe/Berlin&lang=fr&use_labels_for_header=true&csv_separator=%3B"
)

# Create the folder if it doesn't exist
mkdir -p "$path"    

# Loop through the URLs and execute wget command
for url in "${urls[@]}"
do
    # Extract the filename from the URL
    filename=$(basename "$url")

    # Save the file inside the folder
    wget --content-disposition --header="Authorization: Bearer $API_TOKEN" -P "$path" "$url"
done