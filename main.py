
import pandas as pd
import pymysql

from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import CountVectorizer

from flask import Flask,jsonify,request
conn=pymysql.connect(host='127.0.0.1',user='root',passwd='',db='soft')


app = Flask(__name__)


@app.route('/recommendeduser', methods = ['GET'])
def getfun():
    username=request.args.get('username')
    features=[]
    user_df=pd.read_sql_query(" SELECT *,ROW_NUMBER() OVER() AS id1 FROM theusers WHERE username NOT IN (SELECT `to` FROM messages WHERE `from` = '{}' ) AND username NOT IN (SELECT `from` FROM messages WHERE `to` = '{}' )".format(username,username),conn)
    user_id=user_df[user_df['username'] == username]["id1"].values[0]-1
    
    for z in range(0,user_df.shape[0]):
        allfeature=''
        id=''
        intrest=user_df['intrest'][z].split(",")
        for i in range(len(intrest)):
            allfeature+=str(intrest[i] ) +' '
        eventid=pd.read_sql_query("SELECT eventid FROM userevent where username='{}' ".format(user_df['username'][z]),conn)
        for i in range(0,eventid.shape[0]):
            if i==eventid.shape[0]-1:
                id+=str(eventid['eventid'][i] )
            else:
                id+=str(eventid['eventid'][i] ) +','
        if id !='':     
            groups=pd.read_sql_query("SELECT title FROM therapygroup where id IN ({}) ".format(id),conn)
            for i in range(0,groups.shape[0]):
                allfeature+=str(groups['title'][i] ) +' '
        cat_df=pd.read_sql_query("SELECT * FROM usercat where username='{}' ORDER BY browsing".format(user_df['username'][z]),conn)
        for i in range(0,cat_df.shape[0]):
            if i==6:
                break
            if  allfeature.find(str(cat_df['category'][i] ))==-1:
                if i==cat_df.shape[0]-1:
                    allfeature+=str(cat_df['category'][i] )
                else:
                    allfeature+=str(cat_df['category'][i] ) +' '
        features.append(allfeature)    
    # colums=['interest','groups']
    user_df['combined_features']=features
    cm=CountVectorizer().fit_transform(user_df['combined_features'])
    cs=cosine_similarity(cm)
     
    scores=list(enumerate(cs[user_id]))
  
    sorted_scores=sorted(scores,key=lambda x:x[1],reverse=True)
    print(sorted_scores)
    j=0 
   
    recomandeduser=[]
    for item in sorted_scores:
        if user_df['username'][item[0]] !=username:
          recomandeduser.append({'username':user_df['username'][item[0]],'Bio':user_df['Bio'][item[0]],'gender':user_df['gender'][item[0]],'DoB':user_df['DoB'][item[0]],'imagename':user_df['imagename'][item[0]]})
          j=j+1
        if j>=3:
            break
    return jsonify({'recomandeduser':recomandeduser})    




if __name__ == "__main__":
    app.run(debug = True,port=5000,host='192.168.1.248')
    







