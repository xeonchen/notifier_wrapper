#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import configparser
import os
import sys

NOTIFIERS = {}

def register_notifier(cls):
    NOTIFIERS[cls.NAME] = cls
    return cls

class Notifier(object):
    @classmethod
    def create(cls, **kw):
        return cls(**kw)

    def run(self):
        raise NotImplementedError

    def parse_message(self):
        for i, arg in enumerate(sys.argv):
            if arg == "-message":
                return sys.argv[i + 1]
        return "<empty message>"

@register_notifier
class IftttNotifier(Notifier):
    NAME = "ifttt"
    IFTTT_URL = "https://maker.ifttt.com/trigger/{event}/with/key/{key}"

    def __init__(self, key, event):
        super(IftttNotifier, self).__init__()
        self._message = self.parse_message()
        self._url = IftttNotifier.IFTTT_URL.format(key=key, event=event)

    def run(self):
        import urllib.parse
        import urllib.request

        post_fields = urllib.parse.urlencode({ "value1": self._message }).encode()
        request = urllib.request.Request(self._url, post_fields)
        with urllib.request.urlopen(request) as f:
            _msg = f.read().decode()
            return f.getcode() == 200

@register_notifier
class TerminalNotifier(Notifier):
    NAME = "terminal-notifier"

    def __init__(self, path):
        super(TerminalNotifier, self).__init__()
        self._path = path

    def run(self):
        import subprocess
        return subprocess.call([self._path] + sys.argv[1:]) == 0

def main():
    config = configparser.ConfigParser()
    config.read(os.path.expanduser("~/.notifier_wrapper"))
    for name in config.sections():
        if name in NOTIFIERS:
            notifier = NOTIFIERS[name].create(**config[name])
            notifier.run()

if __name__ == '__main__':
    main()