from flask import Flask,render_template,request,jsonify,Response,make_response
import json

#For scrapping
import requests
from bs4 import BeautifulSoup as bs
import re
import csv
import time
import threading
import os
import shutil


# https://realpython.com/flask-by-example-part-1-project-setup/
# For auto restast of sever while saving a file
# FLASK_ENV=deployement flask run
# FLASK_ENV=development flask run

app = Flask(__name__)

site_url = "https://www.yellowpages.com"
rating_dict = {"zero":'0',"one":'1',"two":'2',"three":'3',"four":'4',"five":'5',"one half":'1.5',"two half":'2.5',"three half":'3.5',"four half":'4.5'}

links = []
busines_names = []
address = []
phone = []
website_link = [] 
email = []
extra_phone = []
rating = []



def parse_list_page(scrape_url,page_no):
    url = scrape_url + f"{page_no}"
    print('Scraping Urls........',url,flush=True)
    res = requests.get(url)
    if res.status_code == 200:    
        soup = bs(res.content,features="html.parser")
        link_soup_list = soup.findAll(class_ = 'business-name')
        for link in link_soup_list:
            links.append(site_url + link.get("href"))
    else:
        print("somthing went wrong")


# For downloading the html pages
def download_url(url):
    resp = requests.get(url)
    title = "".join(x for x in url if x.isalpha()) + ".html"
    with open(f"pages/{title}", "wb") as fh:
        fh.write(resp.content)
        fh.close()

def parse_inner_page(link):
    # print("Inside Parse_inner_page Function!!!!!!!!!!")
    title = link
    path = os.path.join("pages",title)
    with open(path,"rb") as f:
        data = f.read()
        f.close

    # Making soup object for each download pages    
    soup = bs(data,features="html.parser")

    var =  soup.find(class_ = "sales-info")
    try:                
        busines_names.append(var.find("h1").text)
    except:
        busines_names.append("none")

    var = soup.find(class_ = "result-rating")
    try:
        rating.append(rating_dict[(" ").join(var.get("class")[1:])])
    except:
        rating.append("none")

    var = soup.find(class_='address')
    try:
        address.append(var.text)
    except:
        address.append("none")
    # Formate phone Number
    # pat = re.compile("\d+")
    # p = ("").join (pat.findall(s))

    var = soup.find(class_='phone')
    try:
        p = var.text
        phone.append(p)
    except:
        phone.append("none")

    var = soup.find(class_ = 'website-link')
    try:
        website_link.append(var.get("href"))
    except:
        website_link.append("none")

    var = soup.find(class_="email-business")
    try:
        email.append(var.get("href")[7:])
    except:
        email.append("none")

    var = soup.findAll(class_ = "extra-phones")
    try:
        ex_pn = ""
        s = var[-1].text
        pat = re.compile("\d+")
        pl=pat.findall(s)
        for i in range(0,len(pl) ,3):
            ex_pn = ex_pn+("").join(pl[i:i+3]) + ","
        extra_phone.append(ex_pn)
    except:
        extra_phone.append("none")

        
@app.route('/')
def home():
    return render_template("home.html")

#Scrapes the links
@app.route("/scrape",methods=['POST'])
def scrape():
    global links
    # values from the json body
    data = request.get_json()
    scrape_url = data["scrape_url"]
    start_page_no = int(data["start_page_no"])
    end_page_no = int(data["end_page_no"])
    location   =   data["location"]
    keyword   =    data["keyword"]

    if not os.path.exists("pages"):
        os.mkdir("pages")

    if not "&page" in scrape_url:
        scrape_url = scrape_url + "&page="

    list_page_threads = []
    total_page = end_page_no - start_page_no + 1
    page_no = start_page_no

    # This fasten the process using threading
    for _ in range(total_page):
        t = threading.Thread(target=parse_list_page,args = [scrape_url,page_no])
        t.start()
        list_page_threads.append(t)
        page_no+=1

    for thread in list_page_threads:
        thread.join()

    # Removing redundend links 
    links = list(set(links))

    if len(links) > 0 and len(links) < 1500:
        # Start downloading the html of given links into page folder
        download_threads = []
        for link in links:
            t = threading.Thread(target=download_url,args=[link])
            t.start()
            download_threads.append(t)
            
        for thread in download_threads:
            thread.join()
    return jsonify({"total_links":len(links)})

@app.route("/result",methods=["POST"])
def result():
    # Fetching Data
    
    data = request.get_json()
    idx = int(data['idx'])
    location = data['location']
    keyword = data['keyword']
    title = os.listdir("pages")
    # print('idx',idx,'Len Title>>>>>>>>>>>>>>>>>>>>>>>>>>',len(title))
    try:
        # print('inside try block','idx',idx,'Len Title>>>>>>>>>>>>>>>>>>>>>>>>>>',len(title))
        parse_inner_page(title[idx])
        # time.sleep(2)
        return jsonify({0:idx,1:busines_names[idx],2:address[idx],3:rating[idx],4:phone[idx],5:website_link[idx],6:email[idx],7:extra_phone[idx],8:keyword,9:location})
    except Exception as e:
        print('EXPECTION >>>>>>>>>>',e,flush=True)
        try:
            shutil.rmtree('pages')
            #os.mkdir('pages')
            print("Removed pages",flush=True)
        except Exception as e:
            print("ERROR!!! while deleting pages", e ,flush=True)
        return jsonify({"stop":True})
        

# Download CSV     
@app.route("/tocsv")
def tocsv():
    table = json.loads(request.cookies.get('mycookie'))
    csv = ""
    for t in table:
        row = ("**").join(t)
        row = row.replace(","," ")
        row = row.replace("**",",")
        row += "\n"
        csv+=row
    response = make_response(csv)
    cd = 'attachment; filename=mycsv.csv'
    response.headers['Content-Disposition'] = cd 
    response.mimetype='text/csv'
    return response
