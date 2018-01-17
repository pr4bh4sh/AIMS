from ..command_line.command_line import CommandLine as cmd
import json


class IOS:
    def __init__(self):
        out = cmd.execute('xcrun simctl list -j')
        self.all = json.loads(out.result)
        self.devices = self.all['devices']
        self.runtime = self.all['runtimes']
