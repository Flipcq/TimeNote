import os
import json
from tkinter import *
from tkinter.messagebox import *
from tkinter.filedialog import *

class TimeNote:
    # Initializing our window
    __root = Tk()

    # Initial settings for our text editor
    __thisWidth = 730
    __thisHeight = 600
    __thisTextArea = Text(__root, pady=10, padx=10, wrap='word', font=('Consolas 12'), bg='#F0F0F0', fg='black')
    __thisMenuBar = Menu(__root, bg='#F0F0F0', fg='black')
    __thisFileMenu = Menu(__thisMenuBar, tearoff=0, bg='#F0F0F0', fg='black')
    __thisEditMenu = Menu(__thisMenuBar, tearoff=0, bg='#F0F0F0', fg='black')
    __thisViewMenu = Menu(__thisMenuBar, tearoff=0, bg='#F0F0F0', fg='black')
    __thisHelpMenu = Menu(__thisMenuBar, tearoff=0, bg='#F0F0F0', fg='black')
    
    __thisScrollBar = Scrollbar(__root)
    __file = None
    __default_wpm = 130  # Default words per minute
    __theme = 'light'  # Theme mode: 'light' or 'dark'

    def __init__(self, **kwargs):
        # Set icon
        try:
            self.__root.wm_iconbitmap('icon.ico')
        except:
            pass

        # Configure screen size
        try:
            self.__thisWidth = kwargs['width']
        except KeyError:
            pass

        try:
            self.__thisHeight = kwargs['height']
        except KeyError:
            pass

        self.__root.title('TimeNote')

        screenWidth = self.__root.winfo_screenwidth()
        screenHeight = self.__root.winfo_screenheight()

        left = (screenWidth / 2) - (self.__thisWidth / 2)
        top = (screenHeight / 2) - (self.__thisHeight / 2)

        self.__root.geometry('%dx%d+%d+%d' % (self.__thisWidth, self.__thisHeight, left, top))

        self.__root.grid_rowconfigure(0, weight=1)
        self.__root.grid_columnconfigure(0, weight=1)

        self.__thisTextArea.grid(row=0, column=0, sticky=N + E + S + W)

        # Adding a frame for bottom bar elements
        self.__bottomFrame = Frame(self.__root, bg='#F0F0F0')
        self.__bottomFrame.grid(row=1, column=0, sticky=W + E)

        # Adding a bottom bar for read time
        self.__thisBottomBar = Label(self.__bottomFrame, text="Reading time: 0 min 0 sec", anchor='w', bg='#F0F0F0', fg='black')
        self.__thisBottomBar.pack(side=LEFT, padx=10, pady=5)

        # Entry to adjust WPM
        self.__wpmLabel = Label(self.__bottomFrame, text="Words per minute (WPM):", anchor='e', bg='#F0F0F0', fg='black')
        self.__wpmLabel.pack(side=LEFT, padx=10, pady=5)

        self.__wpmEntry = Entry(self.__bottomFrame)
        self.__wpmEntry.insert(0, self.__default_wpm)
        self.__wpmEntry.pack(side=LEFT, padx=10, pady=5)

        self.__updateWPMButton = Button(self.__bottomFrame, text="Update WPM", command=self.__updateWPM)
        self.__updateWPMButton.pack(side=LEFT, padx=10, pady=5)

        self.__updateStatusLabel = Label(self.__bottomFrame, text="No changes made 🐦", bg='#F0F0F0', fg='black')
        self.__updateStatusLabel.pack(side=LEFT, padx=10, pady=5)

        # Binding text area modifications to update read time
        self.__thisTextArea.bind('<<Modified>>', self.__updateReadTime)

        # ----------------File menu-------------------
        self.__thisFileMenu.add_command(label='New', command=self.__newfile)
        self.__thisFileMenu.add_command(label='Open', command=self.__openFile)
        self.__thisFileMenu.add_command(label='Save', command=self.__saveFile)
        self.__thisFileMenu.add_separator()

        self.__thisMenuBar.add_cascade(label='File', menu=self.__thisFileMenu)

        # -----------------Theme menu------------------
        self.__thisViewMenu.add_command(label='Dark', command=self.__toggle_theme)
        self.__thisMenuBar.add_cascade(label='Theme', menu=self.__thisViewMenu)

        # ------- Show menu and scrollBar on screen---------
        self.__root.config(menu=self.__thisMenuBar)

        self.__thisScrollBar.grid(row=0, column=1, sticky=N+S)
        self.__thisScrollBar.config(command=self.__thisTextArea.yview)
        self.__thisTextArea.config(yscrollcommand=self.__thisScrollBar.set)

        # Load theme settings
        self.__load_settings()
        self.__apply_theme()

    # --------File menu functions---------------------
    def __newfile(self):
        self.__root.title('Untitled - TimeNote')
        self.__file = None
        self.__thisTextArea.delete(1.0, END)

    def __openFile(self):
        self.__file = askopenfilename(defaultextension='.txt', filetypes=[('All Files', '*.*'), ('Text Documents', '*.txt')])

        if self.__file == '':
            self.__file = None
        else:
            self.__root.title(os.path.basename(self.__file) + ' - TimeNote')
            self.__thisTextArea.delete(1.0, END)

            with open(self.__file, 'r') as file:
                self.__thisTextArea.insert(1.0, file.read())

    def __saveFile(self):
        if self.__file is None:
            self.__file = asksaveasfilename(initialfile='Untitled', defaultextension='.txt', filetypes=[('All Files', '*.*'), ('Text Documents', '*.txt')])

            if self.__file == '':
                self.__file = None
            else:
                with open(self.__file, 'w') as file:
                    file.write(self.__thisTextArea.get(1.0, END))

                self.__root.title(os.path.basename(self.__file) + ' - TimeNote')

        else:
            with open(self.__file, 'w') as file:
                file.write(self.__thisTextArea.get(1.0, END))

    def __quitApplication(self):
        self.__save_settings()
        self.__root.destroy()

    def __updateWPM(self):
        try:
            new_wpm = int(self.__wpmEntry.get())
            if new_wpm > 0:
                self.__default_wpm = new_wpm
                self.__updateReadTime()
                self.__updateStatusLabel.config(text=f"Changed to {self.__default_wpm} 📌")
            else:
                showwarning("Invalid Value", "Please enter a valid value greater than zero.")
        except ValueError:
            showwarning("Invalid Value", "Please enter a valid numeric value.")
            self.__updateStatusLabel.config(text="")

        # Atualiza o campo de entrada para refletir o valor padrão atualizado
        self.__wpmEntry.delete(0, END)
        self.__wpmEntry.insert(0, self.__default_wpm)

        # Salva as configurações após a alteração
        self.__save_settings()

    # ----------- Reading time functions --------------
    def __updateReadTime(self, event=None):
        text = self.__remove_hashes(self.__thisTextArea.get(1.0, END)).strip()
        words = len(text.split())
        read_time_min = words // self.__default_wpm
        read_time_sec = int((words % self.__default_wpm) / (self.__default_wpm / 60))
        self.__thisBottomBar.config(text=f"Reading time: {read_time_min} min {read_time_sec} sec")
        self.__thisTextArea.edit_modified(False)

    def __remove_hashes(self, text):
        start = 0
        while True:
            start = text.find('#', start)
            if start == -1:
                break
            end = text.find('#', start + 1)
            if end == -1:
                break
            text = text[:start] + text[end + 1:]
        return text

    def __toggle_theme(self):
        if self.__theme == 'light':
            self.__theme = 'dark'
        else:
            self.__theme = 'light'

        self.__apply_theme()
        self.__save_settings()

    def __load_settings(self):
        if os.path.exists('settings.json'):
            with open('settings.json', 'r') as file:
                settings = json.load(file)
                self.__theme = settings.get('theme', 'light')
                self.__default_wpm = int(settings.get('wpm', self.__default_wpm))

    def __save_settings(self):
        settings = {
            'theme': self.__theme,
            'wpm': self.__default_wpm
        }
        with open('settings.json', 'w') as file:
            json.dump(settings, file)

    def __apply_theme(self):
        if self.__theme == 'dark':
            self.__root.config(bg='#222222')
            self.__thisTextArea.config(bg='#333333', fg='white')
            self.__thisMenuBar.config(bg='#222222', fg='white')
            self.__thisFileMenu.config(bg='#222222', fg='white')
            self.__thisEditMenu.config(bg='#222222', fg='white')
            self.__thisViewMenu.config(bg='#222222', fg='white')
            self.__thisHelpMenu.config(bg='#222222', fg='white')
            self.__thisScrollBar.config(bg='#333333', troughcolor='#444444')
            self.__bottomFrame.config(bg='#222222')
            self.__wpmLabel.config(bg='#222222', fg='white')
            self.__updateStatusLabel.config(bg='#222222', fg='white')
            self.__updateWPMButton.config(bg='#222222', fg='white')
            self.__wpmEntry.config(bg='#333333', fg='white')
            self.__thisBottomBar.config(bg='#222222', fg='white')
        else:
            self.__root.config(bg='#F0F0F0')
            self.__thisTextArea.config(bg='#F0F0F0', fg='black')
            self.__thisMenuBar.config(bg='#F0F0F0', fg='black')
            self.__thisFileMenu.config(bg='#F0F0F0', fg='black')
            self.__thisEditMenu.config(bg='#F0F0F0', fg='black')
            self.__thisViewMenu.config(bg='#F0F0F0', fg='black')
            self.__thisHelpMenu.config(bg='#F0F0F0', fg='black')
            self.__thisScrollBar.config(bg='#F0F0F0', troughcolor='#D9D9D9')
            self.__bottomFrame.config(bg='#F0F0F0')
            self.__wpmLabel.config(bg='#F0F0F0', fg='black')
            self.__updateStatusLabel.config(bg='#F0F0F0', fg='black')
            self.__updateWPMButton.config(bg='#F0F0F0', fg='black')
            self.__wpmEntry.config(bg='white', fg='black')
            self.__thisBottomBar.config(bg='#F0F0F0', fg='black')

        # Update theme for all subwidgets
        self.__root.update_idletasks()

    def run(self):
        self.__load_settings()
        self.__apply_theme()
        self.__wpmEntry.delete(0, END)
        self.__wpmEntry.insert(0, self.__default_wpm)
        self.__root.mainloop()

note = TimeNote()
note.run()

