
from selenium import webdriver
from datetime import datetime, timedelta
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
import pandas as pd
from bs4 import BeautifulSoup
import time


# Create a new instance of the Edge driver
driver = webdriver.Edge()
driver.maximize_window()
y=0
driver.get('https://www.upwork.com/nx/find-work/most-recent')
time.sleep(2)
try:
    driver.find_element(By.XPATH,"h1[contains(.,'Login')]")
except NoSuchElementException as e:
    print(e)
        
    driver.get('https://www.upwork.com/ab/account-security/login')
    time.sleep(5)
    driver.find_element(By.XPATH,"//input").send_keys('<your email id>')
    time.sleep(2)
    driver.find_element(By.XPATH,"//button[contains(@id,'continue')]").click()
    time.sleep(20)
    pass
while True:
    try:
        dff=pd.read_csv("testjobs.csv")
    except Exception as e:
        print("No csv found")
        dff=pd.DataFrame()
    
    df=pd.DataFrame()
    driver.get('https://www.upwork.com/nx/find-work/most-recent')
    time.sleep(5)
    now = datetime.now()
    total_height = int(driver.execute_script("return document.body.scrollHeight"))

    for i in range(1, total_height, 5):
        driver.execute_script("window.scrollTo(0, {});".format(i))
    time.sleep(5)

    lst=driver.find_elements(By.XPATH,"//div[contains(@data-test,'job-tile-list')]//section")
    y=0
    for sec in lst:
        score=0
        try:
            # Keywords to check for
            keywords = ['database','sql','analy','mining', 'python', 'scrap', 'pandas', 'extraction','join our team','full time',]
            tags = sec.find_elements(By.XPATH, ".//div[@class='air3-token-wrap']//a")
            for tag in tags:
                # Check if any keyword is present in the tag text
                if any(keyword in tag.text.lower() for keyword in keywords):
                    score += 1
        except Exception as e:
            pass
        try:
            job_title=sec.find_element(By.XPATH,".//h3//a")
            df.at[y,"Job_Title"]=job_title.text
            if any(keyword in job_title.text.lower() for keyword in keywords):
                score=score+1
            df.at[y,"Job_Link"]=job_title.get_attribute('href')
        except Exception as e:
            pass
        try:
            job_type=sec.find_element(By.XPATH,'.//small//strong[contains(@data-test,"job-type")]')
            df.at[y,"Job_Type"]=job_type.text
        except Exception as e:
            pass
        try:
            job_duration=sec.find_element(By.XPATH,'.//small//span[@data-test="duration"]')
            df.at[y,"Job_Duration"]=job_duration.text
        except Exception as e:
            pass
        try:
            job_posted=sec.find_element(By.XPATH,'.//small//span[@data-test="posted-on"]')
            if "minute" in job_posted.text:
                t=int(job_posted.text.split(" ")[0])               
                new_time = now - timedelta(minutes=t)                
                nt=new_time.strftime('%Y-%m-%d %H:%M:%S').split(" ")[-1].split(".")[0]
                nt=nt.split(".")[0]
                df.at[y,"Job_Post_Time"]=nt
            elif "second" in job_posted.text:
                t=int(job_posted.text.split(" ")[0])               
                new_time = now - timedelta(seconds=t)                
                nt=new_time.strftime('%Y-%m-%d %H:%M:%S').split(" ")[-1].split(".")[0]
                nt=nt.split(".")[0]
                df.at[y,"Job_Post_Time"]=nt
        except Exception as e:
            pass
        try:
            p=sec.find_element(By.XPATH,'.//span[contains(@data-test,"budget")]')
            budget=int(p.text.replace("$","").replace("+","").replace("K","000"))
            print("Budget:",budget)
            df.at[y,"Budget"]=budget
        except Exception as e:
            print("budget error",e)
            pass
        try:
            job_desc=sec.find_element(By.XPATH,'.//span[@data-test="job-description-text"]')
            df.at[y,"Job_Description"]=job_desc.text
            if any(keyword in job_desc.text.lower() for keyword in keywords):
                score=score+1
        except Exception as e:
            pass
        try:
            prop=sec.find_element(By.XPATH,'.//strong[@data-test="proposals"]')
            df.at[y,"Proposals"]=prop.text
        except Exception as e:
            pass
        try:
            p=sec.find_element(By.XPATH,'.//small[contains(@data-test,"client-feed")]')
            soup=BeautifulSoup(p.get_attribute('outerHTML'),'lxml')
            fb=soup.get_text().strip()
            rating=fb.split("Stars")[0].strip()
            reviews=fb.split("on")[-1].strip().split(" ")[0]
            df.at[y,"Rating"]=float(rating)
            df.at[y,"Reviews"]=int(reviews)
            if reviews > 100:
                score=score+3
            elif reviews > 50:
                score=score+2
            else:
                score=score+1
        except Exception as e:
            pass
        try:
            p=sec.find_element(By.XPATH,'.//span[contains(@data-test,"amount")]')
            amt=int(p.text.replace("$","").replace("K","000").replace("+",""))
            df.at[y,"Amount"]=amt
            if amt > 50000:
                score=score+5
            elif amt > 10000:
                score=score+1
        except Exception as e:
            pass
        try:
            p=sec.find_element(By.XPATH,'.//small[contains(@data-test,"client-country")]')
            df.at[y,"Country"]=p.text.strip()
            keywords = ['United', 'Canada']
            
            # Check if any keyword is present in the tag text
            if any(keyword in p.text.strip() for keyword in keywords):
                score += 1
        except Exception as e:
            pass
        df.at[y,'Score']=score
        y=y+1
        try:
            df=df[~df['Job_Link'].isin(dff['Job_Link'])]
        except Exception as e:
            pass
        #print("Deduplication Error")
        df=pd.concat([df, dff], axis=0)
        df.to_csv("testjobs.csv",index=False)
    print(now)
    time.sleep(30)