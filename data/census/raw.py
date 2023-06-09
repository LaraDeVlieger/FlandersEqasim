import pandas as pd
import os

"""
This stage loads the raw data from the French population census.
"""

def configure(context):
    context.stage("data.spatial.codes")

    context.config("data_path")
    context.config("census_path", "census_2011/dataset_enriched.csv")

"""
COLUMNS_DTYPES = {
?    "CANTVILLE":"str", 
?    "NUMMI":"str", 
#    "AGED":"str",
#    "COUPLE":"str", 
#    "CS1":"str",
#    "DEPT":"str", 
#    "ETUD":"str",  
-    "ILETUD":"str",
#    "ILT":"str", 
-    "IPONDI":"str", 
#    "IRIS":"str",
-    "REGION":"str", 
#    "SEXE":"str",
#    "TACT":"str", 
#    "TRANS":"str",
#    "VOIT":"str", 
#    "DEROU":"str"
} """

COLUMNS_DTYPES = {
    "CD_SEX_LVL_1":"str", #sexe, done
    "CD_GEO_LVL_1":"str", #for filtering
    "CD_GEO_LVL_3":"str", #dept, done
    "CD_GEO_LVL_4":"str", #communityid, done
    "CD_FST_LVL_1":"str", #couple, done
    "CD_EDU_LVL_1":"str", #etud, done
    "CD_CAS_LVL_2":"str", #tact, done
    "CD_AGE_LVL_2":"str", #aged, done
    "CD_IND_LVL_2":"str", #cs1, done
    "CD_LPW_LVL_1":"str", #ilt, done
    "Vehicles":"str", #voit, done
    "Two wheelers":"str", #derou, done
    "Mode": "str" #trans, done
}


def execute(context):
    
    df_records = []
    df_codes = context.stage("data.spatial.codes")
    requested_departements = df_codes["departement_id"].unique()


    with context.progress(label = "Reading census ...") as progress:
        
        csv = pd.read_csv("%s/%s" % (context.config("data_path"),
                context.config("census_path")), usecols = COLUMNS_DTYPES.keys(), sep = ",",
                dtype = COLUMNS_DTYPES,
                chunksize = 10240)
    
    for df_chunk in csv:
        progress.update(len(df_chunk))

        #df_chunk = df_chunk[df_chunk["DEPT"].isin(requested_departements)]

        if len(df_chunk) > 0:
            df_records.append(df_chunk)

    pd.concat(df_records).to_hdf("%s/census.hdf" % context.path(), "census")


def validate(context):
    if not os.path.exists("%s/%s" % (context.config("data_path"), context.config("census_path"))):
        raise RuntimeError("Census 2011 data is not available")

    return os.path.getsize("%s/%s" % (context.config("data_path"), context.config("census_path")))
