from django.core.management.base import BaseCommand
from django.db import connection
import psycopg2
import os


class Command(BaseCommand):
    help = 'Test database connection and connectivity'

    def handle(self, *args, **options):
        self.stdout.write("=== Testing Database Connection ===")

        try:
            # Test Django connection
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
                result = cursor.fetchone()
                self.stdout.write(
                    self.style.SUCCESS(f"✅ Django DB connection successful: {result}")
                )

                # Get some basic database info
                cursor.execute("SELECT version()")
                version = cursor.fetchone()[0]
                self.stdout.write(f"Database version: {version}")

                cursor.execute("SELECT current_database()")
                db_name = cursor.fetchone()[0]
                self.stdout.write(f"Connected to database: {db_name}")

                # Test a simple query
                cursor.execute("SELECT NOW()")
                current_time = cursor.fetchone()[0]
                self.stdout.write(f"Server time: {current_time}")

        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f"❌ Django DB connection failed: {e}")
            )

            # Try direct psycopg2 connection for more detailed debugging
            self.test_direct_connection()

    def test_direct_connection(self):
        self.stdout.write("\n=== Testing Direct psycopg2 Connection ===")

        # Connection parameters for Railway cross-project connection
        conn_params = {
            'host': 'nozomi.proxy.rlwy.net',
            'port': 24106,
            'database': 'railway',
            'user': 'postgres',
            'password': 'CalFyXLkugZMUGFHoYEYkRfbGzsmDVxk',
            'sslmode': 'require',
            'connect_timeout': 30
        }

        try:
            conn = psycopg2.connect(**conn_params)
            cursor = conn.cursor()

            cursor.execute("SELECT 1")
            result = cursor.fetchone()
            self.stdout.write(
                self.style.SUCCESS(f"✅ Direct psycopg2 connection successful: {result}")
            )

            cursor.close()
            conn.close()

        except psycopg2.OperationalError as e:
            self.stdout.write(
                self.style.ERROR(f"❌ Direct connection failed: {e}")
            )

            # Try to ping the host
            self.test_network_connectivity()

    def test_network_connectivity(self):
        self.stdout.write("\n=== Testing Network Connectivity ===")
        import socket

        try:
            # Test if we can reach the host and port
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(10)
            result = sock.connect_ex(('nozomi.proxy.rlwy.net', 24106))
            sock.close()

            if result == 0:
                self.stdout.write(
                    self.style.SUCCESS("✅ Network connection to host:port successful")
                )
            else:
                self.stdout.write(
                    self.style.ERROR(f"❌ Cannot reach host:port, error code: {result}")
                )

        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f"❌ Network connectivity test failed: {e}")
            )
