# coding: utf-8
from __future__ import unicode_literals, absolute_import
import logging
import uuid

from django.db import models
from django.core.urlresolvers import reverse
from common import wechat_client
from remind.utils import nature_time

logger = logging.getLogger(__name__)


class Remind(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    time = models.DateTimeField('提醒时间')
    desc = models.TextField('原始描述', default='', blank=True, null=True)
    event = models.TextField('提醒事件', default='', blank=True, null=True)
    media_url = models.URLField('语音', max_length=320, blank=True, null=True)
    repeat = models.CharField('重复', max_length=128, blank=True, null=True)
    owner = models.ForeignKey('wxhook.User', verbose_name='创建者',
                              related_name='reminds_created')
    subscribers = models.ManyToManyField('wxhook.User', verbose_name='订阅者',
                                         related_name='reminds_subscribed')
    status = models.CharField('状态', max_length=10, default='pending',
                              choices=(('pending', 'pending'),
                                       ('running', 'running'),
                                       ('done', 'done')))

    class Meta:
        ordering = ["-time"]
        db_table = 'remind'

    def nature_time(self):
        return nature_time(self.time)

    def notify_users(self):
        logger.info('Sending notification to user %s', self.owner.nickname)
        wechat_client.message.send_template(
            user_id=self.owner_id,
            template_id='OHwCU_UbAW3XoaLJimwMzbc7RFQMCEX0OBZ4PvsDTuk',
            url=self.get_absolute_url(),
            top_color='#459ae9',
            data={
                   "first": {
                       "value": '\U0001F552%s\n' % self.event if self.event else \
                           self.time.strftime('%Y/%m/%d %H:%M到了'.encode('utf-8')).decode('utf-8'),
                       "color": "#459ae9"
                   },
                   "keyword1": {
                       "value": self.time.strftime('%Y/%m/%d %H:%M'),
                   },
                   "keyword2": {
                       "value": self.desc
                   },
                   # "remark": {
                   #     "value": "欢迎再次购买！",
                   #     "color": "#459ae9"
                   # }
            },
        )

    def get_absolute_url(self):
        return reverse('remind_detail', kwargs={'pk': self.pk})

    def __unicode__(self):
        return '%s: %s' % (self.owner.nickname, self.desc)
