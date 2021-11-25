import argparse
import socket
import json
import time
import copy
import math
import random

import httpimport

with httpimport.github_repo('jewzaam', 'metrics-utility', 'utility', 'main'):
    import utility

PHD_STATE = ""
PHD_SETTLING = False
PHD_RMS_SAMPLES = 15
PHD_RMS_DATA = {}
PIXEL_SCALE = 0
JRPC_CALLBACKS = {}

GLOBAL_LABELS = None

DEBUG = False

def debug(message):
    # simply so I can easily control debug messages
    if DEBUG:
        print(message)

def callback_requestPixelScale(data):
    global GLOBAL_LABELS, PIXEL_SCALE
    PIXEL_SCALE = data["result"]
    utility.set("phd2_pixel_scale", PIXEL_SCALE, GLOBAL_LABELS)
    if "id" in data:
        # unregister the callback, work is done
        JRPC_CALLBACKS.pop(data["id"])

def requestPixelScale(s):
    global JRPC_CALLBACKS
    # socket exception handling done in main loop
    # send request
    request_id = random.randint(1,50000)
    request = {
        "method": "get_pixel_scale",
        "id": request_id,
    }
    JRPC_CALLBACKS[request_id] = callback_requestPixelScale
    s.sendall((json.dumps(request) + "\r\n").encode('utf-8'))
            
def makeLabels(data, label_keys):
    labels = {}

    for label_key in label_keys:
        if label_key in data:
            labels[label_key] = data[label_key]
    
    return labels

def createEventMetrics(data, labels, metric_keys):
    for metric_key in metric_keys:
        if metric_key in data:
            value = data[metric_key]
            if isinstance(value, bool):
                if value == True:
                    value = 1
                else:
                    value = 0
            utility.set(f"phd2_{data['Event']}_{metric_key}", data[metric_key], labels)

def handleEvent(s, data):
    global PHD_STATE, PHD_RMS_SAMPLES, GLOBAL_LABELS, PHD_RMS_DATA, PHD_SETTLING

    if 'Event' not in data:
        return
    
    event = data['Event']

    # all possible states https://github.com/OpenPHDGuiding/phd2/wiki/EventMonitoring#appstate
    app_states = [
        "Stopped",      # PHD is idle
        "Selected",     # A star is selected but PHD is neither looping exposures, calibrating, or guiding
        "Calibrating",  # PHD is calibrating
        "Guiding",      # PHD is guiding
        "LostLock",     # PHD is guiding, but the frame was dropped
        "Paused",       # PHD is paused
        "Looping",      # PHD is looping exposures
    ]
    # use global PHD_STATE to get an updated state, which is then updated at the end of the function
    
    if event in ["Version", "AppState"]:
        # initialze global labels
        GLOBAL_LABELS = {
            "host": data["Host"].lower(),
            "inst": data["Inst"],
        }

    # update state based on event
    if event in ["LoopingExposuresStopped"]:
        PHD_STATE="Stopped"
        # reset RMS data
        PHD_RMS_DATA = {}
    elif event in ["LockPositionSet"]:
        PHD_STATE="Selected"
    elif event in ["StartCalibration", "Calibrating"]:
        PHD_STATE="Calibrating"
    elif event in ["GuideStep"]:
        PHD_STATE="Guiding"
    elif event in ["StarLost"]:
        PHD_STATE="LostLock"
    elif event in ["Paused"]:
        PHD_STATE="Paused"
    elif event in ["LoopingExposures"]:
        PHD_STATE="Looping"
    elif event == "AppState" and "State" in data:
        PHD_STATE = data["State"]
        PHD_SETTLING=False
    elif event in ["SettleBegin", "Settling"]:
        PHD_SETTLING=True
    elif event in ["SettleDone"]:
        PHD_SETTLING=False

    for state in app_states:
        value = int(PHD_STATE == state)
        l = copy.deepcopy(GLOBAL_LABELS)
        l.update({'status': state})
        utility.set("phd2_status", value, l)
    
    # set settling status, which can be true while other states are true
    value = (PHD_SETTLING == True)
    l = copy.deepcopy(GLOBAL_LABELS)
    l.update({'status': "Settling"})
    utility.set("phd2_status", value, l)

    # did equipment change? get pixel scale! uses callback so reading is handled in main loop
    if event in ["AppState", "ConfigurationChange"]:
        requestPixelScale(s)

    if event in ["LockPositionSet", "StarSelected"]:
        createEventMetrics(data, GLOBAL_LABELS, ["X", "Y"])
    elif event == "Calibrating":
        l=copy.deepcopy(GLOBAL_LABELS)
        l.update(makeLabels(data, ["dir"]))
        createEventMetrics(data, l, ["dist", "dx", "dy", "step"])
    elif event == "Settling":
        createEventMetrics(data, GLOBAL_LABELS, ["Distance", "Time", "SettleTime", "StarLocked"])
    elif event == "SettleDone":
        # TODO consider if should flip "Status" from 0==success to 1==success....
        createEventMetrics(data, GLOBAL_LABELS, ["Status", "TotalFrames", "DroppedFrames"])
    elif event == "StarLost":
        createEventMetrics(data, GLOBAL_LABELS, ["StarMass", "SNR", "AvgDist", "ErrorCode"])
    elif event == "GuideStep":
        # general metrics
        createEventMetrics(data, GLOBAL_LABELS, ["dx", "dy", "RADistanceRaw", "DECDistanceRaw", "RADistanceGuide", "DECDistanceGuide", "StarMass", "SNR", "HFD", "AvgDist", "ErrorCode"])

        # RA pulse metric
        l_ra = copy.deepcopy(GLOBAL_LABELS)
        l_ra.update(makeLabels(data, ["RADirection", "RALimited"]))
        createEventMetrics(data, l_ra, ["RADuration"])

        # DEC pulse metric
        l_dec = copy.deepcopy(GLOBAL_LABELS)
        l_dec.update(makeLabels(data, ["DECDirection", "DecLimited"]))
        createEventMetrics(data, l_dec, ["DECDuration"])

        # skip RMS if settling
        if PHD_SETTLING == False:
            # collect data for RMS
            rms_keys = ["DECDistanceRaw", "DECDistanceGuide", "RADistanceRaw", "RADistanceGuide"]
            calculate_rms = True
            for key in rms_keys:
                if key not in data:
                    calculate_rms = False
                    continue
                if key not in PHD_RMS_DATA:
                    PHD_RMS_DATA[key] = []
                if len(PHD_RMS_DATA[key]) >= PHD_RMS_SAMPLES:
                    PHD_RMS_DATA[key].pop(0)
                else:
                    calculate_rms = False
                PHD_RMS_DATA[key].append(data[key])

            if calculate_rms == True:
                # fabricate data for "total" as hypotenuse of each DEC/RA {Raw, Guide} tuple
                PHD_RMS_DATA["TotalDistanceRaw"] = []
                PHD_RMS_DATA["TotalDistanceGuide"] = []
                for i in range(0, PHD_RMS_SAMPLES):
                    PHD_RMS_DATA["TotalDistanceRaw"].append(
                        math.sqrt(
                            math.pow(PHD_RMS_DATA["DECDistanceRaw"][i],2)
                            + math.pow(PHD_RMS_DATA["RADistanceRaw"][i],2)
                        )
                    )
                    PHD_RMS_DATA["TotalDistanceGuide"].append(
                        math.sqrt(
                            math.pow(PHD_RMS_DATA["DECDistanceGuide"][i],2)
                            + math.pow(PHD_RMS_DATA["RADistanceGuide"][i],2)
                        )
                    )

                # do the math for RMS and export metrics
                for key in PHD_RMS_DATA.keys():
                    rms_sum_of_squares = 0
                    # do the sum of squares bit
                    for value in PHD_RMS_DATA[key]:
                        rms_sum_of_squares += math.pow(value, 2)
                    # then divide and sqrt
                    rms_px = math.sqrt(rms_sum_of_squares / PHD_RMS_SAMPLES)
                    utility.set("phd2_rms", rms_px, {"source": key, "scale": "px"})
                
                    # calculate for arcsec if we have pixel scale
                    if PIXEL_SCALE > 0:
                        rms_arcsec = rms_px * PIXEL_SCALE
                        utility.set("phd2_rms", rms_arcsec, {"source": key, "scale": "arcsec"})

    elif event == "GuidingDithered":
        createEventMetrics(data, GLOBAL_LABELS, ["dx", "dy"])

    utility.inc(f"phd2_{event}", GLOBAL_LABELS)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Export PHD2 events as prometheus metrics.")
    parser.add_argument("--phd2port", type=int, help="the port PHD2 is exposing events on, default: 4400")
    parser.add_argument("--phd2host", type=str, help="the host PHD2 is exposing events on, default: 127.0.0.1")
    parser.add_argument("--port", type=int, help="the port to export metrics on, default: 9753")
    parser.add_argument("--rms_samples", type=int, help="number of samples used to calculate RMS, default: 10")

    # treat args parsed as a dictionary
    args = vars(parser.parse_args())

    phd2port = 4400
    if "phd2port" in args and args["phd2port"]:
        phd2port = args["phd2port"]
    phd2host = "127.0.0.1"
    if "phd2host" in args and args["phd2host"]:
        phd2host = args["phd2host"]
    port = 9753
    if "port" in args and args["port"]:
        port = args["port"]
    rms_samples = 10
    if "rms_samples" in args and args["rms_samples"]:
        rms_samples = args["rms_samples"]
    
    PHD_RMS_SAMPLES = rms_samples

    # Start up the server to expose the metrics.
    utility.metrics(port)

    print_connect_error = True

    while True:
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.connect((phd2host,phd2port))
                print_connect_error = True
                s.setblocking(0)
                s.settimeout(2.0)
                while True:
                    try:
                        raw = s.recv(1024)
                        if len(raw) == 0:
                            # empty response without a timeout, server is down
                            # break the loop, which triggers a reconnect
                            break
                        # keep a count (inc / total) for everything
                        if GLOBAL_LABELS is not None:
                            utility.inc("phd2", GLOBAL_LABELS)
                    except socket.timeout:
                        # this is fine, just nothing to read.  PHD2 idle.  No metric so it's not confused as an error
                        # keep a count (inc / total) for everything
                        if GLOBAL_LABELS is not None:
                            utility.inc("phd2", GLOBAL_LABELS)
                        continue
                    except Exception as e:
                        # non-timeout error, this is bad.  break the loop, which will trigger reconnect
                        utility.inc("phd2_error", {"type": type(e).__name__})
                        print(e)
                        break
                    lines = raw.decode()
                    for line in lines.split('\r\n'):
                        if len(line) > 0:
                            data = json.loads(line)
                            if "Event" in data:
                                handleEvent(s, data)
                            elif "jsonrpc" in data and "id" in data:
                                id = data["id"]
                                JRPC_CALLBACKS[id](data)
        except socket.error as e:
            utility.inc("phd2_error", {"type": type(e).__name__})
            # 10061 is connection refused.  don't log these, it's spammy
            if e.errno == 10061:
                if print_connect_error == True:
                    print("Failed to connect to PHD2.  Server is down or unreachable.  Retrying silently...")
                    print_connect_error = False
            else:
                print(e)
            pass
        except Exception as e:
            utility.inc("phd2_error", {"type": type(e).__name__})
            print(e)
            pass
    
        # something went wrong.  try again in a little bit...
        time.sleep(2)

