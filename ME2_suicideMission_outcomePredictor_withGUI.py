import sys
import re
import numpy as np
import tkinter as tk
from tkinter import ttk, scrolledtext
import tkinter.font as tkfont
import copy

'''----------------------------------------Constants, Flags, Options----------------------------------------
'''
stinger = True


'''----------------------------------------Functions and Classes----------------------------------------
'''
class Character:
	"""A ME2 Squadmate's Character Details"""
	def __init__(self, tier, loyal=False, ventPref=False, bioticPref=False, leaderPref=False, squad=False, recruited=True):
		self.loyal = tk.BooleanVar(value=loyal)
		self.ventPref = tk.BooleanVar(value=ventPref)
		self.bioticPref = tk.BooleanVar(value=bioticPref)
		self.leaderPref = tk.BooleanVar(value=leaderPref)
		self.squad = tk.BooleanVar(value=squad)
		self.tier = tk.IntVar(value=tier)
		self.recruited = tk.BooleanVar(value=recruited)

def updateBoolVar(choice, var):
	yes = choice.get()
	var.set(yes == "Yes")

def updateSelections(choice1, choice2, choice3="", choice4=""):
    if isinstance(choice1, str):
        selected1 = choice1
        selected2 = choice2.get()
    else:
        selected1 = choice1.get()
        selected2 = choice2.get()
    if choice3=="":
        selected3 = ""
    else:
        selected3 = choice3.get()
    if choice4=="":
        selected4 = ""
    else:
        selected4 = choice4.get()

    if (selected1 == selected2) and (selected1 != ""):
        choice2.set("")
    if (selected1 == selected3) and (selected1 != ""):
        choice3.set("")
    if (selected1 == selected4) and (selected1 != ""):
        choice4.set("")

def resetSelections(s, lvl):
    s.crewMessage = "The status of the crew is unknown . . ."
    if lvl < 4:
        s.specialistFinalFight_selector.set("")
        s.squadFinalFight1_selector.set("")
        s.squadFinalFight2_selector.set("")
        s.specialistFinalFight_selector["values"] = []
        s.squadFinalFight1_selector["values"] = []
        s.squadFinalFight2_selector["values"] = []
    if lvl < 3:
        s.specialistLongWalk_selector.set("")
        s.leaderLongWalk_selector.set("")
        s.squadLongWalk1_selector.set("")
        s.squadLongWalk2_selector.set("")
        s.specialistLongWalk_selector["values"] = []
        s.leaderLongWalk_selector["values"] = []
        s.squadLongWalk1_selector["values"] = []
        s.squadLongWalk2_selector["values"] = []
    if lvl < 2:
        s.specialistVents_selector.set("")
        s.leaderVents_selector.set("")
        s.squadVents1_selector.set("")
        s.squadVents2_selector.set("")
        s.specialistVents_selector["values"] = []
        s.leaderVents_selector["values"] = []
        s.squadVents1_selector["values"] = []
        s.squadVents2_selector["values"] = []

def armorCheck(d):
    """
    Purpose:    Kill Jack if you fail the armor check
    Args:       d (dict) - {"name of crew member" : Character() class} pairs
    Return:     Name of the dead (str)
    """	
    if ("Jack" in d):
        del d["Jack"]
        return "Jack"
    else:
        return ""

def shieldCheck(d):
    """
    Purpose:    Kill a crew member if you fail the shield check
    Args:       d (dict) - {"name of crew member" : Character() class} pairs
    Return:     Name of the dead (str)
    """	
    l = ["Kasumi", "Legion", "Tali", "Thane", "Garrus", "Zaeed", "Grunt", "Samara", "Morinth"]
    for i, v in enumerate(l):
        if (v in d) and (not d[v].squad.get()):
            del d[v]
            return v

def weaponsCheck(d):
    """
    Purpose:    Kill a crew member if you fail the weapons check
    Args:       d (dict) - {"name of crew member" : Character() class} pairs
    Return:     Name of the dead (str)
    """	
    l = ["Thane", "Garrus", "Zaeed", "Grunt", "Jack", "Samara", "Morinth"]
    for i, v in enumerate(l):
        if (v in d) and (not d[v].squad.get()):
            del d[v]
            return v

def ventCheck(d, leader, spec):
    """
    Purpose:    Kill the vent specialist if you choose the wrong tech specialist or leader
    Args:       d (dict) - {"name of crew member" : Character() class} pairs
                leader (str) - Name of the fire team leader
                spec (str) - name of the tech specialist
    Return:     Name of the dead (str)
    """ 
    if (d[spec].ventPref.get() == False) or (d[spec].loyal.get() == False) or (d[leader].leaderPref.get() == False) or (d[leader].loyal.get() == False):
        del d[spec]
        return spec
    else:
        return ""
   
def bioticCheck(d, spec):
    """
    Purpose:    Kill a squad member if you choose the wrong biotic specialist
    Args:       d (dict) - {"name of crew member" : Character() class} pairs
                leader (str) - Name of the fire team leader
                spec (str) - name of the biotic specialist
    Return:     Name of the dead (str)
    """ 
    if (d[spec].bioticPref.get() == False) or (d[spec].loyal.get() == False):
        l = ["Thane", "Jack", "Garrus", "Legion", "Grunt", "Samara", "Jacob", "Mordin", "Tali", "Kasumi", "Zaeed", "Morinth"]
        for i, name in enumerate(l):
            if (name in d) and (d[name].squad.get()):
                del d[name]
                return name
    else:
        return ""

def secondLeaderCheck(d, leader):
    """
    Purpose:    Kill the fire team leader if you choose the wrong leader
    Args:       d (dict) - {"name of crew member" : Character() class} pairs
                leader (str) - Name of the fire team leader
    Return:     Name of the dead (str)
    """ 
    if ((leader == "Miranda")) or ((d[leader].leaderPref.get()) and (d[leader].loyal.get())):
        return ""
    else:
        del d[leader]
        return leader

def toggleAvailable_squadCargo(s, name):
    resetSelections(s, 0)
    d_all = s.allSquadmates
    d_avl = s.squadAvailFor_SuicideMission
    checks = s.checkButtons
    c1 = s.squadCargo1_choice
    c2 = s.squadCargo2_choice
    s1 = s.squadCargo1_selector
    s2 = s.squadCargo2_selector

    if name == "Morinth":
        d_all["Samara"].recruited.set(False)
        d_all["Samara"].loyal.set(False)
        checks["Samara"][1].config(state="disabled")
        d_all["Morinth"].loyal.set(True)

        if "Samara" in d_avl:
            del d_avl["Samara"]
            updateSelections("Samara", c1)
            updateSelections("Samara", c2)
    elif name == "Samara":
        d_all["Morinth"].recruited.set(False)
        d_all["Morinth"].loyal.set(False)
        checks["Morinth"][1].config(state="disabled")
		
        if "Morinth" in d_avl:
            del d_avl["Morinth"]
            updateSelections("Morinth", c1)
            updateSelections("Morinth", c2)
    if d_all[name].recruited.get():
        if name != "Morinth":
            checks[name][1].config(state="normal")
        d_avl[name] = d_all[name]
    else:
        d_all[name].loyal.set(False)
        checks[name][1].config(state="disabled")
        if name in d_avl:
            del d_avl[name]
            updateSelections(name, c1)
            updateSelections(name, c2)
    l1 = list(d_avl)
    l2 = list(d_avl)
    l1.sort()
    l2.sort()
    s1["values"] = l1
    s2["values"] = l2

def get_em(d, l):
    """
    Purpose:    Kill a crew member holding the line
    Args:       d (dict) - {"name of crew member" : Character() class} pairs
                l (list) - The order to kill people in
    Return:     v (str) - the name of a squadmate who died
    """
    jobDone = False
    for i, v in enumerate(l):
        if (v in d) and (d[v].squad.get() == False) and (d[v].loyal.get() == False):
            del d[v]
            jobDone = True
            return v
    if not jobDone:
        for i, v in enumerate(l):
            if (v in d) and (d[v].squad.get() == False) and (d[v].loyal.get() == True):
                del d[v]
                jobDone = True
                return v
    return ""

def holdTheLine(d):
    """
    Purpose:    Calculate survivors from from the group holding the line
    Args:       d (dict) - {"name of crew member" : Character() class} pairs
    Return:     theDead (list) - list of people who died
    """ 
    l = ["Mordin", "Tali", "Kasumi", "Jack", "Miranda", "Jacob", "Garrus", "Samara", "Morinth", "Legion", "Thane", "Zaeed", "Grunt"]
    theDead = []
    score = 0
    people = 0
    for name, deets in d.items():
        if (deets.squad.get() == False):
            people += 1
            added = deets.tier.get() + int(deets.loyal.get())
            score += added
    score /= people
    if people == 1:
        if score < 2:
            name = get_em(d, l)
            theDead.append(name)
    elif people == 2:
        if score == 0:
            name = get_em(d, l)
            theDead.append(name)
        if score < 2:
            name = get_em(d, l)
            theDead.append(name)
    elif people == 3:
        if score == 0:
            name = get_em(d, l)
            theDead.append(name)
        if score < 1:
            name = get_em(d, l)
            theDead.append(name)
        if score < 2:
            name = get_em(d, l)
            theDead.append(name)
    elif people == 4:
        if score == 0:
            name = get_em(d, l)
            theDead.append(name)
        if score < 0.5:
            name = get_em(d, l)
            theDead.append(name)
        if score <= 1:
            name = get_em(d, l)
            theDead.append(name)
        if score < 2:
            name = get_em(d, l)
            theDead.append(name)
    else:
        if score < 0.5:
            name = get_em(d, l)
            theDead.append(name)
        if score < 1.5:
            name = get_em(d, l)
            theDead.append(name)
        if score < 2:
            name = get_em(d, l)
            theDead.append(name)
    return theDead

def finalFight(d):
    """
    Purpose:    Calculate which squadmates survive the final showdown
    Args:       d (dict) - {"name of crew member" : Character() class} pairs
    Return:     dead (list) - the squamates who died
    """ 
    dead = []
    for name, deets in d.items():
        if (deets.squad.get() == True) and (deets.loyal.get() == False):
            dead.append(name)
    for i, name in enumerate(dead):
        del d[name]
    return dead

def writeReport(box, message):
    box.config(state="normal")
    box.delete("1.0", tk.END)
    box.insert(tk.END, message)
    box.config(state="disabled")

class GUI():
    def __init__(self, root):
        self.root = root
        self.root.title("Jantzi's Super Wham-O-Dyne ME2 Suicide Mission Calculator!!!")
        self.root.geometry("1400x900") # width x height

        self.allSquadmates = {"Grunt":Character(tier=3), "Zaeed":Character(tier=3), "Thane":Character(tier=1), "Legion":Character(ventPref=True, tier=1), "Garrus":Character(leaderPref=True, tier=3), "Jacob":Character(leaderPref=True, tier=1), "Miranda":Character(leaderPref=True, tier=1), "Jack":Character(bioticPref=True, tier=0), "Kasumi":Character(ventPref=True, tier=0), "Tali":Character(ventPref=True, tier=0), "Mordin":Character(tier=0), "Samara":Character(bioticPref=True, tier=1), "Morinth":Character(bioticPref=True, recruited=False, tier=1)}
        self.allSquadmates_names = list(self.allSquadmates)
        self.allSquadmates_names.sort()
        self.crewMessage = "The status of the crew is unknown . . ."

        self.squadAvailFor_SuicideMission = copy.copy(self.allSquadmates)
        del self.squadAvailFor_SuicideMission["Morinth"]
        self.squadAvailFor_Vents, self.squadAvailFor_LongWalk, self.squadAvailFor_FinalFight = ({} for _ in range(3))

        style = ttk.Style()
        style.theme_use("clam")

        style.configure("TFrame", background="#f0f0f0")
        style.configure("TLabel", background="#f0f0f5", font=("Segoe UI", 11))
        style.configure("TCheckbutton", background="#f0f0f5", font=("Segoe UI", 10))
        style.configure("TButton", font=("Segoe UI", 11, "bold"), padding=6)

        style.configure("raised.TFrame", background="#ffffff", borderwidth=20, relief="raised")
        style.configure("raised.TLabel", background="#ffffff", font=("Segoe UI", 11))
        style.configure("raised.TCheckbutton", background="#ffffff", font=("Segoe UI", 10))
        style.configure("raised.TButton", font=("Segoe UI", 11, "bold"), padding=6)

        ################################################# Main Frame #################################################
        mainFrame = ttk.Frame(root, padding=20)
        mainFrame.pack(fill="both", expand=True)      

        ################################# --------------- Options Frame --------------- #################################
        optionsFrame = ttk.Frame(mainFrame, padding=10)
        optionsFrame.pack(fill="both", expand=True)

        title = ttk.Label(optionsFrame, text="ME2 Suicide Mission Calculator", font=("Segoe UI", 24, "bold"))
        title.pack(pady=5)

        self.squadCargo_names = list(self.squadAvailFor_SuicideMission)
        self.squadCargo_names.sort()

        ################### ----------------------------- Character List and Checkboxes ----------------------------- ###################
        ### These take up the leftmost section of the GUI, towards the top
        rowStart = 0 	# Needs as many as crew exist
        colStart = 0 	# Needs 3

        charListFrame = ttk.Frame(optionsFrame, style="raised.TFrame")
        charListFrame.pack(pady=10, side='left')

        ttk.Label(charListFrame, text="Name", style="raised.TLabel").grid(row=rowStart, column=colStart, padx=5, pady=5, sticky="e")
        ttk.Label(charListFrame, text="Recruited", style="raised.TLabel").grid(row=rowStart, column=(colStart+1), padx=10, pady=5, sticky="w")
        ttk.Label(charListFrame, text="Loyal", style="raised.TLabel").grid(row=rowStart, column=(colStart+2), padx=10, pady=5, sticky="w")

        tempCounter = rowStart+1
        
        self.checkButtons = {}
        for i, name in enumerate(self.allSquadmates_names):

        	ttk.Label(charListFrame,
        		text=name,
        		style="raised.TLabel"
        	).grid(row=tempCounter, column=(colStart), padx=10, pady=5, sticky="e")

        	rec_button = ttk.Checkbutton(charListFrame,
        		variable=self.allSquadmates[name].recruited,
        		command=lambda name=name: toggleAvailable_squadCargo(self, name),
        		style="raised.TCheckbutton"
        	)

        	loy_button = ttk.Checkbutton(charListFrame,
        		variable=self.allSquadmates[name].loyal,
        		style="raised.TCheckbutton"
        	)
        	
        	if name == "Morinth":
        		loy_button.config(state="disabled")

        	self.checkButtons[name] = [rec_button, loy_button]
        	rec_button.grid(row=tempCounter, column=(colStart+1), padx=10, pady=5)
        	loy_button.grid(row=tempCounter, column=(colStart+2), padx=10, pady=5)

        	tempCounter += 1

        ################### ----------------------------- Prepwork and Cargo Bay Squad Select ----------------------------- ###################
        ### These are in the options, to hte right of the squad selection
        rowStart = 0	# ???? These might be unnecessary for multiple frames
        colStart = 0 	# ????

        self.upgradeArmor = tk.BooleanVar(value=False)
        self.upgradeShield = tk.BooleanVar(value=False)
        self.upgradeCannon = tk.BooleanVar(value=False)

        prepWorkFrame = ttk.Frame(optionsFrame, style="raised.TFrame")
        prepWorkFrame.pack(padx=10, pady=10, side='left')

        # --------- Missions Performed --------- #
        ttk.Label(prepWorkFrame,
        	text="Missions Complete AFTER Crew\nKidnapped, BEFORE launching\nSuicide Mission:",
        	style="raised.TLabel"
        ).grid(row=rowStart, column=colStart, padx=10, pady=5)

        self.missionsPrior = tk.IntVar(value=0)
        ttk.Spinbox(
        	prepWorkFrame,
        	from_=0,
        	to=100,
        	textvariable=self.missionsPrior,
        	width=10,
        	justify="center"
        ).grid(row=(rowStart+1), column=colStart, padx=10, pady=5)

        # --------- Armor Upgrade --------- #
        ttk.Label(prepWorkFrame,
        	text="Was Normandy's armor upgrded?",
        	style="raised.TLabel"
        ).grid(row=(rowStart+2), column=colStart, padx=10, pady=5)

        self.armorCheckSelect_choice = tk.StringVar(value="Yes")
        armorCheckSelect = ttk.Combobox(prepWorkFrame,
        	textvariable=self.armorCheckSelect_choice,
        	values=["Yes", "No"],
        	state="readonly"
        )
        armorCheckSelect.grid(row=(rowStart+3), column=colStart, padx=10, pady=5)

        # --------- Shield Upgrade --------- #
        ttk.Label(prepWorkFrame,
        	text="Were Normandy's Shield's upgraded?",
        	style="raised.TLabel"
        ).grid(row=(rowStart+4), column=colStart, padx=10, pady=5)

        self.shieldCheckSelect_choice = tk.StringVar(value="Yes")
        shieldCheckSelect = ttk.Combobox(prepWorkFrame,
        	textvariable=self.shieldCheckSelect_choice,
        	values=["Yes", "No"],
        	state="readonly"
        )
        shieldCheckSelect.grid(row=(rowStart+5), column=colStart, padx=10, pady=5)

        # --------- Cannon Upgrade --------- #
        ttk.Label(prepWorkFrame,
        	text="Was Normandy's main gun upgraded?",
        	style="raised.TLabel"
        ).grid(row=(rowStart+6), column=colStart, padx=10, pady=5)

        self.cannonCheckSelect_choice = tk.StringVar(value="Yes")
        cannonCheckSelect = ttk.Combobox(prepWorkFrame,
        	textvariable=self.cannonCheckSelect_choice,
        	values=["Yes", "No"],
        	state="readonly"
        )
        cannonCheckSelect.grid(row=(rowStart+7), column=colStart, padx=10, pady=5)

		# --------- Cargo Bay Squad Select --------- #
        ttk.Label(prepWorkFrame,
			text="Select Squad to Defend Cargo Bay",
			style="raised.TLabel"
		).grid(row=(rowStart+8), column=colStart, padx=10, pady=5)

        self.squadCargo1_choice = tk.StringVar(value="")
        self.squadCargo2_choice = tk.StringVar(value="")
        self.squadCargo1_selector = ttk.Combobox(prepWorkFrame,
			textvariable=self.squadCargo1_choice,
			values=self.squadCargo_names,
			state="readonly"
		)
        self.squadCargo2_selector = ttk.Combobox(prepWorkFrame,
			textvariable=self.squadCargo2_choice,
			values=self.squadCargo_names,
			state="readonly"
		)
        self.squadCargo1_selector.grid(row=(rowStart+9), column=colStart, padx=10, pady=5)
        self.squadCargo2_selector.grid(row=(rowStart+10), column=colStart, padx=10, pady=5)
        self.squadCargo1_selector.bind("<<ComboboxSelected>>", lambda event: updateSelections(self.squadCargo1_choice, self.squadCargo2_choice))
        self.squadCargo2_selector.bind("<<ComboboxSelected>>", lambda event: updateSelections(self.squadCargo2_choice, self.squadCargo1_choice))

        # --------- Launch Suicide Mission Button --------- #
        launchSuicideMission_button = ttk.Button(prepWorkFrame, text="Launch Suicide Mission", command=self.launchSuicideMission)
        launchSuicideMission_button.grid(row=(rowStart+11), column=colStart, padx=10, pady=25)

        ################### ----------------------------- Attack the Base (Vents) ----------------------------- ###################
        ventsFrame = ttk.Frame(optionsFrame, style="raised.TFrame")
        ventsFrame.pack(padx=10, pady=10, side='left')

        rowStart = 0    # ???? These might be unnecessary for multiple frames
        colStart = 0    # ????

        # --------- Vent Specialist Select --------- #
        ttk.Label(ventsFrame,
            text="Select Vent Specialist",
            style="raised.TLabel"
        ).grid(row=(rowStart), column=colStart, padx=10, pady=5)

        self.specialistVents_choice = tk.StringVar(value="")
        self.specialistVents_selector = ttk.Combobox(ventsFrame,
            textvariable=self.specialistVents_choice,
            values=[],
            state="readonly"
        )
        self.specialistVents_selector.grid(row=(rowStart+1), column=colStart, padx=10, pady=5)
        self.specialistVents_selector.bind("<<ComboboxSelected>>", lambda event: updateSelections(self.specialistVents_choice, self.leaderVents_choice, self.squadVents1_choice, self.squadVents2_choice))

        # --------- 1st Fireteam Leader Select --------- #
        ttk.Label(ventsFrame,
            text="Select 1st Fireteam Leader",
            style="raised.TLabel"
        ).grid(row=(rowStart+2), column=colStart, padx=10, pady=5)

        self.leaderVents_choice = tk.StringVar(value="")
        self.leaderVents_selector = ttk.Combobox(ventsFrame,
            textvariable=self.leaderVents_choice,
            values=[],
            state="readonly"
        )
        self.leaderVents_selector.grid(row=(rowStart+3), column=colStart, padx=10, pady=5)
        self.leaderVents_selector.bind("<<ComboboxSelected>>", lambda event: updateSelections(self.leaderVents_choice, self.squadVents1_choice, self.squadVents2_choice, self.specialistVents_choice))

        # --------- 1st Attack Squad Select --------- #
        ttk.Label(ventsFrame,
            text="Select Squad to Accompany You",
            style="raised.TLabel"
        ).grid(row=(rowStart+4), column=colStart, padx=10, pady=5)

        self.squadVents1_choice = tk.StringVar(value="")
        self.squadVents2_choice = tk.StringVar(value="")
        self.squadVents1_selector = ttk.Combobox(ventsFrame,
            textvariable=self.squadVents1_choice,
            values=[],
            state="readonly"
        )
        self.squadVents2_selector = ttk.Combobox(ventsFrame,
            textvariable=self.squadVents2_choice,
            values=[],
            state="readonly"
        )
        self.squadVents1_selector.grid(row=(rowStart+5), column=colStart, padx=10, pady=5)
        self.squadVents2_selector.grid(row=(rowStart+6), column=colStart, padx=10, pady=5)
        self.squadVents1_selector.bind("<<ComboboxSelected>>", lambda event: updateSelections(self.squadVents1_choice, self.squadVents2_choice, self.specialistVents_choice, self.leaderVents_choice))
        self.squadVents2_selector.bind("<<ComboboxSelected>>", lambda event: updateSelections(self.squadVents2_choice, self.squadVents1_choice, self.specialistVents_choice, self.leaderVents_choice))

        # --------- Launch Attack on Base Button --------- #
        launchAttack_button = ttk.Button(ventsFrame, text="Launch Attack on Base", command=self.launchAttack)
        launchAttack_button.grid(row=(rowStart+7), column=colStart, padx=10, pady=25)

        ################### ----------------------------- The Long Walk ----------------------------- ###################
        longWalkFrame = ttk.Frame(optionsFrame, style="raised.TFrame")
        longWalkFrame.pack(padx=10, pady=10, side='left')

        rowStart = 0    # ???? These might be unnecessary for multiple frames
        colStart = 0    # ????

        # --------- Biotic Specialist Select --------- #
        ttk.Label(longWalkFrame,
            text="Select Biotic Specialist",
            style="raised.TLabel"
        ).grid(row=(rowStart), column=colStart, padx=10, pady=5)

        self.specialistLongWalk_choice = tk.StringVar(value="")
        self.specialistLongWalk_selector = ttk.Combobox(longWalkFrame,
            textvariable=self.specialistLongWalk_choice,
            values=[],
            state="readonly"
        )
        self.specialistLongWalk_selector.grid(row=(rowStart+1), column=colStart, padx=10, pady=5)
        self.specialistLongWalk_selector.bind("<<ComboboxSelected>>", lambda event: updateSelections(self.specialistLongWalk_choice, self.leaderLongWalk_choice, self.squadLongWalk1_choice, self.squadLongWalk2_choice))

        # --------- 2nd Fireteam Leader Select --------- #
        ttk.Label(longWalkFrame,
            text="Select 2nd Fireteam Leader",
            style="raised.TLabel"
        ).grid(row=(rowStart+2), column=colStart, padx=10, pady=5)

        self.leaderLongWalk_choice = tk.StringVar(value="")
        self.leaderLongWalk_selector = ttk.Combobox(longWalkFrame,
            textvariable=self.leaderLongWalk_choice,
            values=[],
            state="readonly"
        )
        self.leaderLongWalk_selector.grid(row=(rowStart+3), column=colStart, padx=10, pady=5)
        self.leaderLongWalk_selector.bind("<<ComboboxSelected>>", lambda event: updateSelections(self.leaderLongWalk_choice, self.squadLongWalk1_choice, self.squadLongWalk2_choice, self.specialistLongWalk_choice))

        # --------- 2nd Attack Squad Select --------- #
        ttk.Label(longWalkFrame,
            text="Select Squad to Accompany You",
            style="raised.TLabel"
        ).grid(row=(rowStart+4), column=colStart, padx=10, pady=5)

        self.squadLongWalk1_choice = tk.StringVar(value="")
        self.squadLongWalk2_choice = tk.StringVar(value="")
        self.squadLongWalk1_selector = ttk.Combobox(longWalkFrame,
            textvariable=self.squadLongWalk1_choice,
            values=[],
            state="readonly"
        )
        self.squadLongWalk2_selector = ttk.Combobox(longWalkFrame,
            textvariable=self.squadLongWalk2_choice,
            values=[],
            state="readonly"
        )
        self.squadLongWalk1_selector.grid(row=(rowStart+5), column=colStart, padx=10, pady=5)
        self.squadLongWalk2_selector.grid(row=(rowStart+6), column=colStart, padx=10, pady=5)
        self.squadLongWalk1_selector.bind("<<ComboboxSelected>>", lambda event: updateSelections(self.squadLongWalk1_choice, self.squadLongWalk2_choice, self.specialistLongWalk_choice, self.leaderLongWalk_choice))
        self.squadLongWalk2_selector.bind("<<ComboboxSelected>>", lambda event: updateSelections(self.squadLongWalk2_choice, self.squadLongWalk1_choice, self.specialistLongWalk_choice, self.leaderLongWalk_choice))

        # --------- Launch Attack Long Walk Button --------- #
        launchLongWalk_button = ttk.Button(longWalkFrame, text="Begin the Long Walk", command=self.launchLongWalk)
        launchLongWalk_button.grid(row=(rowStart+7), column=colStart, padx=10, pady=25)

        ################### ----------------------------- The Final Battle ----------------------------- ###################
        finalFightFrame = ttk.Frame(optionsFrame, style="raised.TFrame")
        finalFightFrame.pack(padx=10, pady=10, side='left')

        rowStart = 0    # ???? These might be unnecessary for multiple frames
        colStart = 0    # ????

        # --------- Escort for the Crew Select --------- #
        ttk.Label(finalFightFrame,
            text="Select Escort for the crew",
            style="raised.TLabel"
        ).grid(row=(rowStart), column=colStart, padx=10, pady=5)

        self.specialistFinalFight_choice = tk.StringVar(value="")
        self.specialistFinalFight_selector = ttk.Combobox(finalFightFrame,
            textvariable=self.specialistFinalFight_choice,
            values=[],
            state="readonly"
        )
        self.specialistFinalFight_selector.grid(row=(rowStart+1), column=colStart, padx=10, pady=5)
        self.specialistFinalFight_selector.bind("<<ComboboxSelected>>", lambda event: updateSelections(self.specialistFinalFight_choice, self.squadFinalFight1_choice, self.squadFinalFight2_choice))

        # --------- Final Fight Squad Select --------- #
        ttk.Label(finalFightFrame,
            text="Select Squad to Accompany You",
            style="raised.TLabel"
        ).grid(row=(rowStart+4), column=colStart, padx=10, pady=5)

        self.squadFinalFight1_choice = tk.StringVar(value="")
        self.squadFinalFight2_choice = tk.StringVar(value="")
        self.squadFinalFight1_selector = ttk.Combobox(finalFightFrame,
            textvariable=self.squadFinalFight1_choice,
            values=[],
            state="readonly"
        )
        self.squadFinalFight2_selector = ttk.Combobox(finalFightFrame,
            textvariable=self.squadFinalFight2_choice,
            values=[],
            state="readonly"
        )
        self.squadFinalFight1_selector.grid(row=(rowStart+5), column=colStart, padx=10, pady=5)
        self.squadFinalFight2_selector.grid(row=(rowStart+6), column=colStart, padx=10, pady=5)
        self.squadFinalFight1_selector.bind("<<ComboboxSelected>>", lambda event: updateSelections(self.squadFinalFight1_choice, self.specialistFinalFight_choice, self.squadFinalFight2_choice))
        self.squadFinalFight2_selector.bind("<<ComboboxSelected>>", lambda event: updateSelections(self.squadFinalFight2_choice, self.specialistFinalFight_choice, self.squadFinalFight1_choice))

        # --------- Launch Final Fight Button --------- #
        launchFinalFight_button = ttk.Button(finalFightFrame, text="Begin the Final Battle", command=self.launchFinalFight)
        launchFinalFight_button.grid(row=(rowStart+7), column=colStart, padx=10, pady=25)

        ################################# --------------- Results Frame --------------- #################################
        resultsFrame = ttk.Frame(mainFrame, style="raised.TFrame")
        resultsFrame.pack(padx=10, pady=5)#, side='left')

        ### -------- Output box listing who died and why (after each step)-------- ###
        self.crewDied_box = scrolledtext.ScrolledText(resultsFrame, width=40, height=17, wrap=tk.WORD)
        self.crewDied_box.pack(padx=10, pady=5, side="left")
        self.crewDied_box.config(state="disabled")  # start as read‑only

        ### -------- Output box listing remaining crew (after each step)-------- ###
        self.crewRemain_box = scrolledtext.ScrolledText(resultsFrame, width=60, height=17, wrap=tk.WORD)
        self.crewRemain_box.pack(padx=10, pady=5, side="left")
        self.crewRemain_box.config(state="disabled")  # start as read‑only

    def launchSuicideMission(self):
        resetSelections(self, 1)
        message_crewDied, message_crewRemain = ("" for _ in range(2))
        survived_list = list(self.squadAvailFor_SuicideMission)
        survived_list.sort()

        if ('' == self.squadCargo1_choice.get()) or ('' == self.squadCargo2_choice.get()):
            message_crewDied = "Please select two squad members."
            message_crewRemain = ""
        else:
            for i, name in enumerate(survived_list):
                if (name == self.squadCargo1_choice.get()) or (name==self.squadCargo2_choice.get()):
                    self.squadAvailFor_SuicideMission[name].squad.set(True)
                else:
                    self.squadAvailFor_SuicideMission[name].squad.set(False)

            updateBoolVar(self.armorCheckSelect_choice, self.upgradeArmor)
            updateBoolVar(self.shieldCheckSelect_choice, self.upgradeShield)
            updateBoolVar(self.cannonCheckSelect_choice, self.upgradeCannon)

            self.squadAvailFor_Vents = copy.copy(self.squadAvailFor_SuicideMission)
            killedThisRound = []
            if not self.upgradeArmor.get():
                name = armorCheck(self.squadAvailFor_Vents)
                if name == "Jack":
                    killedThisRound.append(f"The armor was penetrated, killing Jack.\n\n")
            if not self.upgradeShield.get():
                name = shieldCheck(self.squadAvailFor_Vents)
                killedThisRound.append(f"The shields gave out and {name} was killed.\n\n")
            if not self.upgradeCannon.get():
                name = weaponsCheck(self.squadAvailFor_Vents)
                killedThisRound.append(f"The main cannon could not disable the Collector Ship. Their counter attack killed {name}.\n\n")

            if len(killedThisRound) == 0:
                message_crewDied = "No squadmates killed this round."
            else:
                for i, m in enumerate(killedThisRound):
                    message_crewDied += m
            message_crewDied += self.crewMessage

            survived_list = list(self.squadAvailFor_Vents)
            survived_list.sort()
            message_crewRemain = f"After reaching the Collector Base, {len(survived_list)} squadmates remain:\n"
            for i, name in enumerate(survived_list):
                message_crewRemain += f"{i+1}) {name}\n"

        #### Report on Crew Deaths and Who Still Lives ####
        writeReport(self.crewDied_box, message_crewDied)
        writeReport(self.crewRemain_box, message_crewRemain)

        l = ["Legion", "Tali", "Kasumi", "Jacob", "Garrus", "Mordin", "Thane"]
        specialistVents_names = [name for name in l if name in survived_list]
        
        self.specialistVents_selector["values"] = specialistVents_names
        self.leaderVents_selector["values"] = survived_list
        self.squadVents1_selector["values"] = survived_list
        self.squadVents2_selector["values"] = survived_list

    def launchAttack(self):
        resetSelections(self, 2)
        message_crewDied, message_crewRemain = ("" for _ in range(2))
        survived_list = list(self.squadAvailFor_Vents)
        survived_list.sort()

        if ('' == self.squadVents1_choice.get()) or ('' == self.squadVents2_choice.get()) or ('' == self.leaderVents_choice.get()) or ('' == self.specialistVents_choice.get()):
            message_crewDied = "Please select two squad members, a fireteam leader, and specialist."
            message_crewRemain = ""
        else:
            for i, name in enumerate(survived_list):
                if (name == self.squadVents1_choice.get()) or (name==self.squadVents2_choice.get()):
                    self.squadAvailFor_Vents[name].squad.set(True)
                else:
                    self.squadAvailFor_Vents[name].squad.set(False)
                self.squadAvailFor_Vents[name].loyal.set(self.allSquadmates[name].loyal.get())

            self.squadAvailFor_LongWalk = copy.copy(self.squadAvailFor_Vents)
            name = ventCheck(self.squadAvailFor_LongWalk, self.leaderVents_choice.get(), self.specialistVents_choice.get())
            if name != "":
                message_crewDied = f"{name} was killed opening the door.\n\n"
            else:
                message_crewDied = "No squadmates killed this round.\n\n"
            message_crewDied += self.crewMessage
            
            survived_list = list(self.squadAvailFor_LongWalk)
            survived_list.sort()
            message_crewRemain = f"After launching an attack on the Collector base, {len(survived_list)} squadmates remain:\n"
            for i, name in enumerate(survived_list):
                message_crewRemain += f"{i+1}) {name}\n"

        #### Report on Crew Deaths and Who Still Lives ####
        writeReport(self.crewDied_box, message_crewDied)
        writeReport(self.crewRemain_box, message_crewRemain)

        l = ["Samara", "Morinth", "Jack", "Miranda", "Thane", "Jacob"]
        specialistBiotic_names = [name for name in l if name in survived_list]

        self.specialistLongWalk_selector["values"] = specialistBiotic_names
        self.leaderLongWalk_selector["values"] = survived_list
        self.squadLongWalk1_selector["values"] = survived_list
        self.squadLongWalk2_selector["values"] = survived_list
        
    def launchLongWalk(self):
        resetSelections(self, 3)
        message_crewDied, message_crewRemain = ("" for _ in range(2))
        survived_list = list(self.squadAvailFor_LongWalk)
        survived_list.sort()

        if ('' == self.squadLongWalk1_choice.get()) or ('' == self.squadLongWalk2_choice.get()) or ('' == self.leaderLongWalk_choice.get()) or ('' == self.specialistLongWalk_choice.get()):
            message_crewDied = "Please select two squad members, a fireteam leader, and specialist."
            message_crewRemain = ""
        else:
            for i, name in enumerate(survived_list):
                if (name == self.squadLongWalk1_choice.get()) or (name==self.squadLongWalk2_choice.get()):
                    self.squadAvailFor_LongWalk[name].squad.set(True)
                else:
                    self.squadAvailFor_LongWalk[name].squad.set(False)
                self.squadAvailFor_LongWalk[name].loyal.set(self.allSquadmates[name].loyal.get())

            self.squadAvailFor_FinalFight = copy.copy(self.squadAvailFor_LongWalk)

            name1 = bioticCheck(self.squadAvailFor_FinalFight, self.specialistLongWalk_choice.get())
            name2 = secondLeaderCheck(self.squadAvailFor_FinalFight, self.leaderLongWalk_choice.get())
            if (name1 != "") or (name2 != ""):
                message_crewDied = ""
                if (name1 != ""):
                    message_crewDied += f"{name1} was dragged away by the swarm.\n\n"
                if (name2 != ""):
                    message_crewDied += f"{name2} was killed holding the door.\n\n"
            else:
                message_crewDied = "No squadmates killed this round.\n\n"


            if self.missionsPrior.get() == 0:
                self.crewMessage = "You have found Dr. Chakwas and the entire crew alive!\n\n"
            elif self.missionsPrior.get() <=3:
                self.crewMessage = "You have found Dr. Chakwas and half your crew, but the rest are dead.\n\n"
            else:
                self.crewMessage = "You have found Dr. Chakwas alive, but the entire crew is dead.\n\n"
            message_crewDied += self.crewMessage

            survived_list = list(self.squadAvailFor_FinalFight)
            survived_list.sort()
            message_crewRemain = f"After the long walk through the seeker swarms, {len(survived_list)} squadmates remain:\n"
            for i, name in enumerate(survived_list):
                message_crewRemain += f"{i+1}) {name}\n"

        #### Report on Crew Deaths and Who Still Lives ####
        writeReport(self.crewDied_box, message_crewDied)
        writeReport(self.crewRemain_box, message_crewRemain)

        crewEscort_list = survived_list.copy()
        crewEscort_list.append("None")
        self.specialistFinalFight_selector["values"] = crewEscort_list
        self.squadFinalFight1_selector["values"] = survived_list
        self.squadFinalFight2_selector["values"] = survived_list
        
    def launchFinalFight(self):
        message_crewDied, message_crewRemain = ("" for _ in range(2))
        survived_list = list(self.squadAvailFor_FinalFight)
        survived_list.sort()
        dead_holdTheLine, dead_finalFight = ([] for _ in range(2))

        if ('' == self.squadFinalFight1_choice.get()) or ('' == self.squadFinalFight2_choice.get()) or ('' == self.specialistFinalFight_choice.get()):
            message_crewDied = "Please select two squad members, a fireteam leader, and specialist."
            message_crewRemain = ""
        else:
            for i, name in enumerate(survived_list):
                if (name == self.squadFinalFight1_choice.get()) or (name==self.squadFinalFight2_choice.get()):
                    self.squadAvailFor_FinalFight[name].squad.set(True)
                else:
                    self.squadAvailFor_FinalFight[name].squad.set(False)
                self.squadAvailFor_FinalFight[name].loyal.set(self.allSquadmates[name].loyal.get())

            survived = copy.copy(self.squadAvailFor_FinalFight)
            escortName = self.specialistFinalFight_choice.get()
            if escortName != "None":
                del survived[escortName]

            dead_holdTheLine = holdTheLine(survived)
            dead_finalFight = finalFight(survived)
            survived_list = list(survived)
            message_crewDied += "Dr. Chakwas"
            if self.missionsPrior.get() < 3:
                message_crewDied += " and the remaining crew"
            if (escortName == "None"):
                message_crewDied += " died returning to the ship.\n\n"
            else:
                message_crewDied += " safely returning to the ship.\n\n"
                if self.allSquadmates[escortName].loyal.get():
                    survived_list.append(escortName)
                else:
                    message_crewDied += f"{escortName} died en route to the ship as well.\n\n"
            survived_list.sort()

            len_dead = len(dead_holdTheLine)
            if (len_dead == 1):
                message_crewDied += f"{dead_holdTheLine[0]} died holding the line.\n\n"
            elif (len_dead == 2):
                message_crewDied += f"{dead_holdTheLine[0]} and {dead_holdTheLine[1]} died holding the line.\n\n"
            elif (len_dead > 2):
                for i in range(len_dead-1):
                    message_crewDied += f"{dead_holdTheLine[i]}, "
                message_crewDied += f" and {dead_holdTheLine[len_dead-1]} died holding the line.\n\n"

            len_dead = len(dead_finalFight)
            if len_dead > 0:
                message_crewDied += f"{dead_finalFight[0]}"
                if len_dead > 1:
                    message_crewDied += f" and {dead_finalFight[1]}"
                message_crewDied += f" died during the final battle.\n\n"

            if len(survived_list) < 2:
                message_crewDied += "Unfortunately, Commander Shepard also perished racing back to the ship."
                if len(survived_list) == 1:
                    message_crewRemain = f"Only {survived_list[0]} survived."
                else:
                    message_crewRemain = f"No survivors."
            else:
                message_crewRemain = f"After the Final Battle, Commander Shepard along with {len(survived_list)} squadmates escaped the Collector base:\n"
                for i, name in enumerate(survived_list):
                    message_crewRemain += f"{i+1}) {name}\n"

        #### Report on Crew Deaths and Who Still Lives ####
        writeReport(self.crewDied_box, message_crewDied)
        writeReport(self.crewRemain_box, message_crewRemain)














        #### Report on Crew Deaths and Who Still Lives ####
        writeReport(self.crewDied_box, message_crewDied)
        writeReport(self.crewRemain_box, message_crewRemain)


'''------------------------------------------------------------------------------------------
'''
if stinger:
	print()
	print("\nOkay. 3, 2, 1, let's jam! \n".center(152, "-"))
	print()

'''--------------------MAIN-------------------MAIN-------------------MAIN--------------------
'''
if __name__ == "__main__":
    root = tk.Tk()
    app = GUI(root)
    root.mainloop()


'''------------------------------------------------------------------------------------------
'''
if stinger:
	print()
	print("\nSee you, Space Cowboy...\n".center(150, "-"))
	print()
'''------------------------------------------------------------------------------------------
'''