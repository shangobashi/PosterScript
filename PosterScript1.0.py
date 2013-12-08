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

##Opens a box to let the user decide on a browser
msg         = "Choose between the Firefox or Chrome as your browser of choice. Choose Firefox if you do not have chrome_driver.exe in your PATH"
title       = "PosterScript"
choices     = ['Chrome', 'Firefox']
fieldValues = eg.buttonbox(msg,title,choices)
browser_name = fieldValues
print 'You chose', browser_name, 'as your browser of choice.'

##Initialize the browser driver based on the user's choice
if browser_name == 'Chrome':
    driver = webdriver.Chrome()
if browser_name == 'Firefox':
    driver = webdriver.Firefox()
driver.implicitly_wait(30)
base_url = "http://www.mondotees.com/"
verificationErrors = []
accept_next_alert = True

##Opens a box for the user to enter their Mondo account info and the poster name
msg         = "Enter your Mondo account information."
##title       = "PosterScritp"
fieldNames  = ["Email","Password","Poster",]
fieldValues = []  # we start with blanks for the values
fieldValues = eg.multenterbox(msg,title, fieldNames)
while 1:  # do forever, until we find acceptable values and break out
    if fieldValues == None: 
        break
    errmsg = ""
    
    # look for errors in the returned values
    for i in range(len(fieldNames)):
        if fieldValues[i].strip() == "":
           errmsg = errmsg + ('"%s" is a required field.\n\n' % fieldNames[i])
        
    if errmsg == "": 
        break # no problems found
    else:
        # show the box again, with the errmsg as the message    
        fieldValues = eg.multenterbox(errmsg, title, fieldNames, fieldValues)
print fieldValues


##Initialize the account info based on the user's input
email=fieldValues[0]
passw=fieldValues[1]
printname=fieldValues[2]

##Prompt the user for their choice for the poster's edition
msg='Choose between variant or regular(choose regular if there is only one kind of edition)'
choices_edition=['Regular','Variant']
edition_choice=eg.buttonbox(msg,title,choices_edition)

##Opens a box to let the user decide on a payment method
msg= 'Choose your payment method'
choices=['Gift Card', 'Credit Card']
fieldValues = eg.buttonbox(msg,title,choices)
payment_method = fieldValues

##Opens a box based on the user's choice of payment and prompt them for their payment info
if payment_method =='Gift Card':
    msg='Enter your Gift Card number'
    fieldNames = ['Gift Card 1', 'Gift Card 2(optional)']
    fieldValues = eg.multenterbox(msg,title, fieldNames)
    gift= fieldValues[0]
    gift2= fieldValues[1]
if payment_method == 'Credit Card':
    msg='Enter your credit card information'
    fieldNames = ['CC Number', 'CVV2']
    fieldValues = eg.multenterbox(msg,title, fieldNames)
    cc_num=fieldValues[0]
    cvv2=fieldValues[1]
    msg='Expiration Month'
    choices_month=['01','02','03','04','05','06','07','08','09','10','11','12']
    exp_month = eg.choicebox(msg,title,choices_month)
    msg='Expiration Year'
    choices_year=['2014','2015','2016','2017','2018','2019','2020','2021','2022']
    exp_year=eg.choicebox(msg,title,choices_year)
    msg='Card Type'
    choices_type=['Mastercard','Visa','American Express','Discover']
    cc_type=eg.choicebox(msg,title,choices_type)
    

##Initializing the regexp used for finding the correct edition of the poster
only_reg=re.compile("^((?!variant).)*$", re.IGNORECASE)
variant = re.compile(".*variant.*", re.IGNORECASE)

##Defining the procedures used for finding the poster drop
def play_sound(): ##sound played when browser lands on the poster page
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

##Logging in to the user account
driver.get("https://www.mondotees.com/myaccount.asp")
driver.find_element_by_name("email").send_keys(email)
driver.find_element_by_id("Password1").send_keys(passw)
driver.find_element_by_id("Submit1").click()

##if the user chose Gift Card as payment method, the gift card needs to be entered in the cart before the chekout process
##To do so, one needs to add a random item to the cart first, enter the gift card, and take the random item off the cart afterwards
if payment_method =='Gift Card':
    driver.get("http://www.mondotees.com/MISC_c_18.html")
    driver.find_element_by_partial_link_text("$50").click()
    driver.find_element_by_name("Add").click()
    driver.find_element_by_name("coupon_code").send_keys(gift)
    driver.find_element_by_id("Submit1").click()
    if gift2:
        driver.find_element_by_name("coupon_code").send_keys(gift2)
        driver.find_element_by_id("Submit1").click()
    driver.find_element_by_name("qty0").clear()
    driver.find_element_by_name("qty0").send_keys("0")
    driver.find_element_by_id("Submit2").click()

##Refreshing process starts. browser checks the link text of all links on the page after each refresh and compares it to the printname entered by the user.
##For each unsuccesful refresh, False + the number of refreshes is printed. Once the printname is found in a link, the refreshing process is stopped and True is printed.
driver.get(base_url + "/POSTERS_c_12.html")    
drop = check_exists_by_partial_link_text(printname)
print drop
refresh_count = 0
while not drop :
    driver.get(base_url + "/POSTERS_c_12.html") 
    drop = check_exists_by_partial_link_text(printname)
    refresh_count = refresh_count + 1
    print drop , refresh_count


##Once the browser finds at least one link containing the printname, we store the link's href in list_posters. The Href contains the naem of the print and its edition, regular or variant.
##The href is needed to determine if the link directs to the Regular editon or the Variant edition.
list_links = driver.find_elements_by_partial_link_text(printname)
list_posters=[]
for i in list_links:
    list_posters.append(i.get_attribute('href'))

##We first choose the method to apply based on the user's choice. Regular and Variant use different regexp to determine the edition of the poster.
##If the Variant and the Regular editon both dropped at the same time, we have 2 links in our list.
##If only one edition dropped, and the other edition is coming seconds after, we have to determine if the edition that dropped first is the edition the user wanted. If so, we simply use that link to start the checkout process.
##If the edition that dropped first is the wrong edition, we have to keep refreshing untill the list includes both editions.
if edition_choice =='Regular':
    
    print 'Found ',len(list_posters),'link matching the postername'
    if len(list_posters) == 1:
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

if edition_choice=='Variant':
    print list_posters
    print len(list_posters)
    if len(list_posters) == 1:
        print variant.search(list_posters[0])
        if variant.search(list_posters[0]):
            print "One link found, variant found"
            poster_link=list_posters[0]
            print poster_link
        else:
           print "One link found, no variant found, while loop initiated"
           print list_posters
           while  not len(list_posters) == 2:
              list_posters=[]
              time.sleep(0.5)
              driver.get(base_url + "/POSTERS_c_12.html")
              list_links = driver.find_elements_by_partial_link_text(printname)
              for i in list_links:
                 list_posters.append(i.get_attribute('href'))
              print list_posters

    if len(list_posters) == 2:
        print "Two links found"
        for i in list_posters:
            print i
            if variant.search(i):
               poster_link=i
               print poster_link
            

##We now have the correct link directing to the product page the user requested
print 'Going to the poster_link'
driver.get(poster_link)
play_sound()
if EC.element_to_be_clickable(driver.find_element_by_name("Add")): ##We have to verify that the Add to Cart button is clickable.
    print "Add To Cart button is clickable"
    print "Clicking Add to Cart button"
    driver.find_element_by_name("Add").click()
    
else : ## If it isn't clickable, we have to wait till it is to continue.
    print "Add to Cart button is not clickable"
    x = "False"
    while x== "False":
       if EC.element_to_be_clickable(driver.find_element_by_name("Add")):
          x="True"
       print x
    print "Clicking Add to Cart button"
    driver.find_element_by_name("Add").click()

print "Page Title is " + driver.title
cart_regexp=re.compile(".*Cart.*")
if cart_regexp.search(driver.title): ##If the Add to cart button doesnt redirect to the Cart page, we need to click the Add to Cart button again untill is does.
    print "Page title contains Cart"
    print "Clicking Proceed to Checkout"
    driver.find_element_by_id("Button7").click()
else:
    print "Page title doest not contain Cart"
    x = 1
    while not cart_regexp.search(driver.title):
        tries = x
        print "Now clicking Add to Cart again, try #"+tries
        x=x+1
        driver.find_element_by_name("Add").click()
    print "Page title now contains Cart"
    print "Clicking Proceed to Checkout"
    driver.find_element_by_id("Button7").click()
        
      
print "Page Title is " + driver.title
checkout_regexp=re.compile(".*Checkout.*")
if checkout_regexp.search(driver.title):
    print 'Page Title contains Checkout'
    print "Cliking Proceed to Shipping Calculation"
    driver.find_element_by_name("Add22").click()
else:
    print 'Page Title does not contain Checkout'
    play_sound()
    print "Cliking Proceed to Shipping Calculation"
    driver.find_element_by_name("Add22").click()

##If the user chose Credit Card as a payment method, we need to enter the cc info provided now
if payment_method == 'Credit Card':
    print 'Entering Credit Card Information'
    driver.find_element_by_name("ff11_ocardno").send_keys(cc_num)
    select = Select(driver.find_element_by_name('ff11_ocardexpiresmonth'))
    select.select_by_value(exp_month)
    select = Select(driver.find_element_by_name('ff11_ocardexpiresyear'))
    select.select_by_value(exp_year)
    select = Select(driver.find_element_by_name('ff11_ocardtype'))
    select.select_by_value(cc_type)
    driver.find_element_by_name("ff11_ocardcvv2").send_keys(cvv2)
    
print 'Clicking Final Checkout' ##Final checkout button.
driver.find_element_by_name("B1").click()

print "Congrats! You just succesfully bought a poster."

