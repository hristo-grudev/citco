import scrapy

from scrapy.loader import ItemLoader
from ..items import CitcoItem
from itemloaders.processors import TakeFirst


class CitcoSpider(scrapy.Spider):
	name = 'citco'
	start_urls = ['http://www.citco.com/our-thinking/latest-news']

	def parse(self, response):
		post_links = response.xpath('//article')
		for post in post_links:
			url = post.xpath('./a[@class="blue-link"]/@href').get()
			date = post.xpath('./span/text()').get()
			yield response.follow(url, self.parse_post, cb_kwargs=dict(date=date))

		next_page = response.xpath('//li[@class="next"]/a/@href').getall()
		yield from response.follow_all(next_page, self.parse)


	def parse_post(self, response, date):
		title = response.xpath('//div[@class="article-container"]//h2/text()').get()
		description = response.xpath('//div[@class="rich-text"]//text()[normalize-space() and not(ancestor::a)]').getall()
		description = [p.strip() for p in description]
		description = ' '.join(description).strip()

		item = ItemLoader(item=CitcoItem(), response=response)
		item.default_output_processor = TakeFirst()
		item.add_value('title', title)
		item.add_value('description', description)
		item.add_value('date', date)

		return item.load_item()
