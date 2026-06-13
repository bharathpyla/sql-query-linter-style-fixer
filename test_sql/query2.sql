select o.orderId, o.totalAmount, c.customerName, (select max(orderDate) from orders sub where sub.customerId = c.customerId) as lastOrderDate
from orders o, customers c
where o.customerId = c.customerId and o.status = 'COMPLETED';
