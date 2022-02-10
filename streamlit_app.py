import streamlit as st
import pandas as pd
import altair as alt

st.title("Let's analyze some Penguin Data 🐧📊.")

@st.cache  # add caching so we load the data only once
def load_data():
    # Load the penguin data from https://github.com/allisonhorst/palmerpenguins.
    penguins_url = "https://raw.githubusercontent.com/allisonhorst/palmerpenguins/v0.1.0/inst/extdata/penguins.csv"
    return pd.read_csv(penguins_url)

df = load_data()

st.write("Let's look at raw data in the Pandas Data Frame.")

st.write(df)

st.write("Hmm 🤔, is there some correlation between body mass and flipper length? Let's make a scatterplot with [Altair](https://altair-viz.github.io/) to find.")

chart = alt.Chart(df).mark_point().encode(
    x=alt.X("body_mass_g", scale=alt.Scale(zero=False)),
    y=alt.Y("flipper_length_mm", scale=alt.Scale(zero=False)),
    color=alt.Y("species")
).properties(
    width=600, height=400
).interactive()

st.write(chart)

st.markdown("This project was created by Student1 and Student2 for the [Interactive Data Science](https://dig.cmu.edu/ids2022) course at [Carnegie Mellon University](https://www.cmu.edu).")
