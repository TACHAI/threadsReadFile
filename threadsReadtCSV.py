# _*_coding:utf-8_*_
import time, threading, configparser,os,requests,json,csv

'''
Reader类，继承threading.Thread
@__init__方法初始化
@run方法实现了读文件的操作
'''
class Reader(threading.Thread):
    def __init__(self, file_name, temp, end_pos,url):
        super(Reader, self).__init__()
        self.file_name = file_name
        self.temp = temp
        self.end_pos = end_pos
        self.url = url

    def run(self):
        path = os.getcwd();

        with open(path + '\\'+self.file_name, 'r',encoding='utf-8')as f:
            fd = csv.reader(f)
            for index, rows in enumerate(fd):
                if(index>self.temp*self.end_pos and index<=(self.temp+1)*self.end_pos):
                    successFile = open(path + '\\' + 'successFile.csv', 'a', encoding='gbk');
                    errorFile = open(path + '\\' + 'errorFile.csv', 'a', encoding='gbk');
                    line = rows
                    error=0
                    try:
                        thread = threading.current_thread()

                        print("当前线程:" + thread.getName())
                        print("当前线程数:" + str(self.temp*self.end_pos))
                        print("行数:" + str(self.end_pos))
                        print("line:"+str(line))
                        #第一个是问题
                        ques = line[0];
                        answer = line[1];
                        # 在下面的json添加请求的数据体
                        print("请求的url:"+self.url)
                        print("请求的问题:"+ques)
                        res = requests.post(self.url, json={"query": ques + "?split"},headers={"Content-Type": "application/json"})
                        print("response:" + res.text)
                        # 批量测试接口
                        res.encoding = 'utf-8'
                        response = json.loads(res.text)
                        if response['answer'] == answer:
                            successFile.writelines('\n成功,' + ques)
                        if response['answer'].split("&&")[0] != answer:
                            errorFile.write('\n失败,' + ques + "," + response['answer'])
                    except:
                        error+=1
                        print("ERROR:"+str(error))

'''
对文件进行分块，文件块的数量和线程数量一致
'''
class Partition(object):
    def __init__(self, file_name, thread_num):
        self.file_name = file_name
        self.block_num = thread_num

    def part(self):
        path = os.getcwd()
        with open(path + '\\' + self.file_name, 'r', encoding='utf-8')as f:
            fd = csv.reader(f)
            t = 0;
            for row in fd:
                t +=1;

            print("line_num:"+str(t))
            temp=t%self.block_num
            block_size = (t-temp)/self.block_num
            end_pos = block_size
            return end_pos

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
    p = Partition(file_name, thread_num)
    t = []
    pos = p.part()
    #生成线程
    for i in range(thread_num):
        t.append(Reader(file_name,i, pos,url))
    #开启线程
    for i in range(thread_num):
        t[i].start()
    for i in range(thread_num):
        t[i].join()
    #结束时间
    end_time = time.clock()
    print ("Cost time is %f" % (end_time - start_time))