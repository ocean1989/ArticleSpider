# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
import codecs
import json

from scrapy.pipelines.images import ImagesPipeline
from scrapy.exporters import JsonItemExporter

class ArticlespiderPipeline(object):
    def process_item(self, article_item, spider):
        return article_item

class JsonWithEncodingPipeline(object):
    #自定义json文件的导出
    def __init__(self):
        self.file = codecs.open('article.json','w',encoding="utf-8")
    def process_item(self, article_item, spider):
        lines = json.dumps(dict(article_item),ensure_ascii=False) + "\n"
        self.file.write(lines)
        return article_item
    def spider_close(self):
        self.file.close()

class JsonExporterPipeline(object):
    #调用scrapy提供的json_export导出json文件
    def __init__(self):
        self.file = open('articleexport.json','wb')
        self.exporter = JsonItemExporter(self.file,encoding = 'utf-8',ensure_ascii=False)
        self.exporter.start_exporting()

    def close_spider(self,spider):
        self.exporter.finish_exporting()
        self.file.close()

    def process_item(self,article_item,spider):
        self.exporter.export_item(article_item)
        return article_item

class ArticleImagePipeline(ImagesPipeline):
    def item_completed(self, results, item, info):
        for ok, vaule in results:
            image_file_path = vaule['path']
        item['front_image_path'] = image_file_path

        return item
