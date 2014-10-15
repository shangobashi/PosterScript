from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support.select import Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import re
import winsound, sys
import time
import easygui as eg
from selenium.webdriver.common.action_chains import ActionChains
from selenium.selenium import *

##Initialitialing global variables 
program_title = 'MondoPye'
base_url = "http://www.mondotees.com/"
bogus_url_shirt= '/Blue-Sunshine-Original-Motion-Picture-Soundtrack_p_1356.html'
bogus_url_poster= '/Blue-Sunshine-Original-Motion-Picture-Soundtrack_p_1356.html'
poster_info = open('poster_name.txt', 'r').read()
list_info= []
list_accounts = []
with open('account_info.txt', 'r') as f:
    data = f.readlines()
    for line in data:
        words = line.split()
        list_info.append(words)
        list_accounts.append(words[0])

#only_reg = re.compile("^((?!variant).)*$", re.IGNORECASE)
#variant  = re.compile(".*variant.*", re.IGNORECASE)
only_reg = re.compile("^((?!Version-B).)*$", re.IGNORECASE)
variant  = re.compile(".*Version-B.*", re.IGNORECASE)
fp = webdriver.FirefoxProfile('MOW')
driver = webdriver.Firefox(fp)
driver.implicitly_wait(5)

def main():
    email = drop_info_choices()
    gift = ''
    gift2 = ''
    for sublist in list_info:
        if sublist[0] == email:
            passw = sublist[1]
            name = sublist[2]
            if len(sublist) == 4:
                gift = sublist[3]
    if poster_info == '':
        poster_name = poster_name_box()
    else:
        poster_name = poster_info
    edition_choice = edition_choice_box()
    payment_method = 'Gift Card'
    if gift == '':
        gift, gift2 = gift_box()
    browser_name = "Firefox"
    print "Account is           ",email
    print "Poster is            ",poster_name, edition_choice
    print "Payment method is    ",payment_method
    print "Gift Card code is    ",gift ,'   ', gift2
    
    logging_in(email, passw)
    gift_add(gift, gift2)
    create_newtab()
    switch_tab(2)
    bogus_checkout_shirt()
    switch_tab(1)
    clear_cart()
    refresh_process(poster_name)
    list_urls = get_href(poster_name)
    if edition_choice =='Regular':
        poster_link = get_poster_link_regular(list_urls, poster_name)
    if edition_choice=='Variant':
        poster_link = get_poster_link_variant(list_urls, poster_name)
    driver.get(poster_link)
    play_sound()
    time.sleep(1)
    print driver.title
    switch_tab(2)
    print driver.title
    driver.execute_script("check_and_add()")
    time.sleep(2)
    print driver.title
    print 'Clicking Final Checkout' ##Final checkout button.
    driver.find_element_by_name("B1").click()
    print "Congrats! You just succesfully bought a poster."

    
def drop_info_choices():
    msg         = "Choose account"
    account = eg.choicebox(msg,program_title, list_accounts)
    return account
def poster_name_box():
    msg    = "Enter poster name"
    fieldValues = eg.enterbox(msg, program_title)
    return fieldValues


def edition_choice_box():
    msg='Choose between variant or regular(choose regular if there is only one kind of edition)'
    choices_edition=['Regular','Variant']
    edition_choice=eg.buttonbox(msg,program_title,choices_edition)
    return edition_choice

def payment_choice_box():
    msg= 'Choose your payment method'
    choices=['Gift Card', 'Credit Card']
    fieldValues = eg.buttonbox(msg,program_title,choices)
    return fieldValues


def gift_box():
    msg='Enter your Gift Card number'
    fieldNames = ['Gift Card 1', 'Gift Card 2(optional)']
    fieldValues = eg.multenterbox(msg,program_title, fieldNames)
    gift= fieldValues[0]
    gift2= fieldValues[1]
    return fieldValues[0], fieldValues[1]

def cc_box():
    msg='Enter your credit card information'
    fieldNames = ['CC Number', 'CVV2']
    fieldValues = eg.multenterbox(msg,program_title, fieldNames)
    cc_num=fieldValues[0]
    cvv2=fieldValues[1]
    msg='Expiration Month'
    choices_month=['01','02','03','04','05','06','07','08','09','10','11','12']
    exp_month = eg.choicebox(msg,program_title,choices_month)
    msg='Expiration Year'
    choices_year=['2014','2015','2016','2017','2018','2019','2020','2021','2022']
    exp_year=eg.choicebox(msg,program_title,choices_year)
    msg='Card Type'
    choices_type=['Mastercard','Visa','American Express','Discover']
    cc_type=eg.choicebox(msg,program_title,choices_type)
    return cc_num, cvv2, exp_month,exp_year,cc_type

def play_sound(): 
    winsound.PlaySound("SystemExclamation", winsound.SND_ASYNC)
    
def check_exists_by_partial_link_text(link_text):
    driver.implicitly_wait(0.5)
    try:
        driver.find_element_by_partial_link_text(link_text)
    except NoSuchElementException:
        return False
    driver.implicitly_wait(30)
    return True

def logging_in(email, passw):
    driver.get("https://www.mondotees.com/myaccount.asp")
    driver.find_element_by_name("email").send_keys(email)
    driver.find_element_by_id("Password1").send_keys(passw)
    driver.find_element_by_id("Submit1").click()

def gift_add(gift,gift2):
    driver.get("http://www.mondotees.com/Gift-Card-50_p_193.html")
    driver.find_element_by_name("Add").click()
    driver.find_element_by_name("coupon_code").send_keys(gift)
    driver.find_element_by_id("Submit1").click()
    if gift2:
        driver.find_element_by_name("coupon_code").send_keys(gift2)
        driver.find_element_by_id("Submit1").click()
    driver.find_element_by_name("qty0").clear()
    driver.find_element_by_name("qty0").send_keys("0")
    driver.find_element_by_id("Submit2").click()

def create_newtab():
    driver.get("https://www.mondotees.com/myaccount.asp")
    elem = driver.find_element_by_partial_link_text("Shop")
    elem.send_keys(Keys.CONTROL + Keys.RETURN + "2")
def bogus_checkout_shirt():
    driver.get(base_url + bogus_url_shirt)
    driver.find_element_by_name("Add").click()
    driver.find_element_by_id("Button7").click()
    driver.find_element_by_name("Add22").click()
    #driver.find_element_by_xpath("(//input[@name='shipping'])[2]").click()
    time.sleep(1)
    driver.find_element_by_name("Add222").click()
    time.sleep(1)

def bogus_checkout_poster():
    driver.get(base_url + bogus_url_poster)
    driver.execute_script("check_and_add()")
    driver.find_element_by_id("Button7").click()
    driver.find_element_by_name("Add22").click()    

def enter_cc_info(cc_num, cvv2, exp_month, exp_year, cc_type):
    print 'Entering Credit Card Information'
    driver.find_element_by_name("ff11_ocardno").send_keys(cc_num)
    select = Select(driver.find_element_by_name('ff11_ocardexpiresmonth'))
    select.select_by_value(exp_month)
    select = Select(driver.find_element_by_name('ff11_ocardexpiresyear'))
    select.select_by_value(exp_year)
    select = Select(driver.find_element_by_name('ff11_ocardtype'))
    select.select_by_value(cc_type)
    driver.find_element_by_name("ff11_ocardcvv2").send_keys(cvv2)

def switch_tab(tab_number):
    if tab_number == 1:
        x = Keys.NUMPAD1
    if tab_number == 2:
        x = Keys.NUMPAD2
    button = driver.find_element_by_tag_name('html')
    button.send_keys(Keys.CONTROL + x)

def clear_cart():
    driver.get('http://www.mondotees.com/view_cart.asp')
    driver.find_element_by_name("qty0").clear()
    driver.find_element_by_name("qty0").send_keys("0")
    driver.find_element_by_id("Submit2").click()

def refresh_process(poster_name):
    driver.get(base_url + "/view_category.asp?cat=19")    
    drop = check_exists_by_partial_link_text(poster_name)
    refresh_count = 0
    while drop is False :
        driver.get(base_url + "/view_category.asp?cat=19") 
        drop = check_exists_by_partial_link_text(poster_name)
        refresh_count = refresh_count + 1
        print "Refresh #" , str(refresh_count) + '\r',

def get_href(poster_name):
    list_positions = driver.find_elements_by_partial_link_text(poster_name)
    list_urls=[]
    for i in list_positions:
        list_urls.append(i.get_attribute('href'))
    return list_urls

def get_poster_link_regular(list_urls, poster_name):
    print 'Found ',len(list_urls),'link matching the postername'
    if len(list_urls) == 1:
        if  not variant.search(list_urls[0]):
            print "Link points to Regular"
            poster_link=list_urls[0]
            print poster_link
        else:
           print "Link points to Variant, while loop initiated"
           while len(list_urls) != 2:
              list_urls=[]
              time.sleep(0.5)
              driver.get(base_url + "/POSTERS_c_12.html")
              list_positions = driver.find_elements_by_partial_link_text(poster_name)
              for i in list_positions:
                 list_urls.append(i.get_attribute('href'))

    if len(list_urls) == 2:
        print "Two links found"
        for i in list_urls:
            print i
            if only_reg.search(i):
               poster_link=i
               print poster_link
    if len(list_urls) > 2 :
        print " More than 2 links found, going to the first one"
        poster_link = list_urls[0]
    return poster_link

def get_poster_link_variant(list_urls,poster_name):
    print 'Found ',len(list_urls),'link matching the postername'
    if len(list_urls) == 1:
        if variant.search(list_urls[0]):
            print "Link points to Variant"
            poster_link=list_urls[0]
            print poster_link
        else:
           print "Link points to Regular, while loop initiated."
           while len(list_urls) != 2:
              list_urls=[]
              time.sleep(0.5)
              driver.get(base_url + "/POSTERS_c_12.html")
              list_positions = driver.find_elements_by_partial_link_text(poster_name)
              for i in list_positions:
                 list_urls.append(i.get_attribute('href'))
              
    if len(list_urls) == 2:
        print "Two links found"
        for i in list_urls:
            print i
            if variant.search(i):
               poster_link=i
               print poster_link
    if len(list_urls) > 2 :
        print " More than 2 links found, going to the first one"
        poster_link = list_urls[0]
    return poster_link


if __name__ == '__main__':
    main()

