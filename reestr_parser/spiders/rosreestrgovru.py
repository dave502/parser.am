import time
import sys
import os
sys.path.insert(0, os.getenv("ROOT_DIR", '/home/dave/DEV/ReestrParser'))
import scrapy
from scrapy.http import HtmlResponse, TextResponse
from logger.logger import setup_logger, PROCEDURES_LOGGER_NAME
from reestr_parser.items import ReestrParserItem
from selenium import webdriver
from selenium.webdriver.firefox.service import Service as FirefoxService
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.action_chains import ActionChains

from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import datetime
import pathlib

app_path = pathlib.Path(__file__).parent.resolve().parents[1]
testlogger = setup_logger(PROCEDURES_LOGGER_NAME, f'{app_path}/logs/{PROCEDURES_LOGGER_NAME}.log')


class RosreestrgovruSpider(scrapy.Spider):
    name = "rosreestrgovru"
    allowed_domains = ["rosreestr.gov.ru"]
    start_urls = ["https://rosreestr.gov.ru/eservices/services/"]

    # ссылка на "Получите сведения из Фонда данных государственной кадастровой оценки"
    URL_TO_FOND = "//a[contains(@href,'portal') and contains(@href, 'sved')]/@href"
    BTN_TO_FOND = "//a[contains(@href,'portal') and contains(@href, 'sved')]/.."

    LINK_TO_PROCEDURES = "//a[contains(@href,'procedure')]/.."
    BTN_DATE_SORT = "//a[contains(@onclick, 'procedureDateBegin')]"
    DATES_OF_PROCEDURES = "//div[@id='procedure']//tr[@class='tbody']/td[last()]/text()"
    LINK_PROCEDURE = f"//div[@id='procedure']//tr[@class='tbody']/td[last() " \
                     f"and (contains(text(), '{datetime.date.today().year}')  " \
                     f"or contains(text(), '{datetime.date.today().year + 1}') )]/..//a"
    URL_TO_PROCEDURE = LINK_PROCEDURE + "/@href"
    PROCEDURES_TABLE = "//div[@id='procedure']//tr[@class='tbody']/td"

    BTN_TO_NEXT_PAGE = "//input[@name='page.number_procedure']/parent::td/following-sibling::td//td[1]"
    BASE_URL = "//base/@href"

    DOC_FIELDS = {
        'title': "//div[@class='title1']/span/text()",
        'status': "//div[@id='state']/div[@class='row_right']/text()",
        'region': "//div[@id='procedure_region_code']/div[@class='row_right']/text()",
        'objects': "string(//div[@id='procedure_pr_realty_type']/div[@class='row_right'])",
        'law': "//div[@id='procedure_type']/div[@class='row_right']/text()",
        'authority': "//div[@id='organName']/div[@class='row_right']/text()",
        'year': "//div[@id='psDateBegin']/div[@class='row_right']/text()",

        'solution_date': "//div[@id='psSolutionDate']/div[@class='row_right']/text()",
        'solution_act_num': "//div[@id='psSolutionNum']/div[@class='row_right']/text()",
        'solution_act_link': "//a[@title='Скачать файл решения']/@href",

        'report_date': "//div[@id='lfr_report_creation_date']/div[@class='row_right']/text()",
        'report_region': "//div[@id='lfr_report_region']/div[@class='row_right']/text()",
        'report_reality_type': "string(//div[@id='lfr_report_realty_type']/div[@class='row_right'])",
        'report_quantity': "//div[@id='lfr_report_quantity']/div[@class='row_right']/text()",

        'report_project_date': "//div[@id='project_report_projectNum']/div[@class='row_right']/text()",
        # Дата размещения проекта отчёта
        'report_project_date_start': "//div[@id='project_report_projectDateStart']/div[@class='row_right']/text()",
        # Дата окончания срока ознакомления с проектом отчета
        'report_project_date_end': "//div[@id='project_report_projectDateEnd']/div[@class='row_right']/text()",
        'report_check_act_link': "//a[contains(@title, 'Скачать файл решения')]/@href",
        'report_intermediate_docs_link': "//div[@class='title2' and "
                                         "contains(text(), 'Промежуточные отчётные документы')]//a/@href",

    }
    url_fond = ""

    def __init__(self):
        super().__init__()

        # install_dir = Path("/usr/bin/firefox")
        driver_loc = "geckodriver"
        binary_loc = "/usr/bin/firefox"  # install_dir / "firefox"

        service = FirefoxService(str(driver_loc))
        opts = webdriver.FirefoxOptions()
        opts.binary_location = str(binary_loc)
        opts.headless = True
        opts.add_argument("user-agent=Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/111.0")
        self.driver = webdriver.Firefox(service=service, options=opts)
        self.wait = WebDriverWait(self.driver, 120)
        self.actions = ActionChains(self.driver)

    def __del__(self):
        testlogger.info(f'__del__')
        if self.driver:
            self.driver.close()

    # class wait_for_page_load(object):
    #     def __init__(self, browser):
    #         self.browser = browser
    #
    #     def wait_for(self, condition_function):
    #         start_time = time.time()
    #         while time.time() < start_time + 3:
    #             if condition_function():
    #                 return True
    #             else:
    #                 time.sleep(0.1)
    #         raise Exception(
    #             'Timeout waiting for {}'.format(condition_function)
    #         )
    #
    #     def __enter__(self):
    #         self.old_page = self.browser.find_element(by=By.TAG_NAME, value='html')
    #
    #     def page_has_loaded(self):
    #         new_page = self.browser.find_element(by=By.TAG_NAME, value='html')
    #         return new_page.id != self.old_page.id
    #
    #     def __exit__(self, *_):
    #         self.wait_for(self.page_has_loaded)

    def parse(self, response, **kwargs):

        if not self.url_fond:
            self.url_fond = response.xpath(self.URL_TO_FOND)[0].extract()
            yield response.follow(self.url_fond, callback=self.parse)
        else:
            self.driver.get(response.url)
            link_to_procedures = self.wait.until(EC.presence_of_element_located((By.XPATH, self.LINK_TO_PROCEDURES)))
            link_to_procedures.click()
            self.wait.until(EC.presence_of_all_elements_located((By.XPATH, self.PROCEDURES_TABLE)))

            # sorted = False
            # btn_sort_by_dates = self.wait.until(EC.presence_of_element_located((By.XPATH, self.BTN_DATE_SORT)))
            # with self.wait_for_page_load(self.driver):
            #     btn_sort_by_dates.click()
            # self.wait.until(EC.presence_of_element_located((By.XPATH, self.LINK_TO_PROCEDURES)))
            # #self.wait.until(EC.presence_of_element_located((By.XPATH, self.DATES_OF_PROCEDURES)))
            # dates_of_procedures = response.xpath(self.DATES_OF_PROCEDURES).extract()
            # if all([int(i.strip()) < datetime.datetime.today().year for i in dates_of_procedures]) :
            #     btn_sort_by_dates = self.wait.until(EC.presence_of_element_located((By.XPATH, self.BTN_DATE_SORT)))
            #     btn_sort_by_dates.click()
            #     self.wait.until(EC.presence_of_element_located((By.XPATH, self.LINK_TO_PROCEDURES)))
            #     dates_of_procedures = response.xpath(self.DATES_OF_PROCEDURES).extract()
            #     if all([int(i.strip()) < datetime.datetime.today().year for i in dates_of_procedures]):
            #         sorted = True
            # else:
            #     sorted = True

            page_counter = 0
            have_next = True
            while have_next:
                try:
                    page_counter += 1
                    # if page_counter == 3: break
                    testlogger.info(f'парсинг страницы с процедурами N {page_counter}')
                    link_base = response.xpath(self.BASE_URL)[0].extract()
                    links_to_procedures = response.xpath(self.URL_TO_PROCEDURE).extract()
                    testlogger.info(f'найдено {len(links_to_procedures)} процедур:')
                    for link in links_to_procedures:
                        testlogger.info(link)
                        yield response.follow(link_base + link, callback=self.procedure_parse)

                    if next_page := self.driver.find_element(by=By.XPATH,
                                                             value=self.BTN_TO_NEXT_PAGE):
                        if next_page.get_attribute('onclick'):
                            testlogger.info(f'переход на следующую страницу N {page_counter + 1}')
                            next_page.click()
                            self.wait.until(EC.presence_of_all_elements_located((By.XPATH, self.PROCEDURES_TABLE)))
                            response = TextResponse(url=self.driver.current_url, body=self.driver.page_source,
                                                    encoding='utf-8')
                            # if sorted:
                            #     dates_of_procedures = response.xpath(self.DATES_OF_PROCEDURES).extract()
                            #     if all([int(i) for i in dates_of_procedures]) < datetime.datetime.today().year:
                            #         have_next = False
                        else:
                            testlogger.info(f'была последняя страница')
                            have_next = False
                    else:
                        testlogger.info(f'страница была последней')
                        have_next = False
                except Exception as e:
                    testlogger.critical(f"Critical error while parsing page N {page_counter}: {e}")
                    break
            # self.close(this)

    def spider_closed(self, spider):
        testlogger.info(f'__spider_closed__')
        self.driver.close()

    def procedure_parse(self, response: HtmlResponse):

        doc_values = {field: response.xpath(xpath).extract_first() for (field, xpath) in self.DOC_FIELDS.items()}
        doc_values['url'] = response.url
        yield ReestrParserItem(doc_values)
