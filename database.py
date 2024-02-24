from sqlalchemy import create_engine, text
import os

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