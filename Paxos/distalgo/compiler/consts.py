
SENT_PATTERN_VARNAME = "_sent_patterns"
EVENT_PATTERN_VARNAME = "_event_patterns"
LABEL_EVENTS_VARNAME = "_label_events"
EVENT_PROC_FUNNAME = "_process_event"

TIMER_VARNAME = "__await_timer_"
TIMEOUT_VARNAME = "_timeout"
TIMELEFT_VARNAME = "_timeleft"
TEMP_VARNAME = "__temp_"

LOGICAL_TIMESTAMP_VARNAME = "_timestamp"
MSG_SRCNODE_VARNAME = "_source"

SENDMSG_FUNNAME = "send"
RECEIVED_FUNNAME = "received"
SENT_FUNNAME = "sent"

DISTALGO_BASE_CLASSNAME = "DistProcess"

BUILTIN_FUNCS = {
    "work",
    "send",
    "receive",
    "output",
    "spawn",
    "logical_clock",
    "incr_logical_clock",
    "start_timers",
    "stop_timers",
    "report_times",
    "report_mem",
    EVENT_PROC_FUNNAME
    }

BUILTIN_VARS = {
    EVENT_PATTERN_VARNAME
    }

_use_set_for_queue = False
def set_use_set_for_queue(b):
    global _use_set_for_queue
    _use_set_for_queue = b

def is_use_set_for_queue():
    return _use_set_for_queue
