import streamlit as st
from google.oauth2 import service_account
from gsheetsdb import connect
from pydrive2.drive import GoogleDrive
from pydrive2.auth import GoogleAuth

def login_with_service_account():
    """
    Google Drive service with a service account.
    note: for the service account to work, you need to share the folder or
    files with the service account email.

    :return: google auth
    """
    # Define the settings dict to use a service account
    # We also can use all options available for the settings dict like
    # oauth_scope,save_credentials,etc.
    settings = {
        "client_config_backend": "service",
        "service_config": {
            "client_json_dict": st.secrets["gcp_service_account"],
        }
    }
    gauth = GoogleAuth(settings=settings)
    gauth.ServiceAuth()
    return gauth


gauth = login_with_service_account()
drive = GoogleDrive(gauth)

credentials = service_account.Credentials.from_service_account_info(
    st.secrets['gcp_service_account'],
    scopes=["https://www.googleapis.com/auth/spreadsheets"]
)

conn = connect(credentials=credentials)
cursor = conn.cursor()

st.cache(ttl=600)
def run_query(query):
    rows = conn.execute(query, headers=1)
    rows = rows.fetchall()
    return rows

file_list = drive.ListFile(
    {'q': "mimeType != 'application/vnd.google-apps.folder'"}
).GetList()

file_list = {file["title"]: file["id"] for file in file_list}

st.title('Hojas')

hoja = st.selectbox(
    'Hojas disponibles',
    file_list.keys(),
    index=0
)

base_url = st.secrets['base_url']
file_id = file_list[hoja]
url = base_url.format(file_id)
rows = run_query(f'SELECT * FROM "{url}"')

st.title('Partidas')

partidas = {row[1]: {'unidad': row[0], 'cantidad': row[2]} for row in rows}

partida = st.selectbox(
    'Partidas disponibles',
    partidas.keys(),
    index=0
)

unidad = st.text_input("Unidad", partidas[partida]['unidad'])
cantidad = st.text_input("Cantidad", partidas[partida]['cantidad'])
fecha = st.date_input("Fecha")
