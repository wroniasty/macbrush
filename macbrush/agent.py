from pynetsnmp import netsnmp, twistedsnmp
from twisted.internet import reactor, defer

import logging
logging.basicConfig()

class Agent(netsnmp.Session):

    def __init__(self, ip, community='public', version=netsnmp.SNMP_VERSION_2c, **kw):
        super(Agent, self).__init__(peername=ip, version=version,
            community=community, community_len = len(community), **kw
        )
        self.results = {}
        self.max_bulk = 40
        self._currentTarget = None
        self._currentName = None

    def fetch(self, targets):
        self.fetch_defer = defer.Deferred()
        self.targets = targets
        self.next_target()
        twistedsnmp.updateReactor()
        return self.fetch_defer

    def next_target(self):
        if self._currentTarget:
            self.results[self._currentName] = self._currentTarget.results

        try:
            target = self.targets.pop(0)
            self._currentName, self._currentTarget = target
            self.getbulk(0, self.max_bulk, [self._currentTarget.root])
        except IndexError:

            self.fetch_defer.callback(self.results)



    def callback(self, pdu):
        results = netsnmp.getResult(pdu)
        for oid, result in results:
            if oid in self._currentTarget:
                self._currentTarget.insert(oid, result)
            else:
                self.next_target()
                return

        if not results:
            self.next_target()
        else:
            self.getbulk(0, self.max_bulk, [results[-1][0]])

    def timeout(self):
        print "TIMEOUT"
