import pandas as pd
import base64
import io
from dash import html
def parse_data(contents, filename):
    content_type, content_string = contents.split(',')
    decoded = base64.b64decode(content_string)
    try:
        if 'csv' in filename:
            df = pd.read_csv(io.StringIO(decoded.decode('utf-8')))
        elif 'xls' in filename or 'xlsx' in filename:
            df = pd.read_excel(io.BytesIO(decoded))
        else:
            return html.Div(["Le format du fichier n'est pas supporté."])
        return df
    except Exception as e:
        return html.Div([f"Erreur lors du traitement du fichier : {str(e)}"])


