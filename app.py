import mysql.connector
import tkinter as tk
import tkinter.ttk as ttk

from drones import Drone, DroneStore
from operators import Operator, OperatorStore


class Application(object):
    """ Main application view - displays the menu. """

    def __init__(self, conn):
        # Initialise the stores
        self.drones = DroneStore(conn)
        self.operators = OperatorStore(conn)

        # Initialise the GUI window
        self.root = tk.Tk()
        self.root.title('Drone Allocation and Localisation')
        frame = tk.Frame(self.root)
        frame.pack(padx=10, pady=10)

        # Add in the buttons
        drone_button = tk.Button(
            frame, text="View Drones", command=self.view_drones, width=40, padx=5, pady=5)
        drone_button.pack(side=tk.TOP)
        operator_button = tk.Button(
            frame, text="View Operators", command=self.view_operators, width=40, padx=5, pady=5)
        operator_button.pack(side=tk.TOP)
        exit_button = tk.Button(frame, text="Exit System",
                                command=quit, width=40, padx=5, pady=5)
        exit_button.pack(side=tk.TOP)

    def main_loop(self):
        """ Main execution loop - start Tkinter. """
        self.root.mainloop()

    def view_operators(self):
        """ Display the operators. """
        # Instantiate the operators window
        # Display the window and wait
        wnd = OperatorListWindow(self)
        self.root.wait_window(wnd.root)

    def view_drones(self):
        """ Display the drones. """
        wnd = DroneListWindow(self)
        self.root.wait_window(wnd.root)


class ListWindow(object):
    """ Base list window. """

    def __init__(self, parent, title):
        # Add a variable to hold the stores
        self.drones = parent.drones
        self.operators = parent.operators

        # Initialise the new top-level window (modal dialog)
        self._parent = parent.root
        self.root = tk.Toplevel(parent.root)
        self.root.title(title)
        self.root.transient(parent.root)
        self.root.grab_set()

        # Initialise the top level frame
        self.frame = tk.Frame(self.root)
        self.frame.pack(side=tk.TOP, fill=tk.BOTH,
                        expand=tk.Y, padx=10, pady=10)
        

    def add_list(self, columns, edit_action):
        # Add the list
        self.tree = ttk.Treeview(self.frame, columns=columns, show='headings')
        for col in columns:
            self.tree.heading(col, text=col.title())
        ysb = ttk.Scrollbar(self.frame, orient=tk.VERTICAL,
                            command=self.tree.yview)
        xsb = ttk.Scrollbar(self.frame, orient=tk.HORIZONTAL,
                            command=self.tree.xview)
        self.tree['yscroll'] = ysb.set
        self.tree['xscroll'] = xsb.set
        self.tree.bind("<Double-1>", edit_action)

        # Add tree and scrollbars to frame
        self.tree.grid(in_=self.frame, row=0, column=0, sticky=tk.NSEW)
        ysb.grid(in_=self.frame, row=0, column=1, sticky=tk.NS)
        xsb.grid(in_=self.frame, row=1, column=0, sticky=tk.EW)

        # Set frame resize priorities
        self.frame.rowconfigure(0, weight=1)
        self.frame.columnconfigure(0, weight=1)

    def close(self):
        """ Closes the list window. """
        self.root.destroy()


class DroneListWindow(ListWindow):
    """ Window to display a list of drones. """

    def __init__(self, parent):
        super(DroneListWindow, self).__init__(parent, 'Drones')

        # Add the list and fill it with data
        columns = ('id', 'name', 'class', 'rescue', 'operator')
        self.add_list(columns, self.edit_drone)
        self.populate_data()

        # Add the command buttons
        add_button = tk.Button(self.frame, text="Add Drone",
                               command=self.add_drone, width=20, padx=5, pady=5)
        add_button.grid(in_=self.frame, row=2, column=0, sticky=tk.E)
        exit_button = tk.Button(self.frame, text="Close",
                                command=self.close, width=20, padx=5, pady=5)
        exit_button.grid(in_=self.frame, row=3, column=0, sticky=tk.E)

    def populate_data(self):
        """ Populates the data in the view. """
        self.tree.delete(*self.tree.get_children())
        for drone in self.drones.list_all():  
            values = (drone.id, drone.name, drone.class_type, drone.rescue, drone.operator)
            self.tree.insert('', 'end', values = values)

    def add_drone(self):
        """ Starts a new drone and displays it in the list. """
        
        #get number of items in tree
        num_items = len(self.tree.get_children())
        
        #set new drone ID 
        id = num_items + 1
        # Start a new drone instance
        drone = Drone(id, None, None, None, None)

        # Display the drone
        self.view_drone(drone, self._save_new_drone)

    def _save_new_drone(self, drone):
        """ Saves the drone in the store and updates the list. """
        self.drones.add(drone)
        self.populate_data()

    def edit_drone(self, event):
        """ Retrieves the drone and shows it in the editor. """
        # Retrieve the identifer of the drone
        item = self.tree.item(self.tree.focus())
        item_id = item['values'][0]

        # Load the drone from the store
        drone = self.drones.get(item_id)
        # Display the drone
        self.view_drone(drone, self._update_drone)

    def _update_drone(self, drone):
        """ Saves the new details of the drone. """
        self.drones.update(drone)
        self.populate_data()

    def view_drone(self, drone, save_action):
        """ Displays the drone editor. """
        wnd = DroneEditorWindow(self, drone, save_action)
        self.root.wait_window(wnd.root)

class OperatorListWindow(ListWindow):
    """ Window to display a list of operators. """

    def __init__(self, parent):
        super(OperatorListWindow, self).__init__(parent, 'Operators')

        # Add the list and fill it with data
        columns = ('id', 'name', 'class', 'rescue', 'operations', 'drone')
        self.add_list(columns, self.edit_operator)
        self.populate_data()

        # Add the command buttons
        add_button = tk.Button(self.frame, text="Add Operator",
                               command=self.add_operator, width=20, padx=5, pady=5)
        add_button.grid(in_=self.frame, row=2, column=0, sticky=tk.E)
        exit_button = tk.Button(self.frame, text="Close",
                                command=self.close, width=20, padx=5, pady=5)
        exit_button.grid(in_=self.frame, row=3, column=0, sticky=tk.E)

    def populate_data(self):
        """ Populates the data in the view. """
        self.tree.delete(*self.tree.get_children())
        for operator in self.operators.list_all():  
            #Get drone assigned to operator
            for drone in self.drones.list_all():
                if drone.operator != None:
                    if drone.operator == operator.id:
                        #Get drone name to display in window
                        drone_operator = str(drone.id) +": " + drone.name
                        if drone.class_type == 1:
                            class_type = "One"
                        elif drone.class_type == 2:
                            class_type = "Two"
                else:
                    drone_operator = "<None>"
                    class_type = "One"
                    
            if operator.rescue_endorsement == 1:
                rescue_endorsement = "Yes"
            elif operator.rescue_endorsement == 0:
                rescue_endorsement = "No"
                
                
            name = operator.first_name + " " + operator.family_name
            values = (operator.id, name, class_type, rescue_endorsement, operator.operations, drone_operator)
            self.tree.insert('', 'end', values = values)
            
            #Hide ID column
            self.tree["displaycolumns"] = ("name", "class", "rescue", "operations", "drone")

    def add_operator(self):
        """ Starts a new operator and displays it in the list. """
        
        #get number of items in tree
        num_items = len(self.tree.get_children())
        
        #set new operator ID 
        id = num_items + 1
        operator = Operator(id, None, None, None, None, None, None, None)

        # Display the operator
        self.view_operator(operator, self._save_new_operator)

    def _save_new_operator(self, operator):
        """ Saves the operator in the store and updates the list. """
        self.operators._add(operator)
        self.populate_data()

    def edit_operator(self, event):
        """ Retrieves the operator and shows it in the editor. """
        # Retrieve the identifer of the operator
        item = self.tree.item(self.tree.focus())
        item_id = item['values'][0]

        # Load the operator from the store
        operator = self.operators.get(item_id)
        self.view_operator(operator, self._update_operator)

    def _update_operator(self, operator):
        """ Saves the new details of the operator. """
        self.operators.update(operator)
        self.populate_data()

    def view_operator(self, operator, save_action):
        """ Displays the operator editor. """
        wnd = OperatorEditorWindow(self, operator, save_action)
        self.root.wait_window(wnd.root)

class EditorWindow(object):
    """ Base editor window. """

    def __init__(self, parent, title, save_action):
        # Initialise the new top-level window (modal dialog)
        self._parent = parent.root
        self.root = tk.Toplevel(parent.root)
        self.root.title(title)
        self.root.transient(parent.root)
        self.root.grab_set()

        # Initialise the top level frame
        self.frame = tk.Frame(self.root)
        self.frame.pack(side=tk.TOP, fill=tk.BOTH,
                        expand=tk.Y, padx=5, pady=5)

        # Add the editor widgets
        last_row = self.add_editor_widgets()

        # Add the command buttons
        add_button = tk.Button(self.frame, text="Save",
                               command=save_action, width=15, padx=5, pady=5)
        add_button.grid(in_=self.frame, row=last_row + 1, column=1, sticky=tk.E)
        exit_button = tk.Button(self.frame, text="Close",
                                command=self.close, width=15, padx=5, pady=5)
        exit_button.grid(in_=self.frame, row=last_row + 2, column=1, sticky=tk.E)

    def add_editor_widgets(self):
        """ Adds the editor widgets to the frame - this needs to be overriden in inherited classes. 
        This function should return the row number of the last row added - EditorWindow uses this
        to correctly display the buttons. """
        return -1

    def close(self):
        """ Closes the editor window. """
        self.root.destroy()

class OperatorEditorWindow(EditorWindow):
    """ Editor window for operators. """
    def __init__(self, parent, operator, save_action):

        #Set window title depending on whether operator is new or not
        self._operator = operator
        self._save_action = save_action
        name = operator.first_name
        if name is None:
            name = "<new>"
        else:
            name = operator.first_name + " " + operator.family_name
        super(OperatorEditorWindow, self).__init__(parent, 'Operator: ' + name, self.save_operator)
        

    def add_editor_widgets(self):
        """ Adds the widgets for editing a operator. """
        # First Name Label
        tk.Label(self.frame, text="First Name:",
                 padx=5, pady=5).grid(in_=self.frame,  row=0, column=0, sticky=tk.W)   
        #First Name Entry
        self.first_name = tk.Entry(self.frame, width = 40)
        self.first_name.grid(in_=self.frame, row = 0, column=1)
        #Insert data if existing
        if self._operator.first_name != None:
            self.first_name.insert(0, self._operator.first_name)   
            
        # Last Name Label
        tk.Label(self.frame, text="Last Name:",
                 padx=5, pady=5).grid(in_=self.frame,  row=1, column=0, sticky=tk.W)   
        #Last Name Entry
        self.last_name = tk.Entry(self.frame, width = 40)
        self.last_name.grid(in_=self.frame, row = 1, column=1)
        #Insert data if existing
        if self._operator.family_name != None:
            self.last_name.insert(0, self._operator.family_name)
            
        #License label
        tk.Label(self.frame, text="Drone License:",
                 padx=5, pady=5).grid(in_=self.frame, row=2, column=0, sticky=tk.W)
        #License entry
        self.license = ttk.Combobox(self.frame, values = ["One", "Two"])
        self.license.grid(in_=self.frame, row=2, column=1, sticky=tk.W)  
        #Insert data if existing
        if self._operator.drone_license != None:  
            #Change license value to text to display in window
            if self._operator.drone_license == 1:
                self._operator.drone_license = "One"
            elif self._operator.drone_license == 2:
                self._operator.drone_license = "Two"
            self.license.insert(0, self._operator.drone_license)
        else:
            #Set default value
            self._operator.drone_license = 1
            drone_license = "One"
            self.license.insert(0, drone_license)
            
        #Rescue label
        tk.Label(self.frame, text="Rescue Endorsement:",
                 padx=5, pady=5).grid(in_=self.frame, row=3, column=0, sticky=tk.W)
        #Rescue read-only text
        self.rescue_endorsement = tk.Entry(self.frame)  
        self.rescue_endorsement.grid(in_=self.frame, row=3, column =1, sticky=tk.W)  
        #Insert data if existing
        if self._operator.rescue_endorsement != None:
            #Checks for setting rescue endorsement flag
            if self._operator.rescue_endorsement == 1: 
                rescue_end = "Yes"
            else:
                rescue_end = "No"
                
            if self._operator.operations >=5:
                rescue_end = "Yes"
            else:
                rescue_end = "No"
            self.rescue_endorsement.insert(0, rescue_end)
        else:
            #Set default value
            self.rescue_endorsement.insert(0, "No")
            
        #Make widget read-only
        self.rescue_endorsement.config(state="readonly")
        
        #operations label
        tk.Label(self.frame, text="Number of operations:",
                 padx=5, pady=5).grid(in_=self.frame, row=4, column=0, sticky=tk.W)
        #operations spinbox 
        var = tk.IntVar()
        self.operations = tk.Spinbox(self.frame, textvariable = var, from_=0, to=100)
        self.operations.grid(in_=self.frame, row = 4, column=1, sticky=tk.W)
        #Insert data if existing
        if self._operator.operations != None:
            self.operations.insert(0, self._operator.operations)
            var.set(self._operator.operations)
        else: 
            #Set default value
            var.set(3)
        
        #Return row number of last row added
        return 4
    
    def save_operator(self):
        """ Updates the operator details and calls the save action. """
        self._operator.first_name = self.first_name.get()
        self._operator.last_name = self.last_name.get()
        #Change license info from text to int
        if self.license.get() == "One":
            self._operator.drone_license = 1
        elif self.license.get() == "Two":
            self._operator.drone_license = 2
        #Set rescue endorsement according to no. of operations
        if int(self.operations.get())>=5:
            self._operator.rescue_endorsement=1
        else:
            self._operator.rescue_endorsement=0
        self._operator.operations = self.operations.get()
        self._save_action(self._operator)

class DroneEditorWindow(EditorWindow):
    """ Editor window for drones. """

    def __init__(self, parent, drone, save_action):
        
        #Set window title depending on whether drone is new or not
        self._drone = drone
        self._save_action = save_action
        name = drone.name
        if name is None:
            name = "<new>"
        super(DroneEditorWindow, self).__init__(parent, 'Drone: ' + name, self.save_drone)

    def add_editor_widgets(self):
        """ Adds the widgets for editing a drone. """
        
        # Name Label
        tk.Label(self.frame, text="Name:",
                 padx=5, pady=5).grid(in_=self.frame,  row=0, column=0, sticky=tk.W)   
        #Name Entry
        self.name = tk.Entry(self.frame, width = 40)
        self.name.grid(in_=self.frame, row = 0, column=1)
        #Insert data if existing
        if self._drone.name != None:
            self.name.insert(0, self._drone.name)   
            
        #Class label
        tk.Label(self.frame, text="Drone Class:",
                 padx=5, pady=5).grid(in_=self.frame, row =1, column=0, sticky=tk.W)
        #Class entry
        self.drone_class = ttk.Combobox(self.frame, values = ["One", "Two"])
        self.drone_class.grid(in_=self.frame, row = 1, column=1, sticky=tk.W)
        #Insert data if existing
        if self._drone.class_type != None:
            if self._drone.class_type == 1:
                self._drone.class_type = "One"
            else:
                self._drone.class_type = "Two"
            self.drone_class.insert(0, self._drone.class_type)
        else:
            #Set default value
            self._drone.class_type = 1
            self.drone_class.insert(0, "One")
            
        #Rescue label
        tk.Label(self.frame, text="Rescue Drone:",
                 padx=5, pady=5).grid(in_=self.frame, row=2, column=0, sticky=tk.W)
        #Rescue entry
        self.rescue = ttk.Combobox(self.frame, values = ["Yes", "No"])
        self.rescue.grid(in_=self.frame, row=2, column=1, sticky=tk.W)
        #Insert data if existing
        if self._drone.rescue != None:
            if self._drone.rescue == 1:
                self._drone.rescue = "Yes"
            elif self._drone.rescue == 0:
                self._drone.rescue = "No"
            self.rescue.insert(0, self._drone.rescue)
        else:
            #Set default value
            self._drone.resuce = 0
            self.rescue.insert(0, "No")
        
        #return row number of last row added
        return 2
    
    def save_drone(self):
        """ Updates the drone details and calls the save action. """
        self._drone.name = self.name.get()
        if self.drone_class.get() == "One":
            self._drone.class_type  = 1
        elif self.drone_class.get() == "Two":
            self._drone.class_type  = 2
        if self.rescue.get() == "Yes":
            self._drone.rescue = 1
        elif self.rescue.get() == "No":
            self._drone.rescue = 0
        self._save_action(self._drone)


if __name__ == '__main__':
    conn = mysql.connector.connect(
        user='',
        password='',        
        host='',   
        database='',       
        charset='utf8',
        use_pure = True )
    app = Application(conn)
    app.main_loop()
    conn.close()
