import numpy as np
import pandas as pd
from sklearn.neighbors import KDTree
import os

"""
Loads and prepares income distributions by municipality:
- Load data with centiles per municipality
- For those which only provide median: Attach another distribution with most similar median
- For those which are missing: Attach the distribution of the municiality with the nearest centroid
"""

# okay so the problem here now is that it won't work because we have no deciles or anything we only have the median in belgium
# this ensures that we are in the second scenario, but there is no distribution to attach another distribution from
# we could attach some of the distributions from paris as france is kind of similar but not as a whole
# We could find a totally different way to construct a distribution but seems like a lot of work and dont know how at the moment
# for Region it needs to be the same? Or what did Elle see as Region vs Municipality vs Statistical zone
# also at the moment it doesn't work as it gives the error that the zones aren't similar

def configure(context):
    context.config("data_path")
    context.stage("data.spatial.municipalities")
    context.config("income_com_path", "incomeBE20/fisc2020_D_NL.xls")
    context.config("income_path_france", "filosofi_2019/FILO2019_DISP_COM.xlsx")
    context.config("income_year", 19)

def execute(context):
    # Load income distribution
    year = str(context.config("income_year"))
    
    df = pd.read_excel(
        "%s/%s" % (context.config("data_path"), context.config("income_com_path")),
        sheet_name = "fisc2020_D_NL", skiprows = 5
    )[["NIS code van de gemeente"] + ["Extra column" if q != 5 else "Mediaan inkomen per aangifte" for q in range(1, 10)]]
    # median = q5, at the moment all the rest is NaN --> de decilen nodig
    df.columns = ["commune_id", "q1", "q2", "q3", "q4", "q5", "q6", "q7", "q8", "q9"]
    df["reference_median"] = df["q5"].values
    #print(df)
    
    df_france = pd.read_excel(
        "%s/%s" % (context.config("data_path"), context.config("income_path_france")),
        sheet_name = "ENSEMBLE", skiprows = 5
    )[["CODGEO"] + [("D%d" % q) + year if q != 5 else "Q2" + year for q in range(1, 10)]]
    df_france.columns = ["commune_id", "q1", "q2", "q3", "q4", "q5", "q6", "q7", "q8", "q9"]
    df_france["reference_median"] = df_france["q5"].values

    # Verify spatial data for education
    # now it checks if the data is compatible within france 
    # if Elle her part works this should go back to being right and change it to df instead of df_france
    # the purpose is that the ones which are too much or missing are found
    df_municipalities = context.stage("data.spatial.municipalities")
    requested_communes = set(df_municipalities["commune_id"].unique())
    df_france = df_france[df_france["commune_id"].isin(requested_communes)]
    
    # okay so the thing is at the moment they here only select the things for paris
    # if we only want leuven we can do that here or otherwise maybe here summarize the communes
    # another assumption we make here is that the ones which have an . for an iris id are not taken into account
    df["is_missing"] = False
    df = df.reset_index()
    for index, row in df.iterrows():
        if row['q5'] == ".":
            df.at[index, 'is_missing'] = True
    df_clean = df[df["is_missing"] != True]
    #print(df_clean)
    #print(df_clean['q5'].dtype)
    df_clean['q5'] = df_clean['q5'].astype(float)

    df_clean['mean'] = df_clean.groupby(['commune_id'])['q5'].transform('mean')
    df_clean = df_clean.drop_duplicates(subset=['commune_id'])
    df = df_clean
    
    # for now we fill in the commune id's ourselves
    df_municipalities["commune_id"] = df_municipalities["commune_id"].astype("int64")
    #print(df_municipalities["commune_id"])
    #print(df["commune_id"])
    df_municipalities = df
    requested_communes = set(df_municipalities["commune_id"].unique())
    

    # Find communes without data
    df["commune_id"] = df["commune_id"].astype("category")
    missing_communes = set(df_municipalities["commune_id"].unique()) - set(df["commune_id"].unique())
    print("Found %d/%d municipalities that are missing" % (len(missing_communes), len(requested_communes)))

    # Find communes without full distribution
    df["is_imputed"] = df["q2"].isna()
    df_france["is_imputed"] = df_france["q2"].isna()
    print("Found %d/%d municipalities which do not have full distribution" % (sum(df["is_imputed"]), len(requested_communes)))

    # First, find suitable distribution for incomplete cases by finding the one with the most similar median
    incomplete_medians = df[df["is_imputed"]]["q5"].values

    # use the France data set as the complete one
    df_complete = df_france[~df_france["is_imputed"]]
    complete_medians = df_complete["q5"].values

    indices = np.argmin(np.abs(complete_medians[:, np.newaxis] - incomplete_medians[np.newaxis, :]), axis = 0)

    for k in range(1, 10):
        df.loc[df["is_imputed"], "q%d" % k] = df_complete.iloc[indices]["q%d" % k].values
    
    # until here it works the ones where you have a median they are added
    print(df)

    # AT THE MOMENT TURNED OFF --> not needed and gives a lot of errors
    # # Second, add missing municipalities by neirest neighbor
    # # ... build tree of existing communes
    # df_existing = df_municipalities[df_municipalities["commune_id"].astype(str).isin(df["commune_id"])] # pandas Bug
    # coordinates = np.vstack([df_existing["geometry"].centroid.x, df_existing["geometry"].centroid.y]).T
    # kd_tree = KDTree(coordinates)

    # # ... query tree for missing communes
    # df_missing = df_municipalities[df_municipalities["commune_id"].astype(str).isin(missing_communes)] # pandas Bug

    # if len(df_missing) > 0:
    #     coordinates = np.vstack([df_missing["geometry"].centroid.x, df_missing["geometry"].centroid.y]).T
    #     indices = kd_tree.query(coordinates)[1].flatten()

    #     # ... build data frame of imputed communes
    #     df_reconstructed = pd.concat([
    #         df[df["commune_id"] == df_existing.iloc[index]["commune_id"]]
    #         for index in indices
    #     ])
    #     df_reconstructed["commune_id"] = df_missing["commune_id"].values
    #     df_reconstructed["is_imputed"] = True
    #     df_reconstructed["is_missing"] = True

    #     # ... merge the data frames
    #     df = pd.concat([df, df_reconstructed])

    # Validation
    assert len(df) == len(df["commune_id"].unique())
    assert len(requested_communes - set(df["commune_id"].unique())) == 0

    return df[["commune_id", "q1", "q2", "q3", "q4", "q5", "q6", "q7", "q8", "q9", "is_imputed", "is_missing", "reference_median"]]

def validate(context):
    if not os.path.exists("%s/%s" % (context.config("data_path"), context.config("income_com_path"))):
        raise RuntimeError("Filosofi data is not available")

    return os.path.getsize("%s/%s" % (context.config("data_path"), context.config("income_com_path")))
