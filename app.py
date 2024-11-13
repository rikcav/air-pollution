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

def formatar_numero(valor):
    if valor >= 1_000_000:
        return f"{valor / 1_000_000:.1f}M"
    elif valor >= 1_000:
        return f"{valor / 1_000:.1f}K"
    else:
        return str(valor)
    
traducao_causas = {
    "ALL CAUSES": "Todas as causas",
    "Trachea, bronchus, lung cancers": "Câncer",
    "Chronic obstructive pulmonary disease": "Obstrução da respiração",
    "Acute lower respiratory infections": "Infecções respiratórias",
    "Stroke": "AVC",
    "Ischaemic heart disease": "Doença cardíaca isquêmica"
}

st.title("Mortes por Continente")

option = st.selectbox("Selecione a Visualização", ["Total de Mortes por Continente", "Tendência de Mortes por Continente", "Causas das mortes ao longo dos anos", "Tendência de Mortes por Ano"])

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
elif option == "Tendência de Mortes por Continente":
    st.header("Tendência de Mortes por Continente")

    mortes_anuais_por_continente = df.groupby(['continente', 'ano'])['mortes'].sum().unstack().fillna(0).reset_index()

    mortes_anuais_por_continente = mortes_anuais_por_continente.melt(id_vars="continente", var_name="ano", value_name="mortes")

    mortes_anuais_por_continente['ano'] = mortes_anuais_por_continente['ano'].astype(int)

    mortes_anuais_por_continente['mortes'] = mortes_anuais_por_continente['mortes'].fillna(0)

    fig = px.line(mortes_anuais_por_continente, x="ano", y="mortes", color="continente", 
                title="Tendência de Mortes por Continente")
    st.plotly_chart(fig)
elif option == "Causas das mortes ao longo dos anos":
    st.header("Causas das mortes ao longo dos anos")

    col1, col2 = st.columns([2, 3])

    causas_traduzidas = ["Todas as causas"] + [traducao_causas.get(causa, causa) for causa in df['causa'].unique() if causa != "ALL CAUSES"]

    with col2:
        causa_traduzida_selecionada = st.selectbox("Selecione uma Causa", options=causas_traduzidas, index=0)

    causa_selecionada = {v: k for k, v in traducao_causas.items()}.get(causa_traduzida_selecionada, causa_traduzida_selecionada)

    dados_filtrados = df[df['causa'] == causa_selecionada].groupby(['ano'])['mortes'].sum().reset_index()
    total_mortes = df[df['causa'] == causa_selecionada]['mortes'].sum()

    with col1:
        st.markdown("<span style='font-size:16px; margin:0;'>Total de mortes:</span>", unsafe_allow_html=True)
        st.markdown(f"<h4 style='font-size:38px; margin:0;'>{total_mortes:,.0f}</h4>", unsafe_allow_html=True)

    dados_filtrados['mortes_formatado'] = dados_filtrados['mortes'].apply(formatar_numero)
    
    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=dados_filtrados['ano'],
            y=dados_filtrados['mortes'],
            mode='lines+markers+text',
            marker=dict(size=13),
            line=dict(dash='dash', shape='spline', color="#3867D6"),
            text=dados_filtrados['mortes_formatado'],
            textposition="top center",
            textfont=dict(size=13, color="#3867D6")
        )
    )
    
    fig.update_layout(legend_title_text='Causa')
    fig.update_yaxes(showticklabels=False, title_text='')

    st.plotly_chart(fig)

elif option == "Tendência de Mortes por Ano":
    mortes_anuais = df.groupby('ano')['mortes'].sum().reset_index()

    anos = list(mortes_anuais['ano'].unique())
    anos.insert(0, "Todos os anos")  

    ano_selecionado = st.selectbox("Anos", anos,label_visibility='hidden')

    if ano_selecionado == "Todos os anos":
    
        fig = px.line(mortes_anuais, x="ano", y="mortes", 
                  title="Tendência de Mortes por Ano", 
                  markers=True)
    else:
    
        fig = px.line(mortes_anuais, x="ano", y="mortes", 
                  title="Tendência de Mortes por Ano", 
                  markers=False)
    
    
        ano_destaque = mortes_anuais[mortes_anuais['ano'] == ano_selecionado]
        fig.add_scatter(x=ano_destaque['ano'], y=ano_destaque['mortes'], 
                    mode='markers', marker=dict(size=10, color='red'), 
                    name=f"Destaque {ano_selecionado}")

    
    st.plotly_chart(fig)