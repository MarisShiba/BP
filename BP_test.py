import google_auth_httplib2
import httplib2
import pandas as pd
import streamlit as st
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import HttpRequest

st.title('Daily BP Measurements')
#
# # Create a connection object.
# credentials = service_account.Credentials.from_service_account_info(
#     dict(st.secrets["gcp_service_account"]),
#     scopes=[
#         "https://www.googleapis.com/auth/spreadsheets",
#     ],
# )
#
# conn = connect(credentials=credentials)
#


SCOPE = "https://www.googleapis.com/auth/spreadsheets"
SPREADSHEET_ID = "1E337krN2CW7qzDCz6exUbT1KbY4Treol6o1UaY3yUk8"
# SHEET_NAME = "Test"

@st.experimental_singleton()
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
    df = df[-10:]
    return df


def add_row_to_gsheet(gsheet_connector, SHEET_NAME, row) -> None:
    gsheet_connector.values().append(
        spreadsheetId=SPREADSHEET_ID,
        range=f"{SHEET_NAME}!A:E",
        body=dict(values=row),
        valueInputOption="USER_ENTERED",
    ).execute()

gsheet_connector = connect_to_gsheet()

form = st.form(key="annotation")

with form:
    date = st.date_input("Date:")
    cols = st.columns((1, 1))
    time = cols[0].time_input("Time:")
    pulse = cols[1].text_input("Pulse:")

    cols = st.columns(2)
    sys = cols[0].text_input("SYS:")
    dia = cols[1].text_input("DIA:")

    codeword = st.text_area("Code word:")
    submitted = st.form_submit_button(label="Submit")


if submitted and codeword=='Aayush Marishi':
    add_row_to_gsheet(
        gsheet_connector,
        'Aayush',
        [[str(date), str(time)[:5], sys, dia, pulse]],
    )
    st.success("Thanks! Your data was recorded.")
elif submitted and codeword=='Jamie Liang':
    add_row_to_gsheet(
        gsheet_connector,
        'Jamie',
        [[str(date), str(time)[:5], sys, dia, pulse]],
    )
    st.success("Thanks! Your data was recorded.")
else:
    st.error("Wrong code name.")

expander = st.expander("See all records of A")
with expander:
    st.dataframe(get_data(gsheet_connector, 'Aayush'))

expander2 = st.expander("See all records of B")
with expander2:
    st.dataframe(get_data(gsheet_connector, 'Jamie'))
