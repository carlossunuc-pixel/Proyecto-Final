#Dashboard Final — Acciones vs Criptomonedas
#Versión para GitHub (Deploy Ready)

#1. IMPORTACIONES
import pandas as pd
import numpy as np
import yfinance as yf
from dash import Dash, dcc, html, Input, Output, dash_table
import plotly.express as px
import dash_bootstrap_components as dbc


#2. DESCARGA DE ACCIONES DESDE YFINANCE

tickers = ["PG", "KO", "PEP", "CAT", "HON", "MMM"]

raw = yf.download(tickers, period="5y")
close_acc = raw["Close"].dropna(axis=1, how="all").copy()

df_acciones = close_acc.reset_index()
df_acciones_ret = close_acc.pct_change().dropna().reset_index()


#3. CARGA DE DATASET CSV DE CRIPTOMONEDAS

df_crypto = pd.read_csv("Crypto_historical_data.csv")

df_crypto["Date"] = pd.to_datetime(df_crypto["Date"])
df_crypto["Return"] = df_crypto.groupby("ticker")["Close"].pct_change()


#4. FUNCIÓN PARA CALCULAR INDICADORES

def calcular_indicadores(df):

    if "Return" not in df.columns:
        return {
            "Volatilidad": None,
            "VaR_95": None,
            "VaR_90": None,
            "Skewness": None,
            "Kurtosis": None,
            "Beta": None
        }

    returns = df["Return"].dropna()

    if len(returns) < 2:
        return {
            "Volatilidad": None,
            "VaR_95": None,
            "VaR_90": None,
            "Skewness": None,
            "Kurtosis": None,
            "Beta": None
        }

    indicadores = {
        "Volatilidad": returns.std(),
        "VaR_95": np.percentile(returns, 5),
        "VaR_90": np.percentile(returns, 10),
        "Skewness": returns.skew(),
        "Kurtosis": returns.kurtosis(),
        "Beta": None   # beta opcional
    }

    return indicadores


#5. TABLAS DE INDICADORES

#Crypto
tabla_crypto = (
    df_crypto.groupby("ticker")
    .apply(calcular_indicadores)
    .reset_index()
)

#Acciones en formato largo
df_acc_long = df_acciones_ret.melt(id_vars="Date", var_name="ticker", value_name="Return")

tabla_acciones = (
    df_acc_long.groupby("ticker")
    .apply(calcular_indicadores)
    .reset_index()
)


#6. DASHBOARD

app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
server = app.server     # ← IMPORTANTE para GitHub / Render

app.title = "Dashboard Final — Acciones y Criptomonedas"


app.layout = html.Div([

    html.H1("Dashboard Final — Acciones vs Criptomonedas", style={"textAlign": "center"}),

    # --------------------------------------------------------
    # ACCIONES
    # --------------------------------------------------------

    html.H2("Análisis de Acciones"),
    html.Label("Selecciona acciones:"),
    dcc.Dropdown(
        id="drop_acciones",
        options=[{"label": t, "value": t} for t in close_acc.columns],
        value=["PG"],
        multi=True
    ),

    dcc.Graph(id="grafico_acciones"),

    html.H3("Indicadores de Riesgo — Acciones"),
    dash_table.DataTable(
        id="tabla_acciones",
        columns=[{"name": c, "id": c} for c in tabla_acciones.columns],
        data=tabla_acciones.to_dict("records"),
        page_size=10,
        style_table={"overflowX": "auto"}
    ),

    html.Hr(),

    # --------------------------------------------------------
    # CRIPTOMONEDAS
    # --------------------------------------------------------

    html.H2("Análisis de Criptomonedas"),
    html.Label("Selecciona criptomonedas:"),
    dcc.Dropdown(
        id="drop_crypto",
        options=[{"label": t, "value": t} for t in df_crypto["ticker"].unique()],
        value=["BTC-USD"],
        multi=True
    ),

    dcc.Graph(id="grafico_crypto"),

    html.H3("Indicadores de Riesgo — Criptomonedas"),
    dash_table.DataTable(
        id="tabla_crypto",
        columns=[{"name": c, "id": c} for c in tabla_crypto.columns],
        data=tabla_crypto.to_dict("records"),
        page_size=10,
        style_table={"overflowX": "auto"}
    ),
])


#7. CALLBACKS

@app.callback(
    Output("grafico_acciones", "figure"),
    Input("drop_acciones", "value")
)
def actualizar_acciones(tickers_sel):
    fig = px.line(df_acciones, x="Date", y=tickers_sel, title="Precios de Cierre — Acciones")
    fig.update_layout(title_x=0.5)
    return fig


@app.callback(
    Output("grafico_crypto", "figure"),
    Input("drop_crypto", "value")
)
def actualizar_crypto(crypto_sel):
    df = df_crypto[df_crypto["ticker"].isin(crypto_sel)]
    fig = px.line(df, x="Date", y="Close", color="ticker", title="Precios de Cierre — Criptomonedas")
    fig.update_layout(title_x=0.5)
    return fig


#8. EJECUTAR APP

if __name__ == "__main__":
    app.run_server(debug=False, host="0.0.0.0", port=10000)
