import tkinter as tk

class AlarmFrame(tk.Frame):
    def __init__(self, root):
        tk.Frame.__init__(self, root)
        self.root = root
        self.setup_gui()
        self.launch_gui()


    def setup_gui(self):
        self.alert_status = tk.Label(self, text='Waiting for input', bg='orange')
        self.alert_status.grid(row = 0, sticky = "NESW")

    def detectionIndicator(self, detection):
        """ Function for deciding the detection warning status """ 
        if detection == 'detected':
            self.alert_status.config(bg="red")
        else:
            self.alert_status.config(bg="green")

    def launch_gui(self):
        self.root.mainloop()
        
