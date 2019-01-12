#!/usr/local/bin/python3
#_*_coding:utf-8_*_
# NLPによりMatrix Node Graphを生成する
import os,sys,re,json,time,datetime, calendar
import sklearn
import sqlite3
import numpy as np
import pandas as pd
import networkx as nx
from pytz import timezone
from dateutil import parser
import matplotlib.pyplot as plt
import db_operation

# Intension Matrixの生成(意図を分類するための二次元配列)-------------------------------------------------------------------------
def mngMatrix(sentence):
    target = sentence.lower()
    targets = target.split()  # ターゲット情報を空白で区切ってリストにする
    '''x軸=意図, y軸=カテゴリ
    Intension = [
    [                "Anxiety(不安)", "agitation(扇動)", "Publicity(広告)", "Fun(愉快)", "Desire(願望)", "Admire(賞賛)","Obligation(義務)", "Politics(政治)"],
    ["Disaster(災害) ",   0,               0,                0,               0,             0,             0,              0,                0],
    ["Accident(事故) ",   0,               0,                0,               0,             0,             0,              0,                0],
    ["Terrorism(テロ)",   0,               0,                0,               0,             0,             0,              0,                0],
    ["Medical(医療)  ",   0,               0,                0,               0,             0,             0,              0,                0],
    ["Society(社会)  ",   0,               0,                0,               0,             0,             0,              0,                0],
    ["Politics(政治) ",   0,               0,                0,               0,             0,             0,              0,                0],
    ]
    Intension Matrixの実態は上の形の行列だが実際には 0 のセルだけを作成'''
    # 上の行列と同じ構造を持つ意図分類マトリクスを生成
    target_matrix = np.array([
    [0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0]])

    # NLPによる意図マトリクスの生成
    # 辞書(json)の取得と処理
    dict_category = "./dict/category.json"  # カテゴリに関する固有表現辞書(gazetteer:ガゼッティアとも言う)
    dict_intension = "./dict/intension.json"  # 同じく意図に関する辞書
    category = json.load(open(dict_category, encoding='utf-8'))  # カテゴリのjsonを開きdict型に変換(日本語が含まれるのでエンコード)
    intension = json.load(open(dict_intension, encoding='utf-8'))  # 同じく意図のjsonを開く
    
    # パターンマッチング(カテゴリ)
    category_match = {}  # パターンマッチの結果を格納するリスト(辞書型)
    for categories in category.keys():  # カテゴリ名を取得
        category_text = list(category.get(categories))  # そのカテゴリ内の単語を取得
        category_type = set(category_text) & set(targets)  # カテゴリ内の単語とターゲット情報で一致するものを抽出
        category_count = len(list(category_type))  # set型になっているのでリストに変換しマッチした数を格納
        if category_count != 0:  # カテゴリとの一致数が0でなければ
            category_match.update({categories:category_count})  # 特定のカテゴリにマッチした数をそのカテゴリ名と共に格納

    # パターンマッチング(意図)
    intension_match = {}  # パターンマッチの結果を格納するリスト(辞書型)
    for intensions in intension.keys():  # 意図を取得
        intension_text = list(intension.get(intensions))  # その意図の単語を取得
        intension_type = set(intension_text) & set(targets)  # 意図の単語とターゲット情報で一致するものを抽出
        intension_count = len(list(intension_type))  # set型になっているのでリストに変換しマッチした数を格納
        if intension_count != 0:  # 意図との一致数が0でなければ
            intension_match.update({intensions:intension_count})  # 特定の意図にマッチした数をその意図名と共に格納

    # パターンマッチングの結果をマトリクスに反映(ここから冗長なので一考の余地あり)
    if "Disaster" in category_match.keys():  # もしカテゴリが"Disaster"なら
        if "Anxiety" in intension_match.keys():  # そしてもし意図が"Anxiety"なら
            target_matrix[0,0] = intension_match["Anxiety"]  # "DisasterカテゴリのAnxietyの値をパターンマッチから反映"
        if "Agitation" in intension_match.keys():  # 意図が"Agitation"なら
            target_matrix[0,1] = intension_match["Agitation"]  # "DisasterカテゴリのAgitaionの値をパターンマッチから反映"
        if "Publicity" in intension_match.keys():  # 意図が"Publicity"なら
            target_matrix[0,2] = intension_match["Publicity"]  # "DisasterカテゴリのPublicityの値をパターンマッチから反映"
        if "Fun" in intension_match.keys():  # 意図が"Fun"なら
            target_matrix[0,3] = intension_match["Fun"]  # "DisasterカテゴリのFunの値をパターンマッチから反映"
        if "Desire" in intension_match.keys():  # 意図が"Desire"なら
            target_matrix[0,4] = intension_match["Desire"]  # "DisasterカテゴリのDesireの値をパターンマッチから反映"
        if "Admire" in intension_match.keys():  # 意図が"Admire"なら
            target_matrix[0,5] = intension_match["Admire"]  # "DisasterカテゴリのAdmireの値をパターンマッチから反映"
        if "Obligation" in intension_match.keys():  # 意図が"Obligation"なら
            target_matrix[0,6] = intension_match["Obligation"]  # "DisasterカテゴリのObligationの値をパターンマッチから反映"
        if "Politics" in intension_match.keys():  # 意図が"Admire"なら
            target_matrix[0,7] = intension_match["Politics"]  # "DisasterカテゴリのPoliticsの値をパターンマッチから反映"    
    
    if "Accident" in category_match.keys():  # もしカテゴリが"Accident"なら
        if "Anxiety" in intension_match.keys():
            target_matrix[1,0] = intension_match["Anxiety"]
        if "Agitation" in intension_match.keys():
            target_matrix[1,1] = intension_match["Agitation"]
        if "Publicity" in intension_match.keys():
            target_matrix[1,2] = intension_match["Publicity"]
        if "Fun" in intension_match.keys():
            target_matrix[1,3] = intension_match["Fun"]
        if "Desire" in intension_match.keys():
            target_matrix[1,4] = intension_match["Desire"]
        if "Admire" in intension_match.keys():
            target_matrix[1,5] = intension_match["Admire"]
        if "Obligation" in intension_match.keys():
            target_matrix[1,6] = intension_match["Obligation"]
        if "Politics" in intension_match.keys():
            target_matrix[1,7] = intension_match["Politics"]

    if "Terrorism" in category_match.keys():  # もしカテゴリが"Terrorism"なら
        if "Anxiety" in intension_match.keys():
            target_matrix[2,0] = intension_match["Anxiety"]
        if "Agitation" in intension_match.keys():
            target_matrix[2,1] = intension_match["Agitation"]
        if "Publicity" in intension_match.keys():
            target_matrix[2,2] = intension_match["Publicity"]
        if "Fun" in intension_match.keys():
            target_matrix[2,3] = intension_match["Fun"]
        if "Desire" in intension_match.keys():
            target_matrix[2,4] = intension_match["Desire"]
        if "Admire" in intension_match.keys():
            target_matrix[2,5] = intension_match["Admire"]
        if "Obligation" in intension_match.keys():
            target_matrix[2,6] = intension_match["Obligation"]
        if "Politics" in intension_match.keys():
            target_matrix[2,7] = intension_match["Politics"]
        
    if "Medical" in category_match.keys():  # もしカテゴリが"Medical"なら
        if "Anxiety" in intension_match.keys():
            target_matrix[3,0] = intension_match["Anxiety"]
        if "Agitation" in intension_match.keys():
            target_matrix[3,1] = intension_match["Agitation"]
        if "Publicity" in intension_match.keys():
            target_matrix[3,2] = intension_match["Publicity"]
        if "Fun" in intension_match.keys():
            target_matrix[3,3] = intension_match["Fun"]
        if "Desire" in intension_match.keys():
            target_matrix[3,4] = intension_match["Desire"]
        if "Admire" in intension_match.keys():
            target_matrix[3,5] = intension_match["Admire"]
        if "Obligation" in intension_match.keys():
            target_matrix[3,6] = intension_match["Obligation"]
        if "Politics" in intension_match.keys():
            target_matrix[3,7] = intension_match["Politics"]

    if "Society" in category_match.keys():  # もしカテゴリが"Society"なら
        if "Anxiety" in intension_match.keys():
            target_matrix[4,0] = intension_match["Anxiety"]
        if "Agitation" in intension_match.keys():
            target_matrix[4,1] = intension_match["Agitation"]
        if "Publicity" in intension_match.keys():
            target_matrix[4,2] = intension_match["Publicity"]
        if "Fun" in intension_match.keys():
            target_matrix[4,3] = intension_match["Fun"]
        if "Desire" in intension_match.keys():
            target_matrix[4,4] = intension_match["Desire"]
        if "Admire" in intension_match.keys():
            target_matrix[4,5] = intension_match["Admire"]
        if "Obligation" in intension_match.keys():
            target_matrix[4,6] = intension_match["Obligation"]
        if "Politics" in intension_match.keys():
            target_matrix[4,7] = intension_match["Politics"]

    if "Politics" in category_match.keys():  # もしカテゴリが"Politics"なら
        if "Anxiety" in intension_match.keys():
            target_matrix[5,0] = intension_match["Anxiety"]
        if "Agitation" in intension_match.keys():
            target_matrix[5,1] = intension_match["Agitation"]
        if "Publicity" in intension_match.keys():
            target_matrix[5,2] = intension_match["Publicity"]
        if "Fun" in intension_match.keys():
            target_matrix[5,3] = intension_match["Fun"]
        if "Desire" in intension_match.keys():
            target_matrix[5,4] = intension_match["Desire"]
        if "Admire" in intension_match.keys():
            target_matrix[5,5] = intension_match["Admire"]
        if "Obligation" in intension_match.keys():
            target_matrix[5,6] = intension_match["Obligation"]
        if "Politics" in intension_match.keys():
            target_matrix[5,7] = intension_match["Politics"]
    
    # マトリクスの値の正規化
    # 各行に格納されている値をその合計値で割っていくことで行の合計が1になるようにする
    def normalize(target_matrix):
        normalize_row = []  # 正規化されたマトリクスを格納するための配列
        for row in target_matrix:  # マトリクスの各行を順に取得
            div = sum(row)  # その行に格納された値の合計値を取得
            row_3 = [row_2 / div for row_2 in row]  # リスト内包表記を用いてマトリクスの各行内の要素を合計値で割っていく
            normalize_row.append(row_3)  # 正規化した行をリストに追加していく
        normalize_row = np.array(normalize_row)  # リストを配列に変換(下の関数を使うため)
        normalize_row[np.isnan(normalize_row)]= 0  # 欠損値(nan)がある部分を0に変換
        return normalize_row
    normalize_matrix = normalize(target_matrix)  # ターゲット情報のマトリクスの正規化を実行
    return normalize_matrix, category_match, intension_match  # 正規化したマトリクスに加えカテゴリとintensionがなんだったのかもリターン







# Matrix Node Graphの生成-----------------------------------------------------------------------------------------------
"""
def mngGraph(matrixes):  # タイムスタンプとマトリクスのセットを受け取る
    g = nx.DiGraph()  # 空の有向グラフを生成
    mng_time = []  # 時間を格納するリスト(キューとして使う)
    mng_value = []  # マトリクスを格納するリスト(キューとして使う)
    nodeID = 1  # nodeの番号
    counter = 1  # ループ数をカウント(1回目は1)
    for elements in matrixes.items():  # dictに入ったタイムスタンプとマトリクスのセットを一つずつ取り出し
        element = list(elements)  # リストに変換
        time = element[0]  # タイムスタンプの部分を取得
        date = parser.parse(time).astimezone(timezone('Asia/Tokyo'))  # 表記を数字のみに変換
        date = str(date).replace("+09:00","")  # 余計なものを取り除く
        timestamp = datetime.datetime.strptime(date, '%Y-%m-%d %H:%M:%S')  # タイムスタンプ型に変換
        value = element[1]  # 本文のマトリクスを取得
        if counter == 1:  # ここは初めのループの時のみ実行
            g.add_node(time)  # 時間をノードにする  
            mng_time.append(timestamp)  # タイムスタンプを追加
            mng_value.append(value)  # マトリクスを追加
            #print(list(g.nodes()))
        if counter > 2:
            lag = timestamp - mng_time[0] 
            print(lag)
        counter += 1  # カウンターを増やす
        nodeID += 1  # ノードIDを次へ        
    return
"""
# Matrix間の類似度----------------------------------------------------------------------------------------------------
def Sm():
    return

# Graph間の類似度--------------------------------------------------------------------------------------------------------
def Sg(g1,g2):
    
    return