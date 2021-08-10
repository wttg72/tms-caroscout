from time import time, sleep
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup as soup
import re
import telegram
import os

# functions

def getDesc(link):
    chrome_options = Options()
    chrome_options.binary_location = os.environ.get("GOOGLE_CHROME_BIN")
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-sh-usage")
    driver = webdriver.Chrome(executable_path= os.environ.get("CHROMEDRIVER_PATH"), options=chrome_options)
    driver.get(link)
    paragraphs = driver.find_elements_by_tag_name('section')
    try:
        paragraph = paragraphs[3].text
    except IndexError:
        paragraph = paragraphs[2].text

    driver.quit()
    desc = paragraph.split("Type")[1].split('read more')[0].split('Meet-up')[0]
    return desc

def between(value, a, b):
    # Find and validate before-part.
    pos_a = value.find(a)
    if pos_a == -1: return ""
    # Find and validate after part.
    pos_b = value.rfind(b)
    if pos_b == -1: return ""
    # Return middle part.
    adjusted_pos_a = pos_a + len(a)
    if adjusted_pos_a >= pos_b: return ""
    return value[adjusted_pos_a-3:pos_b+4]

finaltxt = r".\scraped.txt"

def blacklink(link):
    f_w = open(finaltxt, "a", encoding="utf-8")
    f_w.write(link + "\n")
    f_w.close()

def countdown(t): 
    while t: 
        mins, secs = divmod(t, 60) 
        timer = '{:02d}:{:02d}'.format(mins, secs)
        print("Welcome to Auto Carousell Scout Bot! Delay: ",timer, end="\r") 
        sleep(1) 
        t -= 1

    print('Bot Running...                                              ') 

filter_users = ["mikemotorrecovery"]
filter_links = ["scrap","export"]
filter_descs = ["coi","COI","Coi","installment","Installment","instalment","Instalment"]
req_descs = ["coe","COE","Coe"]
    
def filterUser(user, filter_users):
    filter_matches = 0
    for filter_user in filter_users:
        if filter_user in user:
            filter_matches += 1
    if filter_matches == 0:
        return True
    elif filter_matches > 0:
        print(user + " failed filter " + filter_user)
        return False

def filterLink(link, filter_links):
    filter_matches = 0
    for filter_link in filter_links:
        if filter_link in link:
            filter_matches += 1
    if filter_matches == 0:
        return True
    elif filter_matches > 0:
        print(link + " failed filter " + filter_link)
        return False

def filterDesc(desc, filter_descs):
    filter_matches = 0
    for filter_desc in filter_descs:
        if filter_desc in desc:
            filter_matches += 1
    if filter_matches == 0:
        return True
    elif filter_matches > 0:
        print(desc + " failed filter " + filter_desc)
        return False

def reqDesc(desc, req_desc):
    req_matches = 0
    for req_desc in req_descs:
        if req_desc in desc:
            req_matches += 1
    if req_matches == 0:
        print(desc + " failed req " + req_desc)
        return False
    elif req_matches > 0:
        return True

#main loop

print("started")
chrome_options = Options()
#chrome_options.add_argument("--window-size=1920,2160")

chrome_options.binary_location = os.environ.get("GOOGLE_CHROME_BIN")
#chrome_options.add_argument("--headless")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-sh-usage")
driver = webdriver.Chrome(executable_path= os.environ.get("CHROMEDRIVER_PATH"), options=chrome_options)
driver.get("https://www.carousell.sg/categories/motorcycles-108/motorcycles-for-sale-1592/class-2b-1595/?addRecent=false&canChangeKeyword=false&condition_v2=USED&includeSuggestions=false&price_end=12000&price_start=100&sc=0a0208141a0408bbe1722a180a0c636f6e646974696f6e5f763212060a045553454478012a210a05707269636522160a09090000000000005940120909000000000070c74078012a170a0b636f6c6c656374696f6e7312060a043135393578012a180a0c636f6e646974696f6e5f763212060a045553454478012a210a05707269636522160a09090000000000005940120909000000000070c740780132040803780142060800100018005000&searchId=gp6nEV&sort_by=time_created%2Cdescending")
print ("Headless Chrome Initialized")

#click load more
for x in range(0, 8):
    sleep(3)
    load_more_button = driver.find_element_by_xpath('//*[@id="root"]/div/div[3]/div/div/main/div[1]/button')
    #driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    driver.execute_script("arguments[0].scrollIntoView();", load_more_button)
    sleep(3)
    driver.execute_script("scrollBy(0,-300);")
    sleep(3)
    load_more_button.click()
    print("Clicked Load More!")

page_html = driver.page_source
driver.quit()
page_soup = soup(page_html, "html.parser")

#containersA = page_soup.findAll("a",href=True)
containersA = page_soup.findAll("a", href=re.compile("id="))

title_list = []
price_list = []
link_list = []
user_list = []

for container in containersA:
    if "/p/" in str(container):
        if "title=" in str(container).split("<p class=")[1]:
            title = str(container).split("<p class=")[1].split('title="')[1].split('"/><')[0]
            title_list.append(title)
            link = "https://www.carousell.sg" + str(container['href']).split("?t-id=")[0]
            link_list.append(link)

        else:
            title = str(container).split("<p class=")[1].split(">")[1].replace("</p","")
            if title == "Protection" or title == "Spotlight":
                title= str(container).split("<p class=")[2].split(">")[1].replace("</p","")
            title_list.append(title)
            link = "https://www.carousell.sg" + str(container['href']).split("?t-id=")[0]
            link_list.append(link)

        price = str(container).split("<p class=")[2].split(">")[1].replace("</p","").split("<span")[0]
        if "S$" not in price:
            price = str(container).split("<p class=")[3].split(">")[1].replace("</p","").split("<span")[0]
        
        price_list.append(price)

    elif "?t-id=" in str(container):
        user = str(container).split("<p class=")[1].split(">")[1].replace("</p","")
        user_list.append(user)

finalstr = ""

f_r = open(finaltxt, "r", encoding="utf-8")
prev_url = f_r.read()
f_r.close()

for user, title, price, link in zip(user_list, title_list, price_list, link_list):
    if link not in prev_url:
        blacklink(link)
        if filterUser(user, filter_users):
            if filterLink(link, filter_links):
                desc = getDesc(link)
                if filterDesc(desc, filter_descs):
                    if reqDesc(desc, req_descs):
                        new_desc = desc.replace("coe","COE").replace("Coe","COE")
                        coe = between(new_desc,"COE","20")
                        finalstr = (user + "|" + title + "|" + price + "\n" + coe + "\n" + link )
                        print("Sending " + finalstr)
                        bot = telegram.Bot(token="1214910019:AAGJqb0DJpp22Q14dV-hgR9E9wLnr76JW60")
                        bot.sendMessage(chat_id=-498149684,text=finalstr,disable_web_page_preview=False)

print('ended')

# input time in seconds 
t = 10

# function call 
countdown(int(t))