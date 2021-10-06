from scrapy.http import FormRequest, Request
from scrapy.spiders import CrawlSpider
from scrapy.http.response.text import TextResponse

class bcolors:
    SUCCESS = '\033[92m'
    ERROR = '\033[91m'
    ENDC = '\033[0m'

class StaffcloudSpider(CrawlSpider):

    name = 'staffcloud'

    def __init__(self, base_url, username, password, *args, **kwargs):
        super(StaffcloudSpider, self).__init__(*args, **kwargs)
        self.base_url = base_url
        self.start_urls = [self.base_url]
        self.logout_url = f'{self.base_url}/logout'
        self.username = username
        self.password = password

    def parse_start_url(self, response):
        return FormRequest.from_response(
            response,
            formdata={'username': self.username, 'password': self.password},
            callback=self.after_login
        )

    def after_login(self, response):
        status = response.status
        if status != 200:
            print('LOGIN FAILED')
            return

        return Request(url=f'{self.base_url}/planner/staffplanning/index',
                       callback=self.parse_my_url, dont_filter=True)


    def validate_response(self, response):
        color = bcolors.ERROR if response.status >= 400 else bcolors.SUCCESS
        print(f'{color}[{response.status}] {response.url}{bcolors.ENDC}')


    def parse_my_url(self, response):
        self.validate_response(response)
        if isinstance(response, TextResponse):
            for href in response.css('a::attr(href)'):
                url = href.get()
                should_follow = url.startswith(self.start_urls[0]) and url != self.logout_url
                if should_follow:
                    yield response.follow(href, self.parse_my_url)
