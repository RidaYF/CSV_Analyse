import base64
import io
import os
import tempfile
import re


import dash as ds
from dash import dcc, html, Input, Output, State,ctx,no_update
from dash import dash_table
import dash_bootstrap_components as dbc
from dash.exceptions import PreventUpdate
import plotly.express as px
import plotly.graph_objs as go
import plotly.io as pio
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import pandas as pd
from flask_caching import Cache


import firebase_configuration as fc
import graph_types
from utils import *


app = ds.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP], suppress_callback_exceptions=True)


# Global CSS to ensure no unwanted margins or paddings
app.index_string = """
<!DOCTYPE html>
<html>
<head>
    <title>Plot Graph Maker</title>
    <style>
        html, body {
            margin: 0;
            padding: 0;
            height: 100%;
            width: 100%;
        }
    </style>
</head>
<body>
    {%app_entry%}
    <footer>
        {%config%}
        {%scripts%}
        {%renderer%}
    </footer>
</body>
</html>
"""

app = ds.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])



"""********************************************************* LOGIN/SIGNUP *********************************************************"""


# login page layout : 
login_page = html.Div(	
    className="login-page",
    style={
        "fontFamily": "Roboto, sans-serif",
        "margin": "0",
        "padding": "6%",
        "height": "100vh",
        "backgroundColor": "#4a89746c",
        "display": "flex",
        "justifyContent": "center",
        "alignItems": "center"
    },
    children=[
    	dcc.Location(id="redirect-to-home", refresh=True),
        html.Div(
            className="split-container",
            children=[
            
                html.Div(
                    className="left-side",
                    style={
                        "backgroundSize": "cover",
                        "backgroundPosition": "center",
                        "color": "white",
                        "display": "flex",
                        "flexDirection": "column",
                        "justifyContent": "center",
                        "alignItems": "center",
                        "padding": "20px"
                    },
                    children=[
                        html.Img(
                            src="/assets/graphImg.jpg",
                            alt="App Logo",
                            style={"width": "150px", "height": "150px", "marginBottom": "20px"}
                        ),
                        html.H1("Graph Maker", style={"textAlign": "center", "marginBottom": "10px"}),
                        html.P(
                            "This app customizes graphs from a CSV file of population data, cleans the data, and provides analysis tools for insights.",
                            style={"textAlign": "center", "fontSize": "16px", "lineHeight": "1.5"}
                        )
                    ]
                ),
                html.Div(
                    className="right-side",
                    style={
                        "padding": "50px",
                        "display": "flex",
                        "flexDirection": "column",
                        "justifyContent": "center",
                        "alignItems": "center",
                    },
                    children=[
                        html.H2("Login", className="form-title"),
                        dcc.Input(id="username", type="text", placeholder="Username", className="input-field"),
                        dcc.Input(id="password", type="password", placeholder="Password", className="input-field"),
                        html.Button("Login", id="login-button", className="login-button"),
                        html.Div(id="login-feedback"),
                        html.Br(),
                        html.Div(
                            children=[
                                html.A("Sign up", href="/sign-up", className="signup-link")
                            ]
                        )
                    ]
                )
            ]
        )
    ]
)



#sign up page layout : 
sign_up_page = html.Div(
    className="sign-up-page",
    children=[
        dcc.Location(id="redirect-to-login", refresh=True), 
        html.Div(
            className="form-container",
            children=[
                html.H2("Sign Up", className="form-title"),
              
                html.Div(
                    className="form-group",
                    children=[
                        html.Label("First Name:", className="form-label"),
                        dcc.Input(id="first-name", type="text", className="input-field"),
                    ],
                ),
                html.Div(
                    className="form-group",
                    children=[
                        html.Label("Last Name:", className="form-label"),
                        dcc.Input(id="last-name", type="text", className="input-field"),
                    ],
                ),
              
                html.Div(
                    className="form-group",
                    children=[
                        html.Label("Gender:", className="form-label"),
                        dcc.RadioItems(
                            id="gender-radio",
                            options=[
                                {"label": "Male", "value": "male"},
                                {"label": "Female", "value": "female"}
                            ],
                            className="gender-options",
                            inputClassName="radio-item",
                        ),
                    ],
                ),
                
                html.Div(
                    className="form-group",
                    children=[
                        html.Label("Email Address:", className="form-label"),
                        dcc.Input(id="email", type="email", className="input-field"),
                    ],
                ),
                
                html.Div(
                    className="form-group",
                    children=[
                        html.Label("Username:", className="form-label"),
                        dcc.Input(id="username-signup", type="text", className="input-field"),
                    ],
                ),
                html.Div(
                    className="form-group",
                    children=[
                        html.Label("Date of Birth:", className="form-label"),
                        dcc.Input(id="dob", type="date", className="input-field"),
                    ],
                ),
                html.Div(
                    className="form-group",
                    children=[
                        html.Label("Password:", className="form-label"),
                        dcc.Input(id="password-signup", type="password", className="input-field"),
                        html.Button("Show", id="toggle-password-visibility", className="show-password-btn")  
                    ],
                ),
                html.Div(
                    className="form-group",
                    children=[
                        html.Label("Repeat Password:", className="form-label"),
                        dcc.Input(id="repeat-password", type="password", className="input-field"),
                        html.Button("Show", id="toggle-repeat-password-visibility", className="show-password-btn")  
                    ],
                ),
                
                html.Button("Sign Up", id="sign-up-button", className="signup-button"),
                
                html.Div(id="sign-up-feedback"),
            ],
        )
    ],
    style={
        "fontFamily": "Roboto, sans-serif",
        "margin": "0",
        "padding": "6%",
        "height": "100%",
        "backgroundColor": "#4a89746c",
        "display": "flex",
        "justifyContent": "center",
        "alignItems": "center"
    }
)



#log in and sign in functions : 

@app.callback(
    Output("password-signup", "type"),
    [Input("toggle-password-visibility", "n_clicks")],
    [State("password-signup", "type")]
)
def toggle_password_visibility(n_clicks, current_type):
    if n_clicks:
        return "text" if current_type == "password" else "password"
    return current_type  # Keep the current type if button hasn't been clicked

@app.callback(
    Output("repeat-password", "type"),
    [Input("toggle-repeat-password-visibility", "n_clicks")],
    [State("repeat-password", "type")]
)
def toggle_repeat_password_visibility(n_clicks, current_type):
    if n_clicks:
        return "text" if current_type == "password" else "password"
    return current_type  # Keep the current type if button hasn't been clicked




@app.callback(
    [Output("login-feedback", "children"),  
     Output("redirect-to-home", "href")],   
    Input("login-button", "n_clicks"),  
    [State("username", "value"),
     State("password", "value")]  
)
def login_user(n_clicks, username, password):
    if n_clicks is None:
        return "", None  # Aucun clic sur le bouton, pas de changement
    
    if username and password:
        user_valid = fc.user_exist(username, password)  # Vérifie si l'utilisateur existe
        if user_valid:
            # Modifier l'état du fichier pour indiquer que l'utilisateur est connecté
            try:
                with open("connection_state.txt", "w") as file:
                    file.write("1")  # État connecté
            except Exception as e:
                return "Error updating connection state.", None
            
            return "Login successful!", "/"  # Succès : rediriger vers /home
        else:
            return "*Invalid username or password.", None  # Erreur d'identification
    
    return "*Please enter both username and password.", None  # Champs vides
 


@app.callback(
    [Output("sign-up-feedback", "children"),  
     Output("redirect-to-login", "href")],   
    Input("sign-up-button", "n_clicks"),
    State("first-name", "value"),
    State("last-name", "value"),
    State("gender-radio", "value"),
    State("email", "value"),
    State("username-signup", "value"),
    State("password-signup", "value"),
    State("repeat-password", "value")
)


def signup_user(n_clicks, first_name, last_name, gender, email, username, password, repeat_password):
    if n_clicks is None:
        return "", None  

    
    if not first_name or not last_name:
        return "*First Name and Last Name are required.", None
    if not gender:
        return "*Please select a gender.", None
    if not email:
        return "*Email Address is required.", None
    if password != repeat_password:
        return "*Passwords do not match!", None
    if not username or not password:
        return "*Username and Password are required.", None

    
    result = fc.signup_user(first_name, last_name, username, password, email, gender)

    
    if result == "User successfully created!":
        return result, "/sign-in"  
    return result, None  


# App layout with multi-page navigation
"""***************************************************************************************************************************************************************************************************"""
app.layout = html.Div(
    children=[
        dcc.Location(id="url", refresh=False),
        html.Div(id="page-content")
    ]
)


@app.callback(
    Output("page-content", "children"),
    Input("url", "pathname")
)
def display_page(pathname):
   
    try:
        with open("connection_state.txt", "r") as file:
            connection_state = file.read().strip()
    except FileNotFoundError:
        connection_state = "0" 
    

    if connection_state == "0":
        if pathname == "/sign-up":
            return sign_up_page
        elif pathname == "/sign-in" or pathname == "/":
            return login_page
        else:
            return login_page  
    

    if pathname == "/sign-up":
        return sign_up_page
    elif pathname == "/sign-in":
        return login_page
    else:
        return layout

"""***************************************************************************************************************************************************************************************************"""

"""********************************************************* HOME *********************************************************"""


#Home layout :
layout = html.Div([
	dcc.Download(id='download-file'), 
    # Header
    html.Div(
        children=[
            
            dcc.Upload(
                id='upload-data',
                children=html.Button('Upload File', style={
                    'font-size': '16px',
                    'padding': '10px 20px',
                    'border-radius': '0',  
                    'cursor': 'pointer',
                    'box-sizing': 'border-box',
                }),
                multiple=False,
                style={
                    'display': 'flex',
                    'justify-content': 'flex-end',  
                    'width': '100%',  
                    'padding-right': '20px',  
                }
            ),
           html.Button('Sign out',
           		n_clicks=0,
           		id='sign-out' , style={
                        'font-size': '16px',
                        'padding': '10px 20px',
                        'border-radius': '0',  
                        'cursor': 'pointer',
                        'box-sizing': 'border-box',
                        'margin-left' : '30px'
                    }),
        ],
        style={
            'background-color': '#f9fafb',
            'color': 'black',
            'height': '9%',
            'display': 'flex',
            'align-items': 'center',  
            'justify-content': 'flex-end',  
            'border-bottom': '1px solid black',
            'padding-right': '50px',  
            'padding-left': '50px',  
        }
    ),
    # Main container
    html.Div(
        children=[
            # Sidebar with buttons
            html.Div(
                children=[
                    html.Button(
                        "Home",
                        id='btn-home',
                        n_clicks=0,
                        style={
                            'display': 'block',
                            'width': '100%',
                            'padding': '15px',
                            'background-color': 'white',
                            'color': 'black',
                            'text-align': 'center',
                            'border': '1px solid #e5e9e9',
                            'cursor': 'pointer',
                            'box-sizing': 'border-box',
                            'margin-top': '5px',
                            'margin-bottom': '5px'  
                        }
                    ),
                    html.Button(
                        "Analyse Data",
                        id='btn-analyse',
                        n_clicks=0,
                        style={
                            'display': 'block',
                            'width': '100%',
                            'padding': '15px',
                            'background-color': 'white',
                            'color': 'black',
                            'text-align': 'center',
                            'border': '1px solid #e5e9e9',
                            'cursor': 'pointer',
                            'box-sizing': 'border-box',
                            'margin-bottom': '5px'  
                        }
                    ),
                    html.Button(
                        "Clean Data",
                        id='btn-clean',
                        n_clicks=0,
                        style={
                            'display': 'block',
                            'width': '100%',
                            'padding': '15px',
                            'background-color': 'white',
                            'color': 'black',
                            'text-align': 'center',
                            'border': '1px solid #e5e9e9',
                            'cursor': 'pointer',
                            'box-sizing': 'border-box',
                            'margin-bottom': '5px'
                        }
                    ),
                    html.Button(
                        "Save PNG",
                        id='btn-save',
                        n_clicks=0,
                        style={
                            'display': 'block',
                            'width': '100%',
                            'padding': '15px',
                            'background-color': 'white',
                            'color': 'black',
                            'text-align': 'center',
                            'border': '1px solid #e5e9e9',
                            'cursor': 'pointer',
                            'box-sizing': 'border-box',
                            'margin-bottom': '5px'
                        }
                    ),
                ],
                style={
                    'background-color': '#f9fafb',
                    'width': '7%',  
                    'height': '100%',  
                    'box-sizing': 'border-box',
                }
            ),

            # Content section
            html.Div(
                id='main-container',
                style={
                    'background-color': ' #f9fafb',
                    'width': '93%',  
                    'height': '100%',  
                    'overflow': 'auto',
                    'box-sizing': 'border-box',
                }
            ),
        ],
        style={
            'display': 'flex',
            'height': '91%',  
        }
    ),
])

# Home page functions :
@app.callback(
    Output('url', 'pathname'),
    [Input('sign-out', 'n_clicks')]
)
def navigate_to_login(n_clicks):
    if n_clicks:
        # Modifier l'état du fichier pour indiquer la déconnexion
        try:
            with open("connection_state.txt", "w") as file:
                file.write("0")  # État déconnecté
        except Exception as e:
            print(f"Error updating connection state: {e}")  # Log l'erreur
        return '/sign-in'  # Redirection vers la page de connexion
    
    return ds.no_update  # Pas de changement si le bouton n'est pas cliqué


@app.callback(
    Output('download-file', 'data'),
    [Input('btn-save', 'n_clicks')],
    [State('graph', 'figure')]
)
def save_figure_as_png(n_clicks, figure):
    if n_clicks is None or n_clicks == 0:
        raise PreventUpdate

    
    with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as temp_file:
        temp_path = temp_file.name
        pio.write_image(figure, temp_path, format='png')

 
    return dcc.send_file(temp_path, filename="graphique.png")

    
    


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


@app.callback(
    [Output('x-column', 'options'), Output('y-column', 'options')],
    Input('upload-data', 'contents'),
    State('upload-data', 'filename')
)
def update_columns(contents, filename):
    global global_df
    if contents is not None:
        global_df = parse_data(contents, filename)
        if isinstance(global_df, pd.DataFrame):
            options = [{'label': col, 'value': col} for col in global_df.columns]
            return options, options
    return [], []


@app.callback(
    Output('output-data-upload', 'children'),
    Input('upload-data', 'contents'),
    State('upload-data', 'filename')
)
def update_output(contents, filename):
    if contents is None:
        return html.Div("Aucun fichier importé pour l'instant.",style = {'text-align':'center' , 'color' : 'red'})

    df = parse_data(contents, filename)
    if isinstance(df, pd.DataFrame):
        return dash_table.DataTable(
            data=df.to_dict('records'),
            columns=[{'name': col, 'id': col} for col in df.columns],
            page_size=5,  
            style_table={
                'overflowX': 'auto',
                'overflowY': 'auto',
                'maxWidth': '98%',
                'maxHeight': '300px',
            },
            style_cell={
                 'textAlign': 'left',
		    'padding': '5px',
		    'whiteSpace': 'nowrap', 
		    'overflow': 'hidden',   
		    'textOverflow': 'ellipsis'  
            }
        )


# Callback to update graph based on dropdown selections :

graph_types.register_callbacks(app)

"""********************************************************* Analyse *********************************************************"""

#Analyse functions :

def parse_contents(contents):
    content_type, content_string = contents.split(',')
    decoded = base64.b64decode(content_string)
    try:
        if 'csv' in content_type:
            return pd.read_csv(io.StringIO(decoded.decode('utf-8')))
        elif 'excel' in content_type:
            return pd.read_excel(io.BytesIO(decoded))
    except Exception as e:
        raise ValueError("Erreur lors de l'importation du fichier. Assurez-vous qu'il s'agit d'un fichier CSV ou Excel valide.") from e

# Fonction pour générer le PDF
def generate_pdf(df, analysis_type):
    output = io.BytesIO()
    c = canvas.Canvas(output, pagesize=letter)
    width, height = letter

    c.setFont("Helvetica-Bold", 16)
    c.drawString(30, height - 30, f"Résultats de l'analyse ({analysis_type})")

    c.setFont("Helvetica", 10)
    text_y = height - 60
    for i, row in df.iterrows():
        text = " | ".join([f"{col}: {val}" for col, val in row.items()])
        c.drawString(30, text_y, text)
        text_y -= 12
        if text_y < 50:  # Nouvelle page si on atteint la fin de la page
            c.showPage()
            c.setFont("Helvetica", 10)
            text_y = height - 30

    c.showPage()
    c.save()
    output.seek(0)
    return base64.b64encode(output.read()).decode()

@app.callback(
    [
        Output('column-dropdown', 'options'),
        Output('column-dropdown', 'value'),
        Output('analysis-output', 'children'),
        Output('error-output', 'children'),
        Output('download_link', 'children'),
        Output('file-upload-status', 'children')
    ],
    [Input('upload-analyse-data', 'contents'),
     Input('column-dropdown', 'value'),
     Input('analysis-dropdown', 'value'),
     Input('download_link', 'n_clicks'),]
)


def update_analysis(contents, column, analysis_type,n_clicks):
    if contents is None:
        raise PreventUpdate

    # Gestion des erreurs de fichier
    try:
        df = parse_contents(contents)
        file_size = len(contents.encode('utf-8')) / 1024  # Taille en Ko
        file_status = f"Fichier chargé avec succès : {file_size:.2f} Ko"
    except Exception as e:
        return [], None, None, f"Erreur : {str(e)}", None, None

    # Mettre à jour les colonnes dans le menu déroulant
    columns = df.columns.tolist()
    column_options = [{'label': col, 'value': col} for col in columns]

    if not column:
        return column_options, None, None, None, None, file_status
    download_link = None

    if analysis_type == 'stats':
        # Analyse des statistiques descriptives
        try:
            df[column] = pd.to_numeric(df[column], errors='coerce')
            if df[column].isnull().all():
                error_message = f"Erreur : La colonne '{column}' contient uniquement des valeurs non numériques ou est vide."
                return column_options, column, None, error_message, None, file_status

            stats = {
                "Moyenne": df[column].mean(),
                "Écart-type": df[column].std(),
                "Médiane": df[column].median(),
                "Valeur Min": df[column].min(),
                "Valeur Max": df[column].max(),
                "1er Quartile": df[column].quantile(0.25),
                "3e Quartile": df[column].quantile(0.75),
                "Somme": df[column].sum(),
                "Nombre de valeurs": df[column].count()
            }

            stats_df = pd.DataFrame(list(stats.items()), columns=["Statistique", "Valeur"])
            stats_table = dash_table.DataTable(
                columns=[{"name": i, "id": i} for i in stats_df.columns],
                data=stats_df.to_dict('records'),
                style_table={'height': '300px', 'overflowY': 'auto'},
                style_cell={'textAlign': 'center', 'padding': '5px', 'fontFamily': 'Arial'},
                style_header={ 
                    'backgroundColor': '#2c3e50',
                    'color': 'white',
                    'fontWeight': 'bold',
                    'textAlign': 'center'
                },
                style_data={'backgroundColor': '#ecf0f1', 'color': '#2c3e50'}
            )
            
            pdf_data = generate_pdf(stats_df, 'Statistiques')
            download_link = html.A(
                "Télécharger les résultats (PDF)",
                id="download-link",
                download="statistiques.pdf",
                href="data:application/pdf;base64," + pdf_data,
                target="_blank",
                style={
                    'textDecoration': 'none',
                    'color': 'white',
                    'backgroundColor': '#3498db',
                    'padding': '10px 20px',
                    'borderRadius': '5px'
                }
            )
            return column_options, column, stats_table, None, download_link, file_status

        except ValueError as ve:
            error_message = f"Erreur : {str(ve)}"
            return column_options, column, None, error_message, None, file_status

    elif analysis_type == 'demo':
        # Analyse démographique : Compter les occurrences de chaque valeur
        try:
            demo_df = df[column].value_counts().reset_index()
            demo_df.columns = [column, 'Fréquence']

            demo_table = dash_table.DataTable(
                columns=[{"name": i, "id": i} for i in demo_df.columns],
                data=demo_df.to_dict('records'),
                style_table={'height': '300px', 'overflowY': 'auto'},
                style_cell={'textAlign': 'center', 'padding': '5px', 'fontFamily': 'Arial'},
                style_header={ 
                    'backgroundColor': '#2c3e50',
                    'color': 'white',
                    'fontWeight': 'bold',
                    'textAlign': 'center'
                },
                style_data={'backgroundColor': '#ecf0f1', 'color': '#2c3e50'}
            )
              
            pdf_data = generate_pdf(demo_df, 'Analyse démographique')

            # Créer le lien pour télécharger le PDF
            download_link = html.A(
                "Télécharger les résultats (PDF)",
                id="download-link",
                download="analyse_demographique.pdf",
                href="data:application/pdf;base64," + pdf_data,
                target="_blank",
                style={
                    'textDecoration': 'none',
                    'color': 'white',
                    'backgroundColor': '#3498db',
                    'padding': '10px 20px',
                    'borderRadius': '5px'
                }
            )    

            return column_options, column, demo_table, None, download_link, file_status

        except ValueError as ve:
            error_message = f"Erreur : {str(ve)}"
            return column_options, column, None, error_message, None, file_status 
        
    elif analysis_type == 'viz':
        # Visualisation graphique : Histogramme des valeurs
        try:
            histogram = dcc.Graph(
                figure={
                    'data': [
                        {
                            'x': df[column],
                            'type': 'histogram',
                            'marker': {'color': '#3498db'}
                        }
                    ],
                    'layout': {
                        'title': f"Histogramme de {column}",
                        'xaxis': {'title': column},
                        'yaxis': {'title': 'Fréquence'},
                        'plot_bgcolor': '#f7f9fb',
                        'paper_bgcolor': '#f7f9fb'
                    }
                }
            )

            return column_options, column, histogram, None, None, file_status

        except Exception as e:
            error_message = f"Erreur : {str(e)}"
            return column_options, column, None, error_message, None, file_status

    if analysis_type == 'corr':
        try:
            # Vérifiez si une colonne a été sélectionnée
            if not column:
                return column_options, column, None, "Erreur : Veuillez sélectionner une colonne pour l'analyse.", None, file_status

            # Assurez-vous que la colonne sélectionnée existe et est numérique
            if column not in df.columns or not pd.api.types.is_numeric_dtype(df[column]):
                return column_options, column, None, "Erreur : La colonne sélectionnée doit être numérique, veuillez choisir une autre.", None, file_status

            # Liste des colonnes numériques, excluant la colonne sélectionnée
            numeric_columns = [col for col in df.select_dtypes(include=['number']).columns if col != column]

            if not numeric_columns:
                return column_options, column, None, "Erreur : Pas d'autres colonnes numériques disponibles pour l'analyse.", None, file_status

            # Prenez la première colonne numérique disponible
            other_column = numeric_columns[0]

            # Créez un DataFrame avec les deux colonnes pour l'analyse
            selected_df = df[[column, other_column]]

            # Calculer la corrélation entre les deux colonnes
            correlation_matrix = selected_df.corr()

            # Générer le tableau de corrélation
            correlation_table = dash_table.DataTable(
                columns=[{"name": col, "id": col} for col in correlation_matrix.columns],
                data=correlation_matrix.round(2).reset_index().rename(columns={'index': 'Colonne'}).to_dict('records'),
                style_table={'height': '300px', 'overflowY': 'auto'},
                style_cell={'textAlign': 'center', 'padding': '5px', 'fontFamily': 'Arial'},
                style_header={
                    'backgroundColor': '#2c3e50',
                    'color': 'white',
                    'fontWeight': 'bold',
                    'textAlign': 'center'
                },
                style_data={'backgroundColor': '#ecf0f1', 'color': '#2c3e50'}
            )

            # Visualisation de la corrélation avec une heatmap
            fig = px.imshow(
                correlation_matrix,
                text_auto=True,
                color_continuous_scale='Viridis',
                labels={"color": "Coefficient de corrélation"}
            )
            fig.update_layout(
                title=f"Corrélation : {column} et {other_column}",
                title_x=0.5,
                height=500
            )
            
            # Générer le lien de téléchargement en PDF
            pdf_data = generate_pdf(correlation_matrix.round(2), 'Analyse de Corrélation')
            download_link = html.A(
                "Télécharger les résultats (PDF)",
                id="download-link",
                download="correlation_analysis.pdf",
                href="data:application/pdf;base64," + pdf_data,
                target="_blank",
                style={
                    'textDecoration': 'none',
                    'color': 'white',
                    'backgroundColor': '#3498db',
                    'padding': '10px 20px',
                    'borderRadius': '5px'
                }
            )
            
            return column_options, column, html.Div([correlation_table, dcc.Graph(figure=fig)]), None, download_link, file_status


        except Exception as e:
            error_message = f"Erreur : {str(e)}"
            return column_options, column, None, error_message, None, file_status


    else:
        # Si l'analyse n'est ni 'stats', ni 'demo', ni 'corr'
        return column_options, column, None, None, None, file_status
  


"""********************************************************* Clean Data *********************************************************"""
# def parse_data(contents, filename):
#     content_type, content_string = contents.split(',')
#     decoded = base64.b64decode(content_string)
#     try:
#         if 'csv' in filename:
#             df = pd.read_csv(io.StringIO(decoded.decode('utf-8')))
#         elif 'xls' in filename or 'xlsx' in filename:
#             df = pd.read_excel(io.BytesIO(decoded))
#         else:
#             return html.Div(["Le format du fichier n'est pas supporté."])
#         return df
#     except Exception as e:
#         return html.Div([f"Erreur lors du traitement du fichier : {str(e)}"])


def clean_parse_contents(contents):
    try:
        content_type, content_string = contents.split(',')
        if 'csv' in content_type:
            decoded = base64.b64decode(content_string)
            df = pd.read_csv(io.StringIO(decoded.decode('utf-8')))
        elif 'xls' in content_type or 'xlsx' in content_type:
            decoded = base64.b64decode(content_string)
            df = pd.read_excel(io.BytesIO(decoded))
        else:
            return pd.DataFrame()
        return df
    except Exception as e:
        return pd.DataFrame()


# def clean_parse_contents(contents):
#     if not contents:
#         return pd.DataFrame()
#     try:
#         content_type, content_string = contents.split(',')
#         if 'csv' not in content_type:
#             return pd.DataFrame()
#         decoded = base64.b64decode(content_string)
#         df = pd.read_csv(io.StringIO(decoded.decode('utf-8')))
#         return df
#     except Exception as e:
#         return pd.DataFrame()
        
 # supprimer les doublons
def sup_dublon(data):  # supprimer les doublons
    data.drop_duplicates(inplace=True)
    return data

# Fonction pour nettoyer les textes dans les colonnes de type texte
def net_text(data,selected_column):
    if selected_column not in data.columns:
        return data
    data[selected_column] = data[selected_column].apply(lambda x: re.sub(r'[^\w\s]', '',
    str(x)).lower() if isinstance(x,str) else x)
    return data


#  Fonction pour traiter les colonnes selon les types dominants
def rem_v_manquante(data, colonne):
    if colonne in data.columns:
        column_data = data[colonne]
        if column_data.isna().all():
            data[colonne] = 0
        else:

            numeric_values = pd.to_numeric(column_data, errors='coerce') #Convertir les valeurs en numériques

            mean_value = round(numeric_values.mean(), 2) # Calculer la moyenne des valeurs numériques

            if numeric_values.notna().sum() >= (column_data.size - numeric_values.notna().sum()):
                data[colonne] = numeric_values.fillna(mean_value)
            else:
                text_values = column_data[numeric_values.isna()]
                mode_value = text_values.mode()[0] if not text_values.empty else "N/A"
                data[colonne] = column_data.apply(
                    lambda x: mode_value if pd.isna(x) else x if isinstance(x, str) else mode_value
                )

    return data


def Age_C(data,age_colonne):#Fonction pour traiter les âges dans une colonne spécifique.
        if data[age_colonne].isnull().all():
            data[age_colonne] = 0
            return data
        if  age_colonne in data.columns:
            data[age_colonne] = pd.to_numeric(data[age_colonne], errors='coerce')
            data[age_colonne] = data[age_colonne].apply(lambda x: abs(x))
            mean_age = data[age_colonne].mean()
            data[age_colonne].fillna(mean_age, inplace=True)
            data[age_colonne] = data[age_colonne].astype(int)
        return data

# Corriger les dates
def conv_date(data, colonne):
    if colonne in data.columns:
        try:
            data[colonne] = pd.to_datetime(data[colonne], errors='coerce')

            numeric_values = pd.to_numeric(data[colonne], errors='coerce')
            num_count = numeric_values.notna().sum()  # Nombre de valeurs numériques
            text_count = data[colonne].isna().sum()  # Nombre de valeurs textuelles
            if num_count > text_count:
                # Remplacer les valeurs manquantes numériques par la date moyenne
                valid_dates = data[colonne].dropna()
                if not valid_dates.empty:
                    mean_date = valid_dates.mean()
                    data[colonne] = data[colonne].fillna(mean_date)
                    data[colonne] = data[colonne].dt.strftime('%Y-%m-%d')
                    return data ,True
            else:
                return data, False
        except Exception as e:
            return data, False
    return data, False


# Callback pour gérer les actions de chargement et de nettoyage
@app.callback(
    [
        Output('data-table', 'data'),
        Output('data-table', 'columns'),
        Output('clean-column-dropdown', 'options'),
        Output("download-dataframe-csv", "data"),
        Output('message-div', 'children')

    ],
    [
        Input('upload-clean-data', 'contents'),
        Input('clean-button', 'n_clicks'),
        Input('sup-button', 'n_clicks'),
        Input('corige-button', 'n_clicks'),
        Input('Net-button', 'n_clicks'),
        Input('corigeD-button', 'n_clicks'),
        Input("download-button", "n_clicks"),

    ],
    [State('data-table', 'data'),
     State('clean-column-dropdown', 'value'),
     ]
)

def Actions_button(contents, clean_clicks,sup_clicks,corige_clicks,Net_clicks,corigeD_clicks,download_clicks, table_data, selected_column):
    ctx = ds.callback_context
    triggered_id = ctx.triggered[0]['prop_id'].split('.')[0] if ctx.triggered else None
    message = ""

    if triggered_id == 'upload-clean-data' and contents:  # Si un fichier est téléchargé
        df = clean_parse_contents(contents)
        if not df.empty:
            columns = [{'name': col, 'id': col} for col in df.columns]
            options = [{'label': col, 'value': col} for col in df.columns]
            message = "Le fichier a été chargé avec succès."
            return df.to_dict('records'), columns, options, no_update,message
        else:
            message = "Erreur : Échec du chargement du fichier. Assurez-vous qu'il s'agit d'un fichier CSV valide."
            return [], [], [],ds.no_update,message

    elif triggered_id == 'corige-button' and table_data:
        df = pd.DataFrame(table_data)
        if selected_column:
            df = Age_C(df, selected_column)
            columns = [{'name': col, 'id': col} for col in df.columns]
            options = [{'label': col, 'value': col} for col in df.columns]
            message = f"Les âges dans la colonne '{selected_column}' ont été corrigés."
            return df.to_dict('records'), columns, options, ds.no_update,message
        else:
            message = "Erreur : Veuillez sélectionner une colonne pour corrigé l'age."
            return no_update,no_update,no_update,no_update,message


    elif triggered_id == 'sup-button' and table_data:
        df = pd.DataFrame(table_data)
        df = sup_dublon(df)
        message = "Les doublons ont été supprimés avec succès."
        columns = [{'name': col, 'id': col} for col in df.columns]
        options = [{'label': col, 'value': col} for col in df.columns]
        return df.to_dict('records'), columns, options,no_update,message

    elif triggered_id == 'Net-button' and table_data:
        if selected_column:
            df = pd.DataFrame(table_data)
            df = net_text(df,selected_column)
            message = f"Le texte dans la colonne '{selected_column}' a été nettoyé."
            columns = [{'name': col, 'id': col} for col in df.columns]
            options = [{'label': col, 'value': col} for col in df.columns]
            return df.to_dict('records'), columns, options,no_update,message
        else:
            message = f"Le texte dans la colonne '{selected_column}' déja nettoyé."
            return table_data, no_update,no_update,no_update,message



    elif triggered_id == 'clean-button' and table_data:  # Nettoyage des données
        df = pd.DataFrame(table_data)
        if selected_column:
            df = rem_v_manquante(df, selected_column)
            columns = [{'name': col, 'id': col} for col in df.columns]
            options = [{'label': col, 'value': col} for col in df.columns]
            message = f"Les valeurs manquantes dans la colonne '{selected_column}' ont été remplies."
            return df.to_dict('records'), columns, options,no_update,message
        else:
            message = "Erreur : Veuillez sélectionner une colonne pour remplir les valeurs manquantes."
            return no_update, no_update, no_update, no_update, message



    elif triggered_id == 'corigeD-button' and table_data: # corige les dates
        df = pd.DataFrame(table_data)
        if selected_column:
            df, valid = conv_date(df, selected_column)
            if valid:
                message = f"Les dates dans la colonne '{selected_column}' ont été corrigées."
                columns = [{'name': col, 'id': col} for col in df.columns]
                options = [{'label': col, 'value': col} for col in df.columns]
                return df.to_dict('records'), columns, options, no_update, message
            else:
                message = f"Impossible de corriger les dates dans la colonne '{selected_column}'. Vérifiez les valeurs."
                columns = [{'name': col, 'id': col} for col in df.columns]
                options = [{'label': col, 'value': col} for col in df.columns]
                return df.to_dict('records'), columns, options,no_update,message
        else:
            message="Veuillez sélectionner une colonne pour corriger les dates."
            return no_update, no_update, no_update, no_update,message


    # Vérifier si un fichier est prêt pour le téléchargement
    elif triggered_id == 'download-button' and table_data:
        # Générer le contenu du fichier CSV
        df = pd.DataFrame(table_data)
        message = "Le fichier nettoyé est prêt à être téléchargé."
        # Utilisation correcte de dcc.send_data_frame
        return table_data,no_update,no_update, dcc.send_data_frame(df.to_csv, "data_cleaned.csv"),message

    return table_data, no_update, no_update, no_update, message


"""********************************************************* Callback to update content based on button clicks *********************************************************"""



@app.callback(
    Output('main-container', 'children'),
    [Input('btn-home', 'n_clicks'),
     Input('btn-analyse', 'n_clicks'),
     Input('btn-clean', 'n_clicks'),
     ]
)
def update_content(btn_home, btn_analyse, btn_clean):
    ctx = ds.callback_context
    
    button_id = ctx.triggered[0]['prop_id'].split('.')[0]


	#ANALYSE DATA
    if button_id == 'btn-analyse':
        return html.Div([
    html.Div(
        className="header",
        children=[
            html.H1("Analyse des Données de Population", className="header-title"),
            html.P(" Analysez les colonnes de données facilement.", className="header-description")
        ],
        style={
            'textAlign': 'center',
            'backgroundColor': '#2c3e50',
            'color': 'white',
            'padding': '20px',
            'borderRadius': '5px'
        }
    ),

    html.Div(
        className="upload-section",
        children=[
            dcc.Upload(
                id='upload-analyse-data',
                children=html.Div([ 
                    'Glissez et déposez un fichier CSV ou Excell ', 
                    html.A('cliquez pour sélectionner un fichier') 
                ]),
                style={ 
                    'width': '100%', 
                    'height': '60px', 
                    'lineHeight': '60px', 
                    'borderWidth': '1px', 
                    'borderStyle': 'dashed', 
                    'borderRadius': '5px', 
                    'textAlign': 'center', 
                    'margin': '10px 0', 
                    'backgroundColor': '#ecf0f1', 
                    'cursor': 'pointer'  
                },
                multiple=False
            ),
            html.Div(id='file-upload-status', style={ 
                'textAlign': 'center', 
                'marginTop': '10px', 
                'color': '#27ae60', 
                'fontWeight': 'bold' 
            })
        ]
    ),

    html.Div(
        className="dropdown-section",
        children=[ 
            html.Label("Choisissez une colonne :", style={ 'fontWeight': 'bold', 'marginTop': '10px' }), 
            dcc.Dropdown(
                id='column-dropdown',
                options=[],
                value=None,
                placeholder="Sélectionnez une colonne",
                style={ 
                    'width': '100%', 
                    'marginBottom': '20px', 
                    'padding': '5px' 
                }
            )
        ]
    ),

    html.Div(
        className="dropdown-section",
        children=[
            html.Label("Choisissez le type d'analyse :", style={ 'fontWeight': 'bold', 'marginTop': '10px' }),
            dcc.Dropdown(
                id='analysis-dropdown',
                options=[
                    {'label': 'Statistiques Descriptives', 'value': 'stats'},
                    {'label': 'Analyse Démographique', 'value': 'demo'},
                    {'label': "Visualisation Graphique d'Analyse Démographique", 'value': 'viz'},
                    {'label': 'Analyse De Corrélation', 'value': 'corr'},
                    
                ],
                
                placeholder="Sélectionnez un type d'analyse",
                style={
                    'width': '100%',
                    'marginBottom': '20px',
                    'padding': '5px'
                }
            )
        ]
    ),

    html.Div(id='analysis-output', style={'marginTop': '20px'}),

    html.Div(
        id='error-output',
        style={ 
            'color': '#e74c3c', 
            'fontSize': '16px', 
            'marginTop': '20px', 
            'textAlign': 'center' 
        }
    ),

    html.Div(id='download_link', style={'textAlign': 'center', 'marginTop': '20px'},n_clicks=0), 
], style={ 
    'fontFamily': 'Arial, sans-serif', 
    'minWidth': '91vw', 
    'minHeight': '91vh',
    'margin': 'auto', 
    'padding': '20px', 
    'backgroundColor': '#f7f9fb', 
    'borderRadius': '10px', 
    'boxShadow': '0px 4px 6px rgba(0, 0, 0, 0.1)' 
})
	
	
	
	
	#CLEAN DATA
    elif button_id == 'btn-clean':
        return html.Div([

    
    html.H1(
        "Nettoyage des données",
        style={
            'textAlign': 'center',
            'fontSize': '3rem',
            'marginTop': '0px',
            'marginBottom': '20px',
            "backgroundColor": "#343a40",
            "color": "white",
            'padding': '15px'
        }
    ),

    
    html.Div(
        style={
            "width": "30%", 
            "height": "100vh", 
            "backgroundColor": "#f4f6f9", 
            "float": "left",  
            "padding": "20px",  
            "boxSizing": "border-box",  
            "borderRadius": "10px"
        },
        children=[
            
            dcc.Upload(
                id='upload-clean-data',
                children=html.Button('Charger un fichier CSV', style={
                    "backgroundColor": "#5a2d82",
                    'color': 'white',
                    "width": "100%",
                    "padding": "15px",
                    "borderRadius": "8px",
                    "border": "none",
                    "cursor": "pointer",
                    "fontSize": "16px",
                    "boxSizing": "border-box",
                    "marginTop": "20px"
                }),
                multiple=False
            ),
          
            dcc.Dropdown(
                id='clean-column-dropdown',
                placeholder="Choisir une colonne",
                options=[], 
                style={"marginTop": "20px", 'width': '100%', "fontSize": "16px", "borderRadius": "8px"}
            ),

           
            html.Div(
                children=[
                    html.Button('Supprimer Duplicats', id='sup-button', n_clicks=0, style={
                        "width": "100%",
                        "backgroundColor": "#007bff",
                        "color": "white",
                        "border": "2px solid #007bff",
                        "borderRadius": "8px",
                        "cursor": "pointer",
                        "fontSize": "16px",
                        "padding": "15px",
                        "boxSizing": "border-box",
                        "marginTop": "10px"
                    }),
                    html.Button('Remplir Manquants', id='clean-button', n_clicks=0, style={
                        "width": "100%",
                        "backgroundColor": "#007bff",
                        "color": "white",
                        "border": "2px solid #007bff",
                        "borderRadius": "8px",
                        "cursor": "pointer",
                        "fontSize": "16px",
                        "padding": "15px",
                        "boxSizing": "border-box",
                        "marginTop": "10px"
                    }),
                    html.Button('Corriger Age', id='corige-button', n_clicks=0, style={
                        "width": "100%",
                        "backgroundColor": "#007bff",
                        "color": "white",
                        "border": "2px solid #007bff",
                        "borderRadius": "8px",
                        "cursor": "pointer",
                        "fontSize": "16px",
                        "padding": "15px",
                        "boxSizing": "border-box",
                        "marginTop": "10px"
                    }),
                    html.Button('Nettoyer Texte', id='Net-button', n_clicks=0, style={
                        "width": "100%",
                        "backgroundColor": "#007bff",
                        "color": "white",
                        "border": "2px solid #007bff",
                        "borderRadius": "8px",
                        "cursor": "pointer",
                        "fontSize": "16px",
                        "padding": "15px",
                        "boxSizing": "border-box",
                        "marginTop": "10px"
                    }),
                    html.Button('Corriger Dates', id='corigeD-button', n_clicks=0, style={
                        "width": "100%",
                        "backgroundColor": "#007bff",
                        "color": "white",
                        "border": "2px solid #007bff",
                        "borderRadius": "8px",
                        "cursor": "pointer",
                        "fontSize": "16px",
                        "padding": "15px",
                        "boxSizing": "border-box",
                        "marginTop": "10px"
                    }),
                ],
                style={
                    "display": "flex",
                    "flexDirection": "column",
                    "gap": "15px",
                    "alignItems": "stretch"
                }
            ),

            
            html.Button(
                "Télécharger les données nettoyées",
                id="download-button",
                n_clicks=0,
                style={
                    "width": "100%",
                    "backgroundColor": "#28a745",
                    "color": "white",
                    "padding": "15px",
                    "borderRadius": "8px",
                    "border": "none",
                    "cursor": "pointer",
                    "fontSize": "16px",
                    "boxSizing": "border-box",
                    "marginTop": "20px"
                }
            ),
            dcc.Download(id="download-dataframe-csv"),
        ]
    ),

    
    html.Div(
        id='clean-output-data-upload',
        style={
            'height': '100vh',
            'width': '70%',
            'float': 'right',
            'padding': '20px',
            'boxSizing': 'border-box',
            'display': 'flex',
            'flexDirection': 'column',
            'justifyContent': 'flex-start',
            'borderRadius': '10px',  
            'boxShadow': '0 4px 8px rgba(0, 0, 0, 0.1)', 
            'backgroundColor': '#ffffff'  
        },
        children=[
            html.Div(id='message-div', style={'color': 'green', 'textAlign': 'center', 'marginBottom': '10px'}),
            dash_table.DataTable(
                id='data-table',
                columns=[],  
                data=[],
                page_size=15,
                style_table={'height': '100%', 'overflowY': 'auto','overflowX': 'auto','maxHeight': '1000px'},
                style_cell={'textAlign': 'left', 'padding': '5px','whiteSpace': 'nowrap','overflow': 'hidden', 'textOverflow': 'ellipsis'},
                style_header={'backgroundColor': '#f1f1f1', 'fontWeight': 'bold'}
            ),
        ],
    ),
])

              
       
       
        
        
        
    #HOME :   
    else:
        return html.Div([
            html.Div(
                children=[
                    html.Div([
                        html.Label("Select Graph Type:"),
                        dcc.Dropdown(
                            id='graph-type',
                            options=[
				{'label': 'Scatter Plot', 'value': 'scatter'},
				{'label': 'Bar Chart', 'value': 'bar'},
				{'label': 'Line Chart', 'value': 'line'},
				{'label': 'Area Chart', 'value': 'area'},
				{'label': 'Box Plot', 'value': 'box'},
				{'label': 'Violin Plot', 'value': 'violin'},
				{'label': 'Histogram', 'value': 'histogram'},
				{'label': 'Pie Chart', 'value': 'pie'}
						],

                            value='scatter',  
                            clearable=False,
                            style={'width': '200px'}
                        )
                    ], style={'margin-bottom': '20px'}),  
                    html.Br(),
                    
          html.Div([
                        html.Label("X:"),
                        dcc.Dropdown(
                            id='x-column',
                            style={'width': '200px'}
                        )
                    ], style={'margin-bottom': '20px'}),
                    html.Br(),
                    html.Div([
                        html.Label("Y:"),
                        dcc.Dropdown(
                            id='y-column',
                            style={'width': '200px'}
                        )
                    ], style={'margin-bottom': '20px'}),
                ],
                style={
                    'background-color': '#f9fafb',
                    'width': '25%',
                    'display': 'flex',
                    'flex-direction': 'column',
                    'align-items': 'flex-start',
                    'padding': '20px',
                    'min-height': '91vh',
                    'border-right': '1px solid black',
                    'border-left': '1px solid black',
                    'min-height': '91vh',
                }
            ),
            html.Div(
                children=[
                
                    html.Div(id='output-data-upload', style={'margin-top': '20px'}),  
                    
                    
                    dcc.Graph(
                        id='graph',
                        figure={
                            'data': [],
                            'layout': go.Layout(
                                title='Empty Figure',
                                xaxis={'title': 'X-Axis'},
                                yaxis={'title': 'Y-Axis'}
                            )
                        },
                        style={
                            'height': '500px',
                            'width': '100%',
                            'margin-top': 'auto',
                            'margin-bottom': '0',
                        }
                    )
                ],
                style={
                    'background-color': '#f9fafb',
                    'width': '75%',
                    'display': 'flex',
                    'flex-direction': 'column',
                    'justify-content': 'flex-end',
                    'min-height': '91vh',
                }
            )
        ], style={'display': 'flex', 'align-items': 'center'}),



          
html.Div(
    children=[
        html.Div(id='output-data-upload', style={'margin-top': '20px'}),
        dcc.Graph(
            id='graph',
            figure={
                'data': [],
                'layout': go.Layout(
                    title='Empty Figure',
                    xaxis={'title': 'X-Axis'},
                    yaxis={'title': 'Y-Axis'}
                )
            },
            style={
                'height': '500px',
                'width': '100%',
                'margin-top': 'auto',
                'margin-bottom': '0',
            }
        )
    ],
    style={
        'background-color': '#f9fafb',
        'width': '75%',
        'display': 'flex',
        'flex-direction': 'column',
        'justify-content': 'flex-end',
        'min-height': '91vh',
    }
)




if __name__ == "__main__":
    app.run_server(debug=False , host='0.0.0.0', port=8050)








