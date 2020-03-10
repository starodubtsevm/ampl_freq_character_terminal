import random
import curses
from curses import textpad


def main(stdscr):
    # initial settings
    curses.curs_set(0)
    stdscr.nodelay(1)
    stdscr.timeout(100)

    # create a game box
    sy, sx = stdscr.getmaxyx()
    box = [[3,3], [sy-3, sx-3]]  # [[ul_y, ul_x], [dr_y, dr_x]]
    textpad.rectangle(stdscr, box[0][0], box[0][1], box[1][0], box[1][1])


    # print score
    score = 0
    score_text = "Score: {}".format(score)
    stdscr.addstr(1, sx//2 - len(score_text)//2, score_text)

    while 1:
        # non-blocking input
        key = stdscr.getch()
        stdscr.addstr(1,3,str(sy)) #46
        stdscr.addstr(2,3,str(sx)) #183
        fmin = 150
        fstep = 50
        fmax = 1500
        df = fmax - fmin
        n = df // fstep
        count = 0
        
        for y in range(sy-10,10,-1):
            for x in range (10,sx-10,5):
                stdscr.addstr(y,x,'&')
                if y == (sy-10):
                    stdscr.addstr(sy-9, x, "-----")
                    stdscr.addstr(sy-8, x, str(count*fstep+fmin))
                count+=1

curses.wrapper(main)

