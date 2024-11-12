import streamlit as st
import pandas as pd
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

renomear_causas = {
    'Trachea, bronchus, lung cancers': 'Câncer',
    'Chronic obstructive pulmonary disease': 'Obstrução da respiração',
    'Ischaemic heart disease': 'Doença cardíaca isquêmica',
    'Stroke': 'AVC',
    'Acute lower respiratory infections': 'Infecções respiratórias',
    'ALL CAUSES': 'Todas as causas'
}

df['causa'] = df['causa'].replace(renomear_causas)

st.markdown("""
    <style>
        .layout {{
            display: flex;
            align-items: center;
            justify-content: space-between;
        }}
        .title-text {
            font-size: 20px;
            color: #9B9DBF;
            text-align: left;
        }
        .total-mortes {
            font-size: 30px;
            font-weight: bold;
            color: #223254;
            text-align: left;
        }
        .highlight {
            color: #3867D6;
        }
    </style>
""", unsafe_allow_html=True)

total_mortes = df[df['causa'] == 'Todas as causas']['mortes'].sum()
causa_selec = st.selectbox("Selecione uma Causa", options=df['causa'].unique())
mortes_causa_selec = df[df['causa'] == causa_selec]['mortes'].sum()

st.markdown("<div class='title-text'>Total de mortes</div>", unsafe_allow_html=True)
st.markdown(
    f"<div class='total-mortes'><span class='highlight'>{mortes_causa_selec:,}</span>/{total_mortes:,}</div>",
    unsafe_allow_html=True
)


colors = ['#EAEBF8' if causa != causa_selec else '#3867D6' for causa in df['causa']]

fig = go.Figure(data=[
        go.Bar(
            x=df['causa'],
            y=df['mortes'],
            marker_color=colors,
            textposition="outside",
        )
    ])

fig.update_layout(
    title="",
    xaxis_title="",
    yaxis_title="",
    font=dict(size=14, color="black"),
    plot_bgcolor="rgba(0, 0, 0, 0)",
    showlegend=False,
    margin=dict(l=20, r=20, t=20, b=20),
)

fig.add_shape(
    type="line",
    x0=-0.5, x1=5.5,
    y0=mortes_causa_selec, y1=mortes_causa_selec,
    line=dict(color="#3867D6", width=2, dash="dash")
)

fig.add_annotation(
    x=5.5,
    y=mortes_causa_selec,
    text=f"{mortes_causa_selec:,}",
    showarrow=False,
    font=dict(color="#3867D6", size=12),
    align="right",
)

st.plotly_chart(fig, use_container_width=True)
