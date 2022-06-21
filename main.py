from ast import Global
from email import header
from posixpath import split
from signal import signal
from urllib import response
from xml.dom import NotFoundErr
from elasticsearch import Elasticsearch
from fastapi import FastAPI, File, UploadFile, Request, WebSocket
from typing import Optional
from fastapi.middleware.cors import CORSMiddleware
from numpy import sign
from requests import Response
from starlette.responses import FileResponse, JSONResponse, StreamingResponse
import json 
import jwt
from fastapi.encoders import jsonable_encoder
from transcribe_long_audio import transcribe_gcs


USER_ID = 1
TRANSCRIPT_ID = 0
SECRET_KEY = "kasApiToken"
ALGORITHM ="HS256"
ACCESS_TOKEN_EXPIRES_MINUTES = 800

app = FastAPI()

origins = [
    "*"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True, 
    allow_methods=['*'],
    allow_headers=['*']
)

elastic = Elasticsearch(hosts=["http://localhost:9200"])
favicon_path = 'favicon.ico'


@app.post("/{index_name}")
async def index_creation(index_name : str):
    elastic.indices.create(index=index_name, ignore = 400)  


@app.get("/favicon.ico")
async def favicon():
    return FileResponse(favicon_path)

@app.post("/create-user/{index_name}/")
def user_creation(index_name : str, email:str, username: str, password: str):
     user = {
        "email": email, 
        "username": username,
        "password": password
     }
     global USER_ID
     USER_ID += 1
     elastic.index(index=index_name, id=USER_ID, body=user)



@app.get("/availabledata")
def get_all_data(index_name : str):
    result = elastic.search(index = index_name, body={
            "query": {
                "match_all": {}
            }
        })
    return result


@app.get("/{index_name}/")
def get_user_credentials(index_name : str,  email : str, username : str, password: str):
    result = elastic.search(index = index_name, body={
            "query": {
                "match": {
                    "username" : {
                        "query": username
                    }
                }
            }
        })

    
    if len(result['hits']['hits']) > 0: 
        output =  result['hits']['hits'][0]["_source"]  
        if output["email"] == email and output["password"]== password:
            return jsonable_encoder(output)
        else: 
            return NotFoundErr()    
    else:
        return {"404" : "Not Found"}



@app.get("/check-connexion")
def check_connexion(email: str,username:str, password: str):
    data = get_user_credentials('database_users',email, username, password)
    if (data == {"404" : "Not Found"}):
        return data
    if len(data) >0: 
        encoded_jwt = jwt.encode(data, SECRET_KEY, ALGORITHM)
        return json.dumps({"token": encoded_jwt})
    else:
        return {'404' :'Not found'}    


@app.post("/store-transcription/{index_name}/")
async def transcription_storage(index_name: str, title: str, content:str):       
    transcription = {
            "title" : title,
            "content" : content
        }
    global TRANSCRIPT_ID
    TRANSCRIPT_ID = TRANSCRIPT_ID +1
    elastic.index(index=index_name, id=TRANSCRIPT_ID, body=transcription)  
       

def parse_data(data) : 
    output = []
    if 'hits' in data:
        for x in data['hits']['hits']:
            output.append(x['_source'])
    return output

@app.get("/stored_transcriptions")
async def stored_transcriptions(index_name: str):
    data = elastic.search(index = index_name, body={
            "query": {
                "match_all": {}
            }
        })
    if data:
        return parse_data(data)
    else:
        return {"data" : "allo quoi"}        
    

@app.get("/transcription")
def transcribe_audio(public_url : str):
    print(public_url)
    output = transcribe_gcs(public_url)
    if (len(public_url) > 0):
        return  output
    else:
        return {'404': 'Not Found'}    
   