from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
import time
from selenium.common.exceptions import TimeoutException, NoSuchElementException, ElementNotInteractableException, StaleElementReferenceException
import re
from BetStat import BetStat

# Set up the options to use a specific Chrome profile
options = webdriver.ChromeOptions()
options.add_argument("user-data-dir=/Users/connordawson/Library/Application Support/Google/Chrome/User Data")
options.add_argument("profile-directory=Profile 1")  # Make sure this matches the actual profile directory name

driver = webdriver.Chrome(options=options)
all_bets = []
player_list = []
counter = 0

def open_underdog():
    global counter
    driver.get('https://underdogfantasy.com/pick-em/higher-lower/all')

    # Wait for the username field to be present and enter the username
    username = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located(
            (By.XPATH, '/html/body/div[1]/div/div/div[2]/div[2]/div[1]/form/div[1]/label/div[2]/input'))
    )
    username.send_keys('email')

    # Wait for the password field to be present and enter the password
    password = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located(
            (By.XPATH, '/html/body/div[1]/div/div/div[2]/div[2]/div[1]/form/div[2]/label/div[2]/input'))
    )
    password.send_keys("password")

    # Wait for the login button to be clickable and click it
    log_in = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, '/html/body/div[1]/div/div/div[2]/div[2]/div[1]/form/button'))
    )
    log_in.click()
    time.sleep(1)
    click_remove_buttons_until_not_found(driver)

    for player in player_list:
        if counter % 3 == 0 and counter > 0:
            try:
                # Dynamic wait for the multiplier element
                multiplier_element = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.XPATH,
                                                    '/html/body/div[1]/div/div[1]/div[3]/div/div[2]/div[2]/div[2]/label[1]/div[2]/div/div/span'))
                )
                multiplier = multiplier_element.text
                pattern = r'\b(\d+\.\d+)x\b'
                mlt_list = re.findall(pattern, multiplier)
                multiplier = mlt_list[0]
                if multiplier == '6':
                    print('Found good bet!')
                    # Dynamic wait for the wager input field
                    wager_input = WebDriverWait(driver, 10).until(
                        EC.element_to_be_clickable(
                            (By.XPATH, '/html/body/div[1]/div/div[1]/div[3]/div/div[2]/div[1]/div/label/div[2]/input'))
                    )
                    wager_input.click()
                    wager_input.send_keys('1')

                    # Dynamic wait for the confirm button
                    confirm_button = WebDriverWait(driver, 10).until(
                        EC.element_to_be_clickable(
                            (By.XPATH, '/html/body/div[1]/div/div[1]/div[3]/div/div[2]/div[3]/button/div'))
                    )
                    confirm_button.click()
                    counter = 0
                else:
                    counter = 0
                    click_remove_buttons_until_not_found(driver)
                    print(multiplier)
            except (NoSuchElementException, TimeoutException) as e:
                print(f"Element not found or timeout occurred: {e}")
                continue
            except Exception as e:
                print(f"Unexpected error: {e}")
                continue
            except NoSuchElementException as e:
                counter = 0
                click_remove_buttons_until_not_found(driver)
                print(f"Multiplier element not found: {e}")
                continue
            except Exception as e:
                print(f"Unexpected error: {e}")
                continue

        search_bar = WebDriverWait(driver, 30).until(
            EC.presence_of_element_located(
                (By.XPATH, '/html/body/div[1]/div/div[1]/div[1]/div/div[1]/div/label/div/input'))
        )
        search_bar.click()
        search_bar.clear()  # Clear any existing text in the search bar
        search_bar.send_keys(player)
        search_bar.send_keys(Keys.RETURN)

        elements = WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.CLASS_NAME, 'styles__overUnderListCell__tbRod'))
        )

        for bet in all_bets:
            if bet.player_name == player:
                isHigher = bet.stat_type != 'Under'
                place_bet(elements, isHigher, bet.over_under)


def click_remove_buttons_until_not_found(driver):
    wait = WebDriverWait(driver, 10)

    while True:
        try:
            remove_button = wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, 'button[data-testid="remove-button"]'))
            )
            # Click the "x" button
            remove_button.click()
        except (NoSuchElementException, TimeoutException):
            print("No more remove buttons found.")
            break




def place_bet(element_list, isHigher, line):
    global counter
    for element in element_list:
        try:
            if line in element.text:
                if isHigher:
                    # Wait for the Higher button to be clickable and then click it
                    higher_button = WebDriverWait(element, 10).until(
                        EC.element_to_be_clickable((By.XPATH, './/button[text()="Higher"]'))
                    )
                    higher_button.click()
                    counter += 1
                else:
                    # Wait for the Lower button to be clickable and then click it
                    lower_button = WebDriverWait(element, 10).until(
                        EC.element_to_be_clickable((By.XPATH, './/button[text()="Lower"]'))
                    )
                    lower_button.click()
                    counter += 1
        except StaleElementReferenceException:
            print(f"Stale element reference exception for line: {line}. Retrying...")
            # Re-find the element and retry the operation
            try:
                if line in element.text:
                    if isHigher:
                        # Wait for the Higher button to be clickable and then click it
                        higher_button = WebDriverWait(element, 10).until(
                            EC.element_to_be_clickable((By.XPATH, './/button[text()="Higher"]'))
                        )
                        higher_button.click()
                        counter += 1
                    else:
                        # Wait for the Lower button to be clickable and then click it
                        lower_button = WebDriverWait(element, 10).until(
                            EC.element_to_be_clickable((By.XPATH, './/button[text()="Lower"]'))
                        )
                        counter += 1
                        lower_button.click()
            except (TimeoutException, NoSuchElementException, ElementNotInteractableException, StaleElementReferenceException) as e:
                print(f"Error interacting with element after retry: {e}")
                continue
        except (TimeoutException, NoSuchElementException, ElementNotInteractableException) as e:
            print(f"Error interacting with element: {e}")
            continue
def open_oddsjam():
    global player_list
    driver.get('https://fantasy.oddsjam.com/fantasy-odds/underdog-fantasy?maxOdds=200')

    # Wait for the top bets section to be present
    top_bets = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, "/html/body/div[1]/div/main/div/div[2]/div/div"))
    )

    # Once present, find the rows within the top bets section
    rows = top_bets.find_elements(By.TAG_NAME, 'tr')
    for row in rows:
        cells = row.find_elements(By.TAG_NAME, 'td')
        if len(cells) > 0:
            player_details = cells[2].text.split('\n')
            player_name = player_details[0]
            matchup = player_details[1]
            stat = cells[3].text
            line = cells[4].text
            over_under = cells[5].text

            chance_to_hit = cells[6].text
            if percentage_to_decimal(chance_to_hit) > 0.55:
                bet = BetStat(player_name, matchup, stat, line, over_under, chance_to_hit)
                player_list.append(player_name)
                all_bets.append(bet)

    for bet in all_bets:
        print(bet)



def percentage_to_decimal(percentage_str):
    clean_str = percentage_str.replace('%', '')
    decimal_value = float(clean_str) / 100
    return decimal_value


open_oddsjam()
open_underdog()

# Optionally, close the driver after all operations are done
time.sleep(100)
driver.quit()
