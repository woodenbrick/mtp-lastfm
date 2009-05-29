#!/usr/bin/env python
import os
import logging

def new_logger(name):
    filename = os.path.join(os.environ['HOME'], ".mtp-lastfm", "debugging.log")
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)
    ch = logging.FileHandler(filename)
    st = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)
    st.setLevel(logging.DEBUG)
    formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(name)s - %(message)s")
    ch.setFormatter(formatter)
    st.setFormatter(formatter)
    logger.addHandler(ch)
    logger.addHandler(st)
    return logger