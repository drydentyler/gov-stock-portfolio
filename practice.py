# for ptr in range(62):
#     plus_one = ptr+1
#     len = 62
#     decimal = plus_one / len
#     by_hundo = decimal*100
#     rounded = round(by_hundo, 2)
#     print(f'Downloading PTR PDF files: {rounded}% complete . . .')


# for ptr in range(62):
#     print(f'Downloading PTR PDF files: {round(((ptr+1)/62)*100, 2)}% complete . . .')

# sample = '1,000'
#
# fizz = int(sample)
# print(fizz)

# x = [0,1,2,2,3,0,4,2]
#
#
# def removeElement(nums: [int], val: int) -> int:
#     count = 0
#     x = len(nums)-1
#     while x != -1:
#         num = nums[x]
#         if val == num:
#             removed = nums.pop(x)
#             nums.append('_')
#             count += 1
#         x -= 1
#
#     return count
#
#
# removeElement(nums=x, val=2)
# # print('hello')

import math


# def getPermutation(n: int, k: int) -> str:
#     return_str = ""
#     vals = [x + 1 for x in range(n)]
#     while n != 1:
#         n_total = math.factorial(n)
#         segment_size = n_total / n
#         index = math.ceil(k / segment_size) - 1
#         return_str += str(vals.pop(index))
#
#         n -= 1
#         k = k % segment_size
#
#     return_str += str(vals[0])
# #     return return_str
#
#
# getPermutation(5, 110)

# Definition for singly-linked list.
class ListNode:
    def __init__(self, val=0, next=None):
        self.val = val
        self.next = next


# def rotateRight(head: [ListNode], k: int) -> [ListNode]:
#     if head:
#         count = 1
#         start = head
#         while head.next:
#             count += 1
#             head = head.next
#         head.next = start
#         actual_moves = count - (k % count)
#         while actual_moves != 1:
#             start = start.next
#             actual_moves -= 1
#         new_start = start.next
#         start.next = None
#         return new_start
#     else:
#         return head




# sample = ListNode(1, ListNode(2, ListNode(3, ListNode(4, ListNode(5)))))
# result = rotateRight(sample, 6)
# print(result)

import xml.etree.ElementTree as ET

# tree = ET.parse(f'2025FD.xml')
# root = tree.getroot()
#
# member_dict: {str: int} = {}

# Check every child of the root in the XML to see if the filing type is a Periodic Transaction Report
# for child in root:
#     if child.find('FilingType').text == 'P':
#         id = child.find('DocID').text
#         first_name = child.find('First').text
#         last_name = child.find('Last').text
#
#         full_name = first_name+" "+last_name
#         if full_name in member_dict:
#             member_dict[full_name].append(id)
#         else:
#             member_dict[full_name] = [id]
#
# for key in member_dict:
#     print(f'Member: {key}: {member_dict[key]}')

# import os
# ids = []
#
# for filename in os.listdir(os.getcwd()):
#     if filename.endswith('.pdf'):
#         ids.append(int(filename[:-4]))
#
# print(ids)


# class Transaction:
#     def __init__(self, id: int):
#         self.transactions = [x*2 for x in range(id)]
#
#
# def generator_func():
#     reports = [(1, 'Nancy'), (2, 'Dick'), (3, 'Barack'), (4, 'Nancy')]
#     for x in reports:
#         yield x
#
#
# person_dict = {}
# transactions = []
# for id, name in generator_func():
#     transactions.append(Transaction(id))
#     if name in person_dict:
#         person_dict[name].append(id)
#     else:
#         person_dict[name] = [id]

########################################################################################################################
from db_controller import DBController
from datetime import datetime


controller = DBController()
today = datetime.now().date()
for t in controller.tran_model.get_transaction_by():
    print(t)





