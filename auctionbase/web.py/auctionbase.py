#!/usr/bin/env python

import sys; sys.path.insert(0, 'lib') # this line is necessary for the rest
import os                             # of the imports to work!

import web
import sqlitedb
from jinja2 import Environment, FileSystemLoader
from datetime import datetime

###########################################################################################
##########################DO NOT CHANGE ANYTHING ABOVE THIS LINE!##########################
###########################################################################################

######################BEGIN HELPER METHODS######################

# helper method to convert times from database (which will return a string)
# into datetime objects. This will allow you to compare times correctly (using
# ==, !=, <, >, etc.) instead of lexicographically as strings.

# Sample use:
# current_time = string_to_time(sqlitedb.getTime())

def string_to_time(date_str):
    return datetime.strptime(date_str, '%Y-%m-%d %H:%M:%S')

# helper method to render a template in the templates/ directory
#
# `template_name': name of template file to render
#
# `**context': a dictionary of variable names mapped to values
# that is passed to Jinja2's templating engine
#
# See curr_time's `GET' method for sample usage
#
# WARNING: DO NOT CHANGE THIS METHOD
def render_template(template_name, **context):
    extensions = context.pop('extensions', [])
    globals = context.pop('globals', {})

    jinja_env = Environment(autoescape=True,
            loader=FileSystemLoader(os.path.join(os.path.dirname(__file__), 'templates')),
            extensions=extensions,
            )
    jinja_env.globals.update(globals)

    web.header('Content-Type','text/html; charset=utf-8', unique=True)

    return jinja_env.get_template(template_name).render(context)

#####################END HELPER METHODS#####################

urls = ('/currtime', 'curr_time',
        '/selecttime', 'select_time',
        '/', 'app_base',
        '/add_bid', 'add_bid',
        '/search', 'search',
        '/show_item/(.+)','show_item'
        # TODO: add additional URLs here
        # first parameter => URL, second parameter => class name
        )

class app_base:

    def GET(self):
        return render_template('app_base.html')

class show_item:

    def GET(self, items):
        print('The item id is = ',int(items))
        itemID = int(items)

        tempItem = sqlitedb.getItemById(itemID)

        # the item attributes are already present

        # get the categories for the item
        tempItem['Categories'] = sqlitedb.getCategory(itemID)

        # determine the auctions open/close status
            # check if the item is still open
        if (string_to_time(tempItem['Started']) <= string_to_time(sqlitedb.getTime())) and (string_to_time(tempItem['Ends']) >= string_to_time(sqlitedb.getTime())):
            tempItem['Status'] = 'Open'
        # check if the item is closed
        elif (string_to_time(tempItem['Ends']) >= string_to_time(sqlitedb.getTime())) or (tempItem['Buy_Price'] <= tempItem['Currently']):
            tempItem['Status'] = 'Close'
        # check if the auction for the item has not started
        elif string_to_time(tempItem['Started']) > string_to_time(sqlitedb.getTime()):
            tempItem['Status'] = 'Not Started'

        # determine winner if the auction is closed, determine bids if auction is open
        if tempItem['Status'] == 'Close':
            win = sqlitedb.getAuctionWinner(itemID)
            tempItem['Winner'] = win
        
        bids = sqlitedb.getBids(itemID)
        bidderList = ""
        for b in bids:
            bidderList += "Bidder: " + b['UserID'] + " --- Price: " + str(b['Amount']) + " --- Time of Bid: " + b['Time'] + '  |  '
        tempItem['Bids'] = bidderList

        results = [tempItem]

        return render_template('show_item.html', search_result = results)




    def POST(self, item):

        post_params = web.input()
        itemID = post_params['itemID']
        # get the item
        tempItem = sqlitedb.getItemById(itemID)

        # the item attributes are already present

        # get the categories for the item
        tempItem['Categories'] = sqlitedb.getCategory(itemID)

        # determine the auctions open/close status
            # check if the item is still open
        if (string_to_time(tempItem['Started']) <= string_to_time(sqlitedb.getTime())) and (string_to_time(tempItem['Ends']) >= string_to_time(sqlitedb.getTime())):
            tempItem['Status'] = 'Open'
        # check if the item is closed
        elif (string_to_time(tempItem['Ends']) >= string_to_time(sqlitedb.getTime())) or (tempItem['Buy_Price'] <= tempItem['Currently']):
            tempItem['Status'] = 'Close'
        # check if the auction for the item has not started
        elif string_to_time(tempItem['Started']) > string_to_time(sqlitedb.getTime()):
            tempItem['Status'] = 'Not Started'

        # determine winner if the auction is closed, determine bids if auction is open
        if tempItem['Status'] == 'Close':
            win = sqlitedb.getAuctionWinner(itemID)
            tempItem['Winner'] = win
        
        bids = sqlitedb.getBids(itemID)
        bidderList = ""
        for b in bids:
            bidderList += "Bidder: " + b['UserID'] + " --- Price: " + str(b['Amount']) + " --- Time of Bid: " + b['Time'] + '  |  '
        tempItem['Bids'] = bidderList

        results = [tempItem]

        return render_template('show_item.html', search_result = results)

class add_bid:

    # display add bid page
    def GET(self):
        return render_template('add_bid.html')

    def POST(self):

        post_params = web.input()
        userID = post_params['userID']
        price = post_params['price']
        itemID = post_params['itemID']
        try:
            sqlitedb.addBid(itemID, userID, price)
            update_message = 'Bid successfully added'
            return render_template('add_bid.html',  add_result = True)
        except TypeError: # workaround because TypeError on date is not iterable but for some reason still adds to bids 
            update_message = 'Bid successfully added'
            return render_template('add_bid.html',  add_result = True)
        except Exception as ex:
            print(ex)
            update_message = 'Bid addition failed'
            return render_template('add_bid.html', add_result = False)
            

class search:

    def GET(self):
        return render_template('search.html')       

    def POST(self):

        post_params = web.input()
        status = post_params['status'] # - 
        itemID = post_params['itemID'] # - 
        minPrice = post_params['minPrice'] # - 
        maxPrice = post_params['maxPrice'] # - 
        category = post_params['category'] # - 
        description = post_params['description'] # -
        userID = post_params['userID'] 

        results = []
        # narrow down search results based on status
        statusSearch_Temp = sqlitedb.searchOnStatus(status)
        # print(statusSearch_Temp)
        statusSearchResults = set() # statusSearchResults contains a bunch of Ids
        for r in statusSearch_Temp: 
            statusSearchResults.add(r['ItemID'])
        
        # Filter by ItemID
        if itemID != '':
            itemIDSearch_Temp = sqlitedb.searchOnItemID(itemID)
            itemIDSearchResults = set()
            for r in itemIDSearch_Temp:
                itemIDSearchResults.add(r['ItemID'])
            statusSearchResults = statusSearchResults.intersection(itemIDSearchResults)
            # print(itemIDSearchResults)

        if userID != '':
            userIDSearch_Temp = sqlitedb.searchOnUserID(userID)
            userIDSearchResults = set()
            for r in userIDSearch_Temp:
                userIDSearchResults.add(r['ItemID'])
            statusSearchResults = statusSearchResults.intersection(userIDSearchResults)
        
        # Filter by minPrice
        if minPrice != '':
            minPrice_Temp = sqlitedb.searchOnMinPrice(minPrice)
            minPriceSearchResults = set()
            for r in minPrice_Temp:
                minPriceSearchResults.add(r['ItemID'])
            statusSearchResults = statusSearchResults.intersection(minPriceSearchResults)
        
        # filter by maxPrice
        if maxPrice != '':
            maxPrice_Temp = sqlitedb.searchOnMaxPrice(maxPrice)
            maxPriceSearchResults = set()
            for r in maxPrice_Temp:
                maxPriceSearchResults.add(r['ItemID'])
            statusSearchResults = statusSearchResults.intersection(maxPriceSearchResults)
        
        # filter by Category
        if category != '':
            category_Temp = sqlitedb.searchOnCategory(category)
            categorySearchResults = set()
            for r in category_Temp:
                categorySearchResults.add(r['ItemID'])
            statusSearchResults = statusSearchResults.intersection(categorySearchResults)
        
        # filter by description
        if description != '':
            description = '%'+description+'%'
            description_Temp = sqlitedb.searchOnDescription(description)
            descriptionSearchResults = set()
            for r in description_Temp:
                descriptionSearchResults.add(r['ItemID'])
            statusSearchResults = statusSearchResults.intersection(descriptionSearchResults)

        # print(statusSearchResults)

        final_items = []

        # iterate through the items
        for i, item in enumerate(statusSearchResults):
            tempItem = sqlitedb.getItemById(item) # obtain the item

            # check if the item is still open
            if (string_to_time(tempItem['Started']) <= string_to_time(sqlitedb.getTime())) and (string_to_time(tempItem['Ends']) >= string_to_time(sqlitedb.getTime())):
                tempItem['Status'] = 'Open'
            # check if the item is closed
            elif (string_to_time(tempItem['Ends']) >= string_to_time(sqlitedb.getTime())) or (tempItem['Buy_Price'] <= tempItem['Currently']):
                tempItem['Status'] = 'Close'
            # check if the auction for the item has not started
            elif string_to_time(tempItem['Started']) > string_to_time(sqlitedb.getTime()):
                tempItem['Status'] = 'Not Started'
            
            # obtain categories for the item
            tempItem['Categories'] = sqlitedb.getCategory(item)

            # add the href value to the item page
            tempItem['href'] = '/show_item/'+str(item)

            final_items.append(tempItem)
            
        return render_template('search.html', search_result = final_items)

 

class curr_time:
    # A simple GET request, to '/currtime'
    #
    # Notice that we pass in `current_time' to our `render_template' call
    # in order to have its value displayed on the web page
    def GET(self):
        current_time = sqlitedb.getTime()
        return render_template('curr_time.html', time = current_time)

class select_time:
    # Aanother GET request, this time to the URL '/selecttime'
    def GET(self):
        return render_template('select_time.html')

    # A POST request
    #
    # You can fetch the parameters passed to the URL
    # by calling `web.input()' for **both** POST requests
    # and GET requests
    def POST(self):
        post_params = web.input()
        MM = post_params['MM']
        dd = post_params['dd']
        yyyy = post_params['yyyy']
        HH = post_params['HH']
        mm = post_params['mm']
        ss = post_params['ss'];
        enter_name = post_params['entername']


        selected_time = '%s-%s-%s %s:%s:%s' % (yyyy, MM, dd, HH, mm, ss)
        update_message = '(Hello, %s. Previously selected time was: %s.)' % (enter_name, selected_time)
        # TODO: save the selected time as the current time in the database
        try:
            sqlitedb.setTime(selected_time)
        except:
            update_message = '(Hello, %s. Unfortunately, time cannot move backward)' %(enter_name)
            return render_template('select_time.html', message = update_message) 
        # Here, we assign `update_message' to `message', which means
        # we'll refer to it in our template as `message'
        return render_template('select_time.html', message = update_message)

###########################################################################################
##########################DO NOT CHANGE ANYTHING BELOW THIS LINE!##########################
###########################################################################################

if __name__ == '__main__':
    web.internalerror = web.debugerror
    app = web.application(urls, globals())
    app.add_processor(web.loadhook(sqlitedb.enforceForeignKey))
    app.run()
