import web

db = web.database(dbn='sqlite',
        db='AuctionBase.db'
    )

######################BEGIN HELPER METHODS######################

# Enforce foreign key constraints
# WARNING: DO NOT REMOVE THIS!
def enforceForeignKey():
    db.query('PRAGMA foreign_keys = ON')

# initiates a transaction on the database
def transaction():
    return db.transaction()
# Sample usage (in auctionbase.py):
#
# t = sqlitedb.transaction()
# try:
#     sqlitedb.query('[FIRST QUERY STATEMENT]')
#     sqlitedb.query('[SECOND QUERY STATEMENT]')
# except Exception as e:
#     t.rollback()
#     print str(e)
# else:
#     t.commit()
#
# check out http://webpy.org/cookbook/transactions for examples

# returns the current time from your database
def getTime():
    
    query_string = 'select Time from CurrentTime'
    results = query(query_string)
    # alternatively: return results[0]['currenttime']
    # print(results)
    return results[0].Time 

# returns a single item specified by the Item's ID in the database
# Note: if the `result' list is empty (i.e. there are no items for a
# a given ID), this will throw an Exception!
def getItemById(item_id):
    # TODO: rewrite this method to catch the Exception in case `result' is empty
    query_string = 'select * from Items where ItemID = $itemID'
    result = query(query_string, {'itemID': item_id})
    return result[0]

# wrapper method around web.py's db.query method
# check out http://webpy.org/cookbook/query for more info
def query(query_string, vars = {}):
    return list(db.query(query_string, vars))

#####################END HELPER METHODS#####################

#TODO: additional methods to interact with your database,
# e.g. to update the current time

# sets the current time 
def setTime(time):
    query_string = 'UPDATE CurrentTime SET Time = $time'
    db.query(query_string, {'time': time})
    return


###############################################################################
# adds a bid
def addBid(itemID, userID, price):
    # obtain time
    q_string = 'select Time from CurrentTime'
    time = db.query(q_string)[0]['Time']
    # print(time)

    q_string = 'INSERT INTO Bids (ItemID, UserID, Amount, Time) VALUES ($itemID, $userID, $price, $time);'
    query(q_string, {'itemID': itemID, 'userID': userID, 'price': price, 'time': time })
    return

################################################################################

def getCurrently(itemID):
    """
    Returns the currently value for a given item
    """
    q_string = 'select Currently from Items where ItemID = $itemID;'
    result = query(q_string, {'itemID': itemID})
    return result

def getBuyNow(itemID):
    """
    Returns the Buy Price price for a given item
    """
    q_string = 'select Buy_Price from Items where ItemID = $itemID;'
    result = query(q_string, {'itemID': itemID})
    return result

def getCategory(itemID):
    """
    Returns the category for a given item
    """
    q_string = 'select Category from Categories where ItemID = $itemID;'
    result = query(q_string, {'itemID': itemID})
    return result[0]['Category']

def getAuctionWinner(itemID):
    """
    Returns the winner of a closed bid
    """
    q_string = 'select UserID from Bids where ItemID = $itemID order by Amount desc limit 1;'
    result = query(q_string, {'itemID': itemID})
    return result[0]['UserID']

def getBids(itemID):
    """
    Returns current bids on an open auction
    """
    q_string = 'select UserID, Amount, Time from Bids where ItemID = $itemID;'
    result = query(q_string, {'itemID': itemID})
    return result

##################################################################################

def searchOnStatus(status):
    # An open status implies that the current time is greater than the  starting time and less than the end time
    if status == 'open':
        q_string = 'select ItemID from Items, CurrentTime where CurrentTime.Time > Items.Started and CurrentTime.Time < Items.Ends and Items.Currently < Items.Buy_Price;'
    elif status == 'close': # A close status implies that the current time is greater than the bid and the currently value on the item is greater than or equal the buy price
        q_string = 'select ItemID from Items, CurrentTime where CurrentTime.Time > Items.Ends or Items.Currently >= Items.Buy_Price;'
    elif status == 'notStarted': # this implies that the current time is before the started time
        q_string = 'select ItemID from Items, CurrentTime where  CurrentTime.Time < Items.Started;'
    else: # all status allowed
        q_string = 'select ItemID from Items;'

    result = query(q_string)
    return result

def searchOnItemID(itemID):
    q_string = 'select ItemID from Items where ItemID = $itemID;'
    result = query(q_string, { 'itemID': itemID})
    return result

def searchOnMaxPrice(maxPrice):
    q_string = 'select ItemID from Items where Currently <= $maxPrice;'
    result = query(q_string, {'maxPrice': maxPrice})
    return result

def searchOnMinPrice(minPrice):
    q_string = 'select ItemID from Items where Currently >= $minPrice;'
    result = query(q_string, {'minPrice': minPrice})
    return result

def searchOnCategory(category):
    q_string = 'select ItemID from Categories where Category = $category;'
    result = query(q_string, {'category': category})
    return result

def searchOnDescription(description):
    q_string = 'select ItemID from Items where Description like $description;'
    result = query(q_string, {'description': description})
    return result

def searchOnUserID(userID):
    q_string = 'select ItemID from Items where Seller_UserID = $userID;'
    result = query(q_string, {'userID': userID})
    return result

##################################################################################
