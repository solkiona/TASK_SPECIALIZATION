# import secrets
# secretKey = secrets.token_hex(32)

# print(secretKey)
from flask import Flask
app = Flask(__name__)
import os
basedir = os.path.abspath(os.path.dirname(__file__))

dir = os.path.join(basedir,'static', 'uploads')

lasdir = os.path.join(dir, 'file.txt')
print(lasdir)