select * from OperatorStore where FirstName="John" and LastName = "Doe";
select * from OperatorStore order by LastName asc, FirstName asc;
select * from DroneStore where OperatorID is not null;
select * from DroneStore where OperatorID is null;

select DroneStore.*, OperatorStore.FirstName, OperatorStore.LastName from DroneStore
left join OperatorStore on DroneStore.OperatorID = OperatorStore.ID;