import requests
import json

class AIChallenge:
    URL = "https://eventretrieval.one/api/v2"
    PAYLOAD = {}
    USERNAME = ""
    PASSWORD = ""
    SESSION_ID = ""
    EVALUATION_ID = ""
    STATUS = ""

    def __init__(self) -> None:
        pass

    def log(self, payload) -> None:
        with open("/Users/letri/Downloads/AIC/current_session.log", "a") as log_session:
            json.dump(payload, log_session, indent = 4)
            log_session.write('\n')

    def load_session(self, login_session) -> bool:
        try:
            with open(login_session, "r") as session:
                data = json.load(session)
                self.USERNAME = data["username"]
                self.PASSWORD = data["password"]
                self.SESSION_ID = data["session_id"]
                self.EVALUATION_ID = data["evaluation_id"]
                return True
        except:
            return False

    def save_session(self, login_session) -> bool:
        self.PAYLOAD = {
            "username": self.USERNAME,
            "password": self.PASSWORD,
            "session_id": self.SESSION_ID,
            "evaluation_id": self.EVALUATION_ID
        }

        try:
            with open(login_session, "w") as session:
                json.dump(self.PAYLOAD, session, indent = 4)
                return True
        except:
            return False  
    
    def login(self, username, password) -> bool:
        LOGIN_URL = f'{self.URL}/login'
        self.USERNAME = username
        self.PASSWORD = password
        PAYLOAD = {
            "username": f'{self.USERNAME}',
            "password": f'{self.PASSWORD}'
        }

        try:
            login_respone = requests.post(LOGIN_URL, json = PAYLOAD)
            assert login_respone.status_code == 200
            login_respone_data = login_respone.json()
            self.SESSION_ID = login_respone_data['sessionId']
            return True
        except:
            return False
    
    def get_evaluation_ids(self) -> list:
        EVALUATION_URL = f'{self.URL}/client/evaluation/list?session={self.SESSION_ID}'
        
        try:
            get_evaluation_respone = requests.get(EVALUATION_URL)
            assert get_evaluation_respone.status_code == 200
            get_evaluation_respone_data = get_evaluation_respone.json()
            available_evaluation_ids = [evaluation['id'] for evaluation in get_evaluation_respone_data]
            return available_evaluation_ids
        except:
            return []
        
    def pick_evaluation_id(self) -> bool:
        try:
            available_evaluation_ids = self.get_evaluation_ids()
            msg = f'{available_evaluation_ids}\n{[choice for choice in range(len(available_evaluation_ids))]}\n> '

            while True: # check valid user pick
                try:
                    user_pick = int(input(msg))
                    assert user_pick >= 0 and user_pick < len(available_evaluation_ids)
                    break
                except:
                    print("Please enter valid evaluation_id")
            self.EVALUATION_ID = available_evaluation_ids[user_pick]
            return True
        except:
            return False
    
    def assign_evaluation_id(self, evaluation_id) -> None:
        self.EVALUATION_ID = evaluation_id

    def qa(self, answer, video, time) -> json:
        qa_query = {
            "answerSets": [
                {
                "answers": [
                    {
                    "text": f'{answer}-{video}-{time}'
                    }
                ]
                }
            ]
        }
        return qa_query
    
    def kis(self, video, time) -> json:
        kis_query = {
            "answerSets": [
                {
                "answers": [
                    {
                    "mediaItemName": f'{video}',
                    "start": f'{time}',
                    "end": f'{time}'
                    }
                ]
                }
            ]
        }
        return kis_query

    def submit(self, payload):
        SUBMIT_URL = f'{self.URL}/submit/{self.EVALUATION_ID}?session={self.SESSION_ID}'
        
        try:
            submit_response = requests.post(SUBMIT_URL, json = payload)
            submit_response.raise_for_status()  # Raise an exception for HTTP errors
            submit_response_data = submit_response.json()
            self.STATUS = submit_response_data
        except requests.exceptions.RequestException as e:  # Catch HTTP errors
            error_payload = {
                "error": "Submission failed",
                "reason": str(e),
                "payload": payload
            }
            self.log(error_payload)
            self.STATUS = "Submission failed"
        except Exception as e:  # Catch any other errors
            error_payload = {
                "error": "Unexpected error during submission",
                "reason": str(e),
                "payload": payload
            }
            self.log(error_payload)
            self.STATUS = "Submission failed"
        
    def status(self):
        return self.STATUS
        
    
USIT = AIChallenge()
login_session = "login_session.json"

# try:
#     USIT.load_session(login_session)
#     assert len(USIT.get_evaluation_ids()) != 0
#     USIT.pick_evaluation_id()
# except:
#     USIT.login("team68", "chCBfUGL6E")
#     USIT.pick_evaluation_id()
#     USIT.save_session(login_session)

# USIT.submit(USIT.kis("L03_V006", "876000"))
# USIT.submit(USIT.qa("6", "L01_V010", "177360"))