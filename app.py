import streamlit as st
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit_antd_components as sac

st.markdown(
    """
    <style>
        .block-container {
            max-width: 100% !important;
            padding: 10px 100px;
        }
        h1 {
            text-align: left;
            font-size: 2rem;
            color: #2B3674;
        }
        .ant-btn {
            width: 250px !important; /* Define largura fixa dos botões */
            height: 50px !important; /* Define altura fixa dos botões */
            display: inline-flex; /* Mantém o texto centralizado */
            justify-content: center;
            align-items: center;
            margin: 5px; /* Espaçamento entre os botões */
        }
        .ant-btn-group {
            display: flex;
            flex-wrap: wrap;
            justify-content: center;
        }
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
    """,
    unsafe_allow_html=True
)

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

st.title("Mortes atribuídas à poluição do ar no ano de 2014 ~ 2019")

col1, col2 = st.columns([1, 3])

with col1:
    btn = sac.buttons(
    items=["Total de Mortes por Continente", "Tendência de Mortes por Continente", "Causas das mortes ao longo dos anos", "Tendência de Mortes por Ano", "Total de Mortes por Causa"],
    index=0,
    format_func='title',
    align='center',
    direction='horizontal',
    radius='lg',
    return_index=False,
    color='#4682b4',
    size=15,
    )

with col2:
    if btn == "Total de Mortes por Continente":

        continente_selecionado = st.selectbox("Selecione um Continente", options=df['continente'].unique())

        colors = ['#EAEBF8' if continent != continente_selecionado else '#523DDA' for continent in df['continente']]

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
    elif btn == "Tendência de Mortes por Continente":
        continente_selecionado = st.selectbox(
            "Selecione um Continente para destacar",
            options=df['continente'].unique(),
            index=0
        )

        mortes_anuais_por_continente = df.groupby(['continente', 'ano'])['mortes'].sum().reset_index()
        mortes_anuais_por_continente['ano'] = mortes_anuais_por_continente['ano'].astype(int)
        mortes_anuais_por_continente['mortes_formatado'] = mortes_anuais_por_continente['mortes'].apply(formatar_numero)

        fig = go.Figure()

        for continente in mortes_anuais_por_continente['continente'].unique():
            dados_continente = mortes_anuais_por_continente[mortes_anuais_por_continente['continente'] == continente]
            color = "#3867D6" if continente == continente_selecionado else "#EAEBF8"
            line_dash = "solid" if continente == continente_selecionado else "dash"

            fig.add_trace(
                go.Scatter(
                    x=dados_continente['ano'],
                    y=dados_continente['mortes'],
                    mode='lines+markers+text',
                    name=continente,
                    line=dict(dash=line_dash, shape='spline', color=color),
                    marker=dict(size=10, color=color),
                    text=dados_continente['mortes_formatado'] if continente == continente_selecionado else None,
                    textposition="top center",
                    textfont=dict(size=12, color=color)
                )
            )

        fig.update_layout(
            title="Tendência de Mortes por Continente",
            xaxis=dict(title="Ano", showgrid=False),
            yaxis=dict(title="Mortes", showgrid=True, showticklabels=True),
            plot_bgcolor="white",
            font=dict(size=14, color="black"),
            legend=dict(title="Continente", orientation="h", yanchor="bottom", y=1.02, xanchor="center", x=0.5),
        )

        st.plotly_chart(fig, use_container_width=True)
    elif btn == "Causas das mortes ao longo dos anos":

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

    elif btn == "Tendência de Mortes por Ano":
        
        col1, col2 = st.columns([2, 2])

        
        mortes_anuais = df.groupby('ano')['mortes'].sum().reset_index()
        total_mortes = mortes_anuais['mortes'].sum()

        anos = ["Todos os anos"] + list(mortes_anuais['ano'].unique())
        
        with col2:
            ano_selecionado = st.selectbox("Selecione um Ano", options=anos, index=0)

        with col1:
            if ano_selecionado == "Todos os anos":
                st.markdown("<span style='font-size:16px; margin:0;'>Total de mortes:</span>", unsafe_allow_html=True)
                st.markdown(f"<h4 style='font-size:28px; margin:0;'>{total_mortes:,.0f}</h4>", unsafe_allow_html=True)
            else:
                mortes_ano = mortes_anuais[mortes_anuais['ano'] == ano_selecionado]['mortes'].values[0]
                st.markdown("<span style='font-size:16px; margin:0;'>Mortes selecionadas / Total:</span>", unsafe_allow_html=True)
                st.markdown(f"<h4 style='font-size:28px; margin:0;'>{mortes_ano:,.0f} / {total_mortes:,.0f}</h4>", unsafe_allow_html=True)

        fig = go.Figure()
        
        
        fig.add_trace(
            go.Scatter(
            x=mortes_anuais['ano'],
                y=mortes_anuais['mortes'],
                mode='lines',
                line=dict(dash='dash', shape='spline', color="#3867D6"),
            )
        )

        if ano_selecionado != "Todos os anos":
            ano_destaque = mortes_anuais[mortes_anuais['ano'] == ano_selecionado]
            fig.add_trace(
                go.Scatter(
                    x=ano_destaque['ano'],
                    y=ano_destaque['mortes'],
                    mode='markers+text',
                    marker=dict(size=13, color="#3867D6"),
                    text=[f"{ano_destaque['mortes'].values[0] / 1e6:.1f}M"],
                    textposition="top center",
                    textfont=dict(size=12, color="#3867D6"),
                    name=f"Destaque {ano_selecionado}"
                )
            )
        else:
            fig.add_trace(
                go.Scatter(
                    x=mortes_anuais['ano'],
                    y=mortes_anuais['mortes'],
                    mode='markers+text',
                    marker=dict(size=13, color="#3867D6"),
                    text=mortes_anuais['mortes'].apply(lambda x: f"{x / 1e6:.1f}M"),
                    textposition="top center",
                    textfont=dict(size=12, color="#3867D6"),
                    name="Tendência"
                )
            )
    
            
        
        fig.update_layout(
            xaxis=dict(showgrid=False),
            yaxis=dict(showgrid=True, showticklabels=False),
            legend_title=None,
            showlegend=False,
            plot_bgcolor="white"
        )

        st.plotly_chart(fig, use_container_width=True)

    elif btn == "Total de Mortes por Causa":
        col1, col2 = st.columns([2, 3])

        total_mortes = df[df['causa'] == 'ALL CAUSES']['mortes'].sum()
        with col2:
            causa_selec = st.selectbox("Selecione uma Causa", options=df['causa'].unique())
            mortes_causa_selec = df[df['causa'] == causa_selec]['mortes'].sum()

        with col1:
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
            xaxis=dict(
                tickangle=0,
                tickmode="array",
                tickvals=df['causa'],
                ticktext=[f"<br>".join(causa.split()) for causa in df['causa']],
            ),
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
