from langfuse.callback import CallbackHandler

def check():
    langfuse_handler = CallbackHandler()
    lf = langfuse_handler.auth_check()
    
    return {"langfuse": lf}