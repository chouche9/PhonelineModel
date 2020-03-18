from datetime import *
from data import tiny_data
from test_data import jan_data, com_data, customer, loc_data, filter_data
from contract import *
from customer import *
from phoneline import *
from filter import *
import unittest


def create_customers(log: Dict[str, List[Dict]]) -> List[Customer]:
    """ Returns a list of Customer instances for each customer from the input
    dataset from the dictionary <log>.

    Precondition:
    - The <log> dictionary contains the input data in the correct format,
    matching the expected input format described in the handout.
    """
    customer_list = []
    for cust in log['customers']:
        customer = Customer(cust['id'])
        for line in cust['lines']:
            contract = None

            if line['contract'] == 'prepaid':
                # start with $100 credit on the account
                contract = PrepaidContract(datetime.date(2017, 12, 25), 100)
            elif line['contract'] == 'mtm':
                contract = MTMContract(datetime.date(2017, 12, 25))
            elif line['contract'] == 'term':
                contract = TermContract(datetime.date(2017, 12, 25),
                                        datetime.date(2019, 6, 25))
            else:
                print("ERROR: unknown contract type")

            line = PhoneLine(line['number'], contract)
            customer.add_phone_line(line)
        customer_list.append(customer)
    return customer_list


def create_call(source: dict) -> List[Call]:
    res = []
    event_list = source["events"]
    for event_dict in event_list:
        if event_dict["type"] == "call":
            src_number = event_dict["src_number"]
            dst_number = event_dict["dst_number"]
            duration = event_dict["duration"]
            time = event_dict["time"]
            time = datetime.datetime.strptime(time, "%Y-%m-%d %H:%M:%S")
            src_loc = event_dict["src_loc"]
            dst_loc = event_dict["dst_loc"]
            call = Call(src_number, dst_number, time, duration, src_loc,
                        dst_loc)
            res.append(call)
    return res


class Test21(unittest.TestCase):
    def setUp(self):
        self.history = CallHistory()
        self.single_call = create_call(tiny_data)[0]

    def test_basic(self):
        self.assertDictEqual({}, self.history.incoming_calls)
        self.assertDictEqual({}, self.history.outgoing_calls)
        self.assertEqual(None,
                         self.history.register_incoming_call(self.single_call))
        self.assertEqual(None,
                         self.history.register_incoming_call(self.single_call))

    def test_incoming_1(self):
        call_list = create_call(tiny_data)
        for call in call_list:
            self.history.register_incoming_call(call)
        exp_res = {(1, 2018): [call_list[0]]}
        act_res = self.history.incoming_calls
        self.assertDictEqual(exp_res, act_res,
                             'The call should be registered to the incoming calls')

    def test_incoming_2(self):
        self.maxDiff = None
        call_list = [self.single_call]
        for call in call_list:
            self.history.register_incoming_call(call)
            self.history.register_incoming_call(call)
        exp_res = {(1, 2018): [call_list[0], call_list[0]]}
        act_res = self.history.incoming_calls
        self.assertDictEqual(exp_res, act_res,
                             'There should be two calls registered to the incoming calls')

    def test_incoming_3(self):
        call_list = create_call(jan_data)
        call_list.sort(key=lambda x: x.time)
        for call in call_list:
            self.history.register_incoming_call(call)
        exp_res = {(1, 2018): call_list}
        act_res = self.history.incoming_calls
        self.assertDictEqual(exp_res, act_res,
                             'Every call in the january should be registered to the incoming calls')

    def test_incoming_4(self):
        self.maxDiff = None
        call_list = create_call(com_data)
        call_list.sort(key=lambda x: x.time)
        for call in call_list:
            self.history.register_incoming_call(call)
        exp_res = {(1, 2018): [call_list[0]], (2, 2018): [call_list[1]],
                   (3, 2018): [call_list[2]], (4, 2018): [call_list[3]]}
        act_res = self.history.incoming_calls
        self.assertDictEqual(exp_res, act_res,
                             'Both January and March\'s calls(aka you have two keys) should be registered to the incoming calls')

    def test_outgoing_1(self):
        call_list = create_call(tiny_data)
        for call in call_list:
            self.history.register_outgoing_call(call)
        exp_res = {(1, 2018): [call_list[0]]}
        act_res = self.history.outgoing_calls
        self.assertDictEqual(exp_res, act_res,
                             'There is only one call should be registered to the outgoing calls')

    def test_outgoing_2(self):
        call_list = create_call(tiny_data)
        for call in call_list:
            self.history.register_outgoing_call(call)
            self.history.register_outgoing_call(call)
        exp_res = {(1, 2018): [call_list[0], call_list[0]]}
        act_res = self.history.outgoing_calls
        self.assertDictEqual(exp_res, act_res,
                             "Two calls should be registered to the outoing calls")

    def test_outgoing_3(self):
        call_list = create_call(jan_data)
        call_list.sort(key=lambda x: x.time)
        for call in call_list:
            self.history.register_outgoing_call(call)
        exp_res = {(1, 2018): call_list}
        act_res = self.history.outgoing_calls
        self.assertDictEqual(exp_res, act_res,
                             'Every call in the January should be registered to the history')

    def test_outgoing_4(self):
        call_list = create_call(com_data)
        call_list.sort(key=lambda x: x.time)
        for call in call_list:
            self.history.register_outgoing_call(call)
        exp_res = {(1, 2018): [call_list[0]], (2, 2018): [call_list[1]],
                   (3, 2018): [call_list[2]], (4, 2018): [call_list[3]]}
        act_res = self.history.outgoing_calls
        self.assertDictEqual(exp_res, act_res,
                             'Both of calls in the January and the March should be registered to the outgoing calls')


class Test22(unittest.TestCase):
    def setUp(self):
        self.contract = MTMContract(date(2018, 1, 12))
        self.phoneline = PhoneLine("441-4444", self.contract)
        self.single_call = create_call(tiny_data)[0]
        self.jan_data = sorted(create_call(jan_data), key=lambda x: x.time)
        self.com_data = sorted(create_call(com_data), key=lambda x: x.time)

    def test_basic(self):
        self.assertEqual(None, self.phoneline.make_call(self.single_call))
        self.assertEqual(None, self.phoneline.receive_call(self.single_call))

    def test_make_call(self):
        single_call = create_call(tiny_data)[0]
        self.phoneline.make_call(single_call)
        exp_res = {
            (single_call.time.month, single_call.time.year): [single_call]}
        act_res = self.phoneline.callhistory.outgoing_calls
        exp_key = [(single_call.time.month, single_call.time.year)]
        act_key = list(self.phoneline.bills.keys())
        exp_duration = ceil(single_call.duration / 60.0)
        act_duration = self.phoneline.contract.bill.billed_min
        self.assertDictEqual(exp_res, act_res,
                             'There is a single call should be registered to the outgoing calls of the the phoneline\'s history')
        self.assertCountEqual(exp_key, act_key,
                              'Check the month and years for the bill')
        self.assertEqual(exp_duration, act_duration,
                         "The duration of the call should be added to the billed minute")

    def test_make_call_2(self):
        jan_call = self.jan_data
        exp_month = jan_call[0].time.month
        exp_year = jan_call[1].time.year
        for call in jan_call:
            self.phoneline.make_call(call)
        exp_res = {(exp_month, exp_year): jan_call}
        act_res = self.phoneline.callhistory.outgoing_calls
        exp_key = [(exp_month, exp_year)]
        act_key = list(self.phoneline.bills.keys())
        exp_duration = ceil(sum([call.duration for call in jan_call]) / 60.0)
        act_duration = self.phoneline.contract.bill.billed_min
        self.assertDictEqual(exp_res, act_res,
                             'Every call in the January should be registered to the outgoing calls of the phoneline\'s history')
        self.assertCountEqual(exp_key, act_key,
                              'Check the month and years for the bill')
        self.assertEqual(exp_duration, act_duration,
                         'The duration of the calls in the january should be added to the billed minute')

    def test_make_call_3(self):
        com_data = self.com_data
        exp_res = {}
        exp_key = []
        exp_duration = 0
        act_duration = 0
        for call in com_data:
            self.phoneline.make_call(call)
            m_y_tuple = call.get_bill_date()
            temp = exp_res.get(m_y_tuple, [])
            temp.append(call)
            exp_res[m_y_tuple] = temp
            exp_key.append(m_y_tuple)
            exp_duration += call.duration
            act_duration += self.contract.bill.billed_min
        act_res = self.phoneline.callhistory.outgoing_calls
        act_key = list(self.phoneline.bills.keys())
        self.assertDictEqual(exp_res, act_res,
                             'You should register calls to the outgoing calls')
        self.assertCountEqual(exp_key, act_key,
                              'Check the month and years for the bills')
        self.assertEqual(ceil(exp_duration / 60.0), act_duration,
                         'This checks the sum of total durations')

    def test_receive_call(self):
        single_call = create_call(tiny_data)[0]
        self.phoneline.receive_call(single_call)
        exp_res = {
            (single_call.time.month, single_call.time.year): [single_call]}
        act_res = self.phoneline.callhistory.incoming_calls
        exp_key = [(single_call.time.month, single_call.time.year)]
        act_key = list(self.phoneline.bills.keys())
        self.assertDictEqual(exp_res, act_res,
                             'The single call should be registered to the incoming calls of the history')
        self.assertCountEqual(exp_key, act_key,
                              'Check the month and years for the bill')

    def test_receive_call_2(self):
        jan_call = self.jan_data
        exp_month = jan_call[0].time.month
        exp_year = jan_call[1].time.year
        for call in jan_call:
            self.phoneline.receive_call(call)
        exp_res = {(exp_month, exp_year): jan_call}
        act_res = self.phoneline.callhistory.incoming_calls
        exp_key = [(exp_month, exp_year)]
        act_key = list(self.phoneline.bills.keys())
        self.assertDictEqual(exp_res, act_res,
                             'Every call in the January should be registered to the incoming calls of the history')
        self.assertCountEqual(exp_key, act_key,
                              'Check the month and years for the bill')

    def test_receive_call_3(self):
        com_data = self.com_data
        exp_res = {}
        exp_key = []
        for call in com_data:
            self.phoneline.receive_call(call)
            m_y_tuple = call.get_bill_date()
            temp = exp_res.get(m_y_tuple, [])
            temp.append(call)
            exp_res[m_y_tuple] = temp
            exp_key.append(m_y_tuple)
        act_res = self.phoneline.callhistory.incoming_calls
        act_key = list(self.phoneline.bills.keys())
        self.assertDictEqual(exp_res, act_res,
                             'Calls in the January and March should be registered to the incoming calls')
        self.assertCountEqual(exp_key, act_key,
                              'Check the month and years for the bill')


class Test23(unittest.TestCase):
    def setUp(self):
        self.customer = Customer(2012)
        self.contract = MTMContract(date(2018, 1, 12))
        self.customer.add_phone_line(PhoneLine("422-4785", self.contract))
        self.customer.add_phone_line(PhoneLine("136-5226", self.contract))
        self.single_call = create_call(tiny_data)[0]
        self.jan_call = create_call(jan_data)
        self.com_call = create_call(com_data)

    def test_basic(self):
        self.customer.receive_call(self.single_call)
        self.assertEqual(None, self.customer.make_call(self.single_call))
        self.assertEqual(None, self.customer.receive_call(self.single_call))

    def test_make_call_1(self):
        self.customer.make_call(self.single_call)
        # Test bill is added to a new list
        self.assertEqual(True,
                         list(self.customer._phone_lines[0].bills.keys()) == [
                             (1, 2018)],
                         'The phone co-responding to the src number should add a bill')
        # Test add bill to the contract
        self.assertEqual(True, self.customer._phone_lines[
            0].contract.bill.type == "MTM")
        self.assertEqual(True, self.customer._phone_lines[
            0].contract.bill.fixed_cost == 50.00)
        self.assertEqual(True, self.customer._phone_lines[
            0].contract.bill.min_rate == 0.05)
        # Test register the call to the history
        self.assertCountEqual([(1, 2018)], list(
            self.customer._phone_lines[0].callhistory.outgoing_calls.keys()),
                              'There is only one call got registered to the outgoing call of the co-responding phoneline')
        # Test the added minutes
        self.assertCountEqual([self.single_call], self.customer._phone_lines[
            0].callhistory.outgoing_calls[(1, 2018)],
                              'There is only one call in the month got registered to the outgoing calls')
        # Test bill call
        self.assertEqual(2, self.contract.bill.billed_min,
                         'The duration of the call is the billed min of the bill')

    def test_make_call_2(self):
        self.customer.add_phone_line(
            PhoneLine("731-0105", MTMContract(date(2018, 1, 12))))
        self.customer.add_phone_line(
            PhoneLine("934-0592", MTMContract(date(2018, 1, 12))))
        self.customer.add_phone_line(
            PhoneLine("136-5226", MTMContract(date(2018, 1, 12))))
        self.customer.add_phone_line(
            PhoneLine("420-4785", MTMContract(date(2018, 1, 12))))
        for call in self.jan_call:
            self.customer.make_call(call)
        # Test register call
        self.assertCountEqual([self.jan_call[0], self.jan_call[2]],
                              self.customer._phone_lines[
                                  0].callhistory.outgoing_calls[(1, 2018)],
                              'Calls should be registered into the outgoing calls of the co-responding phoneline with same src-number'
                              )
        self.assertCountEqual([self.jan_call[1]], self.customer._phone_lines[
            3].callhistory.outgoing_calls[(1, 2018)],
                              'Calls should be registered into the outgoing calls of the co-responding phoneline with same src-number'
                              )
        self.assertCountEqual([self.jan_call[-1]], self.customer._phone_lines[
            -1].callhistory.outgoing_calls[(1, 2018)],
                              'Calls should be registered into the outgoing calls of the co-responding phoneline with same src-number'
                              )
        # Test bill call
        self.assertEqual(4,
                         self.customer._phone_lines[0].contract.bill.billed_min,
                         'The duration of the call should be the billed min of the bill')
        self.assertEqual(2,
                         self.customer._phone_lines[3].contract.bill.billed_min,
                         'The duration of the call should be the billed min of the bill')
        self.assertEqual(2, self.customer._phone_lines[
            -1].contract.bill.billed_min,
                         'The duration of the call should be the billed min of the bill')

    def test_make_call_3(self):
        self.customer.add_phone_line(
            PhoneLine("731-0105", MTMContract(date(2018, 1, 12))))
        self.customer.add_phone_line(
            PhoneLine("934-0592", MTMContract(date(2018, 2, 12))))
        self.customer.add_phone_line(
            PhoneLine("420-4785", MTMContract(date(2018, 4, 12))))
        for call in self.com_call:
            self.customer.make_call(call)
        self.assertCountEqual([(1, 2018), (3, 2018)],
                              list(self.customer._phone_lines[0].bills.keys()),
                              'Test the bill month for the src-number')
        self.assertCountEqual([(2, 2018)],
                              list(self.customer._phone_lines[3].bills.keys()),
                              'Test the bill month for the src-number')
        self.assertCountEqual([(4, 2018)],
                              list(self.customer._phone_lines[-1].bills.keys()),
                              'Test the bill month for the src-number')

    def test_receive_call(self):
        self.customer.receive_call(self.single_call)
        self.assertEqual(True,
                         list(self.customer._phone_lines[1].bills.keys()) == [
                             (1, 2018)],
                         'The call should be registered to the co-responding phoneline with same dst-number')
        self.assertEqual(True,
                         self.customer._phone_lines[
                             1].contract.bill.type == "MTM")
        self.assertEqual(True,
                         self.customer._phone_lines[
                             1].contract.bill.fixed_cost == 50.00)
        self.assertEqual(True,
                         self.customer._phone_lines[
                             1].contract.bill.min_rate == 0.05)
        # Test register the call to the history
        self.assertCountEqual([(1, 2018)], list(self.customer._phone_lines[
                                                    1].callhistory.incoming_calls.keys()))
        # Test the added minutes
        self.assertCountEqual([self.single_call],
                              self.customer._phone_lines[
                                  1].callhistory.incoming_calls[(1, 2018)])
        self.assertEqual(0,
                         self.customer._phone_lines[1].contract.bill.billed_min,
                         'The incoming call should not be billed')

    def test_receive_call_2(self):
        self.customer.add_phone_line(
            PhoneLine("731-0105", MTMContract(date(2018, 1, 12))))
        self.customer.add_phone_line(
            PhoneLine("934-0592", MTMContract(date(2018, 1, 12))))
        self.customer.add_phone_line(
            PhoneLine("420-4785", MTMContract(date(2018, 1, 12))))
        self.customer.add_phone_line(
            PhoneLine("137-5226", MTMContract(date(2018, 1, 12))))
        for call in self.jan_call:
            self.customer.receive_call(call)
        self.assertCountEqual([self.jan_call[0]], self.customer._phone_lines[
            2].callhistory.incoming_calls[(1, 2018)],
                              'Check the proper incoming_calls for the phoneline')
        self.assertCountEqual([self.jan_call[1], self.jan_call[2]],
                              self.customer._phone_lines[
                                  1].callhistory.incoming_calls[(1, 2018)])
        self.assertCountEqual([self.jan_call[-1]], self.customer._phone_lines[
            -1].callhistory.incoming_calls[(1, 2018)])
unittest.main(exit=False)
