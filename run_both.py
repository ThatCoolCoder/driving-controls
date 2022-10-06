import threading

import pedals.main as pedals
import wheel.main as wheel


if __name__ == '__main__':
    threading.Thread(target=wheel.main).start()
    threading.Thread(target=pedals.main, args=('/dev/ttyACM1',)).start()