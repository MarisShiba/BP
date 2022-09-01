import google_auth_httplib2
import httplib2
import pandas as pd
import streamlit as st
import plotly.express as px
from plotly.subplots import make_subplots
import plotly.graph_objects as go
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import HttpRequest

SCOPE = "https://www.googleapis.com/auth/spreadsheets"
SPREADSHEET_ID = "1E337krN2CW7qzDCz6exUbT1KbY4Treol6o1UaY3yUk8"

st.set_page_config(page_title="Plotting BP", page_icon="📈")

st.markdown("# Plotting BP History")

def connect_to_gsheet():
    # Create a connection object.
    credentials = service_account.Credentials.from_service_account_info(
        st.secrets["gcp_service_account"],
        scopes=[SCOPE],
    )

    # Create a new Http() object for every request
    def build_request(http, *args, **kwargs):
        new_http = google_auth_httplib2.AuthorizedHttp(
            credentials, http=httplib2.Http()
        )
        return HttpRequest(new_http, *args, **kwargs)

    authorized_http = google_auth_httplib2.AuthorizedHttp(
        credentials, http=httplib2.Http()
    )
    service = build(
        "sheets",
        "v4",
        requestBuilder=build_request,
        http=authorized_http,
    )
    gsheet_connector = service.spreadsheets()
    return gsheet_connector


def get_data(gsheet_connector, SHEET_NAME) -> pd.DataFrame:
    values = (
        gsheet_connector.values()
        .get(
            spreadsheetId=SPREADSHEET_ID,
            range=f"{SHEET_NAME}!A:E",
        )
        .execute()
    )

    df = pd.DataFrame(values["values"])
    df.columns = df.iloc[0]
    df = df[1:]
    return df

gsheet_connector = connect_to_gsheet()

expander = st.expander("Records of A")
with expander:
    df = get_data(gsheet_connector, 'Aayush')

    df['Date'] = pd.to_datetime(df['Date'], dayfirst=True)
    df = df.sort_values("Date", ascending=True)
    df['SYS'] = pd.to_numeric(df['SYS'])
    df['DIA'] = pd.to_numeric(df['DIA'])
    df['Pulse'] = pd.to_numeric(df['Pulse'])

    sys_mean = df['SYS'].mean()
    dia_mean = df['DIA'].mean()
    pulse_mean = df['Pulse'].mean()

    fig = make_subplots(rows=3, cols=1,
                        shared_xaxes=True,
                        vertical_spacing=0.07,
                        subplot_titles=("SYS", "DIA", "Pulse"))

    fig.add_trace(go.Scatter(x=df['Date'], y=df['SYS'], name='SYS'),
                  row=1, col=1)

    fig.add_trace(go.Scatter(x=df['Date'], y=df['DIA'], name='DIA'),
                  row=2, col=1)

    fig.add_trace(go.Scatter(x=df['Date'], y=df['Pulse'], name='Pulse'),
                  row=3, col=1)

    fig.add_annotation(xref="paper", yref="paper", x=0.9, y=1,
                       text=f"Avg: {round(sys_mean, 1)}", showarrow=False)

    fig.add_annotation(xref="paper", yref="paper", x=0.9, y=0.6,
                       text=f"Avg: {round(dia_mean, 1)}", showarrow=False)

    fig.add_annotation(xref="paper", yref="paper", x=0.9, y=0.22,
                       text=f"Avg: {round(pulse_mean, 1)}", showarrow=False)

    fig.update_layout({'plot_bgcolor': 'rgba(0, 0, 0, 0)',
                       'paper_bgcolor': 'rgba(0, 0, 0, 0)'}, height=600, width=680, showlegend=False, )

    fig.update_xaxes(showgrid=True, gridwidth=1, gridcolor='LightGrey')
    fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor='LightGrey')
    st.plotly_chart(fig)

expander = st.expander("Records of B")
with expander:
    df = get_data(gsheet_connector, 'Jamie')

    df['Date'] = pd.to_datetime(df['Date'], dayfirst=True)
    df = df.sort_values("Date", ascending=True)
    df['SYS'] = pd.to_numeric(df['SYS'])
    df['DIA'] = pd.to_numeric(df['DIA'])
    df['Pulse'] = pd.to_numeric(df['Pulse'])

    sys_mean = df['SYS'].mean()
    dia_mean = df['DIA'].mean()
    pulse_mean = df['Pulse'].mean()

    fig = make_subplots(rows=3, cols=1,
                        shared_xaxes=True,
                        vertical_spacing=0.07,
                        subplot_titles=("SYS", "DIA", "Pulse"))

    fig.add_trace(go.Scatter(x=df['Date'], y=df['SYS'], name='SYS'),
                  row=1, col=1)

    fig.add_trace(go.Scatter(x=df['Date'], y=df['DIA'], name='DIA'),
                  row=2, col=1)

    fig.add_trace(go.Scatter(x=df['Date'], y=df['Pulse'], name='Pulse'),
                  row=3, col=1)

    fig.add_annotation(xref="paper", yref="paper", x=0.9, y=1,
                       text=f"Avg: {round(sys_mean, 1)}", showarrow=False)

    fig.add_annotation(xref="paper", yref="paper", x=0.9, y=0.6,
                       text=f"Avg: {round(dia_mean, 1)}", showarrow=False)

    fig.add_annotation(xref="paper", yref="paper", x=0.9, y=0.22,
                       text=f"Avg: {round(pulse_mean, 1)}", showarrow=False)

    fig.update_layout({'plot_bgcolor': 'rgba(0, 0, 0, 0)',
                       'paper_bgcolor': 'rgba(0, 0, 0, 0)'}, height=600, width=680, showlegend=False, )

    fig.update_xaxes(showgrid=True, gridwidth=1, gridcolor='LightGrey')
    fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor='LightGrey')
    st.plotly_chart(fig)

# Streamlit widgets automatically run the script from top to bottom. Since
# this button is not connected to any other logic, it just causes a plain
# rerun.
st.button("Re-run")
