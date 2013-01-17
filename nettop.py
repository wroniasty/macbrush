
from macbrush.brush import FdbTable, IfTable, Dot1dBasePort
from macbrush.agent import Agent

from twisted.internet import reactor, defer, task
from collections import defaultdict
import time
import curses, curses.panel

class CasaStatDevice(Agent):

    def __init__(self, ip, interval=3):
        super(CasaStatDevice, self).__init__(ip)
        self.target_ip = ip
        self.poll_interval = interval
        self.data = {}

    def run(self):
        self.open()
        d = self.fetch([("interfaces", IfTable()), ])
        d.addCallback(self.on_done)
        self.mapper_deferred = defer.Deferred()
        self.mapper_deferred.addCallback(self.process_results)
        return self.mapper_deferred

    def process_results(self, results):
        #print results['interfaces']
        if results:
            for index, iff in results['interfaces'].items():

                if_data = self.data.get(index, iff)
                ts = time.time()
                if_data['history'] = if_data.get('history', { 'InOctets' : [], 'OutOctets' : [], 'InUcastPkts' : [], 'OutUcastPkts' : [], 'InErrors' : [], 'OutErrors' : []} )
                if_data['rate'] = if_data.get('rate', defaultdict(lambda : 0))
                if_data['bitrate'] = if_data.get('bitrate', defaultdict(lambda : 0))

                def calculate_rate(H1, H2):
                    t1, v1 = H1
                    t2, v2 = H2
                    return max((v2 - v1) / (t2 - t1), 0)

                for stat_name in if_data['history']:
                    if_data['history'][stat_name].append((ts, iff.get(stat_name, 0)))
                    H = if_data['history'][stat_name]
                    if len(H) >= 2:
                        if_data['rate'][stat_name] = calculate_rate(H[-1], H[-2])
                        if_data['bitrate'][stat_name] = if_data['rate'][stat_name] * 8;

                #print index, if_data['Descr'], if_data['Speed'], if_data['rate']['InOctets']
                self.data[index] = if_data

        reactor.callLater(self.poll_interval, self.run)

    def on_done(self, results):
        try:
            if results:
                self.mapper_deferred.callback( results )
            else:
                self.mapper_deferred.errback(self)
        except Exception, e:
            self.mapper_deferred.errback( e )

class CursesStdIO:
    """fake fd to be registered as a reader with the twisted reactor.
       Curses classes needing input should extend this"""

    def fileno(self):
        """ We want to select on FD 0 """
        return 0

    def doRead(self):
        """called when input is ready"""

    def logPrefix(self): return 'CursesClient'

class Screen(CursesStdIO):
    def __init__(self, stdscr):
        self.timer = 0
        self.stdscr = stdscr

        # set screen attributes
        self.stdscr.nodelay(1) # this is used to make input calls non-blocking
        curses.cbreak()
        self.stdscr.keypad(1)
        curses.curs_set(0)     # no annoying mouse cursor

        self.rows, self.cols = self.stdscr.getmaxyx()
        curses.start_color()

        # create color pair's 1 and 2
        curses.init_pair(1, curses.COLOR_WHITE, curses.COLOR_BLACK)
        curses.init_pair(2, curses.COLOR_CYAN, curses.COLOR_BLACK)
        curses.init_pair(3, curses.COLOR_BLACK, curses.COLOR_CYAN)

        self.panels = defaultdict(lambda :curses.newwin(self.rows-2, self.cols-2, 1, 1))

        self.stdscr.clear()
        self.current_type = 6

    def update(self, data):
        self.rows, self.cols = self.stdscr.getmaxyx()
        self.stdscr.clear()

        self.stdscr.box()

        self.available_types = [t for t in set([ t["Type"] for t in data.values() ]) ]
        self.stdscr.addstr(self.rows-1, 1, `self.available_types`, curses.color_pair(1))

        def ifOfType(data, ifType):
            if not isinstance(ifType, list): ifType = [ ifType ]
            items = [ item for item in data.values() if item["Type"] in ifType]
            items.sort( lambda x,y: x["Index"] - y["Index"])
            return items

        def shortenText(txt, l):
            if len(txt) > l:
                txt = txt[0:l/2 - 2] + "...." + txt[-l/2 + 2:]
            return txt

        if 129 in self.available_types:
            win = self.panels[129]
            for idx, iff in enumerate(ifOfType(data,129)[:self.rows-4]):
                row = idx + 1
                col_off = 5
                win.addstr(row, col_off + 0, shortenText(iff["Descr"],16), curses.color_pair(1) )
                if iff["AdminStatus"] == 1:
                    win.addstr(row, col_off + 18, "up", curses.color_pair(1) )
                if (iff["bitrate"]["InOctets"] > 0):
                    win.addstr(row, col_off + 23, "{: >3.1f}M".format(iff["bitrate"]["InOctets"] / 1000 / 1000), curses.color_pair(1) )
                    win.addstr(row, col_off + 43, "{: >3d}%".format(int(iff['bitrate']["InOctets"] / iff['Speed'] * 100)), curses.color_pair(1) )

                win.addstr(row, col_off + 29, "{: >5.1f}e".format(iff["rate"]["InErrors"]), curses.color_pair(1) )

        if 128 in self.available_types:
            win = self.panels[128]
            for idx, iff in enumerate(ifOfType(data,128)[:self.rows-4]):
                row = idx + 1
                col_off = 2
                win.addstr(row, col_off + 0, shortenText(iff["Descr"],16), curses.color_pair(1) )
                if iff["AdminStatus"] == 1:
                   win.addstr(row, col_off + 18, "up", curses.color_pair(1) )
                if (iff["bitrate"]["OutOctets"] > 0):
                    win.addstr(row, col_off + 23, "{: >3.1f}M".format(iff["bitrate"]["OutOctets"] / 1000 / 1000), curses.color_pair(1) )
                    win.addstr(row, col_off + 43, "{: >3d}%".format(int(iff['bitrate']["OutOctets"] / iff['Speed'] * 100)), curses.color_pair(1) )

        if 6 in self.available_types:
            win = self.panels[6]
            for idx, iff in enumerate(ifOfType(data,6)[:self.rows-4]):
                row = idx + 1
                col_off = 2
                win.addstr(row, col_off + 0, shortenText(iff["Descr"],16), curses.color_pair(1) )
                if iff["AdminStatus"] == 1:
                    win.addstr(row, col_off + 18, "up", curses.color_pair(1) )

                win.addstr(row, col_off + 23, "{: >3.1f}M    ".format(iff["bitrate"]["OutOctets"] / 1000 / 1000), curses.color_pair(1) )
                win.addstr(row, col_off + 33, "{: >3.1f}M    ".format(iff["bitrate"]["InOctets"] / 1000 / 1000), curses.color_pair(1) )

        self.panels[self.current_type].overwrite(self.stdscr)
            #self.stdscr.addstr(idx+1, 0, `iff`, curses.color_pair(1))

        self.type_names = {
            6  : "Ethernet",
            128 : "Downstream",
            129 : "Upstream"
        }
        col = 1
        for if_type in self.type_names.keys():
            name =  self.type_names.get(if_type, None)
            if not name: continue
            if if_type == self.current_type: clr = 3
            else: clr = 2
            self.stdscr.addstr(1, col, name, curses.color_pair(clr))
            col += len(name) + 2

        self.stdscr.refresh()

    def connectionLost(self, reason):
        self.close()


    def redisplayLines(self):
        """ method for redisplaying lines
            based on internal list of lines """

        self.stdscr.clear()
        self.paintStatus(self.statusText)
        i = 0
        index = len(self.lines) - 1
        while i < (self.rows - 3) and index >= 0:
            self.stdscr.addstr(self.rows - 3 - i, 0, self.lines[index],
                curses.color_pair(2))
            i = i + 1
            index = index - 1
        self.stdscr.refresh()

    def paintStatus(self, text):
        if len(text) > self.cols: text = text[:self.cols]
        self.stdscr.addstr(self.rows-2,0,text + ' ' * (self.cols-len(text)),
            curses.color_pair(1))
        # move cursor to input line
        self.stdscr.move(self.rows-1, self.cols-1)

    def doRead(self):
        """ Input is ready! """
        curses.noecho()
        self.timer = self.timer + 1
        c = self.stdscr.getch() # read a character

        Ks = self.type_names.keys()
        idx = Ks.index(self.current_type)
        if c == curses.KEY_LEFT:
            idx = idx - 1
            if idx < 0: idx = len(Ks) - 1
        elif c == curses.KEY_RIGHT:
            idx = idx + 1
            if idx >= len(Ks): idx = 0
        self.current_type = Ks[idx]


        #if c == curses.KEY_BACKSPACE:
        #    self.searchText = self.searchText[:-1]

        #elif c == curses.KEY_ENTER or c == 10:
        #    self.addLine(self.searchText)
        #    self.stdscr.refresh()

        #else:
        #    if len(self.searchText) == self.cols-2: return
        #    self.searchText = self.searchText + chr(c)

        #self.stdscr.addstr(self.rows-1, 0,
        #    self.searchText + (' ' * (
        #        self.cols-len(self.searchText)-2)))
        #self.stdscr.move(self.rows-1, len(self.searchText))
        #self.paintStatus(self.statusText + ' %d' % len(self.searchText))
        self.stdscr.refresh()

    def close(self):
        """ clean up """

        curses.nocbreak()
        self.stdscr.keypad(0)
        curses.echo()
        curses.endwin()

def main(argv):


    topper = CasaStatDevice("10.1.2.1")
    topper.run()

    stdscr = curses.initscr()
    screen = Screen(stdscr)
    def update_display(topper):
        screen.update(topper.data)
    reactor.addReader(screen)
    display_task = task.LoopingCall ( update_display, topper )
    display_task.start(0.5)

    try:
        reactor.run()
    except KeyboardInterrupt:
        reactor.stop()
    finally:
        pass #screen.close()

if __name__ == "__main__":
    import sys
    main(sys.argv)