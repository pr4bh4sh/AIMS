from ..command_line.command_line import CommandLine as cmd
import json
import delegator


class IOS:
    def __init__(self):
        # out = cmd.execute('xcrun simctl list -j')
        result = delegator.run('xcrun simctl list -j')
        self.all = json.loads(result.out)
        self.devices = self.all['devices']
        self.runtime = self.all['runtimes']
