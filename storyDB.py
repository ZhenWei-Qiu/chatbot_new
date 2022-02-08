# 建立故事內容及關鍵字資料庫
import pymongo
from allennlp.predictors.predictor import Predictor
import copy
from nltk.stem import WordNetLemmatizer
from googletrans import Translator
import createLibrary
story_name = "Fairy friendss"
content_list = []
words = []
entityInfo = {}


def createStory():
    global words
    path = "story/" + story_name + ".txt"
    f = open(path, mode='r')
    words = f.read()
    story_content = words.replace('*', '').replace('\n', ' ')
    createLibrary.addBook(story_name, story_content)
    f.close()


def coReference():
    global content_list, entityInfo
    createStory()
    content = words.replace('\n', ' ')
    predictor = Predictor.from_path(
        "https://storage.googleapis.com/allennlp-public-models/coref-spanbert-large-2020.02.27.tar.gz")
    result_1 = predictor.predict(
        document=content
    )
    result = copy.deepcopy(result_1)

    content_list = result['document']
    # 找出代名詞對應主詞 修改原文
    delchar = ['a ', 'the ', 'A ', "The "]
    for i in range(len(result['clusters'])):
        count = 0
        temp_name = ' '.join(result['document'][result['clusters'][i][0][0]:result['clusters'][i][0][1] + 1])

        for index in delchar:
            if temp_name[0:2] == index or temp_name[0:4] == index:
                temp_name = temp_name.replace(index, "")
        print(temp_name)

        for j in result['clusters'][i]:
            count += 1
            print(str(j) + ":" + str(result['document'][j[0]:j[1] + 1]), end=',')
            print(' '.join(result['document'][j[0]:j[1] + 1]))
            print("story_list", end=':')
            print(content_list[j[0]])
            if j[0] == j[1]:
                if story_name == 'Sheep on the Run!' and content_list[j[0]] == 'Lee':
                    content_list[j[0]] = 'Lee'
                else:
                    content_list[j[0]] = temp_name

        entityInfo[temp_name] = {"Frequence": count}
        # print("出現次數：" + str(count), end='\r\n\r\n')


def story_analysis():
    myClient = pymongo.MongoClient("mongodb://root:ltlab35316@140.115.53.196:27017/")
    # myClient = pymongo.MongoClient("mongodb://localhost:27017/")
    myBook = myClient[story_name.replace(' ', '_').replace("'", "").replace("!", "").replace(",", "")]
    myVerbList = myBook.VerbTable
    myKeyList = myBook.KeywordTable
    coReference()
    wnl = WordNetLemmatizer()
    verbName = []
    verbInfo = {}
    storyPhraseList = words.replace('*', '').split('\n')

    story_2 = ' '.join(content_list)
    print(story_2)
    # *符號表示換行
    story_2 = story_2.replace(' * ', ' \r\n')
    story_2_PhraseList = story_2.split('\r\n')
    for i in story_2_PhraseList:
        print(i)

    # Dependency Parsing
    predictor = Predictor.from_path(
        "https://storage.googleapis.com/allennlp-public-models/biaffine-dependency-parser-ptb-2020.04.06.tar.gz")

    counter_speech = False

    for i in range(len(story_2_PhraseList)):
        c1_list = []
        c2_list = []
        v_list = []
        v = False
        if story_2_PhraseList[i].endswith(', '):
            sentence = story_2_PhraseList[i].replace(',', '')
        else:
            sentence = story_2_PhraseList[i].replace(' .', '')
        result = predictor.predict(
            sentence=sentence
        )
        print(sentence)
        # 抓出主要SVO
        svo = {}
        for j in range(len(result['pos'])):
            if v == False and (result['pos'][j] == 'PROPN' or result['pos'][j] == 'NOUN' or result['pos'][j] == 'PRON'):
                if result['words'][j] not in c1_list:
                    c1_list.append(result['words'][j])
                continue
            if (result['pos'][j] == 'VERB' and result['predicted_dependencies'][j] != 'aux') or (
                    result['pos'][j] == 'AUX' and result['predicted_dependencies'][j] == 'root'):
                if result['words'][j].lower() != 'can':
                    v = True
                    if result['words'][j] not in v_list:
                        # 找出動詞keyword
                        word = wnl.lemmatize(result['words'][j], 'v')
                        v_list.append(word.lower())
                        verbName.append(word.lower())
                continue
            if v == True and (result['pos'][j] == 'PROPN' or result['pos'][j] == 'NOUN'):
                if result['words'][j] not in c2_list:
                    c2_list.append(result['words'][j])
                continue
        print('S:' + str(c1_list) + ' V:' + str(v_list) + ' O:' + str(c2_list))
        if len(c1_list) != 0:
            svo['C1'] = c1_list
        if len(v_list) != 0:
            svo['Verb'] = v_list
        if len(c2_list) != 0:
            svo['C2'] = c2_list

        speaker = ''
        speak_to = ''
        if '"' in story_2_PhraseList[i]:
            dialog_sentence = story_2_PhraseList[i].replace(' . ', '')
            counter_speech_ind = i
            if dialog_sentence.startswith('" '):
                dialog_list = dialog_sentence.split(' " ')
                if len(dialog_list) == 1:
                    # 說話者為空
                    speaker = ''
                else:
                    match = False
                    if ', ' in dialog_list[1]:
                        temp = dialog_list[1].split(", ")[0].split(" ")
                    else:
                        temp = dialog_list[1].split(" ")
                    for d_index in range(len(temp)):
                        for index in range(len(v_list)):
                            if temp[d_index] == v_list[index]:
                                match = True
                                if d_index == 0:
                                    # "" say XXX
                                    speaker = ' '.join(temp[1:])
                                else:
                                    # "" XXX say
                                    speaker = ' '.join(temp[0:d_index])
                                    # 改寫原句 將對話句子的說話者代名詞改為角色名稱
                                    temp_phrase = storyPhraseList[i].split('" ')[1].split(' ' + temp[d_index])[0]
                                    storyPhraseList[i] = storyPhraseList[i].replace(" " + temp_phrase + " ",
                                                                                    " " + speaker + ' ')
                                    print(storyPhraseList[i])
                                break
                        if match:
                            break
            else:
                # XXX say ""
                match = False
                dialog_list = dialog_sentence.split(', " ')
                if ', ' in dialog_list[0]:
                    temp = dialog_list[0].split(", ")[1].split(" ")
                else:
                    temp = dialog_list[0].split(" ")
                for d_index in range(len(temp)):
                    for index in range(len(v_list)):
                        if temp[d_index] == v_list[index]:
                            match = True
                            speaker = ' '.join(temp[0:d_index])
                            # 改寫原句 將對話句子的說話者代名詞改為角色名稱
                            temp_phrase = storyPhraseList[i].split(' "')[0].split(' ' + temp[d_index])[0]
                            storyPhraseList[i] = storyPhraseList[i].replace(" " + temp_phrase + " ",
                                                                            " " + speaker + ' ')
                            print(storyPhraseList[i])
                            break
                    if match:
                        break
            # speak_to
            if counter_speech and (i - counter_speech_ind) == 1:
                speak_to = counter_speech_ind - 1
            elif counter_speech and (i - counter_speech_ind) != 1:
                if speaker in story_2_PhraseList[i]:
                    speak_to = counter_speech_ind - 1

            counter_speech = True
        else:
            counter_speech = False

        translator = Translator()
        while True:
            try:
                sentence_Translate = translator.translate(storyPhraseList[i], src="en", dest="zh-TW").text
                break
            except Exception as e:
                print(e)

        if speaker != '' and sentence_Translate.startswith('“'):
            temp = sentence_Translate.split('”')
            temp.reverse()
            sentence_Translate = ''.join(temp)

        sentence_info = {'Sentence_Id': i, 'Sentence': story_2_PhraseList[i],
                         'Sentence_translate': sentence_Translate, 'Speaker': speaker, 'Speak_to': speak_to}
        mydict = svo.copy()
        mydict.update(sentence_info)
        myVerbList.insert_one(mydict)
        print(mydict)

    for index in verbName:
        verbInfo[index] = {"Frequence": verbName.count(index)}
    myKeyDict = {'Entity_list': entityInfo, 'Verb_list': verbInfo}
    myKeyList.insert_one(myKeyDict)
    print(myKeyDict)


# 建立主要人物、動詞、對話資料庫
def getMaterial():
    myClient = pymongo.MongoClient("mongodb://root:ltlab35316@140.115.53.196:27017/")
    # myClient = pymongo.MongoClient("mongodb://localhost:27017/")
    myBook = myClient[story_name.replace(' ', '_').replace("'", "").replace("!", "").replace(",", "")]
    myMaterialList = myBook.MaterialTable
    myKeyList = myBook.KeywordTable
    myVerbList = myBook.VerbTable
    # Character   Main_Verb   Reply(Sentence_id, Replier)
    temp_Entity = {}
    temp_Verb = {}
    # find_document = myKeyList.find()
    find_document = myKeyList.find_one()

    # 主角
    for i in find_document['Entity_list'].keys():
        temp_Entity[i] = find_document['Entity_list'][i]['Frequence']

    # for i in find_document[0]['Entity_list'].keys():
    #     temp_Entity[i] = find_document[0]['Entity_list'][i]['Frequency']

    # 動詞
    find_documentVerb = find_document['Verb_list']
    # find_documentVerb = find_document[1]['Verb_list']
    stop_words = ['is', 'are', 'was', 'were', 'do', 'can', 'may', 'would', 'ca', 'has', "'s", 'say', 'be', 'ask', 'make', 'will', 'have']
    for i in stop_words:
        if i in find_documentVerb:
            del find_documentVerb[i]
    for i in find_documentVerb.keys():
        # temp_Verb[i] = find_documentVerb[i]['Frequency']
        temp_Verb[i] = find_documentVerb[i]['Frequence']

    # 對話 {'Sentence_id': sentence_id, 'Replier': replier}
    sentence_id = []
    for i in myVerbList.find():
        temp = i['Speak_to']
        if temp != '':
            sentence_id.append(temp)

        # temp = myVerbList.find_one({'Sentence_Id': i['Sentence_Id'], "Speak_to": {'$exists': True}})
        # if temp is not None:
        #     sentence_id.append(i['Speak_to'])

    sort_Entity = sorted(temp_Entity.items(), key=lambda x: x[1], reverse=True)
    sort_Verb = sorted(temp_Verb.items(), key=lambda x: x[1], reverse=True)
    character = []
    verb = []
    for i in sort_Entity[0:3]:
        character.append(i[0])
    for i in sort_Verb[0:3]:
        verb.append(i[0])
    myMateriaDict = {'Character': character, 'Main_Verb': verb}
    # myMateriaDict = {'Character': character, 'Main_Verb': verb, 'Sentence_id': sentence_id}
    myMaterialList.insert_one(myMateriaDict)
    print(myMateriaDict)


if __name__ == "__main__":
    story_analysis()
    getMaterial()
    # coReference()
    # createStory()
