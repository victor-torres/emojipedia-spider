from collections import defaultdict
import scrapy


class EmojiSpider(scrapy.Spider):
    name = 'emoji'
    allowed_domains = ['emojipedia.org']
    start_urls = ['http://emojipedia.org/about']

    def parse(self, response):
        for item in response.css('#nav-categories li'):
            url = item.css('a::attr(href)').get()
            meta = {
                'category': item.css('a::text').get().strip(),
            }
            yield response.follow(
                url=url, 
                meta=meta, 
                callback=self.parse_category,
            )

    def parse_category(self, response):
        for item in response.css('.emoji-list li'):
            url = item.css('a::attr(href)').get()
            meta = {
                'category': response.meta['category'],
                'name': item.css('a::text').get().strip(),
            }
            yield response.follow(
                url=url, 
                meta=meta, 
                callback=self.parse_emoji,
            )

    def parse_emoji(self, response):
        character = response.css('.copy-paste input::attr(value)').get()
        
        aliases = response.css('.aliases li ::text').getall()[1::2]
        aliases = [a.strip() for a in aliases]

        shortcuts = defaultdict(list)
        for item in response.css('.shortcodes li'):
            shortcut = response.css('span::text').get().strip()
            for key in item.css('a::text').getall():
                shortcuts[key.strip()].append(shortcut)

        yield {
            'name': response.meta['name'],
            'category': response.meta['category'],
            'character': character,
            'aliases': aliases,
            'shortcuts': shortcuts,
        }
