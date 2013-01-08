
from macbrush.brush import FdbTable, IfTable
from macbrush.agent import Agent

from twisted.internet import reactor

def main(argv):

    agent = Agent("10.1.1.12")
    #BRIDGE-MIB::dot1dBasePortIfIndex.1 !!!
    #BRIDGE-MIB::dot1dBasePortTable
    agent.open()
    d = agent.fetch([
                       ("interfaces", IfTable()),
                       ("fdb", FdbTable())
                    ])


    def success(result):
        print result["interfaces"].keys()
        for fdbEntry in result["fdb"].values():
            #port = result["interfaces"][fdbEntry["Port"]]
            print fdbEntry["PhysAddress"], fdbEntry["Port"]
        reactor.stop()

    def error(reason):
        print "ERROR"
        reactor.stop()

    d.addErrback(error)
    d.addCallback(success)
    reactor.run()

if __name__ == "__main__":
    import sys
    main(sys.argv)