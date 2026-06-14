SELECT * FROM product_inventory join suppliers on product_inventory.supplierId = suppliers.id WHERE stock_count < 10
