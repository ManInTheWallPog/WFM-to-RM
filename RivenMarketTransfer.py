from os import name
import requests
import base64
from time import sleep
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.alert import Alert
from selenium.common.exceptions import NoSuchElementException 

global email
global password 


WFM_API = "https://api.warframe.market/v1"


def get_name():
    try:
            name = str(input("Introduce your profile name: "))
    except ValueError:
            print("An error happened when reading your profile name, please try again. \n")
    if name:
            return name

def get_email():
        try:
            email = str(input("Introduce the email associated to your riven.market account: "))
        except ValueError:
            print("An error happened when reading your email, please try again. \n")
        if email:
            return email

def get_pass():

    while True:
        try:
            password = str(input("Introduce your password to riven.market: "))
        except ValueError:
            print("An error happened when reading your password, please try again. \n")
        if password:
            return password

def ask_delete():
    while True:
        try:
            global ans 
            ans = str(input("Do you want to delete your current riven.market listings? This may take a while. (Y/N): "))
        except ValueError:
            print("An error happened when reading your Selection, please try again. \n")
        if ans:
            return ans

def get_request(url):
    """Executes a wfm query"""
    request = requests.get(WFM_API + url, stream=True)
    if request.status_code == 200:
        return request.json()["payload"]
    return None

def get_auctions():
    """Returns the current auctions of the user."""
    result = get_request("/profile/" +name +"/auctions")
    return result["auctions"]

def save_rivens():
        email = str(get_email())
        passw = str(get_pass())
        global name
        name = get_name()
        ask_delete()
        startbrowser (email, passw)
        for auction in get_auctions():
           weaponName = auction["item"]["weapon_url_name"].replace("_", " ").title().replace(" ", "_")
           rivenName = auction["item"]["name"].capitalize().replace("_", " ")
           rivenPrice = str(auction["starting_price"])
           rivenPol = auction["item"]["polarity"].capitalize()
           Rank =  str(auction["item"]["mod_rank"]) + ","
           Rolls = str(auction["item"]["re_rolls"])
           MR = str(auction["item"]["mastery_level"])
           attributes = ""
           poscount = 0
           rivenMarketattr="""{"weaponData":"""""+ ' "' +weaponName + """", "Rank": """ + Rank +""" "MR": """ +MR + """, "Rolls": """ + Rolls +""", "Positives": {"""
           for attr in auction["item"]["attributes"]:    
               posi = attr["positive"]
               if posi == True:
                    poscount = poscount +1
               elif posi == False and poscount == 2:
                   attributes = attributes + ",,"  
               if posi == False:
                   rivenMarketattr = rivenMarketattr[:-2]
                   rivenMarketattr = rivenMarketattr + """}, "Negatives": {"""                   
               new_attr_rm = cleanrivenmarket(attr["url_name"]) 
               rivenMarketattr = rivenMarketattr + new_attr_rm + " " + str(abs(attr["value"])) + ", "
           rivenMarketattr = rivenMarketattr[:-2] + "}}"
           rivenMarketattrbase = base64.b64encode(rivenMarketattr.encode())
           rivenMarketattrbase = str(rivenMarketattrbase)
           rivenMarketattrbasea = rivenMarketattrbase[2:] 
           rivenMarketattrbasea = rivenMarketattrbasea [:-1]
           rivenMarketUrl = "https://riven.market/sell?import=" + rivenMarketattrbasea 
           postriven(rivenMarketUrl, rivenPrice, rivenPol, rivenName)
           print (weaponName + " " + rivenName +" posted")

def cleanrivenmarket (attr):
    if attr == "base_damage_/_melee_damage":
        return """"Damage":"""
    elif attr == "multishot":
        return """"Multi":"""
    elif attr == "fire_rate_/_attack_speed":
        return """"Speed":"""
    elif attr == "damage_vs_corpus":
        return """"Corpus":"""
    elif attr == "damage_vs_grineer":
        return """"Grineer":"""
    elif attr == "damage_vs_infested":
        return """"Infested":"""
    elif attr == "impact_damage":
        return """"Impact":"""
    elif attr == "puncture_damage":
        return """"Puncture":"""
    elif attr == "slash_damage":
        return """"Slash":"""
    elif attr == "cold_damage":
        return """"Cold":"""
    elif attr == "toxin_damage":
        return """"Toxin":"""
    elif attr == "heat_damage":
        return """"Heat":"""
    elif attr == "electric_damage":
        return """"Electric":"""
    elif attr == "combo_duration":
        return """"Combo":"""
    elif attr == "critical_chance":
        return """"CritChance":"""
    elif attr == "critical_damage":
        return """"CritDmg":"""
    elif attr == "critical_chance_on_slide_attack":
        return """"Critical Chance for Slide Attack":"""
    elif attr == "finisher_damage":
        return """"Finisher":"""
    elif attr == "projectile_speed":
        return """"Flight":"""
    elif attr == "ammo_maximum":
        return """"Ammo":"""
    elif attr == "magazine_capacity":
        return """"Magazine":"""
    elif attr == "punch_through":
        return """"Punch":"""
    elif attr == "reload_speed":
        return """"Reload":"""
    elif attr == "range":
        return """"Range":"""
    elif attr == "status_chance":
        return """"StatusC":"""
    elif attr == "status_duration":
        return """"StatusD":"""
    elif attr == "recoil":
        return """"Recoil":"""
    elif attr == "zoom":
        return """"Zoom":"""
    elif attr == "channeling_damage":
        return """"InitC":"""
    elif attr == "channeling_efficiency":
        return """"ComboEfficiency":"""
    elif attr == "chance_to_gain_combo_count":
        return """"Combo":"""
    return (attr)

def startbrowser (mail, passw):
    
    global browser
    browser = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
    browser.get("https://riven.market/login")
    browser.implicitly_wait(20)
    options = webdriver.ChromeOptions()
    options.add_experimental_option('excludeSwitches', ['enable-logging'])
    email = browser.find_element(By.NAME, "login_email")
    password = browser.find_element(By.NAME, "login_password")
    LogIn = browser.find_element(By.NAME, "login")
    email.send_keys(str(mail))
    password.send_keys(str(passw))
    LogIn.click()  
    browser.get("https://riven.market/profile")
    if ans == "Y":
        del_listings()
    ##print("done starting")
    
  

def postriven(url, price, Polarity, Name):
    ##print("startposting")
    browser.get(url)
    RivenName = browser.find_element(By.ID, "namepicker")
    RivenName.send_keys(Name)
    Polarity = Select(browser.find_element(By.ID, "polarity"))
    Polarity.select_by_visible_text("Madurai")
    Next = browser.find_element(By.ID, "createriven")
    Next.click()
    Price = browser.find_element(By.ID, "price")
    Price.clear()
    Price.send_keys(price)
    Sell = browser.find_element(By.ID, "sellriven")
    Sell.click()
    Alert(browser).accept()
    ##postriven(url, price, Polarity, Name) ##experimental to post a lot of rivens

def del_listings():
    try: 
        for elem in browser.find_elements(By.CSS_SELECTOR, "div.attribute.action.actionbar > i:nth-child(5)"):
            elem.click()
            Alert(browser).accept()
            ##print("deltedListing")
            sleep(1) ##idk might be needed for it to not get ratelimited
    except NoSuchElementException:
        return()