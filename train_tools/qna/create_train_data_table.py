import pymysql

import configparser

config = configparser.ConfigParser()
config.read('config/DatabaseConfig.ini') # DB 접속 정보 불러오기


db = None
try:
    db = pymysql.connect(
        host=config['DEFAULT']['DB_HOST'].replace('"', ''),
        user=config['DEFAULT']['DB_USER'].replace('"', ''),
        passwd=config['DEFAULT']['DB_PASSWORD'].replace('"', ''),
        db=config['DEFAULT']['DB_NAME'].replace('"', ''),
        charset='utf8'
    )

    # 테이블 생성 sql 정의
    sql = '''
        CREATE TABLE IF NOT EXISTS `chatbot_train_data` (
        `id` INT UNSIGNED NOT NULL AUTO_INCREMENT,
        `intent` VARCHAR(45) NULL,
        `ner` VARCHAR(1024) NULL,
        `query` TEXT NULL,
        `answer` TEXT NOT NULL,
        `answer_image` VARCHAR(2048) NULL,
        PRIMARY KEY (`id`))
    ENGINE = InnoDB DEFAULT CHARSET=utf8
    '''

    # 테이블 생성
    with db.cursor() as cursor:
        cursor.execute(sql)

except Exception as e:
    print(e)

finally:
    if db is not None:
        db.close()