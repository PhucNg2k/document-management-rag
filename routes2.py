import os
import tempfile
import shutil  
<<<<<<< HEAD:flask_app.py
from flask import Flask, jsonify, request, render_template, redirect, url_for
=======
from flask import Blueprint, jsonify, request, render_template
>>>>>>> 949eb90fc113c2f81610069fc66bbb434a346ecc:routes2.py
from elasticsearch import Elasticsearch
from datetime import datetime
from langchain.text_splitter import RecursiveCharacterTextSplitter
from read_data.kotaemon.loaders import *
from llama_index.core.readers.json import JSONReader
from llama_index.readers.file import PandasCSVReader, UnstructuredReader

es = Elasticsearch('https://localhost:9200', basic_auth=("elastic", "*VHP8vPHOY4tI5yVad_n"), verify_certs=False)

text_splitter = RecursiveCharacterTextSplitter.from_tiktoken_encoder(
    chunk_size=256,
    chunk_overlap=50
)

main_blueprint = Blueprint('main', __name__)

def get_extractor(file_name: str):
    
    map_reader = {
        "docx": DocxReader(),
        "html": UnstructuredReader(),
        "csv": PandasCSVReader(pandas_config=dict(on_bad_lines="skip")),
        "xlsx": PandasExcelReader(),
        "json": JSONReader(),
        "txt": TxtReader()
    }
    return map_reader[ os.path.splitext(file_name)[1][1:]]

<<<<<<< HEAD:flask_app.py
app = Flask(__name__)
es = Elasticsearch('https://localhost:9200', basic_auth=("elastic", "J-E+YAAiYGPEVHboST=o"), verify_certs=False)

=======
>>>>>>> 949eb90fc113c2f81610069fc66bbb434a346ecc:routes2.py
def create_index(index_name='documents'):
    if not es.indices.exists(index=index_name):
        es.indices.create(index=index_name, body={
            "mappings": {
                "properties": {
                    "title": {"type": "text"},
                    "content": {"type": "text"},
                    "topic": {"type":"text"},
                    "datetime": {"type":"text"}
                }
            }
        })

<<<<<<< HEAD:flask_app.py
@app.route('/')
def home_redirect():
    return redirect(url_for('index'))

@app.route('/home', methods=['GET'])
=======
@main_blueprint.route('/home', methods=['GET'])
>>>>>>> 949eb90fc113c2f81610069fc66bbb434a346ecc:routes2.py
def index():
    return render_template('index.html')

@main_blueprint.route('/upload', methods=['POST'])
def upload_documents():
    files = request.files.getlist('files')
    index_name = request.form.get('index_name', 'documents')
    topic = request.form.get('topic', 'general')
    
    if len(files) == 0:
        return jsonify({"error": "No files uploaded"}), 400

    temp_dir = tempfile.mkdtemp()
    print(f"Temporary directory created at: {temp_dir}")
    
    try:
        for file in files:
            
            temp_file_path = os.path.join(temp_dir, file.filename)
            file.save(temp_file_path)
            title = file.filename

            try:
                print(f"Processing file: {file.filename}")
                extractor = get_extractor(file.filename)
                print(f"Load extractor success")
                document = extractor.load_data(temp_file_path)  
                print(f"Load document success")
                splits = text_splitter.split_text(document[0].text)
                print(f"Split document success")
            except Exception as e:
                return jsonify({"error": f"Unsupported file type: {e}"}), 400

            for split in splits:
                body = {
                    'title': title,
                    'content': split,
                    "topic": topic,
                    "datetime": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                }

                try:
                    es.index(index=index_name, body=body)
                except Exception as e:
                    return jsonify({"error": f"Failed to upload file {title}: {str(e)}"}), 500

        return jsonify({"message": f"{len(files)} document(s) uploaded successfully!"}), 201
    finally:
        shutil.rmtree(temp_dir)
        print(f"Temporary directory {temp_dir} deleted")

# Route to search documents
@main_blueprint.route('/search', methods=['POST'])
def search_documents():
    keyword = request.form['keyword']
    index_name = request.form.get('index_name', 'documents')

    body = {
        "query": {
            "multi_match": {
                "query": keyword,
                "fields": ["content", "title"]
            }
        }
    }

    try:
        res = es.search(index=index_name, body=body)
        return jsonify(res['hits']['hits'])
    except Exception as e:
        return jsonify({"error": str(e)}), 500
<<<<<<< HEAD:flask_app.py

if __name__ == '__main__':
    create_index()
    app.run(port=5000, debug=True)


=======
>>>>>>> 949eb90fc113c2f81610069fc66bbb434a346ecc:routes2.py
