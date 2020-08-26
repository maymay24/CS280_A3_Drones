create table DroneStore(
	ID int not null auto_increment,
    Name varchar(100) not null,
    ClassType int not null,
    Rescue boolean,
    OperatorID int unique,
    primary key(ID),
    foreign key(OperatorID) references Operator(ID)
); 

create table OperatorStore(
	ID int not null auto_increment,
    FirstName varchar(100) not null,
    LastName varchar(100),
    DateOfBirth date not null,
    DroneLicense tinyint,
    RescueEndorsement boolean not null,
    RescueOperations int,
    primary key(ID)
);