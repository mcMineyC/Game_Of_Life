import multiprocessing as mp
from lib import game_runner as runner
from lib import convert_functions as cf
from lib import communication_functions as comms
from lib import test_patterns as tp
from lib.simulator import CGOLSimulator
import time

def runner_thread(incoming, outgoing, client, verbose=False):
    simulator = CGOLSimulator(verbose=verbose)
    if verbose:
        print("CGOL runner_thread: Runner thread created")

    needsToDie = False
    last_grid_update = time.time()
    MIN_UPDATE_INTERVAL = 0.016  # Minimum time between grid updatesa, ~60fps
    IDLE_SLEEP = 0.1  # Sleep time when not running
    def send_grid():
        # Helper function to consistently send grid through both channels
        curr_grid = simulator.process_grid()
        outgoing.send({
            "type": "grid",
            "data": curr_grid
        })
        if verbose:
            print("Sent grid to pipe")
        try:
            comms.send_message(client, curr_grid)
            if verbose:
                print("Sent grid to comms socket")
        except Exception as e:
            if verbose:
                print(f"CGOL runner_thread: Error sending message to comms socket: {e}")

    while True:

        # Process incoming messages
        while incoming.poll():
            item = incoming.recv()
            match(item["type"]):
                case "setgrid":
                    simulator.set_grid(item["data"])
                    send_grid()
                case "setinterval":
                    simulator.set_interval(item["data"])
                case "setcamera":
                    if verbose:
                        print("CGOL runner_thread: Setting camera to ", item["data"])
                    simulator.camera_pos = item["data"]
                    send_grid()
                case "stop":
                    simulator.stop()
                case "start":
                    if verbose:
                        print("CGOL runner_thread: Starting Main Loop")
                    simulator.start()
                case "avadakadavra":
                    needsToDie = True
                    break
        if needsToDie:
            if verbose:
                print("CGOL runner_thread: Received avadakadavra. Exiting.")
            else:
                print("Fly away, Stanley. Be free!!")
            break

        # Main simulation loop
        if simulator.running:
            if verbose:
                print("CGOL runner_thread: Running Main Loop")

            simulator.tick()

            send_grid()

            # Use the simulator interval directly for sleep
            if simulator.interval > 0:
                time.sleep(simulator.interval)
            else:
                time.sleep(MIN_UPDATE_INTERVAL)
        else:
            # Sleep longer when not running
            time.sleep(IDLE_SLEEP)
