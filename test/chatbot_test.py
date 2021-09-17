import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))

import configparser

config = configparser.ConfigParser()
config.read('config/DatabaseConfig.ini') # DB 접속 정보 불러오기

from uts.Database import Database
from uts.Preprocess import Preprocess

# 전처리 객체 생성
p = Preprocess(word2index_dic='train_tools/dict/chatbot_dict.bin',
               userdic='uts/user_dic.tsv')

# 질문/답변 학습 DB 연결 객체 생성
db = Database(
    host=config['DEFAULT']['DB_HOST'].replace('"', ''), user=config['DEFAULT']['DB_USER'].replace('"', ''), password=config['DEFAULT']['DB_PASSWORD'].replace('"', ''), db_name=config['DEFAULT']['DB_NAME'].replace('"', '')
)
db.connect()  # DB 연결

# 원문
query = input()

# 의도 파악
from models.intent.IntentModel import IntentModel
intent = IntentModel(model_name='models/intent/intent_model.h5', preprocess=p)
predict = intent.predict_class(query)
intent_name = intent.labels[predict]

# 개체명 인식
from models.ner.NerModel import NerModel
ner = NerModel(model_name='models/ner/ner_model.h5', preprocess=p)
predicts = ner.predict(query)
ner_tags = ner.predict_tags(query)

print("질문 : ", query)
print("=" * 40)
print("의도 파악 : ", intent_name)
print("개체명 인식 : ", predicts)
print("답변 검색에 필요한 NER 태그", ner_tags)
print("=" * 40)

# 답변 검색
from uts.FindAnswer import FindAnswer

try:
    f = FindAnswer(db)
    answer_text, answer_image = f.search(intent_name, ner_tags)
    answer = f.tag_to_word(predicts, answer_text)
except:
    answer = "죄송해요, 무슨 말인지 모르겠어요."

print("답변 : ", answer)

db.close()  # DB 연결 끊음