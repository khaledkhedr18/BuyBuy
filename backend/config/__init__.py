import os

# Only import pymysql for local development with MySQL
# Railway uses PostgreSQL, so we don't need this there
if not os.environ.get('RAILWAY_ENVIRONMENT') and not os.environ.get('DATABASE_URL'):
    try:
        import pymysql
        pymysql.install_as_MySQLdb()
    except ImportError:
        pass  # pymysql not available, probably using PostgreSQL
