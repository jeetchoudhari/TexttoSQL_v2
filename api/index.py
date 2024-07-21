from flask import Flask, request, jsonify
from flask_cors import CORS
import pandas as pd
from dotenv import load_dotenv
import google.generativeai as genai
import pandasql as ps
import os

app = Flask(__name__)
CORS(app)

# Load environment variables
load_dotenv()

# Configure GenAI key
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# Function to load Google Gemini Model and provide queries as response
def get_gemini_response(question, prompt):
    model = genai.GenerativeModel('gemini-pro')
    response = model.generate_content([prompt[0], question])
    return response.text

# Function to retrieve query from the DataFrame using eval
def read_sql_query(sql, df):
    try:
        result_df = ps.sqldf(sql, locals())
        return result_df
    except Exception as e:
        return pd.DataFrame(), f"Query error: {e}"

@app.route('/')
def home():
    return 'Hello, Flask!'

@app.route('/upload', methods=['POST'])
def upload():
    if 'file' not in request.files:
        return jsonify({"message": "No file part"}), 400
    
    file = request.files['file']
    
    if file.filename == '':
        return jsonify({"message": "No selected file"}), 400
    
    if 'transcription' not in request.form:
        return jsonify({"message": "No transcription query"}), 400
    
    transcription = request.form['transcription']

    if file and file.filename.endswith('.csv'):
        # Read the CSV file into a DataFrame
        df = pd.read_csv(file)
        df_name = "df"

        # Dynamically create the prompt based on the DataFrame columns
        columns = ', '.join(df.columns)
        prompt = [
            f"""
            You are an expert in converting English questions to SQL query!
            The SQL database has the name {df_name} and has the following columns - {columns}.

            For example:
            Example 1 - How many entries of records are present?, the SQL command will be something like this:
            SELECT COUNT(*) FROM {df_name};

            Example 2 - Tell me all the entries where {df.columns[0]} is equal to "value", the SQL command will be something like this:
            SELECT * FROM {df_name} WHERE {df.columns[0]}="value";

            Please do not include ``` at the beginning or end and the SQL keyword in the output.
            """
        ]

        response = get_gemini_response(transcription, prompt)

        sql_query = response.strip().split(';')[0].strip()
        try:
            result = read_sql_query(sql_query, df)
            data = result.to_dict(orient='records')  # Convert DataFrame to JSON-compatible format
        except Exception as e:
            return jsonify({"message": "Query error", "error": str(e)}), 500
        
        return jsonify({"message": "File successfully uploaded and processed", "data": data}), 200
    
    return jsonify({"message": "Invalid file format"}), 400

if __name__ == '__main__':
    app.run(debug=True)
