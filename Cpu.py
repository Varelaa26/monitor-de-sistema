import psutil as ps

class Cpu:
    def __init__(self):
        self.cpu_usage = ps.cpu_percent(interval=1)

        def get_cpu_usage(self):
            print(self.cpu_usage)