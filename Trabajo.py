import streamlit as st
import pandas as pd
from sodapy import Socrata
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
from streamlit_option_menu import option_menu
import streamlit.components.v1 as html  
from  PIL import Image


def get_data ():
    token = "WxYMCDvVjMlkgbMZPQuhxYjl4"
    client = Socrata("healthdata.gov", token)
    gety = client.get("g62h-syeh", limit=50000)
    return gety

def dataFrame():
    df = pd.read_csv("./COVID-19_Reported_Patient_Impact_and_Hospital_Capacity_by_State_Timeseries.csv")
    df.sort_values("date", inplace=True)
    df = df.reset_index().drop(columns="index")
    df.fillna(0)
    df["date"] = pd.to_datetime(df["date"], format="%Y-%m-%d")
    for i in df.columns:
        if i == "state" or i == "date":
            continue
        else:
            df[i] = pd.to_numeric(df[i])
    return df


df_covid = dataFrame()

imagen = Image.open("./imagen.jpg")

with st.sidebar:
    choose = option_menu("Galeria", ["Inicio", "Primer Analisis", "Top 5 Mayor ocupacion", "New York", "Camas UCI","Pacientes Pediatricos","Camas UCI confirmados","Muertes 2021","Peor Mes","Suministros"],
                         icons=['house', 'map', 'clipboard-data', 'geo-fill','file-medical', "file-medical", "file-medical", "heart", "file-medical", "activity"],
                         menu_icon="app-indicator", default_index=0,
                         styles={
        "container": {"padding": "8!important", "background-color": "#202022"},
        "icon": {"color": "#00747C", "font-size": "15px"}, 
        "nav-link": {"font-size": "18px", "text-align": "down", "margin":"0px", "--hover-color": "#363333"},
        "nav-link-selected": {"background-color": "#579DFF"},
    }
    )


if choose == "Inicio":
    st.markdown(""" <style> .font {
    font-size:35px ; font-family: 'Cooper Black'; color: #00747C;} 
    </style> """, unsafe_allow_html=True)
    st.markdown('<p class="font">COVID-19 Estados Unidos</p>', unsafe_allow_html=True)   
    st.write('En el siguiente informe se presentan algunos datos de relevancia en Estados Unidos durante la pandemia de COVID-19')     

    st.image(imagen)


if choose == "Primer Analisis":
    st.markdown("""
    # Primer Analisis

    ## 
    En esta seccion se precentan las primeras observaciones del DataSet. En primer lugar se encuentra la tabla que se utilizo para
    la presentación y luego unas metricas que ayudan a entender la informacion que nos brinda. """, unsafe_allow_html=False)
    #Tabla
    st.header("Datos")
    st.write(df_covid)

    #Rango de fechas
    set_col, disp_col = st.columns(2)
    ini = set_col.selectbox("Elegir fecha inicial", options=df_covid["date"].iloc[0:-1].unique())
    fin = disp_col.selectbox("Elegir fecha final", options=df_covid["date"].iloc[::-1].unique())

    #Mapa
    st.header("Mapa de calor")
    st.write("Este mapa muestra la cantidad de hospitalizados por covid en los distintos estados de USA")
    mapa = df_covid[["date", "state", "total_adult_patients_hospitalized_confirmed_covid"]]
    mapa = mapa[mapa["date"].between(ini, fin)]
    mapa = mapa.groupby("state", as_index=False).sum().sort_values("total_adult_patients_hospitalized_confirmed_covid", ascending=False)
    fig = px.choropleth(data_frame=mapa, 
                        locations=mapa["state"], 
                        locationmode="USA-states", scope="usa", 
                        color=mapa["total_adult_patients_hospitalized_confirmed_covid"], 
                        labels={"location":"Estado", "color":"Muertes"}, 
                        color_continuous_scale="ylorrd", color_discrete_map="black")
    st.plotly_chart(fig)

    #Uso de camas UCI
    st.header("Uso de camas UCI")
    ucis = df_covid[["date","adult_icu_bed_utilization_numerator"]]
    ucis = ucis[ucis["date"].between(ini, fin)]
    fig = plt.figure()
    sns.lineplot(data=ucis, x="date", y="adult_icu_bed_utilization_numerator", ci=None)
    st.pyplot(fig)

    #Cantidad de camas 
    st.header("Cantidad de camas ocupadas por COVID-19")
    camas = df_covid[["date", "state", "inpatient_beds_used_covid"]]
    camas = camas[camas["date"].between(ini, fin)].groupby("state").sum().sort_values("inpatient_beds_used_covid", ascending=False)
    fig = plt.figure(figsize=(18,12))
    sns.barplot(data=camas, x=camas .index, y="inpatient_beds_used_covid")
    st.pyplot(fig)

    #Ocupacion Hospitalaria
    st.header("Ocupacion Hospilaria")
    ocupacion = df_covid[["date", "state", "total_adult_patients_hospitalized_confirmed_covid", "total_pediatric_patients_hospitalized_confirmed_covid"]]
    ocupacion["Total"] = ocupacion["total_adult_patients_hospitalized_confirmed_covid"] + ocupacion["total_pediatric_patients_hospitalized_confirmed_covid"]
    ocupacion = ocupacion[ocupacion["date"].between(ini, fin)]
    ocupacion = ocupacion.groupby(by="state").mean().sort_values("Total", ascending=False)
    fig = plt.figure(figsize=(18,12))
    sns.barplot(data=ocupacion, x=ocupacion.index, y="Total")
    st.pyplot(fig)


if choose == "New York":
    st.header("Casos New York")
    st.write("""En el siguiente grafico podemos ver la cantidad de camas que se utilizaron para covid durante la 
            cuarentena del estado de New York. Esta comenzo el dia 22-03-2020 y finalizo el 13-06-2020. En el grafico se ve como 
            los primeros dias de la cuarentena fueron aumentando los casos de hospitalizacion. Pero al correr de los dias, los 
            casos se fueron reduciendo.""")
    new = df_covid[["state",
                    "date",
                    "inpatient_bed_covid_utilization_numerator"]]
    new = new[new["date"].between("2020-03-22", "2020-06-13")]
    new = new[new["state"] == "NY"]
    fig = plt.figure()
    sns.lineplot(data=new, x="date", y="inpatient_bed_covid_utilization_numerator",  ci=None)
    st.pyplot(fig)


if choose == "Pacientes Pediatricos":
    st.header("Pacientes Pediatricos")
    st.write("Como podemos ver en el grafico, el estado que mas casos de COVID-19 en pacientes pediatricos es Texas. Lo sigue California, Florida y Pensilvania​ ")
    ped = df_covid[df_covid["date"].between("2020-01-01", "2020-12-31")]
    ped = ped[["state","date", "total_pediatric_patients_hospitalized_confirmed_covid"]]
    ped = ped.groupby(by="state").sum().sort_values(by="total_pediatric_patients_hospitalized_confirmed_covid", ascending=False)
    fig = plt.figure(figsize=(18,12))
    sns.barplot(data=ped, x=ped.index, y="total_pediatric_patients_hospitalized_confirmed_covid" )
    st.pyplot(fig)
    st.table(ped.head())



if choose == "Camas UCI":
    st.header("Top 5 camas UCI utilizadas por estado 2020")
    st.write("""En la primera tabla se tomo el dia con mayor numero de camas UCI utilizadas. Podemos ver que en el estado de Iowa se
            utilizaron 41,473 camas de 709 camas en total. Revisando los datos descubri que se debe a un error al cargar la informacion.""")
    uci = df_covid[df_covid["date"].between("2020-01-01", "2020-12-31")]
    uci = uci[["date","state","adult_icu_bed_utilization_numerator","adult_icu_bed_utilization"]]
    uci["Total De Camas"] = (1 * uci["adult_icu_bed_utilization_numerator"]) / uci["adult_icu_bed_utilization"]
    uci1 = uci.groupby(by=["state","date"]).max().sort_values(by="adult_icu_bed_utilization_numerator", ascending=False).head()
    st.table(uci[(uci["state"] == "IA") & (uci["date"].between("2020-08-14", "2020-08-18"))])
    st.table(uci1)
    st.write("""Debido al error encontrado decidi obtener el promedio de la cantidad de camas UCI utilizadas y el resultado fue
            el siguiente""")
    uci2 = uci.groupby(by="state").mean().sort_values(by="adult_icu_bed_utilization_numerator", ascending=False).head()
    st.table(uci2)
    fig = plt.figure()
    sns.barplot(data=uci2, x=uci2.index, y="adult_icu_bed_utilization_numerator", label=uci2["adult_icu_bed_utilization_numerator"].values)
    st.pyplot(fig)



if choose == "Camas UCI confirmados":
    st.header("Porcentaje camas UCI COVID-19 positivo")
    st.write("""El siguiente grafico nos muestra el porcentaje de camas UCI utilizadas por pacientes COVID-19 positivo. Como podemos ver
            no es muy alto el porcentaje en los estados. Esto se debe a que no se aplico ningun filtro en la columna "date".""")

    uci_COVID = df_covid[["state",
                            "date",
                            "adult_icu_bed_covid_utilization",
                            "total_staffed_adult_icu_beds"]]
    uci_COVID["Total De Camas COVID"] = round((uci_COVID["adult_icu_bed_covid_utilization"] * uci_COVID["total_staffed_adult_icu_beds"]) / 1, 0)
    uci_COVID = uci_COVID.groupby("state").mean()
    uci_COVID["Porcentaje"] = (uci_COVID["Total De Camas COVID"] / uci_COVID["total_staffed_adult_icu_beds"]) * 100 
    uci_COVID.sort_values("Porcentaje", ascending=False, inplace=True)
    
    fig = plt.figure(figsize=(18,12))
    sns.barplot(data=uci_COVID, x=uci_COVID.index, y="Porcentaje")
    st.pyplot(fig)

    st.table(uci_COVID.head())


if choose == "Muertes 2021":
    st.header("Muertes en 2021 y falta de personal")
    st.write("En la primera tabla podemos ver la cantidad de muertes que hubo en el año 2021 a causa de COVID-19")

    personal = df_covid[["state",
                        "date",
                        "critical_staffing_shortage_today_yes",
                        "deaths_covid"]]
    personal = personal[personal["date"].between("2021-01-01", "2021-12-31")]
    bajas = personal.groupby("state").sum()[["deaths_covid"]]

    st.table(bajas.sort_values("deaths_covid", ascending=False).head())

    st.write("En la segunda tabla se muestra la cantidad de hospitales que informaron escacez de personal medico en el dia")

    st.table(personal.head())
    fig = plt.figure()
    sns.lineplot(data=personal, x="date", y="deaths_covid", ci=None, label="Muertes")
    sns.lineplot(data=personal, x="date", y="critical_staffing_shortage_today_yes", ci=None, label="Falta de personal")
    plt.legend()
    st.pyplot(fig)



if choose == "Top 5 Mayor ocupacion":
    st.header("Top 5")
    st.write("Tomando como referencia los primeros seis meses del 2020 se calculo la cantidad de pacientes con COVID-19")
    ocup = df_covid[["state",
                    "date",
                    "hospital_onset_covid",
                    "total_adult_patients_hospitalized_confirmed_covid",
                    "total_pediatric_patients_hospitalized_confirmed_covid"]]

    ocup = ocup[ocup["date"].between("2020-01-01", "2020-06-30")]
    ocup["Mes"] = ocup["date"].dt.month_name()
    tot = ocup.groupby("state").sum()
    tot["Total"] = tot["total_adult_patients_hospitalized_confirmed_covid"] + tot["total_pediatric_patients_hospitalized_confirmed_covid"]
    tot = tot.sort_values("Total", ascending=False).head()
    mes = ocup.groupby("Mes").sum().sort_values("hospital_onset_covid", ascending=False).head()
    
    st.table(tot)
    
    fig = plt.figure()
    sns.barplot(data=tot, x=tot.index, y="Total")
    st.pyplot(fig)

    st.table(mes)
    fig2 = plt.figure()
    sns.barplot(data=mes, x=mes.index, y="hospital_onset_covid")
    st.pyplot(fig2)


if choose == "Peor Mes":
    st.header("Peor me de la pandemia")
    st.write("Teniendo en cuenta la cantidad de muertos, la falta de personal medico y la falta de suministros el peor mes es enero")

    peor = df_covid[["state",
                        "date",
                        "critical_staffing_shortage_today_yes",
                        "deaths_covid",
                        "on_hand_supply_therapeutic_c_bamlanivimab_etesevimab_courses"]]
    peor["Mes"] = peor["date"].dt.month_name()
    peor = peor.groupby("Mes").sum()

    st.table(peor)

    fig,ax=plt.subplots(3,1) 
    fig.set_size_inches(15,19) 
    ax[0].set_title("Muertes") #Titulo del grafico
    sns.barplot(ax=ax[0],data=peor, x=peor.index, y="deaths_covid", ci=None)
    ax[1].set_title("Suministros")
    sns.barplot(ax=ax[1],data=peor, x=peor.index, y="on_hand_supply_therapeutic_c_bamlanivimab_etesevimab_courses", ci=None)
    ax[2].set_title("Personal")
    sns.barplot(ax=ax[2],data=peor, x=peor.index, y="critical_staffing_shortage_today_yes", ci=None)
    st.pyplot(fig)


if choose == "Suministros":
    st.header("Recursos Hospitalarios")
    st.write("""Tomando como punto de partida los suministros, podemos ver que cuando hubo mayor cantidad de suministros las muertes por COVID-19 bajaron
                y cuando mas faltaban subieron.
                Ademas, si tomamos en cuenta las muertes por COVID-19 antes que aumentaran los recursos hospitalarios, vemos que las fallecimientos eran incontrolables. 
                """)
    sumi = df_covid[["state",
                    "date",
                    "adult_icu_bed_covid_utilization_numerator",
                    "on_hand_supply_therapeutic_a_casirivimab_imdevimab_courses",
                    "on_hand_supply_therapeutic_b_bamlanivimab_courses",
                    "on_hand_supply_therapeutic_c_bamlanivimab_etesevimab_courses",
                    "deaths_covid"]]

    sumi["Suministro_A_utilizados"] = round(sumi["on_hand_supply_therapeutic_a_casirivimab_imdevimab_courses"] / sumi["adult_icu_bed_covid_utilization_numerator"],0)
    sumi["Suministro_B_utilizados"] = round(sumi["on_hand_supply_therapeutic_b_bamlanivimab_courses"] / sumi["adult_icu_bed_covid_utilization_numerator"],0)
    sumi["Suministro_C_utilizados"] = round(sumi["on_hand_supply_therapeutic_c_bamlanivimab_etesevimab_courses"] / sumi["adult_icu_bed_covid_utilization_numerator"],0)


    fig = plt.figure(figsize=(20,12))
    sns.lineplot(data=sumi, x="date", y="Suministro_A_utilizados", label="Suministro A", ci=None)
    sns.lineplot(data=sumi, x="date", y="Suministro_B_utilizados", label="Suministro B", ci=None)
    sns.lineplot(data=sumi, x="date", y="Suministro_C_utilizados", label="Suministro C", ci=None)
    sns.lineplot(data=sumi, x="date", y="deaths_covid", label="M", ci=None)
    plt.legend()
    st.pyplot(fig)

    st.write("""En el siguiente grafico podemos ver cuales fueron los estados que menos recursos usaron. Podemos concluir que, cuanto mas faltan recursos las muertes aumentan.
            Por ello, mi recomendacion es que, en general, se apliquen medidas sanitarias preventivas y no esperar a que ocurra una catastrofe
            para tomar conciencia""")
    fig,ax=plt.subplots(4,1) 
    fig.set_size_inches(15,19) 
    ax[0].set_title("Suministros A") #Titulo del grafico
    sns.barplot(ax=ax[0],data=sumi, x="state", y="Suministro_A_utilizados", ci=None)
    ax[1].set_title("Suministros B")
    sns.barplot(ax=ax[1],data=sumi, x="state", y="Suministro_B_utilizados", ci=None)
    ax[2].set_title("Suministros C")
    sns.barplot(ax=ax[2],data=sumi, x="state", y="Suministro_C_utilizados", ci=None)
    ax[3].set_title("Muertes")
    sns.barplot(ax=ax[3],data=sumi, x="state", y="deaths_covid", ci=None)
    st.pyplot(fig)

    
