import google_auth_httplib2
import httplib2
import pandas as pd
import streamlit as st
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import HttpRequest

st.set_page_config(
    page_title="Daily BP Measurements Data Entry",
    page_icon="✍️"
)



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

# @st.experimental_singleton()
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

def clear_form():
    st.session_state["code"] = ""
    st.session_state["time"] = ""
    st.session_state["pulse"] = 0
    st.session_state["sys"] = 0
    st.session_state["dia"] = 0

gsheet_connector = connect_to_gsheet()

clear = st.button(label='Clear fields', on_click=clear_form)
form = st.form(key="annotation")

with form:
    date = st.date_input("Date:", key="date")
    cols = st.columns((1, 1))
    time = cols[0].text_input("Time (24h):", key='time')
    pulse = cols[1].number_input("Pulse:", key='pulse', min_value=0)

    cols = st.columns(2)
    sys = cols[0].number_input("SYS:", key='sys', min_value=0)
    dia = cols[1].number_input("DIA:", key='dia', min_value=0)

    codeword = st.text_area("Code word:", key='code')
    submitted = st.form_submit_button(label="Submit")


if submitted and codeword=='Aayush Marishi':
    if len(time)==5:
        if time[2]==':':
            add_row_to_gsheet(
                gsheet_connector,
                'Aayush',
                [[date.strftime("%d.%m.%Y"), str(time)[:5], sys, dia, pulse]],
            )
            st.success("Thanks! Your data was recorded.")
        else:
            st.error("Wrong time format.")
    else:
        st.error("Wrong time format.")
elif submitted and codeword=='Jamie Liang':
    if len(time)==5:
        if time[2]==':':
            add_row_to_gsheet(
                gsheet_connector,
                'Jamie',
                [[date.strftime("%d.%m.%Y"), str(time)[:5], sys, dia, pulse]],
            )
            st.success("Thanks! Your data was recorded.")
        else:
            st.error("Wrong time format.")
    else:
        st.error("Wrong time format.")
elif submitted:
    st.error("Wrong code name.")

expander = st.expander("See all records of A")
with expander:
    st.dataframe(get_data(gsheet_connector, 'Aayush'))

expander2 = st.expander("See all records of B")
with expander2:
    st.dataframe(get_data(gsheet_connector, 'Jamie'))
