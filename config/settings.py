from dotenv import load_dotenv
import os

load_dotenv()

EMAIL_CONFIG = {
      "from": os.getenv("EMAIL_FROM"),
      "to": os.getenv("EMAIL_TO"),
      "password": os.getenv("EMAIL_PASSWORD")
}

GO_APP_PID = 2946 # Change it according to your application PID



######################


INFLUX_URL = os.getenv("INFLUX_URL")
INFLUX_TOKEN = os.getenv("INFLUX_TOKEN")
INFLUX_ORG = os.getenv("INFLUX_ORG")
INFLUX_BUCKET = os.getenv("INFLUX_BUCKET")
