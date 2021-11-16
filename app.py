import streamlit as st
import sqlite3
import re
import time
import webbrowser

chromepath = r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe"
webbrowser.register('chrome', None, webbrowser.BackgroundBrowser(chromepath))  

#邮箱格式验证
def validateEmail(email):
    if re.match("^.+\\@(\\[?)[a-zA-Z0-9\\-\\.]+\\.([a-zA-Z]{2,3}|[0-9]{1,3})(\\]?)$", email) != None:
        return True
    else:
        return False

#兑换码导入
def redemptionCodeImport(code):
    conn = sqlite3.connect('test.db')
    cursor = conn.cursor()
    #兑换码批量导入
    #cursor.executemany("insert into tab_FDVDownload (apple_id,redemption_code,download_count,last_downloadtime) values(?)", code)
    #兑换码单个导入
    cursor.execute("insert into tab_FDVDownload(redemption_code) values(?)", (code,))
    conn.commit()
    conn.close()

#查询apple是否分配过兑换码
def redemptionCodeDistribute(apple_id):
    conn = sqlite3.connect('test.db')
    cursor = conn.cursor()
    cursor.execute("select * from tab_FDVDownload where apple_id=?",(apple_id,))
    #cursor.execute("select * from tab_FDVDownload")
    apple_id_res = cursor.fetchone()
    if apple_id_res is not None:
        redemption_code = apple_id_res[1]
        # 更新该条数据
        count = apple_id_res[2]
        if count is None:
            count = 1
        else:
            count += 1
        now_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        cursor.execute("update tab_FDVDownload set apple_id=?,download_count=?,last_downloadtime=? where redemption_code=?",(apple_id,count,now_time,redemption_code))
    else:
        #插入数据
        #1.找到未分配兑换码的数据
        cursor.execute("select * from tab_FDVDownload where apple_id is null")
        code_res = cursor.fetchone()
        if code_res is not None:
            #2.更新该条数据
            redemption_code = code_res[1]
            count = code_res[2]
            if count is None:
                count = 1
            else:
                count += 1
            now_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
            cursor.execute("update tab_FDVDownload set apple_id=?,download_count=?,last_downloadtime=? where redemption_code=?",(apple_id,count,now_time,redemption_code))
        else:
            return "兑换码已全部使用，请联系管理员导入兑换码"

    # for line in res:
    #     st.write(line)
    conn.commit()
    conn.close()

    #返回兑换码
    return redemption_code


form = st.form(key="my-form")
apple_id = form.text_input('输入Apple ID')
#code = form.text_input('输入兑换码')
submit = form.form_submit_button('提交')
if submit:
    if validateEmail(apple_id):
        #redemptionCodeImport(code)
        code = redemptionCodeDistribute(apple_id)
        st.success(apple_id+"兑换码为:"+code)
        #重定向到下载连接
        url = "https://apps.apple.com/cn/app/beddit-for-model-3-5/id1411596157"
        st.write(url)
        #webbrowser.get('chrome').open(url,new=0,)
        webbrowser.open(url,new=0,)
    else:
        st.warning('apple id格式有误，请检查！')
