import logging

from django.shortcuts import render
from django.http import HttpResponse
from django.core.paginator import Paginator, EmptyPage
from django.views import View

# Create your views here.
from utils.json_func import to_json_data
from . import models
from . import constants

# 导入日志器
logger = logging.getLogger('django')


class NewsIndexView(View):
    """
    /
    首页
    """
    def get(self, request):
        # 获取所有tags 动态展示在页面
        tags = models.Tag.objects.only('id', 'name').filter(is_delete=False)
        return render(request, 'news/index.html', locals())


class NewsListView(View):
    """
    /news/
    """
    def get(self, request):

        try:
            tag_id = int(request.GET.get('tag_id', 0))
        except Exception as e:
            logger.error("标签错误：\n{}".format(e))
            tag_id = 0

        try:
            pg = int(request.GET.get('page', 1))
        except Exception as e:
            logger.error("当前页数错误：\n{}".format(e))
            pg = 1

        news = models.News.objects.select_related('tag', 'author').only('id', 'title', 'digest', 'update_time', 'image_url', 'tag__name', 'author__username')
        news_list = news.filter(is_delete=False, tag_id=tag_id) or news.filter(is_delete=False)

        paginator = Paginator(news_list, constants.PER_PAGE_NEWS_COUNT)

        try:
            news_info = paginator.page(pg)
        except EmptyPage:
            # 若用户访问的页数大于实际页数，则返回最后一页数据
            logging.info("用户访问的页数大于总页数。")
            news_info = paginator.page(paginator.num_pages)

        news_info_list = []
        for p in news_info:
            news_info_list.append({
                'id': p.id,
                'title': p.title,
                'digest': p.digest,
                'update_time': p.update_time.strftime('%Y年%m月%d日 %H:%M'),
                'image_url': p.image_url,
                'tag_name': p.tag.name,
                'author': p.author.username
            })

        data = {
            'total_pages': paginator.num_pages,
            'news': news_info_list
        }
        return to_json_data(data=data)
