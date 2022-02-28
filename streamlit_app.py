import streamlit as st
import pandas as pd
import altair as alt
from vega_datasets import data




from re import U
import streamlit as st
import pandas as pd
import altair as alt

import numpy as np
#from vega_datasets import data

@st.cache
def load_data():
    """
    Write 1-2 lines of code here to load the data from CSV to a pandas dataframe
    and return it.
    """
    #file = "https://raw.githubusercontent.com/CMU-IDS-2022/assignment-2-tia/master/billionaires.csv"
    file = "billionaires.csv"
    df = pd.read_csv(file)
    df.columns = df.columns.str.replace('.', '_')
    df.columns = df.columns.str.replace(' ', '_')
    return df

def load_data14():
    #file = "https://raw.githubusercontent.com/CMU-IDS-2022/assignment-2-tia/master/billionaires.csv"
    file = "billionaires.csv"
    df = pd.read_csv(file)
    df.columns = df.columns.str.replace('.', '_')
    df.columns = df.columns.str.replace(' ', '_')
    df14 = df[df['year']==2014]
    df14.dropna(inplace=True)
    col = ['rank','wealth_type','location_citizenship','wealth_worth_in_billions','year','company_founded', 'company_type', 'demographics_age', 'demographics_gender', 
           'location_region', 'wealth_how_from_emerging', 'wealth_how_industry', 'wealth_how_inherited',
           'wealth_how_was_founder', 'wealth_how_was_political']
    df14 = df14[col]
    df14 = df14[(df14['demographics_age']!=0) & (df14['company_founded']!=0) & (df14.wealth_how_industry !='0')]
    df14.loc[(df['company_type'] == " new") | (df['company_type'] == "new ") |(df['company_type'] == "new division"),
             'company_type'] = 'new'
    df14.loc[(df['company_type'] == " acquired") | (df['company_type'] == "aquired") |(df['company_type'] == "new/aquired"),
             'company_type'] = 'acquired'
    df14.loc[df['company_type'] == "new, privitization", 'company_type'] = 'privatization'
    
    return df14




def geo_data():
    #file = "https://raw.githubusercontent.com/CMU-IDS-2022/assignment-2-tia/master/billionaires.csv"
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



def get_slice_membership(df, year, genders, industry, citizenship, age_range):
    """

    """
    labels = pd.Series([1] * len(df), index=df.index)
    if genders:
        labels &= df['demographics_gender'].isin(genders)
    if year:
        labels &= df['year']==year
    if industry:
        labels &= df['wealth_how_industry'].isin(industry)
    if citizenship:
        labels &= df['location_citizenship'].isin(citizenship)
    if age_range is not None:
        labels &= df['demographics_age'] >= age_range[0]
        labels &= df['demographics_age'] <= age_range[1]
    return labels



# Main
st.header("Let's analyze some Forbes Billionaires Data💰💰.")
st.text("Researchers have compiled a multi-decade database of the super-rich.\n👉Building off the Forbes World’s Billionaires lists from 1996-2014, scholars at Peterson\nInstitute for International Economics have added a couple dozen more variables about\neach billionaire - including whether they were self-made or inherited their wealth.") 

df = load_data()
if st.checkbox("Show Raw Data"):
    st.write(df)


## Plot 1: TOP billionaires by Year
st.subheader("1. Show TOP 10 billionaires by Year Selected")
st.text('Instruction: \nSelect year from the dropdown menu to see corresponding TOP 10 billionaires in dataframe and barchart!') 


year = st.selectbox("Year", df['year'].unique())
#st.write(df[df['year']==year][['name','wealth_worth_in_billions','rank']].sort_values('wealth_worth_in_billions', ascending = False).head(10).set_index('rank'))
new_df=df[df['year']==year][['name','wealth_worth_in_billions','rank']].sort_values('wealth_worth_in_billions', ascending = False).head(10).set_index('rank')
st.dataframe(data=new_df, width=700, height=768)


df_ranking = df[df['year']==year].sort_values('wealth_worth_in_billions', ascending = False).head(10)

rank_bar = alt.Chart(
    df_ranking,
).mark_bar(tooltip=True).encode(
    x=alt.X('wealth_worth_in_billions'),
    y=alt.Y('name', sort='-x'),
    color=alt.Color('wealth_worth_in_billions')

).transform_window(
    rank='rank(wealth_worth_in_billions)',
    sort=[alt.SortField('rank', order='descending')]
).transform_filter(
    (alt.datum.rank < 11)
)
st.altair_chart(rank_bar,use_container_width=True)



st.write(' ')
st.write(' ')
st.write(' ')

## Plot 2: Cumulative Wealth from Billionaires by Country and Year
st.subheader("2. Cumulative Wealth from Billionaires across Country by Year")
st.text('Instruction: \nSelect year from the dropdown menu below to') 


df_ag = geo_data()
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
               alt.Tooltip("wealth_worth_in_billions:Q", title="Cumulative Wealth Worth in Billions")]
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


## Plot 3: Gender Distribution by Different Categories
st.subheader("3. Visualize gender distribution by selected category")
df_14 = load_data14()

st.text("Number of billionares by different categories, click certain category to see gender percentage")
bar_list = ['wealth_type','company_type','location_region','wealth_how_industry']
feature = st.selectbox('Category', bar_list)

click = alt.selection_multi(encodings=['color'])
brush = alt.selection_multi(fields=[str(feature)])

chart = alt.Chart(df_14).mark_bar(tooltip=True).encode(
    x = 'count()',
    y = str(feature),
    color=alt.condition(click, str(feature), alt.value('lightgray'), legend = None)
    ).add_selection(click)

base = alt.Chart(df_14).encode(
    theta=alt.Theta("count()", stack=True), color=alt.Color('demographics_gender'),
    tooltip=['demographics_gender', 'count()']
).transform_filter(
    click)

pie = base.mark_arc(outerRadius=120)
text = base.mark_text(radius=140, size=20).encode(text='demographics_gender')

p = pie + text
st.altair_chart(chart & p)







## Plot 4: Linked Brushing: Age, Wealth, and Inheritance 
st.subheader("4. Age, Wealth, and Inheritance")
df14 = load_data14()
scatter = alt.Chart(df14).mark_point(
    tooltip=True,filled=True,opacity=0.5
).encode(
    x=alt.X('demographics_age', scale=alt.Scale(zero=False),
            axis=alt.Axis(title='Age')),
    y=alt.Y('wealth_worth_in_billions', scale=alt.Scale(type='log'),
            axis=alt.Axis(format='$', title='Wealth Worth in Billions (log)'))
)



hist = alt.Chart(df14).mark_bar(
    tooltip=True
).encode(
    x=alt.X(aggregate="count", type="quantitative",axis=alt.Axis(title='Count')),
    y=alt.Y("wealth_worth_in_billions", bin=True,axis=alt.Axis(format='$', title='Wealth Worth in Billions (log)'))
)



selection = alt.selection_interval()

comb = scatter.add_selection(selection).encode(
    color=alt.condition(selection, "wealth_how_inherited", alt.value("grey"))
) | hist.encode(
    alt.Color("wealth_how_inherited", scale=alt.Scale(domain=['not inherited', 'spouse/widow','father', '3rd generation',
       '4th generation','5th generation or longer']))
).transform_filter(selection)

st.altair_chart(comb,use_container_width=True)


st.markdown("This project was created by Silvia Gu and Tina Feng for the [Interactive Data Science](https://dig.cmu.edu/ids2022) course at [Carnegie Mellon University](https://www.cmu.edu).")
