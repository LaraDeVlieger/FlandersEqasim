from tqdm import tqdm
import pandas as pd
import numpy as np
import data.hts.hts as hts
import random

"""
This stage cleans the French population census:
  - Assign new unique integer IDs to households and persons
  - Clean up spatial information and sociodemographic attributes
"""

def configure(context):
    context.stage("data.census.raw")
    context.stage("data.spatial.codes")

def execute(context):
    df = pd.read_hdf("%s/census.hdf" % context.path("data.census.raw"))
    
    # np.arange gives an evenly spaced interval (3) -- [0 1 2]
    # Put person IDs
    df["person_id"] = np.arange(len(df))

    # Spatial information
    
    geo = pd.unique(df['CD_GEO_LVL_4'])
    for loc in geo:
        df_codes = context.stage("data.spatial.codes")
        geof2 = df_codes[df_codes["commune_id"] == int(loc)]
        possible_iris = geof2["iris_id"].values
            
        # now same variables in the other set
        if len(possible_iris) == 0:
            df.drop(df[df["CD_GEO_LVL_4"] == loc].index, inplace = True)
        else: df.loc[(df["CD_GEO_LVL_4"] == loc), "iris_id"] = random.choice(possible_iris)
    
    df["departement_id"] = df["CD_GEO_LVL_3"].astype("category")

    df["commune_id"] = df["CD_GEO_LVL_4"].astype("category")
        

    # # Construct household IDs for persons with NUMMI != Z
    # df_household_ids = df[["CANTVILLE", "NUMMI"]]
    # df_household_ids = df_household_ids[df_household_ids["NUMMI"] != "Z"]
    # df_household_ids["temporary"] = df_household_ids["CANTVILLE"] + df_household_ids["NUMMI"]
    # df_household_ids = df_household_ids.drop_duplicates("temporary")
    # df_household_ids["household_id"] = np.arange(len(df_household_ids))
    # df = pd.merge(df, df_household_ids, on = ["CANTVILLE", "NUMMI"], how = "left")

    # # Fill up undefined household ids (those where NUMMI == Z)
    # f = np.isnan(df["household_id"])
    # df.loc[f, "household_id"] = np.arange(np.count_nonzero(f)) + df["household_id"].max()
    
    iris = pd.unique(df['iris_id'])
    idnumber = 1001
    for id in iris:
        irisdf = df[df["iris_id"] == id]
        hhnumbertot = len(irisdf)/2.3
        possible_hh = np.arange(hhnumbertot)
        df.loc[(df["iris_id"] == id), "CANTVILLE"] = str(idnumber)
        idnumber += 1
        households = np.random.choice(possible_hh, len(irisdf))
        households = households.astype(str)
        df.loc[ (df["iris_id"] == id), "NUMMI"] = households
        
    df_household_ids = df[["CANTVILLE", "NUMMI"]]
    df_household_ids["temporary"] = df_household_ids["CANTVILLE"] + df_household_ids["NUMMI"]
    df_household_ids = df_household_ids.drop_duplicates("temporary")
    df_household_ids["household_id"] = np.arange(len(df_household_ids))
    df = pd.merge(df, df_household_ids, on = ["CANTVILLE", "NUMMI"], how = "left")
 
    # Sorting
    df = df.sort_values(by = ["household_id", "person_id"])

    # Verify with requested codes
    #Should be included again if census data from Belgium is fixed
    #excess_communes = set(df["commune_id"].unique()) - set(df_codes["commune_id"].unique())
    #if not excess_communes == {"undefined"}:
    #    raise RuntimeError("Found additional communes: %s" % excess_communes)

    #excess_iris = set(df["iris_id"].unique()) - set(df_codes["iris_id"].unique())
    #if not excess_iris == {"undefined"}:
    #    raise RuntimeError("Found additional IRIS: %s" % excess_iris)

    # Age
    df["age"] = df["CD_AGE_LVL_2"]

    # Clean COUPLE
    df.loc[df["CD_FST_LVL_1"] == "CPL", "couple_mode"] = "partners"
    df.loc[df["CD_FST_LVL_1"] == "CH_PAR", "couple_mode"] = "kids"
    df.loc[df["CD_FST_LVL_1"] == "NAP", "couple_mode"] = "alone"
    df.loc[df["CD_FST_LVL_1"] == "PAR1", "couple_mode"] = "single parent"
    df["couple_mode"] = df["couple_mode"].astype("category")
    

    # Clean SEXE
    df.loc[df["CD_SEX_LVL_1"] == "M", "sex"] = "male"
    df.loc[df["CD_SEX_LVL_1"] == "F", "sex"] = "female"
    df["sex"] = df["sex"].astype("category")

    # Clean employment
    df["employed"] = df["CD_CAS_LVL_2"] == "EMP"

    # Studies
    df.loc[df["CD_EDU_LVL_1"] == "ED1", "studies"] = "lager"
    df.loc[df["CD_EDU_LVL_1"] == "ED2", "studies"] = "secundair"
    df.loc[df["CD_EDU_LVL_1"] == "ED3", "studies"] = "secundair"
    df.loc[df["CD_EDU_LVL_1"] == "ED4", "studies"] = "post-secundair"
    df.loc[df["CD_EDU_LVL_1"] == "ED5", "studies"] = "hoger"
    df.loc[df["CD_EDU_LVL_1"] == "ED6", "studies"] = "doctoraat"
    df.loc[df["CD_EDU_LVL_1"] == "NAP", "studies"] = np.nan
    df.loc[df["CD_EDU_LVL_1"] == "NONE", "studies"] = "geen diploma"
    df.loc[df["CD_EDU_LVL_1"] == "UNK", "studies"] = np.nan
    df["studies"] = df["studies"].astype("category")

    # Number of vehicles
    df["number_of_vehicles"] = df["Vehicles"].apply(
        lambda x: str(x).replace("Z", "0").replace("X", "0")
    ).astype(int)
    
    df["number_of_vehicles"] += df["Two wheelers"].apply(
        lambda x: str(x).replace("U", "0").replace("90", "0").replace("X", "0")
    ).astype(int)

    df.loc[df["Mode"] == "Z", "commute_mode"] = np.nan
    df["commute_mode"] = df["commute_mode"].astype("category")

    # Household size
    df_size = df[["household_id"]].groupby("household_id").size().reset_index(name = "household_size")
    df = pd.merge(df, df_size)

    # Socioprofessional category
    df["socioprofessional_class"] = df["CD_IND_LVL_2"].astype("category")

    # Place of work or education
    df["work_outside_belgium"] = df["CD_LPW_LVL_1"] == "FOR"
    

    # Household size
    df_size = df[["household_id"]].groupby("household_id").size().reset_index(name = "household_size")
    df = pd.merge(df, df_size)


    # Consumption units
    df = pd.merge(df, hts.calculate_consumption_units(df), on = "household_id")

    return df[[
        "person_id", "household_id", "household_size",
        "departement_id", "commune_id", "iris_id",
        "age", "sex", "couple_mode", "employed",
        "studies", "number_of_vehicles", "commute_mode",
        "work_outside_belgium", "socioprofessional_class", "CD_GEO_LVL_1",
        "consumption_units"
    ]]
