import traceback
try:
    from app import create_app
    from config import Config
    app = create_app(Config)
    print("App created successfully")
except Exception as e:
    with open('error_log.txt', 'w') as f:
        traceback.print_exc(file=f)
