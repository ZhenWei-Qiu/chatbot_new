import copy


def updateUser(myUserList, userId, bookName, state, partner):
    bookTalkSummary = {'Finish': state, 'Partner': partner}

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


def addDialog(dialogList, dialog_id, speaker_id, content, time, session_id, prompt_phase):

    mydict = {'Dialog_id': dialog_id, 'Speaker_id': speaker_id, 'Content': content, 'Phase': prompt_phase,
              'Time': time, 'Session_id': session_id}
    dialogList.insert_one(mydict)
    print(mydict)


def addFeedback(feedbackList, userId, sentiment, feedback):

    mydict = {'User_id': userId, 'Sentiment': sentiment, 'Content': feedback}
    feedbackList.insert_one(mydict)
    print(mydict)
