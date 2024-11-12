import streamlit as st
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go


df = pd.read_csv('data.csv')

df = df.drop(['ValueType', 'SpatialDimValueCode', 'FactValueUoM', 
              'FactValueNumericLowPrefix', 'FactValueNumericLow', 
              'FactValueNumericHighPrefix', 'FactValueNumericHigh',
              'Dim3ValueCode', 'DataSourceDimValueCode', 'DataSource',
              'FactValueNumericPrefix', 'FactValueTranslationID', 'FactComments',
              'Dim3 type', 'Dim3', 'IndicatorCode', 'Indicator',
              'Location type', 'Period type', 'Dim1 type', 'Dim2 type',
              'Language', 'DateModified', 'Value', 'IsLatestYear'], axis=1)
df = df.drop(df[df['Period'] < 2014].index)
df = df.drop(df[df['Dim1ValueCode'].isin(['SEX_MLE', 'SEX_FMLE'])].index)
df = df.drop(['Dim1', 'Dim1ValueCode'], axis=1)
df['FactValueNumeric'] = df['FactValueNumeric'].round().astype(int)

df.rename(columns={
    'ParentLocationCode': 'continente_code',
    'ParentLocation': 'continente',
    'Location': 'pais',
    'Period': 'ano',
    'Dim2': 'causa',
    'Dim2ValueCode': 'causa_code',
    'FactValueNumeric': 'mortes'
}, inplace=True)

renomear_continentes = {
    'Americas': 'Américas',
    'Africa': 'África',
    'Western Pacific': 'Pacífico Ocidental',
    'Europe': 'Europa',
    'South-East Asia': 'Sudeste Asiático',
    'Eastern Mediterranean': 'Mediterrâneo Oriental'
}

df['continente'] = df['continente'].replace(renomear_continentes)

st.title("Mortes por Continente")

option = st.selectbox("Selecione a Visualização", ["Total de Mortes por Continente", "Tendência de Mortes por Continente"])

if option == "Total de Mortes por Continente":
    st.header("Total de Mortes por Continente")

    continente_selecionado = st.selectbox("Selecione um Continente", options=df['continente'].unique())

    colors = ['#EAEBF8' if continent != continente_selecionado else '#6256F1' for continent in df['continente']]

    fig = go.Figure(data=[
        go.Bar(
            x=df['continente'],
            y=df['mortes'],
            marker_color=colors
        )
    ])

    fig.update_layout(
        title="Total de Mortes por Continente",
        xaxis_title="Continente",
        yaxis_title="Mortes"
    )

    st.plotly_chart(fig)
else:
    st.header("Tendência de Mortes por Continente")

    mortes_anuais_por_continente = df.groupby(['continente', 'ano'])['mortes'].sum().unstack().fillna(0).reset_index()

    mortes_anuais_por_continente = mortes_anuais_por_continente.melt(id_vars="continente", var_name="ano", value_name="mortes")

    mortes_anuais_por_continente['ano'] = mortes_anuais_por_continente['ano'].astype(int)

    mortes_anuais_por_continente['mortes'] = mortes_anuais_por_continente['mortes'].fillna(0)

    fig = px.line(mortes_anuais_por_continente, x="ano", y="mortes", color="continente", 
                title="Tendência de Mortes por Continente")
    st.plotly_chart(fig)