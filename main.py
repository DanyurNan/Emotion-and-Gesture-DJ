import gui
import client
import threading

if __name__ == "__main__":
    width, height, gui_size = gui.get_display_size()
    app = gui.App(width, height)
    app.geometry(gui_size)
    app.resizable(0, 0) #Non resizable window
    threading.Thread(target=client.run_client).start()
    app.protocol("WM_DELETE_WINDOW", lambda:gui.on_closing(app))
    app.mainloop()
    