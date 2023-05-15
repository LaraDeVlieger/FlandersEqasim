import geopandas as gpd
import numpy as np
import pandas as pd

def configure(context):
    # absolute paths are used here, please change accordingly

    context.config("data_path")
    context.config("activity_path", r"C:\Users\larad\OneDrive\Documenten\school\Leuven\data\poidpy\Activity.shp")

    context.config("data_path")
    context.config("zone_path", r"C:\Users\larad\OneDrive\Documenten\school\Leuven\data\zonal_data\sh_statbel_statistical_sectors_3812_20220101.shp")

    context.stage("data.spatial.municipalities")

def execute(context):
        # Read the shapefiles generated from Poidpy
        activity = gpd.read_file(context.config("activity_path"))[["classifica", "geometry"]]
        activity = activity.rename(columns={
            'classifica': 'NACE'
        })

        # Reproject CRS
        new_crs = "EPSG:3812"
        activity = activity.to_crs(new_crs)

        # Read the zoning shapefile
        zone = gpd.read_file(context.config("zone_path"))[["CNIS5_2022", "CS01012022", "geometry"]]
        zone = zone.rename(columns={
            'CS01012022': 'iris_id',
            'CNIS5_2022': 'commune_id'
        })

        # Filter the activity layer to look for work locations
        non_work_NACE = ["R"]
        work_locations = activity[~activity["NACE"].isin(non_work_NACE)]

        # Join the zone number to the potential locations
        df_workplaces = gpd.sjoin(work_locations, zone, op="within")

        # Drop unnecessary columns
        df_workplaces = df_workplaces.drop(columns=['index_right', 'NACE', 'iris_id'])

        # Randomly assign number of employees
        df_workplaces["employees"] = np.random.lognormal(mean=2, sigma=2, size=len(df_workplaces))
        df_workplaces["employees"] = np.round(df_workplaces["employees"]).astype(int)


        # Add work locations to the centroid of municipalities without any work location
        df_zones = context.stage("data.spatial.municipalities")
        required_communes = set(df_zones["commune_id"].unique())
        missing_communes = required_communes - set(df_workplaces["commune_id"].unique())

        print("Adding work places at the centroid of %d/%d communes without Poidpy observations" % (
            len(missing_communes), len(required_communes)))

        df_added = []

        for commune_id in missing_communes:
            centroid = df_zones[df_zones["commune_id"] == commune_id]["geometry"].centroid.iloc[0]

            df_added.append({
                "commune_id": commune_id, "employees": 1.0, "geometry": centroid,
            })

        df_added = pd.DataFrame.from_records(df_added)

        # Merge together
        df_workplaces["fake"] = False
        df_added["fake"] = True

        df_workplaces = pd.concat([df_workplaces, df_added])


        # Define identifiers
        df_workplaces["location_id"] = np.arange(len(df_workplaces))
        df_workplaces["location_id"] = "work_" + df_workplaces["location_id"].astype(str)

        # Rearrange the column order
        df_workplaces = df_workplaces.reindex(columns=["location_id", "commune_id", "employees", "fake", "geometry"])

        return df_workplaces[["location_id", "commune_id", "employees", "fake", "geometry"]]