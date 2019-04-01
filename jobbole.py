# -*- coding: utf-8 -*-
import scrapy
import re
from scrapy.http import Request
from urllib import parse
from ArticleSpider.items import JobBoleArticleItem #同级函数调用可以直接import
from ArticleSpider.utils.common import get_md5
import datetime

class JobboleSpider(scrapy.Spider):
    name = 'jobbole'
    allowed_domains = ['blog.jobbole.com']
    start_urls = ['http://blog.jobbole.com/all-posts/']

    def parse(self,response):
        # 获取文章列表页中的文章url并交给scrapy下载后并进行解析
        # 获取下一页url并交给scrapy下载，下载完成后交给prase
        post_nodes = response.css('#archive .floated-thumb .post-thumb a')
        for post_node in post_nodes:
            img_url = post_node.css('img::attr(src)').extract_first('')
            post_url = post_node.css('::attr(href)').extract_first('')
            yield Request(url=parse.urljoin(response.url,post_url),meta={'front_image_url':img_url},callback=self.parse_detail)

        #提取下一页并交给scrapy下载
        next_url = response.css('.next.page-numbers::attr(href)').extract_first()
        if next_url:
            yield Request(url=parse.urljoin(response.url,next_url), callback=self.parse)


    def parse_detail(self, response):
        article_item = JobBoleArticleItem()
        front_image_url = response.meta.get('front_image_url','') #文章封面图
        title = response.css('.entry-header h1::text').extract()[0]
        create_date = response.css('.entry-meta-hide-on-mobile::text').extract()[0].strip().replace(' ·', '')
        try:
            create_date = datetime.datetime.strptime(create_date,"%Y/%m/%d").date()
        except Exception as e:
            create_date = datetime.datetime.now.date()
        praise_nums =  response.css('.post-adds h10::text').extract()[0]
        # fav_nums = response.css('.post-adds .bookmark-btn::text').extract()[0]
        # match_re = re.match('.*?(\d+).*',fav_nums).group(1)
        # if match_re:
        #     fav_nums = int(match_re)
        # else:
        #     fav_nums = 0
        # comment_nums = response.css('a[href="#article-comment"] span::text').extract()[0]
        # match_re = re.match('.*?(\d+).*',comment_nums).group(1)
        # if match_re:
        #     comment_nums = int(match_re)
        # else:
        #     comment_nums = 0
        content = response.css('.entry').extract()
        tag_list = response.css('.entry-meta-hide-on-mobile a::text').extract()
        tag_list = [element for element in tag_list if not element.strip().endswith('评论')]
        tags = ','.join(tag_list)

        article_item['url_object_id'] = get_md5(response.url)
        article_item['title'] = title
        article_item['url'] = response.url
        article_item['create_date'] = create_date
        article_item['front_image_url'] = [front_image_url]
        article_item['praise_nums'] = praise_nums
        # article_item['comment_nums'] = comment_nums
        # article_item['fav_nums'] = fav_nums
        article_item['tags'] = tags
        article_item['content'] = content

        yield article_item
