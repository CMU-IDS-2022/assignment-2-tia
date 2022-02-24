from re import U
import streamlit as st
import pandas as pd
import altair as alt

import numpy as np
from vega_datasets import data


@st.cache
def load_data():
    """
    Write 1-2 lines of code here to load the data from CSV to a pandas dataframe
    and return it.
    """
    file = "billionaires.csv"
    df = pd.read_csv(file)
    return df

def geo_data():
    file = "df_ag.csv"
    df = pd.read_csv(file)
    return df


@st.cache
def get_slice_membership(df, genders, races, educations, age_range):
    """
    Implement a function that computes which rows of the given dataframe should
    be part of the slice, and returns a boolean pandas Series that indicates 0
    if the row is not part of the slice, and 1 if it is part of the slice.
    
    In the example provided, we assume genders is a list of selected strings
    (e.g. ['Male', 'Transgender']). We then filter the labels based on which
    rows have a value for gender that is contained in this list. You can extend
    this approach to the other variables based on how they are returned from
    their respective Streamlit components.
    """
    labels = pd.Series([1] * len(df), index=df.index)
    if genders:
        labels &= df['gender'].isin(genders)
    # ... complete this function for the other demographic variables
    if races:
        labels &= df['race'].isin(races)
    if educations:
        labels &= df['education'].isin(educations)
    if age_range:
        labels &= df['age'].isin(range(101))
    return labels


def make_long_reason_dataframe(df, reason_prefix):
    """
    ======== You don't need to edit this =========
    
    Utility function that converts a dataframe containing multiple columns to
    a long-style dataframe that can be plotted using Altair. For example, say
    the input is something like:
    
         | why_no_vaccine_Reason 1 | why_no_vaccine_Reason 2 | ...
    -----+-------------------------+-------------------------+------
    1    | 0                       | 1                       | 
    2    | 1                       | 1                       |
    
    This function, if called with the reason_prefix 'why_no_vaccine_', will
    return a long dataframe:
    
         | id | reason      | agree
    -----+----+-------------+---------
    1    | 1  | Reason 2    | 1
    2    | 2  | Reason 1    | 1
    3    | 2  | Reason 2    | 1
    
    For every person (in the returned id column), there may be one or more
    rows for each reason listed. The agree column will always contain 1s, so you
    can easily sum that column for visualization.
    """
    reasons = df[[c for c in df.columns if c.startswith(reason_prefix)]].copy()
    reasons['id'] = reasons.index
    reasons = pd.wide_to_long(reasons, reason_prefix, i='id', j='reason', suffix='.+')
    reasons = reasons[~pd.isna(reasons[reason_prefix])].reset_index().rename({reason_prefix: 'agree'}, axis=1)
    return reasons


# MAIN CODE


st.title("Billionaires")
#with st.spinner(text="Loading data..."):
df_ag = geo_data()


st.text("Visualize the overall dataset and some distributions here...")




if st.checkbox('Show Map'):
    df_ag = geo_data()
    world = alt.topo_feature(data.world_110m.url, "countries")

    select = alt.binding_select(options=sorted(df_ag.year.unique()), name='Year:')
    select_year = alt.selection_single(name="year", fields=['year'],
                                    bind=select, init={'year':1996})



    background = alt.Chart(world).mark_geoshape(
        fill='lightgray',
        stroke='white'
    ).properties(
        title='Countries over the World',
        width=700,
        height=400
    ).project('naturalEarth1')




    foreground = alt.Chart(df_ag).mark_geoshape().encode(
        color = 'log_wealth_worth_in_billions:Q',
        tooltip = [alt.Tooltip("location_citizenship:N", title="Country"),
                alt.Tooltip("wealth_worth_in_billions:Q", title="wealth")]
    ).add_selection(select_year
    ).transform_filter(select_year
    ).transform_lookup(lookup='country-code',from_=alt.LookupData(world, key='id',fields=["type", "properties", "geometry"])
    ).project('naturalEarth1'
    ).properties(
    width=500,
        height=300,
        title='Title'
    )


    st.altair_chart(background + foreground, use_container_width=True)
   


    














