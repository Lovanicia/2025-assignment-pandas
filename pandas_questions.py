"""Plotting referendum results in pandas.

In short, we want to make beautiful map to report results of a referendum. In
some way, we would like to depict results with something similar to the maps
that you can find here:
https://github.com/x-datascience-datacamp/datacamp-assignment-pandas/blob/main/example_map.png

To do that, you will load the data as pandas.DataFrame, merge the info and
aggregate them by regions and finally plot them on a map using `geopandas`.
"""
import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt


def load_data():
    """Load data from the CSV files referundum/regions/departments."""
    referendum = pd.read_csv("data/referendum.csv", sep=";")
    regions = pd.read_csv("data/regions.csv")
    departments = pd.read_csv("data/departments.csv")
    return referendum, regions, departments


def merge_regions_and_departments(regions, departments):
    """Merge regions and departments in one DataFrame.

    The columns in the final DataFrame should be:
    ['code_reg', 'name_reg', 'code_dep', 'name_dep']
    """
    reg = regions.rename(columns={
        "code": "code_reg",
        "name": "name_reg",
    })
    dep = departments.rename(columns={
        "region_code": "code_reg",
        "code": "code_dep",
        "name": "name_dep",
    })
    reg = reg[["code_reg", "name_reg"]]
    dep = dep[["code_reg", "code_dep", "name_dep"]]
    merged = dep.merge(reg, on="code_reg", how="inner")
    print(merged.head())
    return merged[["code_reg", "name_reg", "code_dep", "name_dep"]]


def merge_referendum_and_areas(referendum, regions_and_departments):
    """Merge referendum and regions_and_departments in one DataFrame.

    You can drop the lines relative to DOM-TOM-COM departments, and the
    french living abroad, which all have a code that contains `Z`.

    DOM-TOM-COM departments are departements that are remote from metropolitan
    France, like Guadaloupe, Reunion, or Tahiti.
    """
    ref = referendum.copy()
    ref["code_dep"] = ref["Department code"].astype(str).str.zfill(2)
    ref = ref[~ref["code_dep"].str.contains("Z", na=False)]
    merged = regions_and_departments.merge(ref, on="code_dep", how="inner")
    return merged


def compute_referendum_result_by_regions(referendum_and_areas):
    """Return a table with the absolute count for each region.

    The return DataFrame should be indexed by `code_reg` and have columns:
    ['name_reg', 'Registered', 'Abstentions', 'Null', 'Choice A', 'Choice B']
    """
    grp = referendum_and_areas.groupby("code_reg")
    sums = grp[["Registered", "Abstentions", "Null", "Choice A", "Choice B"]].sum()
    names = grp["name_reg"].first()
    result = sums.copy()
    result.insert(0, "name_reg", names)
    result = result[["name_reg", "Registered", "Abstentions", "Null", "Choice A", "Choice B"]]
    return result


def plot_referendum_map(referendum_result_by_regions):
    """Plot a map with the results from the referendum.

    * Load the geographic data with geopandas from `regions.geojson`.
    * Merge these info into `referendum_result_by_regions`.
    * Use the method `GeoDataFrame.plot` to display the result map. The results
      should display the rate of 'Choice A' over all expressed ballots.
    * Return a gpd.GeoDataFrame with a column 'ratio' containing the results.
    """
    regions = gpd.read_file("data/regions.geojson")
    if "name_reg" not in regions.columns and "nom" in regions.columns:
        regions = regions.rename(columns={"nom": "name_reg"})
    if "ratio" not in referendum_result_by_regions.columns:
        expressed = referendum_result_by_regions["Choice A"] + referendum_result_by_regions["Choice B"]
        referendum_result_by_regions = referendum_result_by_regions.copy()
        referendum_result_by_regions["ratio"] = referendum_result_by_regions["Choice A"] / expressed
    gdf = regions.merge(
        referendum_result_by_regions[["name_reg", "ratio"]],
        on="name_reg",
        how="left",
    )
    gdf.plot(column="ratio", legend=True)
    return gdf


if __name__ == "__main__":

    referendum, df_reg, df_dep = load_data()
    regions_and_departments = merge_regions_and_departments(
        df_reg, df_dep
    )
    referendum_and_areas = merge_referendum_and_areas(
        referendum, regions_and_departments
    )
    referendum_results = compute_referendum_result_by_regions(
        referendum_and_areas
    )
    print(referendum_results)

    plot_referendum_map(referendum_results)
    plt.show()
