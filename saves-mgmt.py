# from tkinter import Button, Label, StringVar, Tk
import tkinter as tk
import os
from shutil import copy2
from functools import partial
import sys
import datetime
import ntpath

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

    def __gt__(self, other):
        if other:
            return(self.time > other.time)

    def __lt__(self, other):
        return(self.time < other.time)

    def __eq__(self, other):
        return(self.time == other.time)


class Game:

    name = ""
    savesPath = ""
    saves = list()
    numSaves = 10
    originalSaveFiles = list()
    lastSave = None
    lastSaveTime = 0
    useSaveFolders = True
    lblStatus = None
    lblSaves = list()
    txtSaveNum = None

    global DEBUG
    global window

    def displaySaves(self):
        if self.saves:
            self.saves.sort(reverse=True)
            i = 0
            for lblSave in self.lblSaves:
                if i < len(self.saves):
                    lblSave['text'] = f'{self.saves[i].number} - {datetime.datetime.fromtimestamp(self.saves[i].time)}'
                i += 1

    def getSaveFolderName(self, i):
        return f'save-mgmt-{self.name.replace(" ", "_")}-{i}'

    def updateSaves(self):

        for i in range(1, self.numSaves):
            path = os.path.join(self.savesPath, self.getSaveFolderName(i))
            save = Save(path, i, self.originalSaveFiles)

            try:
                saveTime = os.path.getmtime(os.path.join(path, ntpath.basename(self.originalSaveFiles[0])))
            except:
                error = f'ERROR getting save date: {sys.exc_info()[0]}:\n{sys.exc_info()[1]}'
                self.lblStatus['text'] = error
                dprint(error)
                saveTime = 0

            save.time = saveTime
            self.saves.append(save)
            if saveTime >= self.lastSaveTime:
                self.lastSaveTime = saveTime
                self.lastSave = i

        self.displaySaves()

    def __init__(self, name, savesPath, originalSaveFiles):
        self.name = name
        self.savesPath = savesPath
        self.originalSaveFiles = list()

        self.lblStatus = tk.Label(window, text="Initialising...")
        self.lblStatus.grid(column=0, row=12, columnspan=5)
        self.txtSaveNum = tk.Entry(window, width=2)
        self.txtSaveNum.grid(column=1, row=3)

        # create labels for savegames
        lblSaveTitle = tk.Label(window, text="List of saves, sorted from newest to oldest").grid(column=3, row=1, columnspan=2)
        for i in range(self.numSaves):
            lblSave = tk.Label(window, text="")
            lblSave.grid(column=4, row=i+2)
            self.lblSaves.append(lblSave)

        # create original save files list
        i = 0
        for file in originalSaveFiles:
            self.originalSaveFiles.append(os.path.join(self.savesPath, file))
            i += 1
        dprint(f'self.originalSaveFiles.len(): {len(self.originalSaveFiles)}')

        if self.useSaveFolders:
            for i in range(1, self.numSaves):
                path = os.path.join(self.savesPath, self.getSaveFolderName(i))
                dprint(path)
                # check if save folders are created, create if not
                if not os.path.exists(path):
                    # create dir
                    os.makedirs(path)

        dprint([str(save) for save in self.saves])
        self.updateSaves()

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
            self.updateSaves()
            self.lblStatus['text'] = f'Saved game {self.lastSave}'

    def load(self, number):
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

    def loadLatest(self):
        if self.lastSave:
            self.load(self.lastSave)

        else:
            error = f'ERROR - no latest save game found'
            self.lblStatus['text'] = error
            dprint(error)


def setup_BadNorth():
    badNorth = Game(
        "Bad North", "C:\\Users\\Paddy\\AppData\\LocalLow\\Plausible Concept\\Bad North\\Saves\\", ['campaign - 0', 'campaign - 0.meta', 'user'])
    return badNorth


def clickedSave(game):
    game.save()


def clickedLoadLatest(game):
    game.loadLatest()


def clickedLoad(game):
    dprint(game.txtSaveNum)
    loaded = False
    if game.txtSaveNum.get().isnumeric():
        saveNum = int(game.txtSaveNum.get())
        if saveNum < game.numSaves - 1 and game.numSaves > 0:
            dprint(saveNum)
            # game.load(saveNum)
            loaded = True

    if not loaded:
        error = f'ERROR - provided save number is not correct, must be between 1 and {game.numSaves}'
        game.lblStatus['text'] = error
        dprint(error)


def main():

    global window

    window = tk.Tk()
    window.title("Casitos savegame manager")
    window.geometry('400x300')

    # load game save settings
    game = setup_BadNorth()

    lblGame = tk.Label(window, text=f'Game: {game}')
    lblGame.grid(column=0, row=0)

    btnSave = tk.Button(window, text="save", command=partial(clickedSave, game))
    btnSave.grid(column=0, row=1)

    btnLoadLatest = tk.Button(window, text="load latest", command=partial(clickedLoadLatest, game))
    btnLoadLatest.grid(column=0, row=2)

    btnLoadLatest = tk.Button(window, text="load save number: ", command=partial(clickedLoad, game))
    btnLoadLatest.grid(column=0, row=3)

    window.mainloop()


if __name__ == "__main__":
    main()
