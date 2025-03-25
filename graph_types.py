from dash import Input, Output, State
import plotly.graph_objs as go
from utils import parse_data

def register_callbacks(app):
    @app.callback(
        Output('graph', 'figure'),
        [
            Input('x-column', 'value'),
            Input('y-column', 'value'),
            Input('graph-type', 'value'),
            Input('upload-data', 'contents'),
        ],
        State('upload-data', 'filename')
    )
    def update_graph(x_column, y_column, graph_type, contents, filename):
        
        global global_df
        global_df = None

        if contents is not None:
            global_df = parse_data(contents, filename)  

        
        if global_df is None or x_column is None or y_column is None or global_df.empty:
            return go.Figure()

        
        if graph_type == 'scatter':
            fig = go.Figure(
                data=[
                    go.Scatter(
                        x=global_df[x_column],
                        y=global_df[y_column],
                        mode='markers',
                        marker=dict(size=10, color='blue'),
                    )
                ],
                layout=go.Layout(
                    title="Scatter Plot",
                    xaxis_title=x_column,
                    yaxis_title=y_column
                )
            )
        elif graph_type == 'bar':
            fig = go.Figure(
                data=[
                    go.Bar(
                        x=global_df[x_column],
                        y=global_df[y_column],
                        marker=dict(color='blue'),
                    )
                ],
                layout=go.Layout(
                    title="Bar Chart",
                    xaxis_title=x_column,
                    yaxis_title=y_column
                )
            )
        elif graph_type == 'line':
            fig = go.Figure(
                data=[
                    go.Scatter(
                        x=global_df[x_column],
                        y=global_df[y_column],
                        mode='lines',
                        line=dict(color='blue', width=2),
                    )
                ],
                layout=go.Layout(
                    title="Line Chart",
                    xaxis_title=x_column,
                    yaxis_title=y_column
                )
            )
        elif graph_type == 'area':
            fig = go.Figure(
                data=[
                    go.Scatter(
                        x=global_df[x_column],
                        y=global_df[y_column],
                        fill='tozeroy',
                        mode='lines',
                        line=dict(color='blue', width=2),
                    )
                ],
                layout=go.Layout(
                    title="Area Chart",
                    xaxis_title=x_column,
                    yaxis_title=y_column
                )
            )
        elif graph_type == 'box':
            fig = go.Figure(
                data=[
                    go.Box(
                        y=global_df[y_column],
                        name=y_column,
                        boxpoints='all',
                        marker=dict(color='blue'),
                    )
                ],
                layout=go.Layout(
                    title="Box Plot",
                    yaxis_title=y_column
                )
            )
        elif graph_type == 'violin':
            fig = go.Figure(
                data=[
                    go.Violin(
                        y=global_df[y_column],
                        name=y_column,
                        box_visible=True,
                        meanline_visible=True,
                        marker=dict(color='blue'),
                    )
                ],
                layout=go.Layout(
                    title="Violin Plot",
                    yaxis_title=y_column
                )
            )
        elif graph_type == 'histogram':
            fig = go.Figure(
                data=[
                    go.Histogram(
                        x=global_df[x_column],
                        marker=dict(color='blue'),
                    )
                ],
                layout=go.Layout(
                    title="Histogram",
                    xaxis_title=x_column,
                    yaxis_title="Frequency"
                )
            )
        elif graph_type == 'pie':
            fig = go.Figure(
                data=[
                    go.Pie(
                        labels=global_df[x_column],
                        values=global_df[y_column],
                        hole=0.3,
                    )
                ],
                layout=go.Layout(
                    title="Pie Chart",
                )
            )
        else:
            fig = go.Figure()

        return fig

