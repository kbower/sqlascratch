
obj_a=Customer()
obj_a.customerid='7'  # already exists in database, will cause IntegrityError

obj_b=Customer()
obj_b.customerid='77' 

sp_a = transaction.savepoint()
DBSession.add(obj_a)
try:
    DBSession.flush()  # this issues no savepoint
except IntegrityError:
    sp_a.rollback()    # transaction rolledback instead of to savepoint
else:
    sp_a.release()

sp_b = transaction.savepoint() # now the transaction is already over/rolledback
DBSession.add(obj_b)
try:
    DBSession.flush()
except IntegrityError:
    sp_b.rollback()    
else:
    sp_b.release()

