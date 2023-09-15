from flask import Flask
import pymysql

import re
import string
import jieba
import codecs
import os
import math
import time
import Correct as correct
from nltk.tokenize import word_tokenize
from collections import Counter

# from flask_cors import *
# from flask import Response,request

app = Flask(__name__)
# CORS(app, supports_credentials=True)


class Database:

  def __init__(self):
    host = "34.66.155.131"
    user = "root"
    password = "CS410project"
    db = "cs410"
    self.con = pymysql.connect(host=host,
                               user=user,
                               password=password,
                               db=db,
                               cursorclass=pymysql.cursors.DictCursor)
    self.cur = self.con.cursor()

  def getLecture(self, weeks):
    sql = "SELECT * FROM cs410.Lecture WHERE Weeks = %s"
    self.cur.execute(sql, (weeks))
    result = self.cur.fetchall()
    return result
  
  def lecture_detail(self, title):
    sql = "SELECT * FROM cs410.Lecture WHERE Title = %s"
    self.cur.execute(sql, (title))
    result = self.cur.fetchall()
    return result

  # 建立倒排索引(单个文件)
  # 输入:fenci.txt
  # 输出:my_index.txt  格式: word [[所在文件，出现次数],[所在文件，出现次数]...]
  def create_inverted_index(filename, page):
    src_data = codecs.open(filename, 'r+', encoding='utf-8').read()  # 必须事先知道文件的编码格式，这里文件编码是使用的utf-8
    # 去除BOM头
    if src_data[:1].encode('utf-8') == codecs.BOM_UTF8:
      src_data = src_data[1:]

    # 建立词表
    sp_data = src_data.split()

    # 词频TF（词在文档中出现的次数）
    words = list(sp_data)
    dic_word_count = Counter(words)

    # 保存在index
    for word in dic_word_count.keys():
      dic_word_count[word] = [int(page), dic_word_count[word]]
      if word in index.keys():
        index[word].append(dic_word_count[word])
      else:
        index[word] = [dic_word_count[word]]
  
  def get_All_Lecture(self):
    sql = "SELECT * FROM cs410.Lecture"
    self.cur.execute(sql)
    result = self.cur.fetchall()
    # 遍历data\\page下的文件
    # 对于每个文件xx.txt，首先分词，将分词结果写入fenci.txt
    # 然后建立倒排索引，将结果与index（总的索引）合并
    print('>>>建立倒排索引')
    fenci_txt = "fenci.txt"
    N = 0
    # path = "data\\page"  # 文件夹目录
    files = get("Subtitle")  # 得到文件夹下的所有文件名称
    N = len(files)
    s = []
    for file in files:  # 遍历文件夹
      if not os.path.isdir(file):  # 判断是否是文件夹，不是文件夹才打开
        # print('>>>处理', file)
        f = codecs.open(fenci_txt, 'w', encoding="UTF-8-SIG")
        for line in open(path + "\\" + file, encoding='utf-8', errors='ignore').readlines():
          # 去标点
          line = re.sub(r"[0-9\s+\.\!\/_,$%^*()?;；:-【】+\"\']+|[+——！，;:。？、~@#￥%……&*（）]+", " ", line)
          # 分词
          seg_list = word_tokenize(line)
          # 写入199801_new.txt
          f.write(" ".join(seg_list) + "\n")
        f.close()
        # 建立倒排索引
        create_inverted_index(fenci_txt, re.sub(r'\D', "", file))

    print('>>>计算tf-idf')
    # 文档频率df（包含词t的文档的总数）
    # w = (1 + log(tf))*log_10(N/df)
    i = 0
    for key in index.keys():
      df = len(index[key])
      i += 1
      for file_tf in index[key]:
        tf = file_tf[1]
        w = (1.0 + math.log(tf)) * math.log10(N / df)
        file_tf.append(w)

    # print('>>>保存到my_index.txt')
    # with codecs.open("my_index.txt", 'w', encoding="UTF-8-SIG") as i:
    #     for key in index.keys():
    #         i.write(key + str(index[key]) + "\n")

    def search(query):
      time_start = time.time()
      query = re.sub(r"[0-9\s+\.\!\/_,$%^*()?;；:-【】+\"\']+|[+——！，;:。？、~@#￥%……&*（）]+", " ", query)
      # 分词
      fenci = word_tokenize(query)

      pages = {}
      for word in fenci:
        if word in index:
          for page in index[word]:
            if page[0] in pages:
              pages[page[0]] += page[2]
            else:
              pages[page[0]] = page[2]

      page_list = sorted(pages.items(), key=lambda item: item[1], reverse=True)
      time_end = time.time()
      len_page_list = len(page_list)
      if len_page_list != 0:
        if len_page_list <= 10:
          print("搜索【%s】，为您找到%d条结果(用时%.6f秒)：" % (query, len_page_list, time_end - time_start))
          i = 1
          for page in page_list:
            print("%d:%d.txt, tf-idf=%f" % (i, page[0], page[1]))
            i += 1
        else:
          print("搜索【%s】，为您找到%d条结果(用时%.6f秒)：" % (query, len_page_list, time_end - time_start))
          i = 1
          for page in page_list:
            print("%d:%d.txt, tf-idf=%f" % (i, page[0], page[1]))
            i += 1
            if i == 11:
              yes = input("已显示前10条，是否显示所有？[y/n]")
              if yes == 'n':
                break
      else:
        print("无结果")

    return result

    
#   def test(self):
#     sql = "select * from testDB.Unit"
#     self.cur.execute(sql)
#     result = self.cur.fetchall()
#     return result


# if __name__ == '__main__':
#     app.run(debug=True)
