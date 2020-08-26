from datetime import date


class Operator(object):
    """ Stores details on an operator. """

    def __init__(self, id, first_name, family_name, date_of_birth=None, drone_license=None, rescue_endorsement=False, operations=0, drone=None):
        self.id = id
        self.first_name = first_name
        self.family_name = family_name
        self.date_of_birth = date_of_birth
        self.drone_license = drone_license
        self.rescue_endorsement = rescue_endorsement
        self.operations = operations
        self.drone = drone


class OperatorAction(object):
    """ A pending action on the OperatorStore. """

    def __init__(self, operator, commit_action):
        self.operator = operator
        self.messages = []
        self._commit_action = commit_action
        self._committed = False

    def add_message(self, message):
        """ Adds a message to the action. """
        self.messages.append(message)

    def is_valid(self):
        """ Returns True if the action is valid, False otherwise. """
        return len(self.messages) == 0

    def commit(self):
        """ Commits (performs) this action. """
        if self._committed:
            raise Exception("Action has already been committed")

        self._commit_action(self.operator)
        self._committed = True


class OperatorStore(object):
    """ Stores the operators. """

    def __init__(self, conn=None):
        self._operators = {}
        self._last_id = 0
        self._conn = conn

    def add(self, operator):
        """ Starts adding a new operator to the store. """
        action = OperatorAction(operator, self._add)
        check_age = True
        if operator.first_name is None:
            action.add_message("First name is required")
        if operator.date_of_birth is None:
            action.add_message("Date of birth is required")
            check_age = False
        if operator.drone_license is None:
            action.add_message("Drone license is required")
        if check_age and operator.drone_license == 2:
            today = date.today()
            age = today.year - operator.date_of_birth.year - \
                ((today.month, today.day) < (
                    operator.date_of_birth.month, operator.date_of_birth.day))
            if age < 20:
                action.add_message(
                    "Operator should be at least twenty to hold a class 2 license")
        if operator.rescue_endorsement and operator.operations < 5:
            action.add_message(
                "To hold a rescue drone endorsement, the operator must have been involved in ﬁve prior rescue operations")
        return action

    def _add(self, operator):
        """ Adds a new operator to the store. """
        cursor = self._conn.cursor()
        query = 'INSERT INTO OperatorStore (FirstName, LastName, DroneLicense, RescueEndorsement, RescueOperations) VALUES (%s, %s, %s, %s, %s)'
        cursor.execute(query, (operator.first_name, operator.last_name, 
                               operator.drone_license, operator.rescue_endorsement, operator.operations))
        cursor.close()

    def remove(self, operator):
        """ Removes a operator from the store. """
        if not operator.id in self._operators:
            raise Exception('Operator does not exist in store')
        else:
            del self._operators[operator.id]

    def get(self, id):
        """ Retrieves a operator from the store by its ID or name. """
        cursor = self._conn.cursor()
        query = 'SELECT * FROM OperatorStore WHERE ID = %s'
        cursor.execute(query, (id,))
        record = cursor.fetchone()

        if cursor.rowcount == 0 or record is None:
            raise Exception('Unknown drone')
        else:
            record = list(record)
            return Operator(*record)
        cursor.close()
        

    def list_all(self):
        """ Lists all the _operators in the system. """
        cursor = self._conn.cursor()
        query = "SELECT * FROM OperatorStore ORDER BY LastName"
        cursor.execute(query)
        records = cursor.fetchall()
        cursor.close()
        
        operators = {}
        
        for record in records:
            record = list(record)
            operator = Operator(*record)
            operators[operator.id] = operator

        for operator in operators:
            yield operators[operator]
            
    def update(self, operator):
        cursor = self._conn.cursor()
        query = 'UPDATE OperatorStore SET FirstName=%s, LastName=%s, DateOfBirth=%s, DroneLicense=%s, RescueEndorsement=%s, RescueOperations=%s WHERE ID=%s'
        cursor.execute(query, (operator.first_name, operator.family_name, operator.date_of_birth, operator.drone_license, operator.rescue_endorsement, operator.operations, operator.id))
        cursor.close()
        self._conn.commit()

    def save(self):
        """ Saves the store to the database. """
        pass    # TODO: we don't have a database yet
