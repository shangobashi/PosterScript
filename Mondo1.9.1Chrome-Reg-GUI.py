from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException
import re
import winsound, sys
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support.select import Select
from selenium.webdriver.support import expected_conditions as EC
import time
import easygui as eg

## This is only for the regular, it will not buy a variant !

msg         = "Enter your Mondo drop information."
title       = "Mondo Bot"
fieldNames  = ["Email","Password","Poster","Gift Card 1","Gift Card 2"]
fieldValues = []  # we start with blanks for the values
fieldValues = eg.multenterbox(msg,title, fieldNames)
while 1:  # do forever, until we find acceptable values and break out
    if fieldValues == None: 
        break
    errmsg = ""
    
    # look for errors in the returned values
    for i in range(len(fieldNames)-1):
        if fieldValues[i].strip() == "":
           errmsg = errmsg + ('"%s" is a required field.\n\n' % fieldNames[i])
        
    if errmsg == "": 
        break # no problems found
    else:
        # show the box again, with the errmsg as the message    
        fieldValues = eg.multenterbox(errmsg, title, fieldNames, fieldValues)
print fieldValues

driver = webdriver.Chrome()
driver.implicitly_wait(30)
base_url = "http://www.mondotees.com/"
verificationErrors = []
accept_next_alert = True

email=fieldValues[0]
passw=fieldValues[1]
printname=fieldValues[2]
gift=fieldValues[3]
gift2=fieldValues[4]


only_reg=re.compile("^((?!variant).)*$", re.IGNORECASE)
variant = re.compile(".*variant.*", re.IGNORECASE)

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

def check_exists_by_link_text(link_text):
    driver.implicitly_wait(0.5)
    try:
        driver.find_element_by_link_text(link_text)
    except NoSuchElementException:
        return False
    driver.implicitly_wait(30)
    return True

driver.get("https://www.mondotees.com/myaccount.asp")
driver.find_element_by_name("email").send_keys(email)
driver.find_element_by_id("Password1").send_keys(passw)
driver.find_element_by_id("Submit1").click()
driver.get("http://www.mondotees.com/MISC_c_18.html")
driver.find_element_by_partial_link_text("$50").click()
driver.find_element_by_name("Add").click()
driver.find_element_by_name("coupon_code").send_keys(gift)
driver.find_element_by_id("Submit1").click()
##driver.find_element_by_name("coupon_code").send_keys(gift2)
##driver.find_element_by_id("Submit1").click()
##driver.find_element_by_name("coupon_code").send_keys(gift3)
##driver.find_element_by_id("Submit1").click()
driver.find_element_by_name("qty0").clear()
driver.find_element_by_name("qty0").send_keys("0")
driver.find_element_by_id("Submit2").click()


driver.get(base_url + "/POSTERS_c_12.html")    
drop = check_exists_by_partial_link_text(printname)
print drop
refresh_count = 0
while not drop :
    driver.get(base_url + "/POSTERS_c_12.html") 
    drop = check_exists_by_partial_link_text(printname)
    refresh_count = refresh_count + 1
    print drop , refresh_count



list_links = driver.find_elements_by_partial_link_text(printname)
list_posters=[]
for i in list_links:
    list_posters.append(i.get_attribute('href'))

print list_posters
print len(list_posters)
if len(list_posters) == 1:
    print variant.search(list_posters[0])
    if  not variant.search(list_posters[0]):
        print "One link found, no variant found"
        poster_link=list_posters[0]
        print poster_link
    else:
       print "One link found, variant found, while loop initiated"
       list_posters=[]
       while len(list_posters) != 2:
          driver.get(base_url + "/POSTERS_c_12.html")
          list_links = driver.find_elements_by_partial_link_text(printname)
          for i in list_links:
             list_posters.append(i.get_attribute('href'))
          for i in list_posters:
             if only_reg.search(i):
                poster_link=i
                print poster_link
if len(list_posters) == 2:
    print "Two links found"
    for i in list_posters:
        print i
        if only_reg.search(i):
           poster_link=i
           print poster_link
            
print 'Now going to the poster_link'
driver.get(poster_link)
play_sound()
if EC.element_to_be_clickable(driver.find_element_by_name("Add")):
    print "Add To Cart button is clickable"
    print "Now clicking Add to Cart button"
    driver.find_element_by_name("Add").click()
    
else :
    print "Add to Cart button is not clickable"
    x = "False"
    while x== "False":
       if EC.element_to_be_clickable(driver.find_element_by_name("Add")):
          x="True"
       print x
    print "Now clicking Add to Cart button"
    driver.find_element_by_name("Add").click()

print "Page Title is " + driver.title
cart_regexp=re.compile(".*Cart.*")
if cart_regexp.search(driver.title):
    print "Page title contains Cart"
    print "Now clicking Proceed to Checkout"
    driver.find_element_by_id("Button7").click()
else:
    print "Page title doest not contain Cart"
    x = 1
    while not cart_regexp.search(page_title):
        tries = x
        print "Now clicking Add to Cart again, try #"+tries
        x=x+1
        driver.find_element_by_name("Add").click()
    print "Page title now contains Cart"
    print "Now clicking Proceed to Checkout"
    driver.find_element_by_id("Button7").click()
        
      
print "Page Title is " + driver.title
checkout_regexp=re.compile(".*Checkout.*")
if checkout_regexp.search(driver.title):
    print 'Page Title contains Checkout'
    print "Now cliking Proceed to Shipping Calculation"
    driver.find_element_by_name("Add22").click()
else:
    print 'Page Title does not contain Checkout'
    play_sound()
    print "Now cliking Proceed to Shipping Calculation"
    driver.find_element_by_name("Add22").click()
    
print 'Now clicking Final Checkout'
driver.find_element_by_name("B1").click()

print "Congrats! You just succesfully bought a poster."
