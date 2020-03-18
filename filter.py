"""
CSC148, Winter 2019
Assignment 1

This code is provided solely for the personal and private use of
students taking the CSC148 course at the University of Toronto.
Copying for purposes other than this use is expressly prohibited.
All forms of distribution of this code, whether as given or with
any changes, are expressly prohibited.

All of the files in this directory and all subdirectories are:
Copyright (c) 2019 Bogdan Simion, Diane Horton, Jacqueline Smith
"""
import time
import datetime
from typing import List, Tuple
from call import Call
from customer import Customer


class Filter:
    """ A class for filtering customer data on some criterion. A filter is
    applied to a set of calls.

    This is an abstract class. Only subclasses should be instantiated.
    """
    def __init__(self) -> None:
        pass

    def apply(self, customers: List[Customer],
              data: List[Call],
              filter_string: str) \
            -> List[Call]:
        """ Return a list of all calls from <data>, which match the filter
        specified in <filter_string>.

        The <filter_string> is provided by the user through the visual prompt,
        after selecting this filter.
        The <customers> is a list of all customers from the input dataset.

         If the filter has
        no effect or the <filter_string> is invalid then return the same calls
        from the <data> input.

        Precondition:
        - <customers> contains the list of all customers from the input dataset
        - all calls included in <data> are valid calls from the input dataset
        """
        raise NotImplementedError

    def __str__(self) -> str:
        """ Return a description of this filter to be displayed in the UI menu
        """
        raise NotImplementedError


class ResetFilter(Filter):
    """
    A class for resetting all previously applied filters, if any.
    """
    def apply(self, customers: List[Customer],
              data: List[Call],
              filter_string: str) \
            -> List[Call]:
        """ Reset all of the applied filters. Return a List containing all the
        calls corresponding to <customers>.
        The <data> and <filter_string> arguments for this type of filter are
        ignored.

        Precondition:
        - <customers> contains the list of all customers from the input dataset
        """
        filtered_calls = []
        for c in customers:
            customer_history = c.get_history()
            # only take outgoing calls, we don't want to include calls twice
            filtered_calls.extend(customer_history[0])
        return filtered_calls

    def __str__(self) -> str:
        """ Return a description of this filter to be displayed in the UI menu
        """
        return "Reset all of the filters applied so far, if any"


def find_customer_by_number(number: str, customer_list: List[Customer]) \
        -> Customer:
    """ Return the Customer with the phone number <number> in the list of
    customers <customer_list>.
    If the number does not belong to any customer, return None.
    """
    cust = None
    for customer in customer_list:
        if number in customer:
            cust = customer
    return cust


class CustomerFilter(Filter):
    """
    A class for selecting only the calls from a given customer.
    """
    def apply(self, customers: List[Customer],
              data: List[Call],
              filter_string: str) \
            -> List[Call]:
        """ Return a list of all calls from <data> made or received by the
         customer with the id specified in <filter_string>.

        The <customers> list contains all customers from the input dataset.

        The filter string is valid if and only if it contains a valid
        customer ID.
        - If the filter string is invalid, return the original list <data>
        - If the filter string is invalid, your code must not crash, as
        specified in the handout.
        """
        lst = []
        customer_id_list = []
        if len(filter_string) == 0:
            return data
        for customer in customers:
            customer_id_list.append(customer.get_id())
        if filter_string.isnumeric():
            if int(filter_string) in customer_id_list:
                for call in data:
                    curr_customer_1 = find_customer_by_number(call.src_number,
                                                              customers)
                    curr_customer_2 = find_customer_by_number(call.dst_number,
                                                              customers)
                    if curr_customer_1.get_id() == int(filter_string) or \
                            curr_customer_2.get_id() == int(filter_string):
                        lst.append(call)
            else:
                return data
        else:
            return data

        return lst

    def __str__(self) -> str:
        """ Return a description of this filter to be displayed in the UI menu
        """
        return "Filter events based on customer ID"


class DurationFilter(Filter):
    """
    A class for selecting only the calls lasting either over or under a
    specified duration.
    """
    def apply(self, customers: List[Customer],
              data: List[Call],
              filter_string: str) \
            -> List[Call]:
        """ Return a list of all calls from <data> with a duration of under or
        over the time indicated in the <filter_string>.

        The <customers> list contains all customers from the input dataset.

        The filter string is valid if and only if it contains the following
        input format: either "Lxxx" or "Gxxx", indicating to filter calls less
        than xxx or greater than xxx seconds, respectively.
        - If the filter string is invalid, return the original list <data>
        - If the filter string is invalid, your code must not crash, as
        specified in the handout.
        """
        data_copy = []
        if len(filter_string) == 0 or len(filter_string) == 1:
            return data
        if filter_string[0] == "L" and len(filter_string) <= 4 and \
                filter_string[1:].isnumeric():
            for call in data:
                if call.duration < int(filter_string[1:]):
                    data_copy.append(call)
            return data_copy
        elif filter_string[0] == "G" and len(filter_string) <= 4 and \
                filter_string[1:].isnumeric():
            for call in data:
                if call.duration > int(filter_string[1:]):
                    data_copy.append(call)
            return data_copy
        else:
            return data

    def __str__(self) -> str:
        """ Return a description of this filter to be displayed in the UI menu
        """
        return "Filter calls based on duration; " \
               "L### returns calls less than specified length, G### for greater"


class LocationFilter(Filter):
    """
    A class for selecting only the calls that took place within a specific area
    """
    def apply(self, customers: List[Customer],
              data: List[Call],
              filter_string: str) \
            -> List[Call]:
        """ Return a list of all calls from <data>, which took place within
        a location specified by the <filter_string> (at least the source or the
        destination of the event was in the range of coordinates from the
        <filter_string>).

        The <customers> list contains all customers from the input dataset.

        The filter string is valid if and only if it contains four valid
        coordinates within the map boundaries.
        These coordinates represent the location of the lower left corner
        and the upper right corner of the search location rectangle,
        as 2 pairs of longitude/latitude coordinates, each separated by
        a comma and a space:
          lowerLong, lowerLat, upperLong, upperLat
        Calls that fall exactly on the boundary of this rectangle are
        considered a match as well.
        - If the filter string is invalid, return the original list <data>
        - If the filter string is invalid, your code must not crash, as
        specified in the handout.
        """
        fil_str_lst_original = filter_string.strip().split(',')

        # input validation 1) ensure all float
        verification_1 = True
        for coord in fil_str_lst_original:
            try:
                if isinstance(float(coord), float):
                    pass
            except ValueError:
                verification_1 = False
            except Exception:
                verification_1 = False

        fil_str_lst = []
        if verification_1:
            for item in fil_str_lst_original:
                fil_str_lst.append(float(item))

        # input validation 2) ensure len is 4
        verification_2 = True
        if verification_1:
            if len(fil_str_lst) == 4:
                verification_2 = True
            else:
                verification_2 = False

        # input validation 3) inputs are within the map range
        verification_3 = True
        if verification_1 and verification_2:
            if not -79.697878 <= fil_str_lst[0] <= -79.196382:
                verification_3 = False
            elif not -79.697878 <= fil_str_lst[2] <= -79.196382:
                verification_3 = False
            elif not 43.576959 <= fil_str_lst[1] <= 43.799568:
                verification_3 = False
            elif not 43.576959 <= fil_str_lst[3] <= 43.799568:
                verification_3 = False

        if verification_1 and verification_2 and verification_3:
            if fil_str_lst[0] <= fil_str_lst[2] and \
                    fil_str_lst[1] <= fil_str_lst[3]:
                # now we know input is valid
                data_copy = []
                for call in data:
                    if(fil_str_lst[2] > call.src_loc[0] > fil_str_lst[0] and
                       fil_str_lst[3] > call.src_loc[1] > fil_str_lst[1]) or \
                            (fil_str_lst[2] > call.dst_loc[0] > fil_str_lst[0]
                             and fil_str_lst[3] > call.dst_loc[1] >
                             fil_str_lst[1]):
                        data_copy.append(call)
            return data_copy
        else:
            return data

    def __str__(self) -> str:
        """ Return a description of this filter to be displayed in the UI menu
        """
        return "Filter calls made or received in a given rectangular area. " \
               "Format: \"lowerLong, lowerLat, " \
               "upperLong, upperLat\" (e.g., -79.6, 43.6, -79.3, 43.7)"


if __name__ == '__main__':
    import python_ta
    python_ta.check_all(config={
        'allowed-import-modules': [
            'python_ta', 'typing', 'time', 'datetime', 'call', 'customer'
        ],
        'max-nested-blocks': 4,
        'allowed-io': ['apply', '__str__'],
        'disable': ['W0611', 'W0703'],
        'generated-members': 'pygame.*'
    })
