#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun May 16 23:48:54 2021

@author: ilsiren
"""

import pickle

with open('./bank/0_number', 'wb') as f:
    pickle.dump(0, f)