from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base
import os
import logging 
logger = logging.getLogger("pst.{}".format(os.path.basename(__file__)))

try:


    db_connect_string = "postgresql+psycopg2://{user}:{passwd}@{server}:{port}/{db}".format(user="postgres",
                                                                                        passwd="abcd1234",
                                                                                        server="postgres-db.bdf-cloud.iqvia.net",#
                                                                                        #server="10.91.194.165",
                                                                                        db="pstshard_primary_postgres", port="5432",pool_size=50, max_overflow=10)
                                                                                        
                                                                                        

                                                                                 
                                                                                                                                                                               
    prefix = __file__.split("/")[0:-5]  
    postfix = 'src/aiml_post_covid_care/utils/database_connect/certificates'
    prefix = os.path.join("/".join(prefix),postfix)                                                                                    
    ssl_args = {
        "sslmode": "require",
        "sslcert": os.path.join(prefix, "server.crt"),
        "sslkey": os.path.join(prefix, "server.key"),
        "sslrootcert": os.path.join(prefix, "root.crt"),
    }
    print("certificate path:",prefix)
    
    
    #db_connect_string = "postgresql+psycopg2://{user}:{passwd}@{server}:{port}/{db}".format(user="pst",
    #                                                                                         passwd="password",
    #                                                                                         server="localhost",
    #                                                                                         db="pst", port="5432")
    #engine = create_engine(db_connect_string)

    logger.info("creating engine")
    engine = create_engine(db_connect_string, connect_args=ssl_args)
    logger.info("creating db session")
    db_session = scoped_session(sessionmaker(autocommit=False,
                                                autoflush=False,
                                                bind=engine))
    logger.info("declaring base")
    Base = declarative_base()
    Base.query = db_session.query_property()

    Base.metadata.create_all(bind=engine)

    print("SQLAlchemy connection success....")
    logger.info("SQLAlchemy connection success....")
except Exception as E:
    print('Exception Occured: ', E)
    print("SQLAlchemy connection failed....")
    logger.info('Exception Occurred: ', E)
    logger.info("SQLAlchemy connection failed....")
