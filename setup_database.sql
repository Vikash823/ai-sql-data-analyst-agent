CREATE TABLE IF NOT EXISTS public.orders (
    order_id SERIAL PRIMARY KEY,
    store_id VARCHAR(20),
    city VARCHAR(50),
    order_date DATE,
    order_amount NUMERIC(10,2),
    order_status VARCHAR(20)
);

INSERT INTO public.orders
(store_id, city, order_date, order_amount, order_status)
VALUES
('S101','Mumbai','2026-10-18',1200,'DELIVERED'),
('S101','Mumbai','2026-10-18',800,'REJECTED'),
('S102','Delhi','2026-10-19',1500,'DELIVERED'),
('S102','Delhi','2026-10-19',650,'REJECTED'),
('S103','Pune','2026-10-19',950,'DELIVERED'),
('S103','Pune','2026-10-20',750,'REJECTED'),
('S101','Mumbai','2026-10-20',2000,'DELIVERED'),
('S102','Delhi','2026-10-20',1100,'REJECTED'),
('S103','Pune','2026-10-20',1350,'DELIVERED'),
('S104','Bangalore','2026-10-20',700,'REJECTED');