# -*- coding: utf-8 -*-
import os
import logging
from datetime import datetime, timedelta

import openerp
from openerp.tools import config
from openerp import models, fields, api, exceptions, _

from .job import STATES, DONE, PENDING, FAILED, ENQUEUED, STARTED, OpenERPJobStorage, JOB_REGISTRY
from .worker import WORKER_TIMEOUT
from ..session import ConnectorSession
from .worker import watcher
from ..connector import get_openerp_module, is_module_installed

_logger = logging.getLogger(__name__)


class QueueJob(models.Model):
    """ Job status and result """
    _inherit = 'queue.job'

    @api.multi
    def set_timeout_failed(self):
        result = _('[=Job Timeout=] set to failed by system')
        self._change_job_state(FAILED, result=result)
        return True

    @api.model
    def auto_check_timeout_queue_jobs(self):
        channels_time_real = config.misc.get("options-connector", {}).get("channels_time_real") or False
        if channels_time_real:
            conf_channels_list = channels_time_real.split(",")
            for conf_list in conf_channels_list:
                channel_name, channel_time = conf_list.split(":")
                jobs = self.with_context(active_test=False).search(
                    [('state', 'in', [ENQUEUED, STARTED])],
                )
                for job in jobs:
                    if job.channel == channel_name:
                        now = datetime.now()
                        date_started = datetime.strptime(job.date_started, "%Y-%m-%d %H:%M:%S")
                        second_diff = (now-date_started).total_seconds()
                        if second_diff > int(channel_time):
                            _logger.debug("[==Job Timeout==] job %s marked failed in channel %s", job.uuid, job.channel)
                            job.set_timeout_failed()
        return True
