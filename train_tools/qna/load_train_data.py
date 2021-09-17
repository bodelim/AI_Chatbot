import pymysql
import openpyxl

import configparser
from sshtunnel import SSHTunnelForwarder

config = configparser.ConfigParser()
config.read('config/DatabaseConfig.ini') # DB 접속 정보 불러오기

print(config['DEFAULT']['DB_NAME'])

# 학습 데이터 초기화
def all_clear_train_data(db):
    # 기존 학습 데이터 삭제
    sql = '''
        delete from chatbot_train_data
    '''
    with db.cursor() as cursor:
        cursor.execute(sql)

    # auto increment 초기화
    sql = '''
        ALTER TABLE chatbot_train_data AUTO_INCREMENT=1
    '''
    with db.cursor() as cursor:
        cursor.execute(sql)


# db에 데이터 저장
def insert_data(db, xls_row):
    intent, ner, query, answer, answer_img_url = xls_row

    sql = '''
        INSERT chatbot_train_data(intent, ner, query, answer, answer_image)
        values(
            '%s', '%s', '%s', '%s', '%s'
        )
    ''' % (intent.value, ner.value, query.value, answer.value, answer_img_url.value)

    # 엑셀에서 불러온 cell에 데이터가 없는 경우 null로 치환
    sql = sql.replace("'None'", "null")

    with db.cursor() as cursor:
        cursor.execute(sql)
        print('{} 저장'.format(query.value))
        db.commit()



# SSH address mapping setup (not actually connects)
tunnel = SSHTunnelForwarder((config['DEFAULT']['SSH_HOST'].replace('"', ''), int(config['DEFAULT']['SSH_PORT'].replace('"', ''))),  # SSH hosting server
                            ssh_username=config['DEFAULT']['SSH_USER'].replace('"', ''),
                            ssh_password=config['DEFAULT']['SSH_PASSWORD'].replace('"', ''),
                            remote_bind_address=(config['DEFAULT']['SSH_HOST'].replace('"', ''), 3306))    # mapping addr which python will access

# connect and map remote addr to local addr
tunnel.start()


train_file = 'D:\Programming\Project\Python\AI_Chatbot\\train_tools\qna\\train_data.xlsx'
db = None
try:
    db = pymysql.connect(
        host=config['DEFAULT']['DB_HOST'].replace('"', ''),
        user=config['DEFAULT']['DB_USER'].replace('"', ''),
        passwd=config['DEFAULT']['DB_PASSWORD'].replace('"', ''),
        db=config['DEFAULT']['DB_NAME'].replace('"', ''),
        charset='utf8'
    )

    # 기존 학습 데이터 초기화
    all_clear_train_data(db)

    # 학습 엑셀 파일 불러오기
    wb = openpyxl.load_workbook(train_file)
    sheet = wb['Sheet1']
    for row in sheet.iter_rows(min_row=2):  # 헤더는 불러오
        # 데이터 저장
        insert_data(db, row)

    wb.close()

except Exception as e:
    print(e)

finally:
    if db is not None:
        db.close()