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

    @api.model
    def auto_check_timeout_queue_jobs(self):
        _logger.info("[==Job Timeout==] Call of function.")
        channels_time_real = config.misc.get("options-connector", {}).get("channels_time_real") or False
        stop_job_runner = config.misc.get("options-connector", {}).get("stop_job_runner") or False
        if channels_time_real and not stop_job_runner:
            conf_channels_list = channels_time_real.split(",")
            _logger.info("[==Job Timeout==] Start Channels: %s", conf_channels_list)
            for conf_list in conf_channels_list:
                channel_name, channel_time = conf_list.split(":")
                jobs = self.with_context(active_test=False).search(
                    [('state', 'in', [ENQUEUED, STARTED])],
                )
                _logger.info("[==Job Timeout==] Status in [ENQUEUED, STARTED], Len: %s job, Channel: %s" % (len(jobs), channel_name))
                for job in jobs:
                    if job.channel == channel_name:
                        now = datetime.now()
                        str_now = datetime.strftime(now, "%Y-%m-%d %H:%M:%S")
                        check_date = job.date_enqueued
                        if job.state == STARTED:
                            check_date = job.date_started

                        if check_date:
                            date_started = datetime.strptime(check_date, "%Y-%m-%d %H:%M:%S")
                            second_diff = (now-date_started).total_seconds()
                            if second_diff > int(channel_time):
                                if job.retry < job.max_retries:
                                    job.retry = job.retry + 1
                                    job._change_job_state(PENDING, result=result)
                                else:
                                    result = _('Job Timeout more than %s s.' % channel_time)
                                    job._change_job_state(FAILED, result=result)
                                    _logger.info("[==Job Timeout==] job %s marked failed in channel %s (diff[%s] / channel[%s])", job.uuid, job.channel, second_diff, channel_time)
                            # else:
                            #    if job.state == ENQUEUED:
                            #        job._change_job_state(PENDING, result=result)
                            #        _logger.info("[==Job Timeout==] job %s marked pending in channel %s HOOK TRIGGER!!! (diff[%s] / channel[%s])", job.uuid, job.channel, second_diff, channel_time)
                            #    elif job.state == STARTED:
                            #        _logger.info("[==Job Timeout==] job %s starting in channel %s WAITING!!! (diff[%s] / channel[%s])", job.uuid, job.channel, second_diff, channel_time)
                        #else:
                        #    job._change_job_state(PENDING, result=result)
                        #    _logger.info("[==Job Timeout==] job %s ERROR!! Please check date_created IS NULL!!! ", job.uuid, job.channel)



        return True
