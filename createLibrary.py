# 建立通用句及書單資料庫
import copy
import os
import pymongo
from googletrans import Translator

myClient: object
myBotData: object
myBookList: object
myCommonList: object


def connect():
    global myClient, myBotData, myBookList, myCommonList
    try:
        # 連接mongo
        #myclient = pymongo.MongoClient("mongodb://root:ltlab35316@140.115.53.196:27017/")
        myclient = pymongo.MongoClient("mongodb://localhost:27017/")
        myBotData = myclient.Chatbot
        myBookList = myBotData.bookList
        myCommonList = myBotData.commonList
    except Exception as e:
        print(e)
    return myBookList, myCommonList


def addBook(bookName, story_content):
    connect()
    # 新增書單
    translator = Translator()
    book_dict = {'bookName': bookName,
                 'bookNameTranslated': translator.translate(bookName, src="en", dest="zh-TW").text,
                 'story_content': story_content}
    myBookList.insert_one(book_dict)
    print(book_dict)


def addCommon():
    connect()
    myCommonList.delete_many({})
    # 新增通用句
    path = "common_list/"
    allList = os.listdir(path)
    for file in allList:
        common_phrase = []
        file_path = path + file
        if os.path.isfile(file_path):
            with open(file_path, 'r') as f:
                for line in f:
                    common_phrase.append(line.replace('\n', ''))
            common_dict = {'type': file.replace('.txt', ''), 'content': common_phrase}
            myCommonList.insert_one(common_dict)
            print(common_dict)


def updateUser(userId, bookName, match_sentence, record_list, match_entity, match_verb, state, noMatch_count, continue_stage):
    # 連接mongo

    # myClient = pymongo.MongoClient("mongodb://root:ltlab35316@140.115.53.196:27017/")
    myClient = pymongo.MongoClient("mongodb://localhost:27017/")
    myBotData = myClient.Chatbot
    myUserList = myBotData.UserTable
    bookTalkSummary = {'Match_sentence': match_sentence, 'noMatch_count': noMatch_count, 'Sentence_id_list': record_list, 'Entity_list': match_entity,
                       'Verb_list': match_verb, 'Finish': state, 'Continue': continue_stage}

    if not list(myUserList.find()):
        # 資料庫無資料 > 直接新增一筆
        mydict = {'User_id': userId, 'BookTalkSummary': {bookName: bookTalkSummary}}
        myUserList.insert_one(mydict)
    else:
        find_user = {'User_id': userId}
        now_user = myUserList.find_one(find_user)
        # 若沒有該使用者之資料
        if now_user is None:
            # 直接新增一筆
            mydict = {'User_id': userId, 'BookTalkSummary': {bookName: bookTalkSummary}}
            myUserList.insert_one(mydict)
        # 有該使用者資料
        else:
            if bookName in now_user['BookTalkSummary']:
                # 有該本書之資料 > 更新內容
                user_book_result = copy.deepcopy(now_user)
                for book_data in user_book_result['BookTalkSummary'].keys():
                    if book_data == bookName:
                        user_book_result['BookTalkSummary'][book_data] = bookTalkSummary
                myUserList.update_one(find_user, {"$set": user_book_result})
            else:
                # 同一筆資料下新增key值
                user_book_result = copy.deepcopy(now_user)
                user_book_result['BookTalkSummary'].update({bookName: bookTalkSummary})
                myUserList.update_one(find_user, {"$set": user_book_result})


def addDialog(bookName, dialog_id, speaker_id, content, time):
    #myClient = pymongo.MongoClient("mongodb://root:ltlab35316@140.115.53.196:27017/")
    myClient = pymongo.MongoClient("mongodb://localhost:27017/")
    myBook = myClient[bookName.replace(' ', '_').replace("'", "")]
    allDialog = myBook.S_R_Dialog

    mydict = {'Dialog_id': dialog_id, 'Speaker_id': speaker_id, 'Content': content,
              'Time': time}
    allDialog.insert_one(mydict)
    print(mydict)


def addQuestion(bookName, qa_id, dialog_id, response):
    #  myClient = pymongo.MongoClient("mongodb://root:ltlab35316@140.115.53.196:27017/")
    myClient = pymongo.MongoClient("mongodb://localhost:27017/")
    myBook = myClient[bookName.replace(' ', '_').replace("'", "")]
    QATable = myBook.QATable

    mydict = {'QA_Id': qa_id, 'Dialog_id': dialog_id, 'Response': response}
    QATable.insert_one(mydict)
    print(mydict)


def addElaboration(bookName, qa_id, elaboration, confidence, sentence_id):
    #myClient = pymongo.MongoClient("mongodb://root:ltlab35316@140.115.53.196:27017/")
    myClient = pymongo.MongoClient("mongodb://localhost:27017/")
    myBook = myClient[bookName.replace(' ', '_').replace("'", "")]
    Elaboration_Table = myBook.Elaboration

    if sentence_id == '':
        mydict = {'QA_Id': qa_id, 'Elaboration': elaboration, 'Confidence': confidence}
    else:
        mydict = {'QA_Id': qa_id, 'Elaboration': elaboration, 'Confidence': confidence, 'Sentence_Id': sentence_id}
    Elaboration_Table.insert_one(mydict)
    print(mydict)


def addFeedback(userId, bookName, sentiment, feedback):
    #myClient = pymongo.MongoClient("mongodb://root:ltlab35316@140.115.53.196:27017/")
    myClient = pymongo.MongoClient("mongodb://localhost:27017/")
    myBook = myClient[bookName.replace(' ', '_').replace("'", "")]
    Feedback_Table = myBook.Feedback
    mydict = {'User_id': userId, 'Sentiment': sentiment, 'Content': feedback}
    Feedback_Table.insert_one(mydict)
    print(mydict)


if __name__ == "__main__":
    addCommon()