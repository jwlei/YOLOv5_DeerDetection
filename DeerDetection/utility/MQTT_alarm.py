class AlarmFrame(Frame):
    def __init__(self, master=None):
        Frame.__init__(self, master)
        self.master = master
        self.pack(fill=BOTH, expand=1)
        
        self.alert_status = Label(self, text='Waiting for input', bg='Orange')
        self.update_alarm()

    def update_alarm(self):
        global currentDetectionCount

        if currentDetectionCount > 0:
            self.alert_status.config(bg="red")
        else:
            self.alert_status.config(bg="green")

        self.after(1000, self.update_alarm)
        
        

root = Tk()
root.geometry = ("150x150")
alarmWindow = AlarmFrame(root)
root.mainloop()