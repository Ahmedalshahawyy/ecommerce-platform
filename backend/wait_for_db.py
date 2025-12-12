import os
import time

from sqlalchemy import create_engine

url = os.getenv("DATABASE_URL", "sqlite:///./ecommerce.db")
timeout = int(os.getenv("DB_WAIT_TIMEOUT", "60"))
interval = 1


def wait_for_db():
    if url.startswith("sqlite"):
        return True
    engine = create_engine(url)
    start = time.time()
    while True:
        try:
            with engine.connect():
                return True
        except Exception as err:
            elapsed = time.time() - start
            if elapsed > timeout:
                raise RuntimeError(
                    f"Timed out waiting for database after {timeout} seconds"
                ) from err
            time.sleep(interval)


if __name__ == "__main__":
    print("Waiting for database...")
    wait_for_db()
    print("Database available")
