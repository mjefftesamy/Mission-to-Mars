#Import Splinter, BeautifulSoup, and Pandas
from splinter import Browser
from bs4 import BeautifulSoup as soup
import pandas as pd
import datetime as dt
import time

def scrape_all():
    #Initiate headless driver for deployment
    browser = Browser("chrome", executable_path = "chromedriver", headless = True)

    news_title, news_paragraph = mars_news(browser)

    #Run all scraping functions and store results in dictionary
    data = {
        "news_title": news_title,
        "news_paragraph": news_paragraph,
        "featured_image": featured_image(browser),
        "facts": mars_facts(),
        "last_modified": dt.datetime.now(),
        "hemispheres": hemisphere_image_urls(browser)
    }

    #Stop webdriver and return data
    browser.quit()
    return data

    
def mars_news(browser):

    #Scrape Mars News
    #Visit the mars nasa news site
    url = 'https://mars.nasa.gov/news/'
    browser.visit(url)

    #Optional delay for loading the page
    browser.is_element_present_by_css("ul.item_list li.slide", wait_time = 1)

    #Convert the browser html to a soup object and then quit the browser
    html = browser.html
    news_soup = soup(html, 'html.parser')

    #Add try/except for error handling
    try:
        slide_elem = news_soup.select_one("ul.item_list li.slide")

        #Use the parent element to find the first 'a' tag and save it as 'news_title'
        news_title = slide_elem.find("div", class_= "content_title").get_text()
    
        #Use the parent element to find the paragraph text
        news_p = slide_elem.find("div", class_ = "article_teaser_body").get_text()
    
    except AttributeError:
        return None, None

    return news_title, news_p


# ### Featured Images

def featured_image(browser):

    #10.3.4
    # Visit Archived JPL URL
    PREFIX = "https://web.archive.org/web/20181114023740"
    url = f'{PREFIX}/https://www.jpl.nasa.gov/spaceimages/?search=&category=Mars'
    browser.visit(url)
    #WAIT FOR THE PAGE TO COMPLETELY LOAD!!!🥃
    article = browser.find_by_tag('article').first['style']
    article_background = article.split("_/")[1].replace('");',"")
    print(f'{PREFIX}_if/{article_background}')

    return (f'{PREFIX}_if/{article_background}')

# ### Mars Facts

def mars_facts():

    try:
        #Use 'read_html' to scrape the facts table into a dataframe
        df = pd.read_html("http://space-facts.com/mars/")[0]
    
    except BaseException:
        return None

    #Assign columns and set index of dataframe
    df.columns = ['Description', 'Mars']
    df.set_index('Description', inplace = True)
    
    #Convert dataframe into HTML format, add bootstrap
    return df.to_html(classes = "table table-striped")


def hemisphere_image_urls(browser):
    # 1. Use browser to visit the URL 
    url = 'https://astrogeology.usgs.gov/search/results?q=hemisphere+enhanced&k1=target&v1=Mars'
    browser.visit(url)
    time.sleep(1)

    # 2. Create a list to hold the images and titles.
    # 3. Write code to retrieve the image urls and titles for each hemisphere.

    html = browser.html
    soups = soup(html, "lxml")

    img_divs = soups.find_all("div", class_ = "description")

    hemisphere_image_urls = []
    base_url = "https://astrogeology.usgs.gov"
    for img_div in img_divs:
        img_info = {}
        img_title = img_div.find("h3").text
        img_info["title"] = img_title
        partial_img_url = img_div.find("a", class_ = "itemLink product-item")["href"]
        full_img_url = base_url + partial_img_url
        browser.visit(full_img_url)
        full_img_url = browser.html
        soups = soup(full_img_url, "lxml")
        img_url = soups.find("div", class_ = "downloads").li.a["href"]    
        img_info["img_url"]=img_url
        hemisphere_image_urls.append(img_info)

    return hemisphere_image_urls


if __name__ == '__main__':

    #If running as script, print scraped dated
    print(scrape_all())