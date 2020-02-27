import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import plotly as py
import  plotly.graph_objects as go
import seaborn as sns
import requests
from bs4 import BeautifulSoup
import time
from statsmodels.stats.anova import anova_lm
from statsmodels.formula.api import ols

'''
时间：2020年2月24日
作者：振兴
分析目标：
    1、统计出版国家、使用饼状图（分类太多，不好描述）、条形图描述
    2、统计电影类型。使用饼状图、条形图
    3、对出版时间进行分段分析
    4、统计电影时长，并判断电影时长与出版时间是否存在相关性
    4、对电影评分进行统计分析
步骤：
    1、首先通过爬虫获取豆瓣电影链接地址
    2、将电影的详情信息输出到csv文件中存储
    3、通过pandas、numpy、matplotlib、plotpy、seaborn 进行分析可视化

'''
#该方法获取豆瓣电影的题目和链接，并转存到csv文件中
def GetMovieInfo():
    url_titlelist=[]
    header = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.70 Safari/537.36'}
    for i in range(0,251,25):
        re = requests.get('https://movie.douban.com/top250?start='+str(i)+'&filter=',headers=header)
        soup = BeautifulSoup(re.text,'lxml')
        urls = soup.findAll(class_='hd')
        #url.a['href'] 获取链接  url.span.text 获取电影名称
        for url in urls:
            url_titlelist.append({'movietitle':url.span.text,'movieurl':url.a['href']})
    #创建Dataframe格式数据,通过字典格式进行转入
    df = pd.DataFrame(url_titlelist)
    df.to_csv('data/douban_movie_url.csv')

def GetDetailInfo():
    #获取电影的详细信息，包括导演、编剧、主演、类型、制作地区、语言、上映时间、片长、评分、评价人数、观看人数、想看人数、短评条数
    data=[]
    movie = pd.read_csv('data/douban_movie_url.csv')
    print(movie)
    MovieDetail=[]
    header = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.70 Safari/537.36',
              'Cookie':'bid=IWe9Z6busEk; douban-fav-remind=1; gr_user_id=f7fae037-6b68-4d42-8a9e-19a1ef3263a7; _vwo_uuid_v2=DB1D5D334A6BE3FD5143EAF4C7FD52463|f63a15d9f0accbd1c8836fedba0591ff; viewed="10571608_10571602_26589104_1195595"; __yadk_uid=Ife4NimEiP6V0taky1FCMpfTWLdNfRan; ll="118136"; trc_cookie_storage=taboola%2520global%253Auser-id%3De88de203-688b-415e-9d09-0e40d41140ec-tuct41d9fc9; __utmv=30149280.17939; douban-profile-remind=1; __gads=ID=6d22200e8d8100ab:T=1580716605:S=ALNI_MY8d2gzAYOhbwuwAKgaSbx9kRa8kw; __utmc=30149280; __utmz=30149280.1582461492.18.13.utmcsr=baidu|utmccn=(organic)|utmcmd=organic; __utmc=223695111; __utmz=223695111.1582461492.11.6.utmcsr=baidu|utmccn=(organic)|utmcmd=organic; ct=y; _pk_ref.100001.4cf6=%5B%22%22%2C%22%22%2C1582518519%2C%22https%3A%2F%2Fwww.baidu.com%2Flink%3Furl%3Dw3K7KtSpdRTRt9Nso7KvfEqEScg3YYFJZms1zZ0A_jhdFN1ZhldskLw7VdKnHSb7%26wd%3D%26eqid%3De6fdfb68004b8856000000035e527231%22%5D; _pk_ses.100001.4cf6=*; __utma=30149280.1262479007.1562647114.1582513563.1582518519.22; __utmb=30149280.0.10.1582518519; __utma=223695111.770823807.1572251330.1582513563.1582518519.15; __utmb=223695111.0.10.1582518519; ap_v=0,6.0; dbcl2="179397940:9GTKde9XxvY"; ck=6E9C; push_doumail_num=0; push_noty_num=0; _pk_id.100001.4cf6=ba941b513938cd23.1572251329.15.1582519262.1582514328.'
              }
    for url in movie['movieurl'].values.tolist():
        re = requests.get(url,headers=header)
        time.sleep(1)
        soup = BeautifulSoup(re.text,'lxml')
        try:
            title = soup.find('h1').span.text #标题
            director = soup.find(class_='attrs').a.text#导演
            Screenwriter = soup.findAll(class_='attrs')[1].text#编剧
            main_performer = soup.findAll(class_='attrs')[2].text.split('/') #这里只选择前3主演
            main_performer = main_performer[0]+'/'+ main_performer[1]+'/'+main_performer[2]
            Type = soup.findAll(class_='pl')[3].find_next_siblings("span")
            Types=''
            for type in Type:
                if(type.text=='制片国家/地区:' or type.text=='官方网站:'):
                    break
                else:
                    Types+=type.text+'/'
            Types = Types[:-1]#类型

            region = soup.findAll(class_='pl')[4]
            if(region.text=='官方网站:'):
                region = soup.findAll(class_='pl')[5]
            region = region.next.next#制作地区

            Language = soup.findAll(class_='pl')[5]
            if(Language.text=='制片国家/地区'):
                Language = soup.findAll(class_='pl')[6]
            Language = Language.next.next#语言

            ShowtTime =  soup.findAll(class_='pl')[6]
            if(ShowtTime.text=='语言:'):
                ShowtTime = soup.findAll(class_='pl')[7]
            ShowtTime = ShowtTime.find_next_sibling("span").text.split('(')[0]#上映日期

            Film_length =  soup.findAll(class_='pl')[7]
            if(Film_length.text=='上映日期:'):
                Film_length = soup.findAll(class_='pl')[8]
            Film_length = Film_length.find_next_sibling("span").text[:-2]#片长

            score = soup.find('strong',class_='ll rating_num').text#评分
            rating_people = soup.find('a',class_='rating_people').text.strip()[:-3]#评价人数
            watching_people = soup.find('div','subject-others-interests-ft').a.text[:-3]#看过人数
            wtsee_people = soup.find('div','subject-others-interests-ft').a.find_next_siblings("a")[0].text[:-3] #想看人数
            comments_people = soup.find('div',class_='mod-hd').h2.span.a.text.split(' ')[1]#短评人数
            #到这里 前面数据已经测试完毕 接下来就是写入文件
            AllInfo={'Title':title,'Director':director,'Screenwriter':Screenwriter,'Main_performer':main_performer,'Types':Types,'Region':region,'Language':Language,'ShowTime':ShowtTime,'Film_length':Film_length,'Score':score,'Rating_people':rating_people,'Watching_people':watching_people,'Wtsee_people':wtsee_people,'Comments_people':comments_people}
            data.append(AllInfo)
            print(AllInfo)
        except:
            print('error')
            continue;
    df = pd.DataFrame(data)
    df.to_csv('data/douban_movie_info.csv',index=False)#不把索引输入到文件中

#首先导入数据，进行数据清洗，再将清洗后的数据进行不保存
def CleanData():
    movie_info = pd.read_csv('data/douban_movie_info.csv')
    movie_info['Title'] = [title[0] for title in movie_info['Title'].str.split(' ')]#只取中文标题
    #提取出版年份
    movie_info['ShowtTime'] = pd.to_datetime(movie_info['ShowtTime'],errors='coerce').dt.year
    #清洗片长数据
    movie_info['Film_length'] =[lenth[0] for lenth in movie_info['Film_length'].str.split('分')]
    flag = movie_info.to_csv('data/douban_movie_info2.0.csv',index=False)
    print(flag)

#统计出版国家的数量，并使用柱状图和饼状图进行描述
def Statistical_nation():
    Movie_info= pd.read_csv('data/douban_movie_info2.0.csv')
    Nations  = []
    for nation in Movie_info['Region'].str.split('/'):
        for nations in nation:
            Nations.append(nations.strip())
    ps = pd.Series(Nations)
    df = pd.DataFrame(ps,columns=['Nation'])
    df['Nation'].value_counts()
    #数据可视化，饼状图
    Piedata = go.Pie(labels=df['Nation'].value_counts().index,values=df['Nation'].value_counts())
    Layout = go.Layout(title='豆瓣电影Top250出版国家比例')
    fig = go.Figure(data=[Piedata],layout = Layout)
    py.offline.plot(fig,filename='pic/doubanTop250_Nation_pie.html')
    #数据可视化-条形图
    Bardata = go.Bar(x=df['Nation'].value_counts().index,y=df['Nation'].value_counts(),marker=dict(color='steelblue'),opacity=0.5)
    Layout = go.Layout(title='豆瓣电影Top250出版国家数据',xaxis=dict(title='国家',tickangle=45),yaxis=dict(title='数量'))
    fig = go.Figure(data=[Bardata],layout=Layout)
    py.offline.plot(fig,filename='pic/doubanTop250_Nation_bar.html')

#
def Statistical_type():
    Types=[]
    Movie_info= pd.read_csv('data/douban_movie_info2.0.csv')
    for type in Movie_info['Types'].str.split('/'):
        for types in type:
            Types.append(types.strip())
    ps = pd.Series(Types)
    #数据可视化-饼状图
    Piedata = go.Pie(labels=ps.value_counts().index,values=ps.value_counts())
    Layout = go.Layout(title='豆瓣电影Top250电影类型比例')
    fig = go.Figure(data=[Piedata],layout = Layout)
    py.offline.plot(fig,filename='pic/doubanTop250_Type_pie.html')
    #数据可视化-条形图
    Bardata = go.Bar(x=ps.value_counts().index,y=ps.value_counts(),marker=dict(color='steelblue'),opacity=0.5)
    Layout = go.Layout(title='豆瓣电影Top250电影类型数据',xaxis=dict(title='种类',tickangle=45),yaxis=dict(title='数量'))
    fig = go.Figure(data=[Bardata],layout=Layout)
    py.offline.plot(fig,filename='pic/doubanTop250_Type_bar.html')

def Statistical_ShowtTime():
    Movie_info= pd.read_csv('data/douban_movie_info2.0.csv')
    Movie_info['ShowTime'] = Movie_info['ShowTime'].astype('int')
    #统计哪一年的优秀影片最多
    Excellent_Year=Movie_info['ShowTime'].mode()#2004年
    #统计出现优秀影片最多的前十个年份
    More_MovieByYear = Movie_info['ShowTime'].value_counts().head(10)
    #统计近31年的影片数量，用折线图表现趋势
    MovieByYear = Movie_info['ShowTime'].value_counts(sort=False).tail(31)
    #进行每10年进行划区，统计在10年内出版的优秀电影
    Cutdata = pd.cut(Movie_info['ShowTime'],9).value_counts(sort=False)
    #将数据按序排列，分别取0、1/4、1/2、3/4、1 的四分位数据进行区间划分
    Qcutdata = pd.qcut(Movie_info['ShowTime'],4).value_counts()
    print(Cutdata)
    #柱状图表示优秀影片的前十个年份
    Bardata = go.Bar(x=More_MovieByYear.index,y=More_MovieByYear.values,marker=dict(color='orange'),opacity=0.5)
    Layout = go.Layout(title='豆瓣电影Top250出版最多的前十个年份',xaxis=dict(title='年份',tickangle=45,tickmode='array',tickvals=More_MovieByYear.index),yaxis=dict(title='数量'))
    fig = go.Figure(data=[Bardata],layout=Layout)
    py.offline.plot(fig,filename='pic/doubanTop250_ShowTime_bar.html')
    #折线图表示近31年影片数量
    Scatterdata = go.Scatter(x=MovieByYear.index,y=MovieByYear.values,mode='lines',name='影片')
    Layout = go.Layout(title='豆瓣电影Top250近31年的影片数量',xaxis=dict(title='年份',tickangle=45),yaxis=dict(title='数量'))
    fig = go.Figure(data=[Scatterdata],layout=Layout)
    py.offline.plot(fig,filename='pic/doubanTop250_ShowTime_scatter.html')
    #饼状图表示
    Piedata = go.Pie(labels=['1930-1940','1940-1950','1950-1960','1960-1970','1970-1980','1980-1990','1990-2000','2000-2010','2010-2020'],values=Cutdata.values)
    Layout = go.Layout(title='豆瓣电影Top250之十年内电影数量')
    fig = go.Figure(data=[Piedata],layout = Layout)
    py.offline.plot(fig,filename='pic/doubanTop250_ShowTime_pie.html')


def Statistical_Film_length():
    Movie_info= pd.read_csv('data/douban_movie_info2.0.csv')
    Movie_info['ShowTime'] = Movie_info['ShowTime'].astype('int')
    Movie_info['Film_length'] = Movie_info['Film_length'].astype('int')
    #电影最长时长为238分钟，最短时长为45分钟
    # print(Movie_info['Film_length'].max(),Movie_info['Film_length'].min())
    #对电影时间数据进行切分
    CutData = pd.cut(Movie_info['Film_length'],4).value_counts()
    #饼状图进行分析
    Pie = go.Pie(values=CutData.values,labels=['94-141分钟','142-189分钟','45-93分钟','190-238分钟'])
    Layout = go.Layout(title='豆瓣电影Top250电影时长分析')
    fig = go.Figure(data=[Pie],layout=Layout)
    #py.offline.plot(fig,filename='pic/doubanTop250_Film_length_pie.html')

    #探索上映时间和电影时长有没有相关性，这里使用方差分析
    model = ols('Film_length ~ C(ShowTime)',data=Movie_info).fit()
    result = anova_lm(model)#方差分析函数
    #print(result)从结果数据中，我们可以看到p-value值为0.0105 小于0.05 表示电影上映时间与电影时长有很大的关系
    #下面用散点图来展示一下我们这个结论
    Scatter = go.Scatter(x=Movie_info['ShowTime'].values,y=Movie_info['Film_length'].values,mode='markers')
    Layout = go.Layout(title='豆瓣电影Top250电影时长与上映时间关系分析',xaxis=dict(title='上映时间'),yaxis=dict(title='电影时长'))
    fig = go.Figure(data=[Scatter],layout=Layout)
    #从结果中可以看到，现代的电影时长更加集中，没有时长很高的，也没有时长很低的。
   # py.offline.plot(fig,filename='pic/doubanTop250_Film_length_scatter.html')
    #使用皮尔森系数对两个变量进行线性分析，结果为-0.097，说明随着上映时间的增加，电影时长变短。但由于值比较小，两个变量的影响程度不大。
    pearson_relation = Movie_info[['ShowTime','Film_length']].corr(method='pearson')
    print(pearson_relation)

def Statistical_Score_And_Rest():
    Movie_info= pd.read_csv('data/douban_movie_info2.0.csv')
    Movie_info['ShowTime'] = Movie_info['ShowTime'].astype('int')
    Movie_info['Score'] = Movie_info['Score'].astype('float')
    Movie_info['Film_length'] = Movie_info['Film_length'].astype('int')
    #先大概看一下评分数据 mean=8.87 min=8.3 max=9.7,50%=8.8
    print(Movie_info['Score'].describe())

    #探索评分与上映时间、时长的关系的关系 先使用散点图进行描述
    # Scatter1 = go.Scatter(x=Movie_info['Score'],y= Movie_info['ShowTime'],name='上映时间',mode='markers')
    # Scatter2 = go.Scatter(x=Movie_info['Score'],y= Movie_info['Film_length'],name='电影时长',yaxis='y2',mode='markers')
    # Layout = go.Layout(title='评分与上映时间、时长的关系',xaxis=dict(title='电影评分'),yaxis=dict(title='上映时间'),yaxis2=dict(title='电影时长',side='right',overlaying='y'))
    # fig = go.Figure(data=[Scatter1,Scatter2],layout = Layout)
    # #从结果图中，我们无法清晰的找到评分与上映时间、时长的关系
    # py.offline.plot(fig,filename='pic/doubanTop250_relation_lenth_score_time.html')
    #接下来使用方差分析进行相关分析
    model = ols('Score ~ C(ShowTime)+C(Film_length)',data=Movie_info).fit()#用来配置几个相关联的变量
    result = anova_lm(model)#方差分析函数
    #print(result)#Score-Showtime pvalue=0.000531  Score-Film_length pvalue=0.0235
    #从结果中，我们可以看到pvalue值均小于0.05 说明，评分与上映时间和时长是有关系的。
    #接下来使用斯皮尔曼相关系数Spearman进行线性分析
    Spearman_relation1 = Movie_info[['Score','Film_length']].corr(method='spearman')
    Spearman_relation2 = Movie_info[['Score','ShowTime']].corr(method='spearman')
    # print(Spearman_relation1)
    # print(Spearman_relation2)
    #Score--File_length 0.1677 正相关，也就是电影评分与电影长度存在一定的正线性相关
    #Score--ShowTime -0.187431 负相关，也就是电影评分与上映时间存在一定的负线性相关

    #接下来接着探索观看人数与评分以及上映时间与观看人数的关系 还是使用spearman相关系数进行分析
    Spearman_relation3 = Movie_info[['Watching_people','Score']].corr(method='spearman')
    Spearman_relation4 = Movie_info[['ShowTime','Watching_people']].corr(method='spearman')
    print(Spearman_relation3)#pvalue=0.1151
    print(Spearman_relation4)#pvalue=0.1580
    #从上面两个结果分析可得，观看人数与评分存在正相关性、上映时间与观看人数呈现正相关性。

    #观看人数、想看人数、评论人数三个数据进行同一张折线图进行趋势显示对比
    Scatterdata1 = go.Scatter(x=Movie_info['Watching_people'].index,y=Movie_info['Watching_people'],mode='lines',name='观看人数')
    Scatterdata2 = go.Scatter(x=Movie_info['Wtsee_people'].index,y=Movie_info['Wtsee_people'],mode='lines',name='想看人数',yaxis='y2')
    Scatterdata3 = go.Scatter(x=Movie_info['Comments_people'].index,y=Movie_info['Comments_people'],mode='lines',name='评论人数',yaxis='y2')
    Layout = go.Layout(title='观看人数、想看人数、评论人数趋势对比',xaxis=dict(title='计数'),yaxis=dict(title='观看人数'),yaxis2=dict(title='想看和评论人数',overlaying='y',side='right'))
    fig = go.Figure(data=[Scatterdata1,Scatterdata2,Scatterdata3],layout=Layout)
    py.offline.plot(fig,filename='pic/doubanTop250peoplenumber_scatter.html')
    #从结果分析来看,这三者基本上是呈现一个非常强烈的正线性相关，仅仅通过图像的形状来看，就非常的相似。

    #接下来统计以下评论率（评论人数/观看人数）
    Movie_info['Comments_rate'] = Movie_info['Comments_people']/Movie_info['Watching_people']
    print(Movie_info['Comments_rate'].describe())#mean=0.130242、min=0.045363、max=0.291848

if __name__ == '__main__':
    Statistical_Score_And_Rest()

