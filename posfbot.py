#!/usr/bin/python

import configparser
from posf import posf
from posf import POSFRedis
from posf import POSFBot

posf  = POSFBot.POSFBot(POSFBot.read_ini())
#posf.get_mentions()
posf.get_stream_mentions()
