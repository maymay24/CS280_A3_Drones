insert into OperatorStore(ID, FirstName, LastName, DateOfBirth, RescueEndorsement, RescueOperations)
values (1, "John", "Doe", '2003-01-01', False, 0); 
insert into OperatorStore(ID, FirstName, LastName, DateOfBirth, DroneLicense, RescueEndorsement, RescueOperations)
values (2, "Josh", "Doe", '2003-01-01', 1, False, 0); 
insert into OperatorStore(ID, FirstName, LastName, DateOfBirth, DroneLicense, RescueEndorsement, RescueOperations)
values (3, "Jake", "Doe", '1990-01-01', 2, False, 0); 
insert into OperatorStore(ID, FirstName, LastName, DateOfBirth, DroneLicense, RescueEndorsement, RescueOperations)
values (4, "Jane", "Doe", '1990-01-01', 2, True, 10); 

insert into DroneStore (ID,  Name, ClassType)
values (1, "Drone1", 1);
insert into DroneStore (ID,  Name, ClassType)
values (2, "Drone2", 2);
insert into DroneStore (ID,  Name, ClassType, Rescue)
values (3, "Drone3", 2, True);

insert into DroneStore (ID,  Name, ClassType, Rescue, OperatorID)
values (4, "Drone4", 1, False, 2);
insert into DroneStore (ID,  Name, ClassType, Rescue, OperatorID)
values (5, "Drone5", 3, True, 3);