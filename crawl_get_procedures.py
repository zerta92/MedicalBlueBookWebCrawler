import re
from bs4 import BeautifulSoup as bs
import requests
import os, csv

categories = []
procedures = []
procedures_urls = []
results = {}


class Crawl:

    def __init__(self, raw_html):
        self.raw_html = raw_html

               
    def get_categories(self):
       soup = bs(self.raw_html)
       tabs = soup.find_all("div", {"class": "fair-price-dropdown"})
       counter = 0
       for tab in tabs[1:2]: 
           counter = counter + 1
           print("Tab Number: " + str(counter) + " started")
           urls = tab.find_all("a")
           counter2 = 0
           for i in range(len(urls)): #len(urls) #iterate trough categories in tab
               print("-category:"+ str(counter2))
               a_tag = str(urls[i])
               number = str(re.findall('\\b\\d+\\b', a_tag))
               left_bracket_index = re.search("\['", number)
               link_noleftBracket = number[:left_bracket_index.start()] + number[left_bracket_index.end():]
               right_bracket_index = re.search("']", str(link_noleftBracket))
               link_noBrackets = link_noleftBracket[:right_bracket_index.start()] + link_noleftBracket[right_bracket_index.end():]
               full_link = Prefix+link_noBrackets
               categories.append(full_link)
                   #self.get_procedures(full_link)
               self.get_procedures_url(full_link)
               counter2 = counter2+1

    def get_procedures(self,category_url):
       soup2 = bs(requests.get(category_url).text)
       links = soup2.find_all("div", {"class": "service-box"})
       for link in links:
           urls = link.find_all("a")
           for i in range(len(urls)):
               procedures.append(urls[i].get_text())

    def get_procedures_url(self,categories_url):
       soup3 =  bs(requests.get(categories_url).text) #"https://healthcarebluebook.com/page_SearchResults.aspx?CatID=209"
       prefix = "https://healthcarebluebook.com/page_ProcedureDetails.aspx"
       links = soup3.find_all("div", {"class": "service-box"})
       #for link in links: commented for doing one tab at a time
       urls = links[0].find_all("a")
       counter3 = 0
       for i in range(len(urls)):
            print("--Subcategory link: " + str(counter3))
            m = re.search(r'\"(.+?)\"', str(urls[i])).group(0) #get everything between quotes
             #remove prefix
            prefix_index = re.search("page_Results.aspx?", m)
            link_noprefix = m[:prefix_index.start()] + m[prefix_index.end():]
             #remove quotes
            left_quote_index = re.search("\"", link_noprefix)
            link_noleftquote = link_noprefix[:left_quote_index.start()] + link_noprefix[left_quote_index.end():]
            right_quote_index = re.search("\"", str(link_noleftquote))
            link_noquotes = link_noleftquote[:right_quote_index.start()] + link_noleftquote[right_quote_index.end():]#url to procedure cost
            full_link = prefix + link_noquotes
            procedures_urls.append(full_link)
            self.get_procedure_cost(full_link)
            counter3 = counter3+1
             #print(prefix+link_noquotes)

    
    def get_procedure_name(self,procedure_url):
        soup = bs(requests.get(procedure_url).text)
        divTag = soup.find_all("div", {"class": "fair-price-results-summary"}) #result list for div class where name is
        for tag in divTag:
            h3tags = tag.find_all("h3")
            procedure = h3tags[0].get_text()
        return procedure

            
    def get_procedure_cost(self,procedure_url):
        procedure = self.get_procedure_name(procedure_url)
        soup = bs(requests.get(procedure_url).text)
        cost = 0#if no cost found assign 0 to avoid error
        try:
            cost = soup.find_all("div", class_="total-line")[0].get_text()#result list for cost class
        except:
            divTag = soup.find_all("div", {"class": "fee-detail-item fee"})
            for tag in divTag:
                divtags = tag.find_all("div", {"class": "value"})
                cost = divtags[0].get_text()
        results[procedure] = cost
        #return cost


Prefix = "https://healthcarebluebook.com/page_SearchResults.aspx?CatID="
r = requests.get(Prefix)
Spyder = Crawl(r.text)
#Spyder.get_procedures_url()
Spyder.get_categories()#populate results array with vategory links
#Spyder.get_procedures()
#print(categories)
#print(procedures)
#print(procedures_urls)

with open('Medication.csv', 'w') as csvfile:
    fieldnames = ['Procedure', 'Cost']
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

    writer.writeheader()
    #sorted_results = sorted(results.keys())
    for keys,values in results.items():
        print(keys, ':', values)
        writer.writerow({'Procedure': keys, 'Cost': values})




