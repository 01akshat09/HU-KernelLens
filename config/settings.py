from dotenv import load_dotenv
import os

load_dotenv()

EMAIL_CONFIG = {
      "from": os.getenv("EMAIL_FROM"),
      "to": os.getenv("EMAIL_TO"),
      "password": os.getenv("EMAIL_PASSWORD")
}

GO_APP_PID = 12858 # Change it according to your application PID