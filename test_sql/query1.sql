select userId, employeeShiftStart, (select count(1) from roles r where r.userId = e.userId) as roleCount, *
from employeeTable e, shiftDetails s
where e.empId = s.employeeId and e.status = 'ACTIVE';
