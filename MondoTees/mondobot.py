__author__ = 'Selim Docquir'

from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import ElementNotVisibleException
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.wait import WebDriverWait
import easygui as eg
import time
import re

##-----------------------------------------##
## ----parameter to be modified -----------##

mode = "p"          # v for vinyl, p for poster.
##-----------------------------------------##
##-----------------------------------------##


##-----------------------------------------------------------------------------------------------------##
##---------------open product_name.txt and assign the correct value to the preset xpaths---------------##
product_names = open('product_name.txt', 'r').read()
product_names = product_names.split()
num_names = len(product_names)
if num_names < 1:
    print "Not enough product names"
    exit()
elif num_names == 1:
    reg_xpath = ("//div[@class='drop-items']/div/div/div/"
                 "a[(contains(@href, '{0}'))"
                 "and not (contains(@href, 'variant'))]").format(product_names[0])
    var_xpath = ("//div[@class='drop-items']/div/div/div/"
                 "a[(contains(@href, '{0}'))"
                 "and (contains (@href, 'variant'))]").format(product_names[0])
    home_add_reg_xpath = ("//div[@class='drop-items']/div/div/"
                          "div[a[(contains(@href,'{0}'))"
                          "and not (contains(@href, 'variant'))]]/"
                          "div[@class= 'drop-actions']/button").format(product_names[0])
    home_add_var_xpath = ("//div[@class='drop-items']/div/div/"
                          "div[a[(contains(@href,'{0}'))"
                          "and (contains(@href, 'variant'))]]/"
                          "div[@class= 'drop-actions']/button").format(product_names[0])
elif num_names == 2:
    reg_xpath = ("//div[@class='drop-items']/div/div/div/"
                 "a[((contains(@href, '{0}'))or(contains(@href, '{1}')))"
                 "and not (contains(@href, 'variant'))]").format(product_names[0], product_names[1])
    var_xpath = ("//div[@class='drop-items']/div/div/div/"
                 "a[((contains(@href, '{0}'))or(contains(@href, '{1}')))"
                 "and (contains (@href, 'variant'))]").format(product_names[0], product_names[1])
    home_add_reg_xpath = ("//div[@class='drop-items']/div/div/"
                          "div[a[((contains(@href,'{0}'))or (contains(@href, '{1}')))"
                          "and not (contains(@href, 'variant'))]]/"
                          "div[@class= 'drop-actions']/button").format(product_names[0], product_names[1])
    home_add_var_xpath = ("//div[@class='drop-items']/div/div/"
                          "div[a[((contains(@href,'{0}'))or (contains(@href, '{1}')))"
                          "and (contains(@href, 'variant'))]]/"
                          "div[@class= 'drop-actions']/button").format(product_names[0], product_names[1])
elif num_names == 3:
    reg_xpath = ("//div[@class='drop-items']/div/div/div/"
                 "a[((contains(@href, '{0}'))or(contains(@href, '{1}')) or(contains(@href, '{2}')))"
                 "and not (contains(@href, 'variant'))]").format(product_names[0], product_names[1],product_names[2])
    var_xpath = ("//div[@class='drop-items']/div/div/div/"
                 "a[((contains(@href, '{0}'))or(contains(@href, '{1}')) or(contains(@href, '{2}')))"
                 "and (contains (@href, 'variant'))]").format(product_names[0], product_names[1], product_names[2])
    home_add_reg_xpath = ("//div[@class='drop-items']/div/div/"
                          "div[a[((contains(@href,'{0}'))or (contains(@href, '{1}')) or (contains(@href, '{2}')))"
                          "and not (contains(@href, 'variant'))]]/"
                          "div[@class= 'drop-actions']/button").format(product_names[0], product_names[1], product_names[2])
    home_add_var_xpath = ("//div[@class='drop-items']/div/div/"
                          "div[a[((contains(@href,'{0}'))or (contains(@href, '{1}')) or (contains(@href, '{2}')))"
                          "and (contains(@href, 'variant'))]]/"
                          "div[@class= 'drop-actions']/button").format(product_names[0], product_names[1], product_names[2])
##---------------------------------------------------------------------------------------------------------------------##
##---------------------------------------------------------------------------------------------------------------------##

program_title       = 'MondoBot'
drop_url            = "http://mondotees.com"
cart_url            = 'http://mondotees.com/cart'
trick_url_poster    = "http://mondotees.com/collections/posters/products/the-fisher-king-poster-hundley"
trick_url_vinyl     = "http://mondotees.com/collections/music/products/paranorman-original-motion-picture-soundtrack"
list_info = []
list_accounts = []
with open('account_info.txt', 'r') as f:
    data = f.readlines()
    for line in data:
        words = line.split()
        list_info.append(words)
        list_accounts.append(words[0])


class Mondobot(object):
    def __init__(self):
        """
        Initialize the recurrent variables to be used in this instance of Mondobot.
        Ask the user for the account information and edition choice.
        """
        self.driver         = None
        self.wait           = None
        self.account        = None
        self.gift           = None
        self.edxpath        = None
        self.edhomeadd      = None
        self.drop           = False
        self.visible        = False
        self.refresh_count  = 0
        self.gift           = ""
        self.email = self.drop_info_choices()
        for sublist in list_info:
            if sublist[0] == self.email:
                self.password = sublist[1]
                if len(sublist) == 3:
                    self.gift = sublist[2]
        self.edition_choice = self.edition_choice_box()
        if self.edition_choice == 'regular':
            self.edxpath = reg_xpath
            self.edhomeadd = home_add_reg_xpath
        elif self.edition_choice == 'variant':
            self.edxpath = var_xpath
            self.edhomeadd = home_add_var_xpath
        print "Account is       ", self.email
        print "Product is       ", product_names, self.edition_choice
        print "GC code is       ", self.gift

    def start_bot(self):
        """Combine start_driver and start_process for easy interaction with multiprocessing."""
        self.start_driver()
        self.start_process()

    def start_driver(self):
        """Start webdriver, but not the bot process"""
        self.driver = webdriver.Chrome()
        self.wait = WebDriverWait(self.driver, 10)
        self.driver.implicitly_wait(5)

    def start_process(self):
        """After having started webdriver, start the actual bot process"""
        self.login()
        self.checkout_trick()
        self.refresh_process()
        self.home_page_add()
        self.switch_tab(2)
        self.driver.refresh()
        while self.visible == False:
            try :
                self.driver.find_element_by_xpath("//input[@id='complete-purchase']").click()
                self.visible = True
            except ElementNotVisibleException:
                self.visible = False

    def login(self):
        """Open login page, and send account info"""
        self.driver.get("http://mondotees.com/account/login")
        self.driver.find_element_by_id("customer_email").send_keys(self.email)
        self.driver.find_element_by_id("customer_password").send_keys(self.password)
        self.driver.find_element_by_xpath("//input[@value='Sign In']").click()

    def switch_tab(self, tab_number):
        """Switching tab mechanism, specific to chromedriver."""
        handles = self.driver.window_handles
        self.driver.switch_to.window(handles[tab_number - 1])

    def checkout_trick(self):
        """
        Create new tab to start the checkout trick, which consists of completing
        checkout with a similar item to the one that is being dropped, but stopping before
        clicking on the last checkout button. Then, keeping that second tab open, switch
        the control of the webdriver to the first tab, and delete the bogus item from cart.
        """
        newtab_actions = webdriver.ActionChains(self.driver)
        faq_link = self.driver.find_element_by_xpath("//a[contains(@href, 'faq')]")
        newtab_actions.move_to_element(faq_link)
        newtab_actions.key_down(Keys.CONTROL + Keys.SHIFT)
        newtab_actions.click(faq_link)
        newtab_actions.key_up(Keys.CONTROL + Keys.SHIFT).perform()
        self.switch_tab(2)
        if mode == 'p':
            self.driver.get(trick_url_poster)
        elif mode == 'v':
            self.driver.get(trick_url_vinyl)
        self.driver.find_element_by_xpath("//button[@id='addToCart']").click()
        time.sleep(0.5)
        self.driver.get(cart_url)
        time.sleep(0.5)
        checkout_buttons = self.driver.find_elements_by_xpath("//input[@name='checkout']")
        check_actions = webdriver.ActionChains(self.driver)
        check_actions.click(checkout_buttons[1]).perform()
        self.driver.find_element_by_xpath("//input[@id='commit-button']").click()
        gc_field = self.driver.find_element_by_xpath("//input[@name='gift_card_code']")
        gc_field.send_keys(self.gift)
        self.driver.find_element_by_xpath("//input[@value='Apply']").click()
        if mode == 'p':
            #Seclecting Priority Mail option, assuming it is 2nd in the dropdown menu
            ship = self.driver.find_element_by_name('shipping_rate')
            ship.click()
            prio_actions = webdriver.ActionChains(self.driver)
            prio_actions.send_keys_to_element(ship, Keys.ARROW_DOWN)
            prio_actions.send_keys_to_element(ship, Keys.ENTER)
            prio_actions.perform()
        time.sleep(1)
        self.switch_tab(1)
        self.driver.get(cart_url)
        self.driver.get('http://mondotees.com/cart/change?line=1&quantity=0')

    def check_exists_by_xpath(self):
        """Return True if element exist, False otherwise Catch Thrown exception"""
        self.driver.implicitly_wait(0.5)
        try:
            self.driver.find_element_by_xpath(self.edxpath)
        except NoSuchElementException:
            return False
        self.driver.implicitly_wait(5)
        return True

    def refresh_process(self):
        """Refresh home page untill coveted item is dropped. Keep refresh count and print out"""
        self.driver.get(drop_url)
        self.drop = self.check_exists_by_xpath()
        while self.drop is False:
            self.driver.get(drop_url)
            self.drop = self.check_exists_by_xpath()
            self.refresh_count += 1
            print "Refresh #", str(self.refresh_count) + '\r',

    def home_page_add(self):
        """Once item has been found via refresh_process, add item to cart from home page"""
        product_location = self.driver.find_element_by_xpath(self.edxpath)
        button_location = self.driver.find_element_by_xpath(self.edhomeadd)
        add_actions = webdriver.ActionChains(self.driver)
        add_actions.move_to_element(product_location)
        add_actions.click(button_location)
        add_actions.perform()

    def drop_info_choices(self):
        """Ask user which account to use"""
        msg = "Choose account"
        self.account = eg.choicebox(msg, program_title, list_accounts)
        return self.account

    def edition_choice_box(self):
        """Ask user which edition to look for on the drop"""
        msg = 'Choose between variant or regular(choose regular if there is only one kind of edition)'
        choices_edition = ['regular', 'variant']
        self.edition_choice = eg.buttonbox(msg, program_title, choices_edition)
        return self.edition_choice
