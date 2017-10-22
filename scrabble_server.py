from board import Board
from dictionary import Dictionary
import zmq
import json

DICTIONARY_FILENAME = "dictionary"

dictionary = Dictionary.load(DICTIONARY_FILENAME)

context = zmq.Context()
socket = context.socket(zmq.REP)
socket.bind('tcp://127.0.0.1:5555')

def success_resp(data):
    return json.dumps({"success": True, "data": data})

def error_resp(msg):
    return json.dumps({"success": False, "error": msg})

while True:
    msg = socket.recv()
    msg = msg.decode("utf-8")
    msg = json.loads(msg)

    board = Board()
    rack = ""

    if len(msg["board"]) != 15*15 or len(msg["hand"]) > 7:
        print("ERROR")
        socket.send_string(error_resp("Invalid board or hand"))
        continue

    for index in range(15*15):
        if msg["board"][index] == "-":
            board.cells[index] = None
        elif msg["board"][index] == " ":
            board.is_blank[index] = True
        else:
            board.cells[index] = msg["board"][index].upper()

    rack = msg["hand"].upper()

    print rack
    print board

    solutions = board.generate_solutions(rack, dictionary)

    solution = board.find_best_solution(solutions, dictionary)

    if solution:
        print(solution)
        socket.send_string(success_resp(str(solution)))
    else:
        print("NOSOLUION")
        socket.send(error_resp("No solution was found"))
