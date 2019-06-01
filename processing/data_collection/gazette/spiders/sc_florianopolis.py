import re
from datetime import date, datetime

from dateparser import parse
from dateutil.relativedelta import relativedelta
from scrapy import FormRequest

from gazette.items import Gazette
from gazette.spiders.base import BaseGazetteSpider


class ScFlorianopolisSpider(BaseGazetteSpider):
    name = "sc_florianopolis"
    URL = "http://www.pmf.sc.gov.br/governo/index.php?pagina=govdiariooficial"
    TERRITORY_ID = "4205407"
    AVAILABLE_FROM = date(2015, 1, 1)  # actually from June/2009

    def start_requests(self):
        target = date.today()
        while target >= self.AVAILABLE_FROM:
            year, month = str(target.year), str(target.month)
            data = dict(ano=year, mes=month, passo="1", enviar="")
            yield FormRequest(url=self.URL, formdata=data, callback=self.parse)
            target = target + relativedelta(months=1)

    def parse(self, response):
        for link in response.css("ul.listagem li a"):
            url = self.get_pdf_url(response, link)
            if not url:
                continue

            yield Gazette(
                date=self.get_date(link),
                file_urls=(url,),
                is_extra_edition=self.is_extra(link),
                territory_id=self.TERRITORY_ID,
                power="executive_legislature",
                scraped_at=datetime.utcnow(),
            )

    @staticmethod
    def get_pdf_url(response, link):
        relative_url = link.css("::attr(href)").extract_first()
        if not relative_url.lower().endswith(".pdf"):
            return None

        return response.urljoin(relative_url)

    @staticmethod
    def get_date(link):
        text = " ".join(link.css("::text").extract())
        pattern = r"\d{1,2}\s+de\s+\w+\s+de\s+\d{4}"
        match = re.search(pattern, text)
        if not match:
            return None

        return parse(match.group(), languages=("pt",)).date()

    @staticmethod
    def is_extra(link):
        text = " ".join(link.css("::text").extract())
        return "extra" in text.lower()
