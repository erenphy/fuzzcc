import pytermgui as ptg
from pytermgui import Container, Label, Splitter, Button, InputField, Window
import time
from sys import exit
from datetime import datetime
from globalVar import TABLEINFO

# TODO 移动到 globalVar 里头去
START_TIME = datetime.now().timestamp()
LAST_NEW_PATH_TIME = None
LAST_CRASH_TIME = None
TOTAL_PATHS = 0
UNIQ_CRASHES = 0

def macro_time(start) -> str:
    if start == "None":
        return "none seen yet"
    usage_time = datetime.now() - datetime.fromtimestamp(float(start))
    return f"{usage_time.days} days, {usage_time.seconds // 3600} hrs, {usage_time.seconds // 60} min, {usage_time.seconds % 60} sec"

ptg.tim.define("!time", macro_time)

def exitting(manager, window, thread_list):
    for thread in thread_list:
        thread.stop()
    window.close()
    manager.stop()
    # global EXIT_FLAG
    # EXIT_FLAG = True
    exit(1)


def start_tui(thread_list):
    with ptg.WindowManager() as manager:
        window = (
            Window( 
                Container(
                    Label("[bold accent]process timing"),
                    "",
                    InputField(f"[!time]{START_TIME}", prompt="run time: "),
                    InputField(f"[!time]{LAST_NEW_PATH_TIME}", prompt="last new path: "),
                    InputField(f"[!time]{LAST_CRASH_TIME}", prompt="last uniq crash: "),
                    "",
                ),
                Container(
                    Label("[bold accent]overall results"),
                    "",
                    InputField(f"{TOTAL_PATHS}", prompt="total paths: "),
                    InputField(f"{UNIQ_CRASHES}", prompt="uniq crashes: "),
                    "",
                ),
                TABLEINFO,
                "",
                ["Exit", lambda *_: exitting(manager, window, thread_list)],
                width=80,
                box="DOUBLE",
            )
            .set_title("[110 bold]fuzzcc")
            .center()
        )

        manager.add(window)