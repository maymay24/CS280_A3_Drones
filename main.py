import mysql.connector
from drones import Drone, DroneStore
import shlex


class Application(object):
    """ Main application wrapper for processing input. """

    def __init__(self, conn):
        self._drones = DroneStore(conn)
        self._commands = {
            'list': self.list,
            'add': self.add,
            'update': self.update,
            'remove': self.remove,
            'allocate': self.allocate,
            'help': self.help,
        }
        self._connection = conn

    def main_loop(self):
        print('Welcome to DALSys')
        cont = True
        while cont:
            val = input('> ').strip().lower()
            cmd = None
            args = {}
            if len(val) == 0:
                continue
            try:
                parts = shlex.split(val)
                if parts[0] == 'quit':
                    cont = False
                    print('Exiting DALSys')
                else:
                    cmd = self._commands[parts[0]]
            except KeyError:
                print('!! Unknown command "%s" !!' % (val))

            if cmd is not None:
                args = parts[1:]
                try:
                    cmd(args)
                except Exception as ex:
                    print('!! %s !!' % (str(ex)))

    def add(self, args):
        """ Adds a new drone. """

        # check for exceptions
        if len(args) == 0:
            raise Exception('Name and Class are required')
        if len(args) == 1 and '-class=' in args[0]:
            raise Exception('Name is required')
        elif len(args) == 1 and '-class' not in args[0]:
            raise Exception('Class is required')

        # extract the fields
        name = args[0].strip()[6:]#7th character onwards to get rid of the "-name="
        class_type = int(args[1].strip().split('-class=')[1]) #get whatever comes after "-class="
        rescue = 0
        if len(args) == 3:
            rescue = 1

        # add the drone
        drone = Drone(None, name, class_type, rescue, None)
        self._drones.add(drone)

        # get the id of the newly added drone
        cursor = self._connection.cursor()
        query = 'SELECT ID FROM DroneStore ORDER BY ID DESC LIMIT 1'
        cursor.execute(query)
        id = cursor.fetchone()[0]
        cursor.close()

        if rescue:
            print(f'\nAdded rescue drone with ID {id:04}')
        else:
            print(f'\nAdded drone with ID {id:04}')

    def allocate(self, args):
        """ Allocates a drone to an operator. """
        if len(args) == 0:
            raise Exception('ID is required and Operator is required')
        elif len(args) == 1:
            try:
                int(args[0])
            except:
                raise Exception('ID is required')
            else:
                raise Exception('Operator is required')

        first_name, last_name = args[1].strip().split(' ', 1)

        self._drones.allocate(args[0], [first_name, last_name])

        # check for the allocation
        cursor = self._connection.cursor()
        query = 'SELECT ID FROM OperatorStore WHERE DroneID = %s'
        cursor.execute(query, (args[0],))
        id = cursor.fetchone()
        if id is not None:
            print(f'\nDrone allocated to {args[1]}')

    def help(self, args):
        """ Displays help information. """
        print("Valid commands are:")
        print("* list [- class =(1|2)] [- rescue ]")
        print("* add 'name ' -class =(1|2) [- rescue ]")
        print("* update id [- name ='name '] [- class =(1|2)] [- rescue ]")
        print("* remove id")
        print("* allocate id 'operator'")

    def list(self, args):
        """ Lists all the drones in the system. """

        # check the args
        if len(args) == 0:
            drones = self._drones.list_all()

        elif len(args) == 1:
            if '-class=1' in str(args):
                drones = self._drones.list_all(class_type=1)
            elif '-class=2' in str(args):
                drones = self._drones.list_all(class_type=2)
            elif '-rescue' in str(args):
                drones = self._drones.list_all(rescue=1)
            else:
                n = args[0].strip().split('-class=')[1]
                raise Exception(f'Unknown drone class {n}')
        else:
            if '-class=1' in str(args) and '-rescue' in str(args):
                drones = self._drones.list_all(class_type=1, rescue=1)
            elif '-class=2' in str(args) and '-rescue' in str(args):
                drones = self._drones.list_all(class_type=2, rescue=1)

        ############    print the drones    ###############
        num_of_drones = 0
        for drone in drones:
            if drone.operator is None:
                drone.operator = '<none>'
            else:
                cursor = self._connection.cursor()
                query = 'SELECT FirstName, LastName FROM OperatorStore WHERE DroneID = %s'
                cursor.execute(query, (drone.id,))
                first_name, last_name = cursor.fetchone()
                drone.operator = f'{first_name} {last_name}'
                cursor.close()
            if drone.rescue == 0:
                drone.rescue = 'No'
            else:
                drone.rescue = 'Yes'
            if drone.class_type == 1:
                drone.class_type = 'One'
            else:
                drone.class_type = 'Two'

            num_of_drones += 1
            if num_of_drones == 1:
                print(
                    f'{"ID": <10} {"Name": <20} {"Class": <10} {"Rescue": <10} {"Operator": <10}')
            print(
                f'{drone.id: <10} {drone.name: <20} {drone.class_type: <10} {drone.rescue: <10} {drone.operator: <10}')

        if num_of_drones == 1:
            print('\n1 drone listed')
        else:
            print(f'\n{num_of_drones} drones listed')

    def remove(self, args):
        """ Removes a drone. """
        if len(args) == 0:
            raise Exception('ID is required')
        else:
            id = args[0].strip()
            self._drones.remove(id)
            print('\nDrone removed')

    def update(self, args):
        """ Updates the details for a drone. """
        try:
            id = int(args[0].strip())
        except:
            raise Exception('ID is required')

        if len(args) == 1:
            query = f'UPDATE DroneStore SET Rescue = 0 WHERE ID = {id}'
            self._drones.update(id, query=query)
        elif len(args) == 2:
            if '-name' in str(args):
                name = args[1].strip().split('-name=', 1)[1]
                query = f'UPDATE DroneStore SET Rescue = 0, Name = "{name}" WHERE ID = {id}'
                self._drones.update(id, query=query)
            elif '-class=' in str(args):
                class_type = args[1].strip().split('-class=')[1]
                query = f'UPDATE DroneStore SET Rescue = 0, ClassType = {class_type} WHERE ID = {id}'
                self._drones.update(id, query=query)
            else:
                query = f'UPDATE DroneStore SET Rescue = 1 WHERE ID = {id}'
                self._drones.update(id, query=query)
        elif len(args) == 3:
            if '-name=' and '-class=' in str(args):
                name = args[1].strip().split('-name=')[1]
                class_type = args[2].strip().split('-class=')[1]
                query = f'UPDATE DroneStore SET Rescue = 0, Name = "{name}", ClassType = {class_type} WHERE ID = {id}'
                self._drones.update(id, query=query)
            elif '-name=' and '-rescue' in str(args):
                name = args[1].strip().split('-name=')[1]
                query = f'UPDATE DroneStore SET Rescue = 1, Name = "{name}" WHERE ID = {id}'
                self._drones.update(id, query=query)
            else:
                class_type = args[1].strip().split('-class=')[1]
                query = f'UPDATE DroneStore SET Rescue = 0, ClassType = {class_type} WHERE ID = {id}'
                self._drones.update(id, query=query)
        else:
            name = args[1].strip().split('-name=')[1]
            class_type = args[2].strip().split('-class=')[1]
            query = f'UPDATE DroneStore SET Rescue = 1, Name = "{name}", ClassType = {class_type} WHERE ID = {id}'
            self._drones.update(id, query=query)


if __name__ == '__main__':
    conn = mysql.connector.connect(
        user='mcho139',
        password='b6f002ef',        
        host='studdb-mysql.fos.auckland.ac.nz',   
        database='stu_mcho139_COMPSCI_280_C_S2_2019',       
        charset='utf8',
        use_pure = True 
    )
    print('connected')
    app = Application(conn)
    app.main_loop()
    conn.close()
