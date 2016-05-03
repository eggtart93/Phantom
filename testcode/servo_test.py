import curses

if __name__ == '__main__':
    servoMgr = ServoManager()
    stdscr = curses.initscr()
    curses.noecho()
    curses.cbreak()
    stdscr.keypad(1)
    running = True
    try:
        while True:
            key = stdscr.getch()

            print curses.keyname(key)
            if curses.keyname(c) == "q":
                break
            


    except KeyboardInterrupt:
        print "Keyboard Interrupt"
    finally:
        curses.nocbreak()
        stdscr.keypad(0)
        curses.echo()
        sys.exit()
        print "Exit"
