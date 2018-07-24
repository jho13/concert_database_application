# -*- coding: utf-8 -*-
"""
Created on Thu Jul 19 17:34:45 2018

@author: 오종훈
"""
 
#checks

import pymysql.cursors


############################ Main Functions ############################

def connect_to_database():
    return pymysql.connect(
        host = 'astronaut.snu.ac.kr',
        user = 'BDE-2018-14',
        password = '0d00f6382a49',
        db = 'BDE-2018-14',
        charset = 'utf8',
        autocommit = True,
        cursorclass = pymysql.cursors.DictCursor)
    
def print_buildings(cursor):
    print_building_header()
    cursor.execute(
            'SELECT * '
            'FROM building '
            'ORDER BY id '
    )
    print_building_data(cursor.fetchall())

def print_performances(cursor):
    print_performance_header()
    cursor.execute(
            'SELECT * ' 
            'FROM performance '
            'ORDER BY id '
    )
    print_performance_data(cursor.fetchall())

def print_audiences(cursor):
    print_audience_header()
    cursor.execute(
            'SELECT * '
            'FROM audience '
            'ORDER BY id '
    )
    print_audience_data(cursor.fetchall())

def insert_building(cursor):
    name = input('Building name: ')
    location = input('Building location: ')
    capacity = int(input('Building capacity: '))
    if (capacity <= 0):
        print('Capacity should be greater than 0!')
        return
    
    cursor.execute(
            'INSERT INTO building(name, location, capacity, assigned) '
            'VALUES(%s, %s, %s, FALSE)',
            (name, location, capacity)
    )
    print('A building is successfully inserted')

def delete_building(cursor):
    b_id = int(input('Building ID: '))
    if (check_building_id_exists(cursor, b_id) == None):
        print('Building with ID', b_id, 'does not exist!')
        return
    
    cursor.execute(
            'DELETE FROM building '
            'WHERE id = %s ',
            b_id
    )
    # delete reservations
    cursor.execute(
            'DELETE FROM seats '
            'WHERE EXISTS(SELECT * '
            '             FROM seat s JOIN performance p ON(s.performance_id = p.id) '
            '             WHERE p.building_id = %s) ',
            b_id
    )
    print('Succesfully deleted')

def insert_performance(cursor):
    name = input('Performance name: ')
    tpe = input('Performance type: ')
    price = int(input('Performance price: '))
    if (price <= 0):
        print('Price should be greater than 0!')
        return
    
    cursor.execute(
            'INSERT INTO performance(name, type, price) '
            'VALUES(%s, %s, %s)',
            (name, tpe, price)
    )
    print('A performance is successfully inserted')

def delete_performance(cursor):
    p_id = int(input('Performance ID: '))
    if (check_performance_id_exists(cursor, p_id) == None):
        print('Performance with ID', p_id, 'does not exist!')
        return
    
    # deletes seats via CASCADE
    cursor.execute(
            'DELETE FROM performance '
            'WHERE id = %s',
            p_id
    )
    print('Succesfully deleted')

def insert_audience(cursor):
    name = input('Audience name: ')
    gender = input('Audience gender: ')
    age = int(input('Audience age: '))
    if (age <= 0):
        print('Age should be greater than 0!')
        return
    
    cursor.execute(
            'INSERT INTO audience(name, gender, age) '
            'VALUES(%s, %s, %s)',
            (name, gender, age)
    )
    print('An audience is successfully inserted')

def delete_audience(cursor):
    a_id = input('Audience ID: ')
    if (check_audience_id_exists(cursor, a_id) == None):
        print('Audience with ID', a_id, 'does not exist!')
        return
        
    # deletes reservations via SET NULL
    cursor.execute(
            'DELETE FROM audience '
            'WHERE id = %s',
            a_id
    )
    print('Succesfully deleted')

def assign_builing_to_performance(cursor):
    b_id = int(input('Building ID: '))
    building = check_building_id_exists(cursor, b_id)
    if (building == None):
        print('Building with ID', b_id, 'does not exist!')
        return
         
    p_id = int(input('Performance ID: '))
    performance = check_performance_id_exists(cursor, p_id)
    if (performance == None):
        print('Performance with ID', p_id, 'does not exist!')
        return
    
    if (performance['building_id'] != None):
        print('A building is already assigned to this performance!')
        return
     
    # assign building to performance
    cursor.execute(
            'UPDATE performance '
            'SET building_id = %s '
            'WHERE id = %s ',
            (b_id, p_id)
    )
    # create seats
    cursor.executemany(
            'INSERT INTO seat(seat_number, performance_id) ' 
            'VALUES(%s, %s) ',
            [[i + 1, p_id] for i in range(building['capacity'])]
    )
    print('Successfully assigned a performance')

def reserve_seats_for_performance(cursor):
    p_id = int(input('Performance ID: '))
    performance = check_performance_id_exists(cursor, p_id)
    if (performance == None):
        print('Performance with ID', p_id, 'does not exist!')
        return
    
    a_id = int(input('Audience ID: '))
    if (check_audience_id_exists(cursor, a_id) == None):
        print('Audience with ID', a_id, 'does not exist!')
        return
    
    seat_numbers = tuple(int(x) for x in input('Seat number: ').split(','))
    seats = check_seats_exist(cursor, p_id, seat_numbers)
    if (seats == None):
        print('Invalid seat number(s).')
        return
        
    # check all the seats are unreserved
    if (not all([seat['audience_id'] == None for seat in seats])):
        print('The seat is already taken')
        return
    
    # assign seats to audience
    cursor.executemany(
            'UPDATE seat '
            'SET audience_id = %s '
            'WHERE performance_id = %s AND seat_number = %s ',
            [[a_id, p_id, x] for x in seat_numbers]
    )
    # increase booked in performance
    cursor.execute(
            'UPDATE performance '
            'SET booked = booked + %s '
            'WHERE id = %s ',
            (len(seat_numbers), p_id))
    print('Successfully booked a performance')
    print('Total ticket price is', len(seat_numbers) * performance['price'])
    
def print_buildings_performances(cursor):
    b_id = int(input('Building ID: '))
    num_rows = cursor.execute(
            'SELECT * '
            'FROM building '
            'WHERE id = %s '
            'ORDER BY id ',
            b_id
    )
    if (num_rows == 0):
        print('Building with ID', b_id, 'does not exist!')
        return
    
    print_performance_header(False)
    cursor.execute(
            'SELECT * '
            'FROM performance '
            'WHERE building_id = %s',
            b_id
    )
    print_performance_data(cursor.fetchall(), False)

def print_performances_audiences(cursor):
    p_id = int(input('Performance ID: '))
    num_rows = cursor.execute(
            'SELECT * '
            'FROM performance '
            'WHERE id = %s ',
            p_id
    )
    if (num_rows == 0):
        print('Performance with ID', p_id, 'does not exist!')
        return
    
    print_audience_header()
    cursor.execute(
            'SELECT DISTINCT a.* '
            'FROM audience a JOIN seat s ON(a.id = s.audience_id) '
            'WHERE s.performance_id = %s '
            'ORDER BY a.id ',
            p_id
    )
    print_audience_data(cursor.fetchall())

def print_performances_seats(cursor):
    p_id = int(input('Performance ID: '))
    num_rows = cursor.execute(
            'SELECT * '
            'FROM performance '
            'WHERE id = %s ',
            p_id
    )
    if (num_rows == 0):
        print('Performance with ID', p_id, 'does not exist!')
        return
    
    if (cursor.fetchone()['building_id'] == None):
        print('No building assigned to performance!')
        return
    
    print_seat_header()
    cursor.execute(
            'SELECT s.seat_number, s.audience_id '
            'FROM seat s '
            'WHERE s.performance_id = %s ',
            p_id
    )
    print_seat_data(cursor.fetchall())
    
action_list = [print_buildings, print_performances, print_audiences, insert_building,
               delete_building, insert_performance, delete_performance, insert_audience,
               delete_audience, assign_builing_to_performance, reserve_seats_for_performance,
               print_buildings_performances, print_performances_audiences, print_performances_seats]

########################################################################


########################### Helper Functions ###########################

def print_commands():
    print(
'''============================================================ 
1. print all buildings 
2. print all performances 
3. print all audiences 
4. insert a new building 
5. remove a building 
6. insert a new performance 
7. remove a performance 
8. insert a new audience 
9. remove an audience 
10. assign a performance to a building 
11. book a performance 
12. print all performances assigned to a building 
13. print all audiences who booked for a performance 
14. print ticket booking status of a performance 
15. exit 
============================================================''')

def print_building_header():
    print(
'''-------------------------------------------------------------------------------- 
id    name                      location      capacity      assigned
--------------------------------------------------------------------------------''')
    
def print_building_data(rows):
    for row in rows:
        values = row.values()
        print('{:<6}{:<26}{:<14}{:<14}{:<14}'.format(*values))
    if (len(rows) != 0):
        print('----------------------------------------'
              '----------------------------------------')
        
def print_performance_header(print_bid = True):
    if (print_bid):
        print(
'''-------------------------------------------------------------------------------- 
id    name                      type          price         booked        builidng_id
--------------------------------------------------------------------------------''')
    else:
        print(
'''-------------------------------------------------------------------------------- 
id    name                      type          price         booked
--------------------------------------------------------------------------------''')
    
def print_performance_data(rows, print_bid = True):
    for row in rows:
        values = row.values()
        print('{:<6}{:<26}{:<14}{:<14}{:<14}'.format(*list(values)[:-1]), end = '') 
        if (print_bid):
            if (row['building_id'] != None):
                print('{:<6}'.format(row['building_id']))     
    if (len(rows) != 0):
        print('----------------------------------------'
              '----------------------------------------')
        
def print_audience_header():
    print(
'''-------------------------------------------------------------------------------- 
id    name                              gender        age
--------------------------------------------------------------------------------''')
    
def print_audience_data(rows):
    for row in rows:
        values = row.values()
        print('{:<6}{:<36}{:<14}{:<14}'.format(*values))
    if (len(rows) != 0):
        print('----------------------------------------'
              '----------------------------------------')
        
def print_seat_header():
    print(
'''-------------------------------------------------------------------------------- 
seat_number                     audience_id
--------------------------------------------------------------------------------''')
        
def print_seat_data(rows):
    for row in rows:
        print('{:<36}'.format(row['seat_number']), end = '')
        if (row['audience_id'] != None):
            print('{:<6}'.format(row['audience_id']))
        else:
            print()
            
    if (len(rows) != 0):
        print('----------------------------------------'
              '----------------------------------------')
        
def check_building_id_exists(cursor, b_id):
    num_rows = cursor.execute(
            'SELECT * '
            'FROM building '
            'WHERE id = %s ',
            b_id
    )
    return None if (num_rows == 0) else cursor.fetchone()

def check_performance_id_exists(cursor, p_id):
    num_rows = cursor.execute(
            'SELECT * '
            'FROM performance '
            'WHERE id = %s ',
            p_id
    )
    return None if (num_rows == 0) else cursor.fetchone()

def check_audience_id_exists(cursor, a_id):
    num_rows = cursor.execute(
            'SELECT * '
            'FROM audience '
            'WHERE id = %s ',
            a_id
    )
    return None if (num_rows == 0) else cursor.fetchone()

def check_seats_exist(cursor, p_id, seat_numbers):
    num_rows = cursor.execute(
            'SELECT * '
            'FROM seat '
            'WHERE performance_id = %s AND seat_number IN %s ',
            (p_id, seat_numbers)
    )
    return None if (num_rows < len(seat_numbers)) else cursor.fetchall()

########################################################################


################################# Main #################################

if (__name__ == '__main__'):
    print_commands()
    connection = connect_to_database()
    cursor = connection.cursor()
    
    action = None
    while (action != 15):
        action = int(input('Select your action: '))
        if (action >= 1 and action <= 14):
            action_list[action - 1](cursor)
        elif (action == 15):
            print('Bye!')
        else:
            print('Invalid action! Enter a number between 1 and 15.')
        
    cursor.close()
    connection.close()