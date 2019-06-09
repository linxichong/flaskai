from selenium import webdriver
from flaskr.controlers.spiderapi.seleniumspider import SeleniumSpider

if __name__ == "__main__":
    spider = SeleniumSpider(None)
    spider.find('p30')