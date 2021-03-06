import json
import plotly
import pandas as pd

from flask import Flask
from flask import render_template, request, jsonify
import joblib


import plotly.express as px
import dash
import dash_core_components as dcc
import dash_html_components as html

from sqlalchemy import create_engine

from wrangle_graphs import return_graphs

app = Flask(__name__)

# load data
engine = create_engine('sqlite:///../data/sparkify.db')
df = pd.read_sql_table('user_table', engine)

# individual days listened
days_list_median = int(df.days_listened.median())
songs_per_day_median = int(df.songs_per_day.median())
number_customers = df.userId.nunique()

# index webpage displays cool visuals and receives user input text for model
@app.route('/')
@app.route('/index')
def index():
    graphs = return_graphs(df)

    # encode plotly graphs in JSON
    ids = ["graph-{}".format(i) for i, _ in enumerate(graphs)]
    graphJSON = json.dumps(graphs, cls=plotly.utils.PlotlyJSONEncoder)

    # render web page with plotly graphs
    return render_template('master.html',
        ids=ids, graphJSON=graphJSON,
        number_customers=number_customers,
        days_list_median=days_list_median,
        songs_per_day_median=songs_per_day_median
        )

# web page that handles user query and displays customer results
@app.route('/go')
def go():
    # save user input in query
    query = request.args.get('query', '')
    try:
        int(query)
    except ValueError:
        return render_template(
            'go.html',
            query=query,
            error=1
        )
    else:
        days_list_user = df[df.userId == int(query)].days_listened.iloc[0]
        days_list_median = int(df.days_listened.median())
        songs_per_day_user = df[df.userId == int(query)].songs_per_day.iloc[0]
        churn_proba = round(df[df.userId == int(query)].probability.iloc[0], 2)

        return render_template(
            'go.html',
            number_customers=number_customers,
            query=query,
            days_list_median=days_list_median,
            days_list_user=days_list_user,
            days_list_user_share=int((days_list_user/days_list_median)*100),
            songs_per_day_median=songs_per_day_median,
            songs_per_day_user=int(songs_per_day_user),
            songs_per_day_user_share=int((songs_per_day_user/songs_per_day_median)*100),
            churn_proba=int(churn_proba*100)
        )

def main():
    app.run(host='0.0.0.0', port=3001, debug=True)

if __name__ == '__main__':
    main()
