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
    file = "billionaires.csv"
    df = pd.read_csv(file)
    df.columns = df.columns.str.replace('.', '_')
    df.columns = df.columns.str.replace(' ', '_')

    url = 'https://raw.githubusercontent.com/lukes/ISO-3166-Countries-with-Regional-Codes/master/all/all.csv'
    geo = pd.read_csv(url, index_col=0)
    geo.reset_index(inplace=True)
    geo = geo[['name','alpha-3','country-code']]

    df=pd.merge(df, geo, how='left', left_on=['location_country_code'], right_on=['alpha-3'])
    df.loc[df['location_citizenship'] == "Taiwan", "country-code"] = geo[geo['alpha-3'] =='TWN']['country-code'].item()
    df.loc[df['location_citizenship'] == "Denmark", "country-code"] = geo[geo['alpha-3'] =='DNK']['country-code'].item()
    df = df.drop(['name_y','alpha-3'],axis=1)

    df_ag = df[['wealth_worth_in_billions','location_citizenship','country-code','year']].groupby(
    ['location_citizenship','year']).agg({'wealth_worth_in_billions' : 'sum',
                     'country-code' : 'first'})
    df_ag = df_ag.reset_index()
    df_ag['Wealth Worth in Billions (log)'] = df_ag.wealth_worth_in_billions.apply(lambda x: np.log(x))
    df_ag["year"] = df_ag["year"].astype(str)

    return df_ag




# MAIN CODE
df = load_data()
df_ag = geo_data()
st.title("Billionaires")
if st.checkbox("Show Raw Data"):
    st.write(df)

    


st.write("### Visualize the overall dataset and some distributions here...")




world = alt.topo_feature(data.world_110m.url, "countries")

select = alt.binding_select(options=sorted(df_ag.year.unique()), name='Year:')
select_year = alt.selection_single(name="year", fields=['year'],
                                bind=select, init={'year':'1996'})


background = alt.Chart(world).mark_geoshape(
    fill='lightgray',
    stroke='white'
).properties(
    title='Countries over the World',
    width=700,
    height=400
).project('naturalEarth1')



foreground = alt.Chart(df_ag).mark_geoshape().encode(
    color = alt.Color('Wealth Worth in Billions (log):Q'),#,legend=None),
    tooltip = [alt.Tooltip("location_citizenship:N", title="Country"),
               alt.Tooltip("wealth_worth_in_billions:Q", title="Wealth Worth in Billions")]
).add_selection(select_year
).transform_filter(select_year
).transform_lookup(lookup='country-code',from_=alt.LookupData(world, key='id',fields=["type", "properties", "geometry"])
).project('naturalEarth1'
).properties(
   width=700,
    height=400,
    title='Title'
)

final = background + foreground

st.altair_chart(final, use_container_width=True)
