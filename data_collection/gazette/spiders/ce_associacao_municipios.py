from gazette.spiders.base.sigpub import SigpubGazetteSpider


class CeAssociacaoMunicipiosSpider(SigpubGazetteSpider):
    name = "ce_associacao_municipios"
    TERRITORY_ID = "2300000"
    CALENDAR_URL = "https://www.diariomunicipal.com.br/aprece"
