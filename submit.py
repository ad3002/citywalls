#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#@created: 21.03.2016
#@author: Aleksey Komissarov
#@contact: ad3002@gmail.com


if __name__ == '__main__':

    settings = {
        "houses_file": "houses.txt",
    }

    with open(settings["houses_file"]) as fh:
    	for line in fh:
    		line = line.strip().split("\t")

    		