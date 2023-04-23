from fastapi import FastAPI
import modal

app = FastAPI()
stub = modal.Stub("img-fusion")