from sqlalchemy import create_engine, text
import os
#db_connection_string = "mysql+pymysql://4rimpv3zph4n9qaa5d89:pscale_pw_4hBLl85dYiAE2Ddth4Nxu5mKlmtsIM9WALzhkksYu68@aws-ap-southeast-2.connect.psdb.cloud/kgolf?charset=utf8mb4"
#TODO: make this connection string a envrionment variable on hosting side.
#then do this instead
# import os
db_connection_string = os.environ['DB_CONNECTION_STRING']

engine = create_engine(
    db_connection_string,
    connect_args={
        "ssl": {
            "ssl_ca": "/etc/ssl/cert.pem"
        }
    })

# with engine.connect() as conn:
#     result = conn.execute(text("select * from Bay"))
    
#     result_dict = [b._asdict() for b in result.all()]    
#     print(result_dict)

def get_bays():
    with engine.connect() as conn:
        result = conn.execute(text("select * from Bay"))        
        bays = [b._asdict() for b in result.all()]  
        return bays