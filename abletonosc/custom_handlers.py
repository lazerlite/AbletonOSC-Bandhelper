import logging
import re

def arm_track_solo_handler(self, params):
    """
    Custom handler for /arm_track_solo: disarm tracks 0-7, arm the specified track.
    This is specifically aimed at the Akai MPK261 controller's track arm buttons.
    """
    track_id = int(params[0])
    for i in range(8):
        try:
            if i != track_id:
                self.song.tracks[i].arm = False
        except Exception:
            pass
    try:
        self.song.tracks[track_id].arm = True
    except Exception:
        pass
    return ()

def parse_multi_arg_handler(self, params):
    """
    Custom handler for /parse_multi_arg: expects a single string param in the form:
    "[osc command] <arg1> <arg2> <arg3>..."
    Each arg can have a type indicator suffix: (i) for int, (f) for float, (s) for string, (b) for bool.
    If no type indicator, will infer type: int if possible, else float, else string.
    Example: "/live/track/volume 0(i) 0.8(f)" or "/live/track/name 1 Hello(s)"
    """
    logger = logging.getLogger("abletonosc")
    if not params or not isinstance(params[0], str):
        logger.warning("parse_multi_arg_handler: Expected a single string param.")
        return ()
    input_str = params[0].strip()
    if not input_str:
        logger.warning("parse_multi_arg_handler: Empty input string.")
        return ()
    # Split into command and args
    parts = input_str.split()
    if not parts:
        logger.warning("parse_multi_arg_handler: No command found in input string.")
        return ()
    target = parts[0]
    arg_strs = parts[1:]
    parsed_args = []
    type_re = re.compile(r"^(.*?)(\((i|f|s|b)\))?$")
    for arg in arg_strs:
        m = type_re.match(arg)
        if not m:
            parsed_args.append(arg)
            continue
        val, _, typ = m.groups()
        val = val.strip()
        if typ == 'i':
            try:
                parsed_args.append(int(val))
            except Exception:
                parsed_args.append(val)
        elif typ == 'f':
            try:
                parsed_args.append(float(val))
            except Exception:
                parsed_args.append(val)
        elif typ == 's':
            parsed_args.append(val)
        elif typ == 'b':
            if val.lower() in ('true', 'yes', 'on'):
                parsed_args.append(True)
            elif val.lower() in ('false', 'no', 'off'):
                parsed_args.append(False)
            elif val == '1':
                parsed_args.append(True)
            elif val == '0':
                parsed_args.append(False)
            else:
                parsed_args.append(bool(val))
        else:
            try:
                parsed_args.append(int(val))
            except Exception:
                try:
                    parsed_args.append(float(val))
                except Exception:
                    parsed_args.append(val)
    logger.info(f"parse_multi_arg_handler: Forwarding to {target} with args {parsed_args}")
    try:
        self.osc_server.send(target, tuple(parsed_args))
    except Exception as e:
        logger.error(f"parse_multi_arg_handler error: {e}")
    return ()
