from konlpy.tag import Kkma
from konlpy.utils import pprint

kkma = Kkma()

pprint(kkma.nouns(u'이 문장은 형태소 분석 테스트용 문장이얌! ㅎㅎ'))