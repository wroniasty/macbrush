
from macbrush.brush import FdbTable, IfTable, Dot1dBasePort
from macbrush.agent import Agent

from twisted.internet import reactor, defer

class MacMapperDevice(Agent):

    def __init__(self, ip):
        super(MacMapperDevice, self).__init__(ip)
        self.mapper_deferred = defer.Deferred()

    def run_mapper(self):
        self.open()
        d = self.fetch([
            ("interfaces", IfTable()),
            ("fdb", FdbTable()),
            ("port1dBase", Dot1dBasePort())
        ])
        d.addCallback(self.on_mapping_done)
        return self.mapper_deferred

    def on_mapping_done(self, results):
        if results:
            print "DONE", self.ip
            self.mapper_deferred.callback(self)
        else:
            print "DONE with FAILURE"
            self.mapper_deferred.errback(self)
        self.close()



def main(argv):

    agents = [MacMapperDevice("10.1.1.12"), MacMapperDevice("10.1.2.1")]
    deferreds = map(lambda a: a.run_mapper(), agents)
    #d = agent.run_mapper()
    #d.addCallback(process_results)

    def process_results(result):
        if not result:
            print "ERROR"
        else:
            print result["port1dBase"].keys()
            for fdbEntry in result["fdb"].values():
                port1d = result["port1dBase"].get(fdbEntry["Port"], None)
                #port = result["interfaces"].get( result["port1dBase"].get(fdbEntry["Port"], None), None)
                interface = result["interfaces"].get(port1d["IfIndex"], {})
                print fdbEntry["PhysAddress"], fdbEntry["Port"], interface.get("Desc", "-")


    try:
        reactor.run()
    except KeyboardInterrupt:
        reactor.stop()

if __name__ == "__main__":
    import sys
    main(sys.argv)