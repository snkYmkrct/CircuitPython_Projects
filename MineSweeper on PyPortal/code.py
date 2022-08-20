import time
import supervisor

while True:
    print("loading minesweeper...")
    time.sleep(2)
    supervisor.set_next_code_file('minesweeper_PPT.py')
    supervisor.reload()
