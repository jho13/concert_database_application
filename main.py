# -*- coding: utf-8 -*-
"""
Created on Thu Jul 19 17:34:45 2018

@author: 오종훈
"""

def print_commands():
    print('''
          ============================================================ 
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
          ============================================================
          ''')
    

if (__name__ == '__main__'):
    print_commands()
    
    action = -1
    while (action != 15):
        
        action = int(input('Select your action: '))
        