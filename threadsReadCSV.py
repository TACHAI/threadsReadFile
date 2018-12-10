# _*_coding:utf-8_*_
import time, threading, configparser,os,requests,json

'''
Reader类，继承threading.Thread
@__init__方法初始化
@run方法实现了读文件的操作
'''
class Reader(threading.Thread):
    def __init__(self, file_name, start_pos, end_pos,url):
        super(Reader, self).__init__()
        self.file_name = file_name
        self.start_pos = start_pos
        self.end_pos = end_pos
        self.url = url

    def run(self):
        path = os.getcwd();

        fd = open(path + '\\'+self.file_name, 'r',encoding='utf-8')
        # fd = open(path + '\\'+self.file_name, 'rb',encoding='utf-8')

        successFile = open(path + '\\' + 'successFile.csv', 'a', encoding='gbk');
        errorFile = open(path + '\\' + 'errorFile.csv', 'a', encoding='gbk');
        '''
        该if块主要判断分块后的文件块的首位置是不是行首，
        是行首的话，不做处理
        否则，将文件块的首位置定位到下一行的行首
        '''
        if self.start_pos != 0:
            fd.seek(self.start_pos-1)
            if fd.read(1).encode('utf-8') != '\n':
                line = fd.readline()
                self.start_pos = fd.tell()
        fd.seek(self.start_pos)
        '''
        对该文件块进行处理
        '''
        while (self.start_pos <= self.end_pos):
            line = fd.readline()
            '''
            do somthing
            '''
            print(line)
            tempArr = line.split(',');
            #第一个是问题
            ques = tempArr[0];
            # 在下面的json添加请求的数据体
            # 聊天接口
            sessionId=str(int(round(time.time() * 1000)))

            thread = threading.current_thread()
            print("当前线程:"+thread.getName())
            print("请求的url:"+self.url)
            print("sessionId:"+sessionId)
            print("请求的问题:"+ques)
            res = requests.post(self.url, data={"word":ques,"sessionId":sessionId}, headers={"Content-Type": "application/x-www-form-urlencoded"})
            print("response:"+res.text)
            # 批量测试接口
            res.encoding = 'utf-8'
            response = json.loads(res.text)
            if response['status']==0:
                successFile.writelines('\ntrue,'+ques+","+response['data'])
            if response['status']==1:
                errorFile.write('false,'+ques+","+response['msg'])
            self.start_pos = fd.tell()

'''
对文件进行分块，文件块的数量和线程数量一致
'''
class Partition(object):
    def __init__(self, file_name, thread_num,url):
        self.file_name = file_name
        self.block_num = thread_num
        self.url = url

    def part(self):
        fd = open(self.file_name, 'r')
        fd.seek(0, 2)
        pos_list = []
        file_size = fd.tell()
        block_size = file_size/self.block_num
        start_pos = 0
        for i in range(self.block_num):
            if i == self.block_num-1:
                end_pos = file_size-1
                pos_list.append((start_pos, end_pos))
                break
            end_pos = start_pos+block_size-1
            if end_pos >= file_size:
                end_pos = file_size-1
            if start_pos >= file_size:
                break
            pos_list.append((start_pos, end_pos))
            start_pos = end_pos+1
        fd.close()
        return pos_list

if __name__ == '__main__':

    '''
    读取配置文件
    '''
    config = configparser.ConfigParser()
    config.readfp(open('conf.ini'))
    #文件名
    file_name = config.get('info', 'fileName')
    #线程数量
    thread_num = int(config.get('info', 'threadNum'))
    #URL
    url = config.get('info','url')
    #起始时间
    start_time = time.clock()
    p = Partition(file_name, thread_num,url)
    t = []
    pos = p.part()
    #生成线程
    for i in range(thread_num):
        t.append(Reader(file_name, *pos[i],url))
    #开启线程
    for i in range(thread_num):
        t[i].start()
    for i in range(thread_num):
        t[i].join()
    #结束时间
    end_time = time.clock()
    print ("Cost time is %f" % (end_time - start_time))