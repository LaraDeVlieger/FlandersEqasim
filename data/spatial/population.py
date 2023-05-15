import os
import pandas as pd

"""
Loads aggregate population data.
"""

"Elle: load in new data file (after adding arro column) and edit so no region is required" \
"plus change column names. Don't need" \
"population year because only 1 year available in our data set"

def configure(context):
    context.config("data_path")
    context.stage("data.spatial.codes")
    context.config("population_path", "zonal_data/OPEN DATA_SECTOREN_2019.xlsx")
    #context.config("population_year", 19)

def execute(context):
    #year = str(context.config("population_year"))
    df_population = pd.read_excel(
        "%s/%s" % (context.config("data_path"), context.config("population_path")),
        sheet_name = "Blad1", usecols = ["CD_SECTOR", "CD_REFNIS", "ARRO", "POPULATION"]
    ).rename(columns = {
        "CD_SECTOR": "iris_id", "CD_REFNIS": "commune_id", "ARRO": "departement_id",
        "POPULATION": "population"
    })

    df_population["iris_id"] = df_population["iris_id"].astype("category")
    df_population["commune_id"] = df_population["commune_id"].astype("category")
    df_population["departement_id"] = df_population["departement_id"].astype("category")
    #df_population["region_id"] = df_population["region_id"].astype(int)

    # Merge into code data and verify integrity
    df_codes = context.stage("data.spatial.codes")
    df_population = pd.merge(df_population, df_codes, on = ["iris_id", "commune_id", "departement_id"])

    requested_iris = set(df_codes["iris_id"].unique())
    merged_iris = set(df_population["iris_id"].unique())

    if requested_iris != merged_iris:
        raise RuntimeError("Some IRIS are missing: %s" % (requested_iris - merged_iris,))

    return df_population[["departement_id", "commune_id", "iris_id", "population"]]

def validate(context):
    if not os.path.exists("%s/%s" % (context.config("data_path"), context.config("population_path"))):
        raise RuntimeError("Aggregated census data is not available")

    return os.path.getsize("%s/%s" % (context.config("data_path"), context.config("population_path")))
     