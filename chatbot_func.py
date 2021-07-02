from random import choice
from googletrans import Translator
from nltk.corpus import wordnet
from nltk.corpus import stopwords
from strsimpy.cosine import Cosine
import pymongo
import createLibrary
import random

myClient: object
myBotData: object
myBookList: object
myCommonList: object
myUserList: object


# 判斷是否為中文
def is_all_chinese(text):
    for _char in text:
        if not '\u4e00' <= _char <= '\u9fa5':
            return False
    return True


def check_input(req):
    print('確認說話內容')
    response = ''
    userSay = req['intent']['query']
    if 'UserSay_temp' in req['session']['params'].keys():
        userSay_temp = req['session']['params']['UserSay_temp']
    else:
        userSay_temp = []
    userSay_temp.append(userSay)
    if 'FirstCheck' in req['session']['params'].keys():
        firstCheck = req['session']['params']['FirstCheck']
    else:
        firstCheck = True
    if userSay == '我不想聊了' or userSay == '故事結束了':
        response_dict = {"scene": {
            "next": {
                'name': 'Expand'
            }
        }}
    else:
        if firstCheck:
            response = ' '
            firstCheck = False
            response_dict = {"prompt": {
                "firstSimple": {
                    "speech": response,
                    "text": response
                },
                'suggestions': [{'title': '確認送出'},
                                {'title': '重講一次'}]
            }, "session": {
                "params": {
                    'UserSay_temp': userSay_temp,
                    'FirstCheck': firstCheck
                }
            }, "scene": {
                "next": {
                    'name': 'Check_input'
                }
            }}
        else:
            if userSay == '重講一次':
                firstCheck = True
                userSay_temp.clear()
                response = '再重新跟我說一次吧'
                response_dict = {"prompt": {
                    "firstSimple": {
                        "speech": response,
                        "text": response
                    }
                }, "session": {
                    "params": {
                        'UserSay_temp': userSay_temp,
                        'FirstCheck': firstCheck
                    }
                }}
            elif userSay == '確認送出':
                firstCheck = True
                userSay_temp.pop()
                userSay = ''.join(userSay_temp)
                userSay_temp.clear()
                scene = req['session']['params']['NextScene']
                response_dict = {"session": {
                    "params": {
                        'UserSay_temp': userSay_temp,
                        'User_say': userSay,
                        'FirstCheck': firstCheck
                    }
                }, "scene": {
                    "next": {
                        'name': scene
                    }
                }}
            else:
                firstCheck = False
                response = ' '
                response_dict = {"prompt": {
                    "firstSimple": {
                        "speech": response,
                        "text": response
                    },
                    'suggestions': [{'title': '確認送出'},
                                    {'title': '重講一次'}]
                }, "session": {
                    "params": {
                        'UserSay_temp': userSay_temp,
                        'FirstCheck': firstCheck
                    }
                }, "scene": {
                    "next": {
                        'name': 'Check_input'
                    }
                }}

    print(response)
    return response_dict


def connect():
    global myClient, myBotData, myBookList, myCommonList, myUserList
    try:
        #myClient = pymongo.MongoClient("mongodb://root:ltlab35316@140.115.53.196:27017/")
        myClient = pymongo.MongoClient("mongodb://localhost:27017/")
        myBotData = myClient.Chatbot
        myBookList = myBotData.bookList
        myCommonList = myBotData.commonList
        myUserList = myBotData.UserTable
    except Exception as e:
        print(e)

    return myBookList, myCommonList, myClient, myUserList


# 詢問班級
def user_login():
    print("START_class")
    response = '哈囉！請先告訴我你的班級唷！'
    response_dict = {"prompt": {
                            "firstSimple": {
                                         "speech": response,
                                         "text": response
                            },
                            'suggestions': [{'title': '丁班'},
                                            {'title': '戊班'}]
                    },
                    "scene": {
                            "next": {
                                    'name': 'input_userId'
                            }
                    }
    }
    return response_dict


# 詢問座號
def input_userId():
    print("START_id")
    response = '好唷！那你的座號是多少呢！'
    response_dict = {"prompt": {
        "firstSimple": {
            "speech": response,
            "text": response
        }
    }, "scene": {
        "next": {
            'name': 'Check_input'
        }}, "session": {
        "params": {
            'NextScene': 'Get_bookName'
        }
    }}
    return response_dict


# 詢問書名
def start_chat(req):
    print("START_ask")
    if 'User_second_check' in req['session']['params'].keys():
        second_check = req['session']['params']['User_second_check']
    else:
        second_check = False
    if second_check:
        response = ''
        user_id = req['session']['params']['User_id']
    else:
        print(req['session']['params'])
        print("班級",req['session']['params']['User_class'])
        print("座號", req['session']['params']['User_say'])
        user_id = req['session']['params']['User_class'] + req['session']['params']['User_say']
        print('使用者：' + str(user_id))
        connect()
        book_record = ''
        find_condition = {'type': 'common_start'}
        find_result = myCommonList.find_one(find_condition)
        response = choice(find_result['content'])
        # 取得該使用者紀錄
        if list(myUserList.find()):
            user_exist = myUserList.find_one({"User_id": user_id})
            if user_exist is not None:
                find_condition = {'type': 'common_combine'}
                find_result = myCommonList.find_one(find_condition)
                allBook = list(user_exist["BookTalkSummary"].keys())
                allBook.reverse()
                for i in range(len(allBook[0:2])):
                    if i > 0:
                        book_record += choice(find_result['content']) + allBook[i].replace("_", " ")
                    else:
                        book_record += allBook[i].replace("_", " ")
                find_condition = {'type': 'common_registered'}
                find_result = myCommonList.find_one(find_condition)
                response = choice(find_result['content']).replace('X', book_record)

    response_dict = {"prompt": {
        "firstSimple": {
            "speech": response,
            "text": response
        }}, "session": {
        "params": {
            'User_id': user_id,
            'NextScene': 'Match_book'
        }
    }, "scene": {
        "next": {
            'name': 'Check_input'
        }}
    }
    print(response)
    return response_dict


# 根據相似度比對結果顯示書名選項給使用者直接點選
def match_book(req):
    print('比對書名')
    userSay = req['session']['params']['User_say']
    connect()
    if 'User_first_match' in req['session']['params'].keys():
        first_match = req['session']['params']['User_first_match']
    else:
        first_match = True
    if first_match:
        # 第一次先找出相似書名給使用者確認
        similarity_book = []
        for index in myBookList.find():
            cosine = Cosine(2)
            s1 = userSay
            if is_all_chinese(userSay):
                # 若輸入全中文
                s2 = index['bookNameTranslated']
            else:
                s2 = index['bookName']
            p1 = cosine.get_profile(s1)
            p2 = cosine.get_profile(s2)
            print('相似度：' + str(cosine.similarity_profiles(p1, p2)))
            value = cosine.similarity_profiles(p1, p2)
            if value >= 0.5:
                similarity_book.append(index['bookName'])
        print(similarity_book)
        if len(similarity_book) == 0:
            second_check = True
            first_match = True
            # 無相似書籍 重新輸入
            find_common = {'type': 'common_book_F'}
            find_common_result = myCommonList.find_one(find_common)
            response = choice(find_common_result['content'])
            response_dict = {"prompt": {
                "firstSimple": {
                    "speech": response,
                    "text": response
                }},
                "session": {
                    "params": {
                        'User_first_match': first_match,
                        'User_second_check': second_check
                    }
                }, "scene": {
                    "next": {
                        'name': 'Get_bookName'
                    }}
            }
        else:
            first_match = False
            button_item = []
            temp_bookList = {}
            allBook = ''
            for index in range(len(similarity_book)):
                temp_bookList[str(index + 1)] = similarity_book[index]
                button_item.append({'title': str(index + 1)})
                if index == 0:
                    allBook += str(index + 1) + '：' + similarity_book[index]
                else:
                    allBook += "、" + str(index + 1) + '：' + similarity_book[index]
            button_item.append({'title': '都不是'})
            response = '我有看過 ' + allBook + " 你是在指哪一本呢? 告訴我書名對應的號碼吧"
            response_dict = {"prompt": {
                "firstSimple": {
                    "speech": response,
                    "text": response
                },
                'suggestions': button_item
            }, "session": {
                "params": {
                    'User_first_match': first_match,
                    'User_temp_bookList': temp_bookList
                }
            }}
    else:
        first_match = True
        userInput = req['intent']['query']
        if userInput == '都不是':
            second_check = True
            # 重新輸入
            response = '那你再跟我說一次書名吧！'
            response_dict = {"prompt": {
                "firstSimple": {
                    "speech": response,
                    "text": response
                }},
                "session": {
                    "params": {
                        'User_first_match': first_match,
                        'User_second_check': second_check
                    }
                }, "scene": {
                    "next": {
                        'name': 'Get_bookName'
                    }}
            }
        else:
            time = req['user']['lastSeenTime']
            user_id = req['session']['params']['User_id']
            temp_bookList = req['session']['params']['User_temp_bookList']
            bookName = temp_bookList[userInput]

            nowBook = myClient[bookName.replace(' ', '_').replace("'", "")]
            myVerbList = nowBook['VerbTable']
            myDialogList = nowBook['S_R_Dialog']
            record_list = []
            match_verb = []
            match_entity = []
            checkStage = ''
            input_sentence = 0
            firstTime = True
            book_finish = False

            dialog_index = myDialogList.find().count()
            if dialog_index == 0:
                dialog_id = 0
            else:
                dialog_id = myDialogList.find()[dialog_index - 1]['Dialog_id'] + 1
            find_common = {'type': 'common_book_T'}
            find_common_result = myCommonList.find_one(find_common)
            response = choice(find_common_result['content'])

            # 取得書本紀錄
            if list(myUserList.find()):
                user_data_load = myUserList.find_one({"User_id": user_id})
                # 確認有該本書
                if user_data_load is not None and bookName in user_data_load["BookTalkSummary"].keys():
                    # 書本狀態紀錄為已完成
                    if user_data_load["BookTalkSummary"][bookName]["Finish"]:
                        find_condition = {'type': 'common_finished_T'}
                        find_result = myCommonList.find_one(find_condition)
                        response = choice(find_result['content'])
                        book_finish = True
                    else:
                        # 抓出過去的故事資料
                        firstTime = False
                        checkStage = user_data_load["BookTalkSummary"][bookName]['Continue']
                        input_sentence = user_data_load["BookTalkSummary"][bookName]["Match_sentence"]
                        record_list = user_data_load["BookTalkSummary"][bookName]["Sentence_id_list"]
                        match_entity = user_data_load["BookTalkSummary"][bookName]["Entity_list"]
                        match_verb = user_data_load["BookTalkSummary"][bookName]["Verb_list"]
                        find_common_combine = {'type': 'common_combine'}
                        common_combine = myCommonList.find_one(find_common_combine)
                        result = ''
                        if list(record_list):
                            temp_list = record_list[-3:]
                            for index in range(len(temp_list)):
                                if index > 0:
                                    result += choice(common_combine['content']) + ' ' + \
                                              myVerbList.find_one({"Sentence_Id": int(temp_list[index])})[
                                                  "Sentence_translate"]
                                else:
                                    result = myVerbList.find_one({"Sentence_Id": int(temp_list[index])})[
                                        "Sentence_translate"]

                            for word in ['。', '，', '！', '“', '”', '：']:
                                result = result.replace(word, '')
                            find_common = {'type': 'common_finished_F'}
                            find_common_result = myCommonList.find_one(find_common)
                            response = choice(find_common_result['content']) + ' ' + result

            # 記錄對話過程
            createLibrary.addDialog(bookName, dialog_id, 'chatbot', response, time)

            if book_finish:
                first_match = True
                second_check = True
                response_dict = {"prompt": {
                    "firstSimple": {
                        "speech": response,
                        "text": response
                    }},
                    "scene": {
                        "next": {
                            'name': 'Get_bookName'
                        }
                    },
                    "session": {
                        "params": {
                            'User_first_match': first_match,
                            'User_second_check': second_check
                        }
                    }
                }
            else:
                response_dict = {"prompt": {
                    "firstSimple": {
                        "speech": response,
                        "text": response
                    }},
                    "scene": {
                        "next": {
                            'name': 'Prompt'
                        }
                    },
                    "session": {
                        "params": {
                            'User_book': bookName,
                            'User_record_list': record_list,
                            'User_matchEntity': match_entity,
                            'User_matchVerb': match_verb,
                            'User_inputCount': input_sentence,
                            'User_newChat': firstTime,
                            'User_stage': checkStage
                        }
                    }
                }

    return response_dict


# 聊書引導
def prompt(req):
    print("PROMPT")
    connect()
    response = ''
    bookName = req['session']['params']['User_book']
    firstTime = req['session']['params']['User_newChat']
    input_sentence = req['session']['params']['User_inputCount']
    checkStage = req['session']['params']['User_stage']
    time = req['user']['lastSeenTime']
    state = False
    go_Continue = False
    if 'User_doubleCheck' in req['session']['params'].keys():
        double_check = req['session']['params']['User_doubleCheck']
    else:
        double_check = False
    if 'User_noMatch' in req['session']['params'].keys():
        noMatch_count = req['session']['params']['User_noMatch']
    else:
        noMatch_count = 0
    nowBook = myClient[bookName.replace(' ', '_').replace("'", "")]
    myVerbList = nowBook['VerbTable']
    myDialogList = nowBook['S_R_Dialog']
    dialog_index = myDialogList.find().count()
    dialog_id = myDialogList.find()[dialog_index - 1]['Dialog_id'] + 1

    all_cursor = myVerbList.find()
    if input_sentence >= (all_cursor.count() / 3) and checkStage == '' and not double_check:
        # 詢問是否繼續
        checkStage = 'first'
        go_Continue = True
    elif input_sentence >= (all_cursor.count() / 2) and checkStage == 'first' and not double_check:
        checkStage = 'second'
        go_Continue = True
    elif input_sentence >= (all_cursor.count() * 2 / 3) and checkStage == 'second' and not double_check:
        checkStage = 'finalCheck'
        go_Continue = True
    else:
        if double_check:
            response = ''
        elif firstTime:
            find_common = {'type': 'common_prompt'}
            find_common_result = myCommonList.find_one(find_common)
            response = choice(find_common_result['content'])
            # 記錄對話過程
            createLibrary.addDialog(bookName, dialog_id, 'chatbot', response, time)
        else:
            find_common = {'type': 'common_repeat'}
            find_common_result = myCommonList.find_one(find_common)
            response = choice(find_common_result['content'])
            # 記錄對話過程
            createLibrary.addDialog(bookName, dialog_id, 'chatbot', response, time)

    if go_Continue:
        response = '\n' + '你已經介紹了很多呢！你想繼續跟我分享嗎？'
        response_dict = {"prompt": {
            "firstSimple": {
                "speech": response,
                "text": response
            },
            'suggestions': [{'title': '繼續聊書'},
                            {'title': '不聊了'}]},
            "scene": {
                "next": {
                    'name': 'Continue'
                }
            },
            "session": {
                "params": dict(User_noMatch=noMatch_count, User_doubleCheck=double_check, User_stage=checkStage,
                               User_state=state)}
        }
    else:
        response_dict = {"prompt": {
            "firstSimple": {
                "speech": response,
                "text": response
            }
        },
            "session": {
                "params": dict(User_noMatch=noMatch_count, User_doubleCheck=double_check, User_stage=checkStage,
                               NextScene='Evaluate', User_state=state)
            }, "scene": {
                "next": {
                    'name': 'Check_input'
                }}
        }

    print(response)
    return response_dict


# 比對故事內容
def evaluate(req, predictor):
    print("EVALUATE")
    firstTime = False
    user_id = req['session']['params']['User_id']
    double_check = req['session']['params']['User_doubleCheck']
    input_sentence = req['session']['params']['User_inputCount']
    noMatch_count = req['session']['params']['User_noMatch']
    bookName = req['session']['params']['User_book']
    record_list = req['session']['params']['User_record_list']
    match_entity = req['session']['params']['User_matchEntity']
    match_verb = req['session']['params']['User_matchVerb']
    time = req['user']['lastSeenTime']
    userSay = req['session']['params']['User_say']

    nowBook = myClient[bookName.replace(' ', '_').replace("'", "")]
    myQATable = nowBook['QATable']
    myVerbList = nowBook['VerbTable']
    myDialogList = nowBook['S_R_Dialog']
    dialog_index = myDialogList.find().count()
    dialog_id = myDialogList.find()[dialog_index - 1]['Dialog_id'] + 1

    input_sentence += 1
    no_match = False
    now_index = []
    repeat_content = []
    response = ''
    response_dict = {}
    stop_words = list(stopwords.words('english'))
    for i in ["yourself", "there", "once", "having", "they", "its", "yours", "itself", "is", "him", "themselves",
              "are",
              "we", "these", "your", "his", "me", "were", "her", "himself", "this", "our", "their", "ours", "had",
              "she", "all", "no", "them", "same", "been", "have", "yourselves", "he", "you", "herself", "has",
              "myself",
              "those", "i", "being", "theirs", "my", "against", "it", "she's", 'hers']:
        stop_words.remove(i)
    for i in range(len(stop_words)):
        stop_words[i] = " " + stop_words[i] + " "
    stop_words.extend([' . ', ' , ', '"', ' ! '])
    connect()

    if not double_check:
        # 記錄對話過程
        createLibrary.addDialog(bookName, dialog_id, 'Student ' + user_id, userSay, time)
        dialog_index = myDialogList.find().count()
        dialog_id = myDialogList.find()[dialog_index - 1]['Dialog_id'] + 1

    translator = Translator()

    now_user_say = userSay
    print(userSay)
    # 將原句翻譯
    while True:
        try:
            trans_word = translator.translate(userSay, src='zh-TW', dest="en").text
            break
        except Exception as e:
            print(e)

    similarity_sentence = {}
    post_similarity = ''
    for word in stop_words:
        post_similarity = trans_word.replace(word, ' ')
    print("USER input:" + str(post_similarity))
    # 使用相似度比對
    all_cursor = myVerbList.find()
    for cursor in all_cursor:
        cosine = Cosine(2)
        s1 = post_similarity
        s2 = cursor['Sentence']
        for word in stop_words:
            s2 = s2.replace(word, ' ')
        print(s2)
        p1 = cosine.get_profile(s1)
        p2 = cosine.get_profile(s2)
        print('第' + str(cursor['Sentence_Id']) + '句相似度：' + str(cosine.similarity_profiles(p1, p2)))
        value = cosine.similarity_profiles(p1, p2)
        if value >= 0.5:
            similarity_sentence[cursor['Sentence_Id']] = value
    similarity_sentence = sorted(similarity_sentence.items(), key=lambda x: x[1], reverse=True)
    print('similarity_sentence：' + str(similarity_sentence))
    twoColumn = []
    if list(similarity_sentence):
        # 有相似的句子
        result = predictor.predict(
            sentence=trans_word
        )
        user_c1 = []
        user_v = []
        user_c2 = []
        v = False
        userColumn_count = 0
        for j in range(len(result['pos'])):
            if v == False and (
                    result['pos'][j] == 'PROPN' or result['pos'][j] == 'NOUN' or result['pos'][j] == 'PRON'):
                if result['words'][j] not in user_c1:
                    user_c1.append(result['words'][j])
                continue
            if (result['pos'][j] == 'VERB' and result['predicted_dependencies'][j] != 'aux') or (
                    result['pos'][j] == 'AUX' and result['predicted_dependencies'][j] == 'root'):
                v = True
                if result['words'][j] not in user_v:
                    user_v.append(result['words'][j])
                continue
            if v == True and (result['pos'][j] == 'PROPN' or result['pos'][j] == 'NOUN'):
                if result['words'][j] not in user_c2:
                    user_c2.append(result['words'][j])
                continue
        # 找出使用者說的話的主動詞
        if list(user_c1):
            userColumn_count += 1
        if list(user_v):
            userColumn_count += 1
        if list(user_c2):
            userColumn_count += 1

        print('USER輸入中的S:' + str(user_c1) + ',V:' + str(user_v) + ',O:' + str(user_c2) + '欄位數量：' + str(
            userColumn_count))

        # 若使用者輸入中結構不完整 > 依照相似度判斷
        if userColumn_count < 2:
            no_match = True
        # 都不為空才進行二次確認
        else:
            for similarity_index in similarity_sentence:
                print(similarity_index[0])

                matchColumn_count = 0
                checkC1 = False
                checkC2 = False
                checkVerb = False

                storyMatch_count = 0
                story_c1 = myVerbList.find_one(
                    {'Sentence_Id': similarity_index[0], "C1": {'$exists': True}})
                if story_c1 is not None:
                    story_c1 = myVerbList.find_one({'Sentence_Id': similarity_index[0]})['C1']
                    storyMatch_count += 1
                story_v = myVerbList.find_one(
                    {'Sentence_Id': similarity_index[0], "Verb": {'$exists': True}})
                if story_v is not None:
                    story_v = myVerbList.find_one({'Sentence_Id': similarity_index[0]})['Verb']
                    storyMatch_count += 1
                story_c2 = myVerbList.find_one(
                    {'Sentence_Id': similarity_index[0], "C2": {'$exists': True}})
                if story_c2 is not None:
                    story_c2 = myVerbList.find_one({'Sentence_Id': similarity_index[0]})['C2']
                    storyMatch_count += 1
                # 滿足兩個欄位
                if storyMatch_count > 1:
                    # 先比對C1
                    word_case = []
                    if not checkC1 and story_c1 is not None:
                        for word in user_c1:
                            word_case = [word, word.lower(), word.capitalize()]
                        word_case = list(set(word_case))
                        # word是否在storyC1中
                        for index in word_case:
                            for c1_index in story_c1:
                                if c1_index == index:
                                    print(c1_index)
                                    checkC1 = True
                                    matchColumn_count += 1
                                    if index not in match_entity:
                                        match_entity.append(index)
                                    break
                            if checkC1:
                                break
                    # 找V
                    if not checkVerb and story_v is not None:
                        word_morphy = []
                        word_case = []
                        for word in user_v:
                            for i in wordnet._morphy(word, pos='v'):
                                word_morphy.append(i)
                        for index in word_morphy:
                            while True:
                                try:
                                    trans_word = translator.translate(index, src='en', dest="zh-TW").extra_data[
                                        'parsed']
                                    if len(trans_word) > 3:
                                        for i in trans_word[3][5][0]:
                                            if i[0] == 'verb':
                                                for verb_index in i[1]:
                                                    for j in verb_index[2]:
                                                        word_case.append(j)
                                                break
                                    break
                                except Exception as translator_error:
                                    print(translator_error)
                        word_case.extend(word_morphy)
                        print(word_case)
                        for index in word_case:
                            for v_index in story_v:
                                verb_allResult = wordnet._morphy(v_index, pos='v')
                                for j in verb_allResult:
                                    if j == index:
                                        print(index)
                                        checkVerb = True
                                        matchColumn_count += 1
                                        if index not in match_verb:
                                            match_verb.append(index)
                                        break
                                if checkVerb:
                                    break
                            if checkVerb:
                                break
                    # 找C2
                    if not checkC2 and story_c2 is not None:
                        word_case = []
                        for word in user_c2:
                            # 找同義字
                            while True:
                                try:
                                    trans_word = translator.translate(word, src='en', dest="zh-TW").extra_data[
                                        'parsed']
                                    if len(trans_word) > 3:
                                        for i in trans_word[3][5][0]:
                                            if i[0] == 'noun':
                                                for verb_index in i[1]:
                                                    for j in verb_index[2]:
                                                        word_case.append(j)
                                                break
                                    break
                                except Exception as translator_error:
                                    print(translator_error)
                            word_case.extend([word.lower(), word.capitalize()])
                        word_case = list(set(word_case))
                        print(word_case)
                        for index in word_case:
                            for c2_index in story_c2:
                                if c2_index == index:
                                    print(index)
                                    checkC2 = True
                                    matchColumn_count += 1
                                    if index not in match_entity:
                                        match_entity.append(index)
                                    break
                            if checkC2:
                                break

                    if matchColumn_count == 2:
                        if similarity_index[0] not in twoColumn:
                            twoColumn.append(similarity_index[0])
                    print(str(checkC1) + ',' + str(checkC2) + ',' + str(checkVerb))
                    all_cursor = myVerbList.find()
                    if matchColumn_count == 3:
                        no_match = False
                        if similarity_index[0] not in record_list:
                            record_list.append(similarity_index[0])
                        now_index.append(similarity_index[0])
                        # 比對成功
                        find_common = {'type': 'common_match_T'}
                        find_common_result = myCommonList.find_one(find_common)
                        response = choice(find_common_result['content'])

                        exist_elaboration = myVerbList.find_one(
                            {"Sentence_Id": similarity_index[0], "Student_elaboration": {'$exists': True}})
                        if exist_elaboration is not None:
                            # 若有學生曾輸入過的詮釋 > 回答該句
                            repeat_content.append(
                                choice(all_cursor[similarity_index[0]]['Student_elaboration']))
                        else:
                            result = all_cursor[similarity_index[0]]['Sentence_translate']
                            for word in ['。', '，', '！', '“', '”', '：']:
                                result = result.replace(word, ' ')
                            repeat_content.append(result)

                        # 記錄對話過程
                        createLibrary.addDialog(bookName, dialog_id, 'chatbot', response, time)

                        response_dict = {"prompt": {
                            "firstSimple": {
                                "speech": response,
                                "text": response
                            }},
                            "scene": {
                                "next": {
                                    'name': 'REPEAT'
                                }
                            },
                            "session": {
                                "params": dict(User_record_list=record_list, User_matchEntity=match_entity,
                                               User_matchVerb=match_verb, User_inputCount=input_sentence,
                                               User_nowInput=now_user_say, User_repeatContent=repeat_content,
                                               User_nowIndex=now_index, User_newChat=firstTime)}
                        }
                        break
                    else:
                        no_match = True
                        similarity_sentence.remove(similarity_index)
                else:
                    no_match = True
    else:
        # 沒有相似的句子
        no_match = True

    if no_match:
        if len(twoColumn) != 0:
            print('有兩欄位的')
            twoColumnMatch = choice(twoColumn)
            print(twoColumnMatch)
            if twoColumnMatch not in record_list:
                record_list.append(twoColumnMatch)
            now_index.append(twoColumnMatch)
            # 比對成功
            find_common = {'type': 'common_match_T'}
            find_common_result = myCommonList.find_one(find_common)
            response = choice(find_common_result['content'])
            exist_elaboration = myVerbList.find_one(
                {"Sentence_Id": twoColumnMatch, "Student_elaboration": {'$exists': True}})
            if exist_elaboration is not None:
                # 若有學生曾輸入過的詮釋 > 回答該句
                repeat_content.append(
                    choice(all_cursor[twoColumnMatch]['Student_elaboration']))
            else:
                result = all_cursor[twoColumnMatch]['Sentence_translate']
                for word in ['。', '，', '！', '“', '”', '：']:
                    result = result.replace(word, ' ')
                repeat_content.append(result)

            # 記錄對話過程
            createLibrary.addDialog(bookName, dialog_id, 'chatbot', response, time)

            response_dict = {"prompt": {
                "firstSimple": {
                    "speech": response,
                    "text": response
                }},
                "scene": {
                    "next": {
                        'name': 'REPEAT'
                    }
                },
                "session": {
                    "params": dict(User_record_list=record_list, User_matchEntity=match_entity,
                                   User_matchVerb=match_verb, User_inputCount=input_sentence,
                                   User_nowInput=now_user_say, User_repeatContent=repeat_content,
                                   User_nowIndex=now_index, User_newChat=firstTime)}
            }
        else:
            if double_check:
                response_dict = {"scene": {
                    "next": {
                        'name': 'Elaboration'
                    }
                },
                    "session": {
                        "params": dict(User_record_list=record_list, User_matchEntity=match_entity,
                                       User_matchVerb=match_verb, User_inputCount=input_sentence,
                                       User_nowIndex=now_index, User_newChat=firstTime)}
                }
            else:
                all_QA_cursor = myQATable.find()
                QAMatch = False
                # 比對QA裡的response
                if all_QA_cursor.count() > 0:
                    for cursor in all_QA_cursor:
                        cosine = Cosine(2)
                        s1 = userSay
                        s2 = cursor['Response']
                        p1 = cosine.get_profile(s1)
                        p2 = cosine.get_profile(s2)
                        print('QA相似度：' + str(cosine.similarity_profiles(p1, p2)))
                        if cosine.similarity_profiles(p1, p2) >= 0.6:
                            qa_id = cursor['QA_Id']
                            QAMatch = True
                            response_dict = {
                                "scene": {
                                    "next": {
                                        'name': 'INQUIRE'
                                    }
                                },
                                "session": {
                                    "params": dict(User_record_list=record_list, User_matchEntity=match_entity,
                                                   User_matchVerb=match_verb, User_inputCount=input_sentence,
                                                   User_newChat=firstTime, User_qaId=qa_id, User_nowIndex=now_index)}
                            }
                            break
                if all_QA_cursor is None or not QAMatch:
                    noMatch_count += 1
                    myQAList = nowBook['QATable']
                    qa_id = myQAList.find().count()

                    # 存入比對不到的使用者對話
                    createLibrary.addQuestion(bookName, qa_id, dialog_id - 1, userSay)

                    # 請使用者補充說明
                    find_common = {'type': 'common_match_F'}
                    find_common_result = myCommonList.find_one(find_common)
                    response = choice(find_common_result['content'])

                    double_check = True

                    # 記錄對話過程
                    createLibrary.addDialog(bookName, dialog_id, 'chatbot', response, time)

                    response_dict = {"prompt": {
                        "firstSimple": {
                            "speech": response,
                            "text": response
                        }},
                        "scene": {
                            "next": {
                                'name': 'Prompt'
                            }
                        },
                        "session": {
                            "params": dict(User_record_list=record_list, User_matchEntity=match_entity,
                                           User_matchVerb=match_verb, User_inputCount=input_sentence,
                                           User_noMatch=noMatch_count, User_newChat=firstTime,
                                           User_doubleCheck=double_check, User_nowInput=now_user_say,
                                           User_repeatContent=repeat_content)}
                    }

    print(response)
    return response_dict


# 比對正確則覆述使用者說的故事
def repeat(req):
    print("REPEAT")
    bookName = req['session']['params']['User_book']
    nowBook = myClient[bookName.replace(' ', '_').replace("'", "")]
    myVerbList = nowBook['VerbTable']
    time = req['user']['lastSeenTime']
    double_check = req['session']['params']['User_doubleCheck']
    myDialogList = nowBook['S_R_Dialog']
    dialog_index = myDialogList.find().count()
    dialog_id = myDialogList.find()[dialog_index - 1]['Dialog_id'] + 1
    now_user_say = req['session']['params']['User_nowInput']
    response = ''
    now_index = req['session']['params']['User_nowIndex']
    repeat_content = req['session']['params']['User_repeatContent']
    if len(repeat_content) > 1:
        for i in repeat_content:
            response += i + " "
    else:
        response = repeat_content[0]
    confidence = 0
    if len(now_index) == 0:
        sentence_id = ''
    else:
        # elaboration連結回故事ID 並存入故事中的句子作為機器人語料庫
        sentence_id = now_index[0]
        exist_elaboration = myVerbList.find_one(
            {'Sentence_Id': sentence_id, "Student_elaboration": {'$exists': True}})
        if exist_elaboration is not None:
            student_elaboration = myVerbList.find_one({'Sentence_Id': sentence_id})['Student_elaboration']
            if now_user_say not in student_elaboration:
                student_elaboration.append(now_user_say)
        else:
            student_elaboration = [now_user_say]
        newvalues = {"$set": {'Student_elaboration': student_elaboration}}
        myVerbList.update_one({'Sentence_Id': sentence_id}, newvalues)

    if double_check:
        myQAList = nowBook['QATable']
        qa_id = myQAList.find().count() - 1
        createLibrary.addElaboration(bookName, qa_id, now_user_say, confidence, sentence_id)

    # 記錄對話過程
    createLibrary.addDialog(bookName, dialog_id, 'chatbot', response, time)
    double_check = False

    response_dict = {"prompt": {
        "firstSimple": {
            "speech": response,
            "text": response
        }},
        "scene": {
            "next": {
                'name': 'RETRIVE'
            }
        },
        "session": {
            "params": dict(User_doubleCheck=double_check)}
    }

    print(response)
    return response_dict


# 接續使用者的下一句
def retrive(req):
    print("RETRIVE")
    noMatch_count = req['session']['params']['User_noMatch']
    input_sentence = req['session']['params']['User_inputCount']
    user_id = req['session']['params']['User_id']
    record_list = req['session']['params']['User_record_list']
    match_entity = req['session']['params']['User_matchEntity']
    match_verb = req['session']['params']['User_matchVerb']
    checkStage = req['session']['params']['User_stage']
    bookName = req['session']['params']['User_book']

    nowBook = myClient[bookName.replace(' ', '_').replace("'", "")]
    time = req['user']['lastSeenTime']
    myDialogList = nowBook['S_R_Dialog']
    dialog_index = myDialogList.find().count()
    dialog_id = myDialogList.find()[dialog_index - 1]['Dialog_id'] + 1
    connect()
    response = ''
    go_expand = False
    now_index = req['session']['params']['User_nowIndex']
    print(record_list)
    myVerbList = nowBook['VerbTable']
    all_cursor = myVerbList.find()
    if len(now_index) == 0:
        # 沒有新故事
        if len(record_list) == 0:
            # 沒有任何故事就直接講第一句
            find_common = {'type': 'common_return'}
            find_common_result = myCommonList.find_one(find_common)
            result = all_cursor[0]["Sentence_translate"]
            for word in ['。', '，', '！', '“', '”', '：']:
                result = result.replace(word, ' ')
            response = choice(find_common_result['content']) + ' ' + result
            record_list.append(0)
        else:
            # 依據前次記錄到的句子接續講下一句
            find_condition = {'Sentence_Id': record_list[-1]}
            find_result_cursor = myVerbList.find_one(find_condition)
            story_conj = '故事裡還有提到'
            result = find_result_cursor["Sentence_translate"]
            for word in ['。', '，', '！', '“', '”', '：']:
                result = result.replace(word, ' ')
            response = story_conj + ' ' + result
            if (record_list[-1]) not in record_list:
                record_list.append(record_list[-1])
    else:
        # 講到最後一句
        if all_cursor.count() - 1 in now_index:
            go_expand = True
        else:
            # 排序now_index
            now_index = sorted(now_index, reverse=True)
            find_condition = {'Sentence_Id': now_index[0] + 1}
            find_result_next = myVerbList.find_one(find_condition)
            find_common_follow = {'type': 'common_retrieve'}
            result_follow = myCommonList.find_one(find_common_follow)
            find_common_conj = {'type': 'common_conj'}
            result_conj = myCommonList.find_one(find_common_conj)
            story_conj = choice(result_conj['content']) + choice(result_follow['content'])
            result = find_result_next["Sentence_translate"]
            for word in ['。', '，', '！', '“', '”', '：']:
                result = result.replace(word, ' ')
            response = story_conj + ' ' + result
            if (now_index[0] + 1) not in record_list:
                record_list.append(now_index[0] + 1)
    if go_expand:
        response_dict = {"prompt": {
            "firstSimple": {
                "speech": response,
                "text": response
            }},
            "scene": {
                "next": {
                    'name': 'Expand'
                }
            },
            "session": {
                "params": dict(User_record_list=record_list)}
        }
    else:
        response_dict = {"prompt": {
            "firstSimple": {
                "speech": response,
                "text": response
            }},
            "scene": {
                "next": {
                    'name': 'Prompt'
                }
            },
            "session": {
                "params": dict(User_record_list=record_list)}
        }

    # 記錄對話過程
    createLibrary.addDialog(bookName, dialog_id, 'chatbot', response, time)

    print(response)
    state = req['session']['params']['User_state']
    createLibrary.updateUser(user_id, bookName, input_sentence, record_list, match_entity, match_verb, state,
                             noMatch_count, checkStage)
    return response_dict


def askContinue(req):
    print('Continue or not')
    userInput = req['intent']['query']
    checkStage = req['session']['params']['User_stage']
    input_sentence = req['session']['params']['User_inputCount']
    user_id = req['session']['params']['User_id']
    record_list = req['session']['params']['User_record_list']
    noMatch_count = req['session']['params']['User_noMatch']
    match_entity = req['session']['params']['User_matchEntity']
    match_verb = req['session']['params']['User_matchVerb']
    bookName = req['session']['params']['User_book']
    if userInput == '繼續聊書':
        response = '太棒了！'
        response_dict = {"prompt": {
            "firstSimple": {
                "speech": response,
                "text": response
            }},
            "scene": {
                "next": {
                    'name': 'Prompt'
                }
            }
        }
    else:
        response = '好唷！沒問題！'
        state = req['session']['params']['User_state']
        createLibrary.updateUser(user_id, bookName, input_sentence, record_list, match_entity, match_verb, state,
                                 noMatch_count, checkStage)
        response_dict = {"prompt": {
            "firstSimple": {
                "speech": response,
                "text": response
            }},
            "scene": {
                "next": {
                    'name': 'Expand'
                }
            },
            "session": {
                "params": {'User_inputCount': input_sentence}
            }}
    print(response)
    return response_dict


# 確認比對到的QA
def inquire(req):
    print('Inquire')
    checkStage = req['session']['params']['User_stage']
    input_sentence = req['session']['params']['User_inputCount']
    user_id = req['session']['params']['User_id']
    record_list = req['session']['params']['User_record_list']
    noMatch_count = req['session']['params']['User_noMatch']
    match_entity = req['session']['params']['User_matchEntity']
    match_verb = req['session']['params']['User_matchVerb']
    bookName = req['session']['params']['User_book']
    time = req['user']['lastSeenTime']
    nowBook = myClient[bookName.replace(' ', '_').replace("'", "")]
    myElaboration = nowBook['Elaboration']
    qa_id = req['session']['params']['User_qaId']
    result = myElaboration.find_one({'QA_Id': qa_id})
    myDialogList = nowBook['S_R_Dialog']
    dialog_index = myDialogList.find().count()
    dialog_id = myDialogList.find()[dialog_index - 1]['Dialog_id'] + 1
    now_index = req['session']['params']['User_nowIndex']

    find_common = {'type': 'common_QA'}
    find_common_result = myCommonList.find_one(find_common)
    response = choice(find_common_result['content']) + " " + result['Elaboration'] + '，'
    if myElaboration.find_one({'QA_Id': qa_id, "Sentence_Id": {'$exists': True}}) is not None:
        record_list.append(result['Sentence_Id'])
        now_index.append(result['Sentence_Id'])

    state = req['session']['params']['User_state']
    createLibrary.updateUser(user_id, bookName, input_sentence, record_list, match_entity, match_verb, state,
                             noMatch_count, checkStage)
    # 記錄對話過程
    createLibrary.addDialog(bookName, dialog_id, 'chatbot', response, time)

    response_dict = {"prompt": {
        "firstSimple": {
            "speech": response,
            "text": response
        }},
        "scene": {
            "next": {
                'name': 'PROMPT'
            }
        },
        "session": {
            "params": dict(User_record_list=record_list, User_nowIndex=now_index)}
    }
    print(response)
    return response_dict


# 增加新的Elaboration
def addElaboration(req):
    print('Elaboration')
    double_check = False
    checkStage = req['session']['params']['User_stage']
    user_id = req['session']['params']['User_id']
    userSay = req['session']['params']['User_say']
    bookName = req['session']['params']['User_book']
    time = req['user']['lastSeenTime']
    noMatch_count = req['session']['params']['User_noMatch']
    input_sentence = req['session']['params']['User_inputCount']
    record_list = req['session']['params']['User_record_list']
    match_entity = req['session']['params']['User_matchEntity']
    match_verb = req['session']['params']['User_matchVerb']
    response = ''
    nowBook = myClient[bookName.replace(' ', '_').replace("'", "")]
    myDialogList = nowBook['S_R_Dialog']
    dialog_index = myDialogList.find().count()
    dialog_id = myDialogList.find()[dialog_index - 1]['Dialog_id'] + 1

    # 暫定信心值
    confidence = 0
    sentence_id = ''
    myQAList = nowBook['QATable']
    qa_id = myQAList.find().count() - 1
    createLibrary.addElaboration(bookName, qa_id, userSay, confidence, sentence_id)

    # 記錄對話過程
    createLibrary.addDialog(bookName, dialog_id, 'Student ' + user_id, userSay, time)

    if noMatch_count == 3:
        noMatch_count = 0
        response_dict = {
            "scene": {
                "next": {
                    'name': 'RETRIVE'
                }
            },
            "session": {
                "params": dict(User_noMatch=noMatch_count,
                               User_doubleCheck=double_check)}
        }
    else:
        find_common = {'type': 'common_elaboration'}
        find_common_result = myCommonList.find_one(find_common)
        response = choice(find_common_result['content']) + " " + userSay + '，'
        response_dict = {"prompt": {
            "firstSimple": {
                "speech": response,
                "text": response
            }},
            "scene": {
                "next": {
                    'name': 'PROMPT'
                }
            },
            "session": {
                "params": dict(User_noMatch=noMatch_count,
                               User_doubleCheck=double_check)}
        }

    # 記錄對話過程
    dialog_index = myDialogList.find().count()
    dialog_id = myDialogList.find()[dialog_index - 1]['Dialog_id'] + 1
    createLibrary.addDialog(bookName, dialog_id, 'chatbot', response, time)
    state = req['session']['params']['User_state']
    createLibrary.updateUser(user_id, bookName, input_sentence, record_list, match_entity, match_verb, state,
                             noMatch_count, checkStage)

    print(response)
    return response_dict


# 學生心得回饋
def expand(req, senta):
    print("Expand")
    state = True
    checkStage = req['session']['params']['User_stage']
    user_id = req['session']['params']['User_id']
    noMatch_count = req['session']['params']['User_noMatch']
    input_sentence = req['session']['params']['User_inputCount']
    record_list = req['session']['params']['User_record_list']
    match_entity = req['session']['params']['User_matchEntity']
    match_verb = req['session']['params']['User_matchVerb']
    bookName = req['session']['params']['User_book']
    userSay = req['session']['params']['User_say']
    time = req['user']['lastSeenTime']
    nowBook = myClient[bookName.replace(' ', '_').replace("'", "")]
    myDialogList = nowBook['S_R_Dialog']
    dialog_index = myDialogList.find().count()
    dialog_id = myDialogList.find()[dialog_index - 1]['Dialog_id'] + 1
    if 'User_expand' in req['session']['params'].keys():
        expand_user = req['session']['params']['User_expand']
    else:
        expand_user = False
    if not expand_user:
        find_common_expand = {'type': 'common_expand'}
        common_result_expand = myCommonList.find_one(find_common_expand)
        find_common = {'type': 'common_like'}
        find_result = myCommonList.find_one(find_common)
        response = "\n" + choice(common_result_expand['content']) + ' ' + choice(find_result['content'])
        expand_user = True
        response_dict = {"prompt": {
            "firstSimple": {
                "speech": response,
                "text": response
            }},
            'session': {
                'params': {
                    'User_expand': expand_user,
                    'NextScene': 'Expand'
                }
            }, "scene": {
                "next": {
                    'name': 'Check_input'
                }}
        }
    else:
        # Senta情感分析
        input_dict = {"text": [userSay]}
        results = senta.sentiment_classify(data=input_dict)
        if userSay == '還好' or userSay == '普通':
            response = '這樣啊！那是為甚麼呢？'
            suggest_like = False
        else:
            if results[0]['sentiment_key'] == "positive" and results[0]['positive_probs'] >= 0.76:
                # 接續詢問使用者喜歡故事的原因
                find_common = {'type': 'common_like_response'}
                find_common2 = {'type': 'common_like_expand'}
                find_result = myCommonList.find_one(find_common)
                find_result2 = myCommonList.find_one(find_common2)
                response = choice(find_result['content']) + ' ' + choice(find_result2['content'])
                suggest_like = True
            else:
                find_common = {'type': 'common_like_F_expand'}
                find_result = myCommonList.find_one(find_common)
                response = choice(find_result['content'])
                suggest_like = False
        expand_user = False
        response_dict = {"prompt": {
            "firstSimple": {
                "speech": response,
                "text": response
            }},
            "scene": {
                "next": {
                    'name': 'Check_input'
                }
            },
            "session": {
                "params": dict(User_sentiment=suggest_like,
                               User_state=state, User_expand=expand_user, NextScene='Feedback')}
        }

    # 記錄對話過程
    createLibrary.addDialog(bookName, dialog_id, 'chatbot', response, time)
    createLibrary.updateUser(user_id, bookName, input_sentence, record_list, match_entity, match_verb, state,
                             noMatch_count, checkStage)
    print(response)
    return response_dict


# 從資料庫中取資料做為機器人給予學生之回饋
def feedback(req):
    print('Feedback')
    userSay = req['session']['params']['User_say']
    user_id = req['session']['params']['User_id']
    bookName = req['session']['params']['User_book']
    time = req['user']['lastSeenTime']
    nowBook = myClient[bookName.replace(' ', '_').replace("'", "")]
    myFeedback = nowBook['Feedback']
    myDialogList = nowBook['S_R_Dialog']
    dialog_index = myDialogList.find().count()
    dialog_id = myDialogList.find()[dialog_index - 1]['Dialog_id'] + 1
    # 記錄對話過程
    createLibrary.addDialog(bookName, dialog_id, 'Student ' + user_id, userSay, time)
    find_common = {'type': 'common_feedback'}
    find_result = myCommonList.find_one(find_common)
    find_feedback_student = {'type': 'common_feedback_student'}
    result_feedback_student = myCommonList.find_one(find_feedback_student)
    suggest_like = req['session']['params']['User_sentiment']
    find_like = {'Sentiment': suggest_like}
    result_like = myFeedback.find(find_like)
    if result_like.count() == 0:
        response = '哦！原來是這樣啊！我了解了，'
    else:
        if result_like.count() > 2:
            choose_number = random.sample(range(0, result_like.count() - 1), 2)
            response = choice(find_result['content']) + " " + result_like[choose_number[0]]['Content'] + "，" + choice(
                result_feedback_student['content']) + " " + result_like[choose_number[1]]['Content']
        elif result_like.count() == 2:
            response = choice(find_result['content']) + " " + result_like[0]['Content'] + "，" + choice(
                result_feedback_student['content']) + " " + result_like[1]['Content']
        else:
            choose_number = 0
            response = choice(find_result['content']) + " " + result_like[choose_number]['Content']
    response += '\n'
    response_dict = {"prompt": {
        "firstSimple": {
            "speech": response,
            "text": response
        }},
        "scene": {
            "next": {
                'name': 'Suggest'
            }
        }
    }
    createLibrary.addFeedback(user_id, bookName, suggest_like, userSay)
    # 記錄對話過程
    dialog_index = myDialogList.find().count()
    dialog_id = myDialogList.find()[dialog_index - 1]['Dialog_id'] + 1
    createLibrary.addDialog(bookName, dialog_id, 'chatbot', response, time)
    print(response)
    return response_dict


# 依據學生喜好建議其他書籍
def suggestion(req):
    print("Suggestion")
    connect()
    suggest_like = req['session']['params']['User_sentiment']
    bookName = req['session']['params']['User_book']
    time = req['user']['lastSeenTime']
    nowBook = myClient[bookName.replace(' ', '_').replace("'", "")]
    myDialogList = nowBook['S_R_Dialog']
    dialog_index = myDialogList.find().count()
    dialog_id = myDialogList.find()[dialog_index - 1]['Dialog_id'] + 1
    suggest_book = {}
    stop_words = list(stopwords.words('english'))
    for i in range(len(stop_words)):
        stop_words[i] = " " + stop_words[i] + " "
    stop_words.extend(['.', ',', '"', '!', "'s", '?'])
    # 與資料庫中其他書的內容作相似度比對
    sample_book = myBookList.find_one({'bookName': bookName.replace('_', ' ')})['story_content']
    comparison_book = myBookList.find({'bookName': {'$ne': bookName.replace('_', ' ')}})
    for word in stop_words:
        sample_book = sample_book.replace(word, ' ')
    story_content = ''
    for book in comparison_book:
        for word in stop_words:
            story_content = book['story_content'].replace(word, ' ')
        cosine = Cosine(2)
        p1 = cosine.get_profile(sample_book.replace('   ', ' ').replace('  ', ' '))
        p2 = cosine.get_profile(story_content.replace('   ', ' ').replace('  ', ' '))
        suggest_book[book['bookName']] = cosine.similarity_profiles(p1, p2)
    find_condition = {'type': 'common_combine'}
    result_combine = myCommonList.find_one(find_condition)
    like_str = ''
    if suggest_like:
        # 學生喜歡則列出前3高相似度的書籍
        find_common = {'type': 'common_like_T'}
        find_result = myCommonList.find_one(find_common)
        sort_suggest_book = sorted(suggest_book.items(), key=lambda x: x[1], reverse=True)
    else:
        find_common = {'type': 'common_like_F'}
        find_result = myCommonList.find_one(find_common)
        sort_suggest_book = sorted(suggest_book.items(), key=lambda x: x[1], reverse=False)
    for index in range(len(sort_suggest_book[0:2])):
        if index > 0:
            like_str += choice(result_combine['content']) + sort_suggest_book[index][0]
        else:
            like_str += sort_suggest_book[index][0]
    response = ',' + choice(find_result['content']).replace('XX', like_str) + '\n' + '謝謝你的分享！期待你下次的故事！Bye Bye！'

    response_dict = {"prompt": {
        "firstSimple": {
            "speech": response,
            "text": response
        }},
        "scene": {
            "next": {
                'name': 'actions.scene.END_CONVERSATION'
            }
        }
    }
    # 記錄對話過程
    createLibrary.addDialog(bookName, dialog_id, 'chatbot', response, time)
    createLibrary.updateUser(req['session']['params']['User_id'], req['session']['params']['User_book'],
                             req['session']['params']['User_inputCount'],
                             req['session']['params']['User_record_list'],
                             req['session']['params']['User_matchEntity'],
                             req['session']['params']['User_matchVerb'], req['session']['params']['User_state'],
                             req['session']['params']['User_noMatch'], req['session']['params']['User_stage'])
    print(response)
    return response_dict


def exit_system(req):
    print("Exit")
    if 'User_id' in req['session']['params'].keys() and 'User_book' in req['session']['params'].keys():
        createLibrary.updateUser(req['session']['params']['User_id'], req['session']['params']['User_book'],
                                 req['session']['params']['User_inputCount'],
                                 req['session']['params']['User_record_list'],
                                 req['session']['params']['User_matchEntity'],
                                 req['session']['params']['User_matchVerb'], req['session']['params']['User_state'],
                                 req['session']['params']['User_noMatch'], req['session']['params']['User_stage'])
