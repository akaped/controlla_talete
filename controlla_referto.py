import json
try:
    from selenium import webdriver
except:
    print("Please instal selenium - pip install selenium")
    exit(1)
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.firefox.options import Options
from selenium.webdriver import FirefoxProfile
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
import telegram_send
import os
from time import sleep
from sys import argv
from pathlib import Path
from os.path import join


home = str(Path.home())
download_path = join(home, 'Downloads')
mime_types = "application/pdf,application/vnd.adobe.xfdf,application/vnd.fdf,application/vnd.adobe.xdp+xml"
fail_mess = "Il referto cercato non è ancora disponibile oppure i codici inseriti non sono corretti."



def main():
    status_referto = False
    while status_referto == False:
        profiles = FirefoxProfile()
        profiles.set_preference('browser.download.folderList', 2) # custom location
        profiles.set_preference('browser.download.manager.showWhenStarting', False)
        profiles.set_preference('browser.download.dir', download_path)
        profiles.set_preference('browser.helperApps.neverAsk.saveToDisk', mime_types)
        profiles.set_preference("plugin.disable_full_page_plugin_for_types", mime_types)
        profiles.set_preference("pdfjs.disabled", True)
        options = Options()
        options.headless = True

        driver = webdriver.Firefox(firefox_profile=profiles, options=options)
        driver.get("https://mdb.ulss.tv.it/Talete/login.jsf")
        driver.set_window_size(1084, 692)
        # reset the fileds
        driver.find_element(By.ID, "loginForm:button2").click()
        # insert the CF
        driver.find_element(By.ID, "loginForm:codFiscale").click()
        driver.find_element(By.ID, "loginForm:codFiscale").send_keys(codice_fiscale)
        # Insert the PIN
        driver.find_element(By.ID, "loginForm:PIN").click()
        driver.find_element(By.ID, "loginForm:PIN").send_keys(codice_referto)
        # search
        driver.find_element(By.ID, "loginForm:button1").click()
        # Get the page source and assess if the
        if fail_mess in driver.page_source:
            #os.system('telegram-send "Referto non Disponibile"')
            print("Referto non ancora disponibile")
            status_referto = False
            sleep(120)
        else:
            print("Referto disponibile")
            status_referto = True
            os.system('telegram-send "Referto Disponibile"')
            driver.find_element_by_css_selector("img[src='/Talete/TV09/images/PDF.png']").click()
            sleep(10)
            filename = max([os.path.join(download_path, f) for f in os.listdir(download_path)], key=os.path.getctime)
            os.system(f'telegram-send --file "{filename}"')
        driver.close()
        driver.quit()
    exit(0)

if __name__ == '__main__':
    print("Controlla presenza referto nel sistema Talete del distretto sanitario Ulls2 di Treviso")
    try:
        codice_fiscale,codice_referto = argv[1],argv[2]
    except Exception as e:
        print("python3 controlla_referto codice_fiscale codice_referto")
        print(e)
        exit(1)
    main()
