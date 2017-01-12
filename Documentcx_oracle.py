import cx_Oracle

conn = cx_Oracle.connect(user='arc', password='arc', dsn=cx_Oracle.makedsn('localhost', 1521, 'xe'))

def output_type_handler(cursor, name, defaultType, size, precision, scale):
    print name, defaultType, precision, scale

conn.outputtypehandler = output_type_handler

cursor = conn.cursor()

try:
    cursor.execute("""DROP TABLE kent""")
except:
    pass
    
cursor.execute("""
CREATE TABLE kent (
    data NUMERIC(20, 2)
)
""")

cursor.execute("INSERT INTO kent (data) VALUES (25.12)")

cursor.execute("SELECT data FROM kent")

print cursor.fetchall()

cursor.execute("""
    SELECT cast(totalsale as numeric(20,2)) from
        (SELECT 
            (SELECT CAST((SELECT data * 3 AS sum_1 FROM kent) AS NUMERIC(20, 2)) FROM DUAL) AS totalsale
        FROM dual)
""")

print cursor.fetchall()

cursor.execute("""select (SELECT to_number((SELECT data  AS sum_1 FROM kent),'9999D99') from dual) from dual""")
    
print cursor.fetchall()


cursor.execute("""
SELECT anon_1.orders_orderid AS anon_1_orders_orderid, CAST(anon_1.totalsale AS NUMERIC (20,2)) AS anon_1_totalsale, orderdetails_1.orderid AS orderdetails_1_orderid, orderdetails_1.lineid AS orderdetails_1_lineid, orderdetails_1.qtyordered AS orderdetails_1_qtyordered, orderdetails_1.saleprice AS orderdetails_1_saleprice
FROM (SELECT orders_orderid, totalsale
FROM (SELECT orders.orderid AS orders_orderid, CAST((SELECT sum(od__a.qtyordered * od__a.saleprice) AS sum_1
FROM orderdetails od__a
WHERE orders.orderid = od__a.orderid) AS NUMERIC(20, 2)) AS totalsale
FROM orders)
WHERE ROWNUM <= 100) anon_1 LEFT OUTER JOIN orderdetails orderdetails_1 ON anon_1.orders_orderid = orderdetails_1.orderid
""")

print cursor.fetchall()
