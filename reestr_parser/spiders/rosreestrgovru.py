import scrapy
from scrapy.http import HtmlResponse, TextResponse
from reestr_parser.items import ReestrParserItem
from selenium import webdriver
from selenium.webdriver.firefox.service import Service as FirefoxService
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.action_chains import ActionChains

from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from pathlib import Path


class RosreestrgovruSpider(scrapy.Spider):
    name = "rosreestrgovru"
    allowed_domains = ["rosreestr.gov.ru"]
    start_urls = ["https://rosreestr.gov.ru/eservices/services/"]

    # ссылка на "Получите сведения из Фонда данных государственной кадастровой оценки"
    URL_TO_FOND = "//a[contains(@href,'portal') and contains(@href, 'sved')]/@href"
    BTN_TO_FOND = "//a[contains(@href,'portal') and contains(@href, 'sved')]/.."

    LINK_TO_PROCEDURES = "//a[contains(@href,'procedure')]/.."

    LINK_PROCEDURE = "//tr[@class='tbody']//a[contains(@href, 'viewProcedure') " \
                     "and not (contains(@href, 'showRep=true'))]"
    URL_TO_PROCEDURE = LINK_PROCEDURE + "/@href"

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
        'report_project_date_end': "//div[@id='project_report_projectDateEnd']/div[@class='row_right']/text()",
        'report_check_act_link': "//a[contains(@title, 'Скачать файл решения')]/@href",
        'report_intermediate_docs_link': "//div[@class='title2' and "
                                                   "contains(text(), 'Промежуточные отчётные документы')]//a/@href",
    }
    url_fond = ""

    def __init__(self):
        super().__init__()

        install_dir = Path("/snap/firefox/current/usr/lib/firefox")
        driver_loc = install_dir / "geckodriver"
        binary_loc = install_dir / "firefox"

        service = FirefoxService(str(driver_loc))
        opts = webdriver.FirefoxOptions()
        opts.binary_location = str(binary_loc)
        opts.add_argument("user-agent=Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/111.0")
        self.driver = webdriver.Firefox(service=service, options=opts)
        self.wait = WebDriverWait(self.driver, 120)
        self.actions = ActionChains(self.driver)
        #

    def parse(self, response: HtmlResponse):

        if not self.url_fond:
            self.url_fond = response.xpath(self.URL_TO_FOND)[0].extract()
            yield response.follow(self.url_fond, callback=self.parse)
        else:
            self.driver.get(response.url)
            link_to_procedures = self.wait.until(EC.presence_of_element_located((By.XPATH, self.LINK_TO_PROCEDURES)))
            link_to_procedures.click()
            self.wait.until(EC.presence_of_all_elements_located((By.XPATH, self.LINK_PROCEDURE)))

            have_next = True
            while have_next:
                try:
                    link_base = response.xpath(self.BASE_URL)[0].extract()
                    links_to_procedures = response.xpath(self.URL_TO_PROCEDURE).extract()
                    for link in links_to_procedures:
                        yield response.follow(link_base + link, callback=self.procedure_parse)

                    if select_region_btn := self.driver.find_element(by=By.XPATH,
                                                                     value=self.BTN_TO_NEXT_PAGE):
                        if select_region_btn.get_attribute('onclick'):
                            select_region_btn.click()
                            self.wait.until(EC.presence_of_all_elements_located((By.XPATH, self.LINK_PROCEDURE)))
                            response = TextResponse(url=self.driver.current_url, body=self.driver.page_source,
                                                encoding='utf-8')
                        else:
                            self.close()
                    else:
                        print()
                except:
                    break

    def spider_closed(self, spider):
        self.driver.close()

    def procedure_parse(self, response: HtmlResponse):

        doc_values = {field: response.xpath(xpath).extract_first() for (field, xpath) in self.DOC_FIELDS.items()}
        doc_values['url'] = response.url
        yield ReestrParserItem(doc_values)



