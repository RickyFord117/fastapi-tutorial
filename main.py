from fastapi import FastAPI, File, UploadFile, HTTPException
from pydantic import BaseModel
from typing import List
import os

import pandas as pd
import json

app = FastAPI()

# Allowed file extensions
ALLOWED_EXTENSIONS = {"csv", "json", "txt"}

class User(BaseModel):
  name: str
  age: int
  email: str

@app.post("/register")
def register_user(user: User):
  return {"message": f"User {user.name} registered successfully!", "data": user}

@app.post("/register_multiple")
async def register_multiple_files(files: List[UploadFile] = File(...)):
  file_details = []
  for file in files:
    file_location = f"uploads/{file.filename}"
    with open(file_location, "wb") as f:
      f.write(await file.read())
    file_details.append({"filename": file.filename, "location": file_location})
  return {"message": "Files uploaded successfully!", "file_details": file_details}

@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
  file_locaton = f"uploads/{file.filename}"
  with open(file_locaton, "wb") as f:
    f.write(await file.read())
  return {"message": f"File '{file.filename}' saved at {file_locaton}"}

@app.get("/")
def read_root():
  return {"mesaage": "Hello FastAPI!"}

@app.get("/greet/{name}")
def greet(name: str, age: int = None):
  if age:
    return {"message": f"Hello {name}, you are {age} years old!"}
  return {"message": f"Hello {name}!"}

@app.post("/upload_training_data")
async def upload_training_data(files: List[UploadFile] = File(...)):
  uploaded_files = []

  for file in files:
    file_extension = file.filename.split(".")[-1].lower()

    # validate file extension
    if file_extension not in ALLOWED_EXTENSIONS:
      raise HTTPException(status_code=400, detail=f"File type {file_extension} not allowed. Only CSV, JSON or TXT is accepted")
    
    # save file
    file_location = f"training_data/{file.filename}"
    os.makedirs("training_data", exists_ok=True) # ensure directory exists
    with open(file_location, "wb") as f:
      f.write(await file.read())

    uploaded_files.append({"filename": file.filename, "location": file_location})

    return {"message": "Files uploaded successfully!", "file_details": uploaded_files}
  
def process_training_data(file_path: str):
  file_extension = file_path.split(".")[-1].lower()

  if file_extension == "csv":
    return pd.read_csv(file_path).to_dict() # convert csv to dictionary
  elif file_extension == "json":
    with open(file_path, "r", encoding="utf-8") as f:
      return json.load(f) # read json
  elif file_extension == "txt":
    with open(file_path, "r", encoding="utf-8") as f:
      return f.read() # read text as string
  else:
    raise ValueError(f"File type {file_extension} not allowed")