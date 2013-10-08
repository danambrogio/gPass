#####################################################################
#   Graphical Password Generator  - gPass.pyw
#
#   Version 3.1.0
#
#   October 7, 2013
#
#   Written by Dan Ambrogio
#
#####################################################################
#
#   Notes on password-generating algorithms:
#           Version 1.0's password calculation took 3 hashed characters
#       from each user input and constructed a password out of them.
#       This meant that a user would have 6 shared characters for a
#       given pair of passwords shared between all sites. This is not
#       ideal, obviously.
#               password pattern: 12s12s12s
#           Version 2.0 improved this by using 2 characters
#       based on each of the passwords, and 5 based on the site,
#       bringing the number of shared characters down to 4.
#               password pattern: 1212sssss
#           Version 3.0 further improved this by adding the 3 inputs
#       together *before* hashing, to prevent any characters from being
#       shared between sites.
#               password pattern: ?????????
#
#
#   
#   Version History:
#       Major version numbers indicate a new and hopefully
#       improved password-calculation. Minor version numbers
#       indicate improved functionality and ease-of-use changes.
#       Letters indicate bugfixes.
#
#   3.1.0 - Added automatic selection of generated
#       passwords for easier copy-pasting and the
#       ability to change output font. Better highlighting
#   3.0.0 - New formula for calculating passwords shares
#       no characters between passwords to add more
#       variety among any given user's passwords
#   2.1.0 - Added <Escape> key functionality for
#       clearing the inputs and resetting the cursor    
#   2.0.0 - New formula for calculating passwords
#       puts a higher focus on the site so that
#       a single user's passwords have more variation
#   1.0.0 - Release
#
#####################################################################

from tkinter import *
import string
import hashlib
import re

#############
#Global vars#
#############
version = "3.1.0"

#Pick your preferred font or none for default
#chosenFont = ("Courier", "8")
#chosenFont = ("Times New Roman", "10")


class Application(Frame):
    def __init__(self, master=None):
        Frame.__init__(self, master)
        self.pack()
        self.createWidgets()
        master.bind('<Escape>', self.OnPressEsc)
        
    def createWidgets(self):
        '''
        This function creates the buttons, text fields, and 
        entry boxes in the GUI.
        '''
        
        ##Labels##
        #first label
        self.label1 = Label(self)
        self.label1["text"] = "First Password:"
        self.label1.grid(column="0", row="0")
        
        #second label
        self.label2 = Label(self)
        self.label2["text"] = "Second Password:"
        self.label2.grid(column="0", row="1")
        
        #third label
        self.label3 = Label(self)
        self.label3["text"] = "Site:"
        self.label3.grid(column="0", row="2")
        
        #Output label 1
        self.outputsite = Label(self)
        self.outputsite["text"] = "Site:"
        self.outputsite.grid(column="0", row="4")
        
        #Output label 2
        self.outputpass = Label(self)
        self.outputpass["text"] = "Password:"
        self.outputpass.grid(column="1", row="4")
        
        #Output label 3
        self.outputsite2 = Label(self)
        self.outputsite2["text"] = ""
        self.outputsite2.grid(column="0", row="5")
        
        
        ##Text Entries##
        #Entry for password 1
        self.entrypassword1 = Entry(self)
        self.password1 = StringVar()
        self.entrypassword1["textvariable"] = self.password1
        self.entrypassword1.grid(column="1", row="0")
        self.entrypassword1.focus_set()
        
        #Entry for password 2
        self.entrypassword2 = Entry(self)
        self.password2 = StringVar()
        self.entrypassword2["textvariable"] = self.password2
        self.entrypassword2.grid(column="1", row="1")
        
        #Entry for site
        self.site = Entry(self)
        self.siteentry = StringVar()
        self.site["textvariable"] = self.siteentry
        self.site.grid(column="1", row="2")
        self.site.bind("<Return>", self.OnPressEnter)
        
        #Entry which is actually an output for password
        self.genpass = Entry(self)
        self.generatedpassword = StringVar()
        self.generatedpassword.set("")
        self.genpass["textvariable"] = self.generatedpassword
        self.genpass.grid(column="1", row="5")
        self.genpass.config(selectbackground="#C0C0C0", selectforeground="#000000")
        #Changes the font of the output, if desired
        try:
            self.genpass.config(font=chosenFont)
        except:
            pass
        
        
        ##Buttons##
        #Button to Generate password
        self.calc = Button(self, text="Generate", command=self.OnGenerate)
        self.calc.grid(column="0", row="3", columnspan=2)
        
        #Button to clear fields
        self.clear = Button(self, text="Clear", command=self.OnClickClear)
        self.clear.grid(column=1, row="6")

    def OnGenerate(self):
        '''
        Event handler for the "Generate" button takes input and
        passes it to the password generator functions.
        '''
    
        #Get the input data
        pass1 = self.password1.get()
        pass2 = self.password2.get()
        sitename = self.siteentry.get()
        self.outputsite2["text"] = sitename
        
        #Clear the input fields
        self.password1.set("")
        self.password2.set("")
        self.siteentry.set("")
        
        #Generate the password
        self.Generate(pass1, pass2, sitename)
        
        #Select the password
        self.genpass.focus_set()
        self.genpass.selection_range(0, END)
        self.genpass.icursor(END)
        
    def Generate(self, pass1, pass2, sitename):
        '''
        This function loops while calling the gen_password function until
        it has a valid password, then returns the valid password.
        '''
        valid = False
        count = 0
        while valid == False:
            output = self.gen_pword(pass1, pass2, sitename, count)
            if (self.check_pword(output) == True):
                valid = True
            else: count += 1
            
        self.generatedpassword.set(output)
            
    def gen_pword(self, pass1, pass2, sitename, trial = 0):
        '''
        This function generates a password based on the two user passwords
        and the site.
        The 'pass1' variable is a string containing the first user password.
        The 'pass2' variable is a string containing the second user password.
        The 'sitename' variable is a string containing the website to generate
        the password for.
        The 'trial' variable is an integer used when the generated password
        does not meet standards; it increments the position in the hash to use
        to try again for a valid password.
        '''
        
        #Combine the passwords and hash them with SHA224 to get hex values
        hashme = pass1+pass2+sitename
        hashedme = hashlib.sha224(bytearray(hashme, 'utf-8')).hexdigest()
        
        # Take pseudorandom values from the hash and combine them
        out = ""
        for i in range(3):
            out += hashedme[1+i+trial]
            out += hashedme[5+i-trial]
            out += hashedme[20-i-trial]
        
        # Convert the first lowercase letter to uppercase
        if (sum(c in string.ascii_lowercase for c in out)) > 1:
            out = re.sub('[a-f]', lambda x: x.group(0).upper(), out, 1)
        
        # Return the generated password
        return (out)
    
    def check_pword(self, password):
        '''
        This function checks the generated password to make sure it complies
        to password standards. The generated password should have lowercase,
        uppercase, and numbers
        The 'password' variable is a string containing the password to be
        checked. The function returns True if it is a valid password.
        '''
        
        # Makes a string containing all the digits and upper/lower characters
        valid = (string.digits + string.ascii_lowercase +
                 string.ascii_uppercase)


        # Checks that each character is a number or letter
        if any(i in valid for i in password):
            if (sum(b in string.digits for b in password)) > 0:
                if (sum(c in string.ascii_lowercase for c in password)) > 0:
                    return True
        else: 
            return False    
    
    def OnPressEnter(self, event):
        '''
        This function maps the <Enter> key to the "Generate" button.
        '''
        self.OnGenerate()
        
    def OnPressEsc(self, event):
        '''
        This function maps the <Escape> key to the "Clear" button.
        '''
        self.OnClickClear()
        
    def OnClickClear(self):
        '''
        This function resets the application by clearing the fields
        and resetting the cursor position to the program's initial
        state.
        '''
        #Clears the input fields
        self.password1.set("")
        self.password2.set("")
        self.siteentry.set("")
        
        #Clears the output fields
        self.outputsite2["text"] = ""
        self.generatedpassword.set("")
        
        #Sets the cursor to the first input
        self.entrypassword1.focus_set()
        
if __name__ == "__main__":
    root = Tk()
    root.geometry('-10+10') #Window placed in top left corner of screen
    app = Application(master=root)
    app.master.title('gPass ' + version)    #Window title
    app.master.maxsize(500, 180)            #Maximum window size
    app.mainloop()