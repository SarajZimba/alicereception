import sys
sys.dont_write_bytecode = True


from root.main import app


if __name__ == "__main__":
    app.run(host="0.0.0.0",debug=True,port=8002)    
