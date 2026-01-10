import uvicorn

if __name__ == "__main__":
    # Since main.py is inside 'src', we refer to the app relative to the root if src is in path
    # OR we use 'presentation.app:app' if we are inside 'src'
    uvicorn.run("presentation.app:app", host="0.0.0.0", port=8000, factory=False)
