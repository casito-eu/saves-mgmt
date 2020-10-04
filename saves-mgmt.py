# from tkinter import Button, Label, StringVar, Tk
import tkinter as tk
import os
from shutil import copy2
from functools import partial
import sys

DEBUG = True
window = None


def dprint(message):

    global DEBUG

    if DEBUG:
        print(message)


class Save:

    folder = ""
    time = 0
    filesFullPath = list()
    number = 0

    def __init__(self, folder, number, files, time=0):
        self.folder = folder
        self.number = number
        self.time = time
        self.filesFullPath = files

    def __str__(self):
        return(f'{self.folder}: {self.time}\n{[file for file in self.filesFullPath]}\n\n')


class Game:

    name = ""
    savesPath = ""
    saves = []
    numSaves = 5
    originalSaveFiles = list()
    lastSave = None
    lastSaveTime = 0
    useSaveFolders = True
    lblStatus = None

    global DEBUG
    global window

    def getSaveFolderName(self, i):
        return f'save-mgmt-{self.name.replace(" ", "_")}-{i}'

    def __init__(self, name, savesPath, originalSaveFiles):
        self.name = name
        self.savesPath = savesPath
        self.originalSaveFiles = list()

        self.lblStatus = tk.Label(window, text="Initialising...")
        self.lblStatus.grid(column=0, row=2)

        self.saves = [None] * self.numSaves

        # create original save files list
        i = 0
        for file in originalSaveFiles:
            self.originalSaveFiles.append(os.path.join(self.savesPath, file))
            i += 1
        dprint(f'self.originalSaveFiles.len(): {len(self.originalSaveFiles)}')

        # check if save folders are created, create if not
        if self.useSaveFolders:
            for i in range(1, 6):
                path = os.path.join(self.savesPath, self.getSaveFolderName(i))
                dprint(path)
                if not os.path.exists(path):
                    # create dir
                    os.makedirs(path)
                else:
                    dprint(i)
                    save = Save(path, i, self.originalSaveFiles)
                    self.saves[i-1] = save
                    # determine save date
                    try:
                        saveTime = os.path.getmtime(self.originalSaveFiles[0])
                    except:
                        error = f'ERROR getting save date: {sys.exc_info()[0]}:\n{sys.exc_info()[1]}'
                        self.lblStatus['text'] = error
                        dprint(error)
                    else:
                        self.saves[i-1].time = saveTime
                        if saveTime >= self.lastSaveTime:
                            self.lastSaveTime = saveTime
                            self.lastSave = i

        dprint([str(save) for save in self.saves])

        self.lblStatus['text'] = f'{self.name} initialised. Last save: {self.lastSave}'

    def __str__(self):
        return self.name

    def save(self):

        copied = False

        if self.lastSave == None or self.lastSave == 5:
            self.lastSave = 0

        dprint(f'copy files:\n{self.saves[self.lastSave].filesFullPath}\nto\n{self.saves[self.lastSave].folder}')
        for file in self.saves[self.lastSave].filesFullPath:
            try:
                copy2(file, self.saves[self.lastSave].folder)
            except:
                error = f'ERROR copying files: {sys.exc_info()[0]}:\n{sys.exc_info()[1]}'
                self.lblStatus['text'] = error
                dprint(error)
            else:
                copied = True

        if copied:
            self.lastSave += 1
            self.lblStatus['text'] = f'Saved game {self.lastSave}'

    def loadLatest(self):
        if self.lastSave:
            dprint(f'copy files {[os.path.join(self.saves[self.lastSave-1].folder, file) for file in os.listdir(self.saves[self.lastSave-1].folder)]} to {self.savesPath}')
            for file in os.listdir(self.saves[self.lastSave-1].folder):
                try:
                    copy2(os.path.join(self.saves[self.lastSave-1].folder, file), self.savesPath)
                except:
                    error = f'ERROR loading lates files: {sys.exc_info()[0]}:\n{sys.exc_info()[1]}'
                    self.lblStatus['text'] = error
                    dprint(error)
                else:
                    self.lblStatus['text'] = f'Loaded savegame {self.lastSave}'

        else:
            error = f'ERROR - no latest save game found'
            self.lblStatus['text'] = error
            dprint(error)

    def load(self, number):
        pass


def setup_BadNorth():
    badNorth = Game(
        "Bad North", "C:\\Users\\Paddy\\AppData\\LocalLow\\Plausible Concept\\Bad North\\Saves\\", ['campaign - 0', 'campaign - 0.meta', 'user'])
    return badNorth


def clickedSave(game):
    game.save()


def clickedLoadLatest(game):
    game.loadLatest()


def main():

    global window

    window = tk.Tk()
    window.title("Casitos savegame manager")
    window.geometry('350x200')

    # load game save settings
    game = setup_BadNorth()

    lblGame = tk.Label(window, text=f'Game: {game}')
    lblGame.grid(column=0, row=0)

    btn = tk.Button(window, text="save", command=partial(clickedSave, game))
    btn.grid(column=0, row=1)

    btn = tk.Button(window, text="load latest", command=partial(clickedLoadLatest, game))
    btn.grid(column=1, row=1)

    window.mainloop()


if __name__ == "__main__":
    main()
