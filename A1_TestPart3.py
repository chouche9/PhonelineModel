# import application as app
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


class Test31(unittest.TestCase):
    def setUp(self):
        self.exp_start = date(2018, 1, 1)
        self.exp_end = date(2018, 3, 28)
        self.contract = TermContract(self.exp_start, self.exp_end)
        self.jan_call = create_call(jan_data)
        self.assertEqual(self.exp_start, self.contract.start)
        self.assertEqual(None, self.contract.bill)
        self.temp_bill = Bill()

    def test_basic(self):
        self.assertEqual(self.exp_start, self.contract.start)
        self.assertEqual(None, self.contract.bill)
        self.assertEqual(None, self.contract.new_month(2, 2018, Bill()))
        self.assertEqual(True,
                         isinstance(self.contract.cancel_contract(), float))

    def test_new_month_1(self):
        self.assertEqual(None, self.contract.new_month(1, 2018, self.temp_bill))
        self.assertEqual(True, self.contract.bill == self.temp_bill)
        self.assertEqual(0, self.contract.bill.free_min)
        self.assertEqual(0.1, self.contract.bill.min_rate)

    def test_new_month_2(self):
        self.contract.new_month(1,2018, Bill())
        temp_bill = Bill()
        self.contract.new_month(2,2018, temp_bill)
        self.assertEqual(0, self.contract.bill.free_min)
        self.assertEqual(0.1, self.contract.bill.min_rate)
        self.assertEqual(20, self.contract.bill.fixed_cost)

    def test_new_month_3(self):
        self.contract.new_month(1, 2018, Bill())
        temp_bill = Bill()
        temp_bill.add_fixed_cost(20)
        self.contract.new_month(2, 2018, Bill())
        self.contract.new_month(3, 2018, temp_bill)
        self.assertEqual(0, self.contract.bill.free_min)
        self.assertEqual(0.1, self.contract.bill.min_rate)
        self.assertEqual(40, self.contract.bill.fixed_cost)

    def test_bill_call(self):
        self.contract.new_month(1, 2018, Bill())
        self.contract.bill_call(self.jan_call[0])
        self.assertEqual(2, self.contract.bill.free_min)
        self.assertEqual(0, self.contract.bill.billed_min)

    def test_bill_call_2(self):
        self.contract.new_month(1, 2018, Bill())
        for call in self.jan_call:
            self.contract.bill_call(call)
        self.assertEqual(8, self.contract.bill.free_min)
        self.assertEqual(0, self.contract.bill.billed_min)

    def test_bill_call_3(self):
        self.contract.new_month(2, 2018, Bill())
        for i in range(15):
            for call in self.jan_call:
                self.contract.bill_call(call)
        self.assertEqual(100, self.contract.bill.free_min)
        self.assertEqual(20, self.contract.bill.billed_min)

    def test_cancel_contract(self):
        self.contract.new_month(1, 2018, Bill())
        exp_res = 320
        act_res = self.contract.cancel_contract()
        self.assertEqual(exp_res, act_res, "There is no call in the first month and no deposit should be refund")

    def test_cancel_contract_2(self):
        self.contract.new_month(2, 2018, Bill())
        exp_res = 20
        act_res = self.contract.cancel_contract()
        self.assertEqual(exp_res, act_res, "You should return the deposit after the term date")

    def test_cancel_contract_3(self):
        self.contract.new_month(2, 2018, Bill())
        for i in range(15):
            for call in self.jan_call:
                self.contract.bill_call(call)
        exp_res = 22
        act_res = self.contract.cancel_contract()
        self.assertEqual(exp_res, act_res, "You should return the deposit even after the term date")

    def test_cancel_contract_4(self):
        self.contract.new_month(3, 2018, Bill())
        for i in range(15):
            for call in self.jan_call:
                self.contract.bill_call(call)
        exp_res = 22
        act_res = self.contract.cancel_contract()
        self.assertEqual(exp_res, act_res, "You should return the deposit even after the term date")

    def test_cancel_contract_5(self):
        self.contract.new_month(4, 2018, Bill())
        for i in range(15):
            for call in self.jan_call:
                self.contract.bill_call(call)
        exp_res = -278
        act_res = self.contract.cancel_contract()
        self.assertEqual(exp_res, act_res,
                         "You should return the deposit even after the term date")

    def test_cancel_contract_6(self):
        contract = TermContract(date(2018,1,1), date(2018,1,18))
        temp_bill = Bill()
        temp_bill.add_fixed_cost(20)
        contract.new_month(1,2018, Bill())
        exp_res = 320
        act_res = contract.cancel_contract()
        self.assertEqual(exp_res, act_res, "You should not return the deposit")

    def test_cancel_contract_7(self):
        contract = TermContract(date(2018, 1, 1), date(2018, 2, 18))
        contract.new_month(1, 2018, Bill())
        temp_bill = Bill()
        contract.new_month(2, 2018, temp_bill)
        exp_res = 20
        act_res = contract.cancel_contract()
        self.assertEqual(exp_res, act_res, "You should not return the deposit and charged the fixed cost")

    def test_cancel_contract_8(self):
        contract = TermContract(date(2018, 1, 1), date(2018, 2, 28))
        contract.new_month(1, 2018, Bill())
        temp_bill = Bill()
        contract.new_month(2, 2018, Bill())
        temp_bill.add_fixed_cost(30)
        contract.new_month(3, 2018, temp_bill)
        exp_res = -250
        act_res = contract.cancel_contract()
        self.assertEqual(exp_res, act_res, "You should  return the deposit")


class Test32(unittest.TestCase):
    def setUp(self):
        self.exp_start = date(2017,1,12)
        self.contract = MTMContract(date(2017, 1, 12))
        self.jan_call = create_call(jan_data)
        self.temp_bill = Bill()
        self.assertEqual(self.exp_start, self.contract.start)
        self.assertEqual(None, self.contract.bill)

    def test_new_month_1(self):
        self.assertEqual(None, self.contract.new_month(1, 2018, self.temp_bill))
        self.assertEqual(True, self.contract.bill == self.temp_bill)
        self.assertEqual(0, self.contract.bill.free_min)
        self.assertEqual(0.05, self.contract.bill.min_rate)
        self.assertEqual(50, self.contract.bill.fixed_cost)

    def test_new_month_2(self):
        self.contract.new_month(1,2018, Bill())
        temp_bill = Bill()
        self.contract.new_month(2,2018, temp_bill)
        self.assertEqual(0, self.contract.bill.free_min)
        self.assertEqual(0.05, self.contract.bill.min_rate)
        self.assertEqual(50, self.contract.bill.fixed_cost)

    def test_new_month_3(self):
        self.contract.new_month(1, 2018, Bill())
        temp_bill = Bill()
        temp_bill.add_fixed_cost(20)
        self.contract.new_month(2, 2018, Bill())
        self.contract.new_month(3, 2018, temp_bill)
        self.assertEqual(0, self.contract.bill.free_min)
        self.assertEqual(0.05, self.contract.bill.min_rate)
        self.assertEqual(70, self.contract.bill.fixed_cost)

    def test_bill_call(self):
        self.contract.new_month(1, 2018, Bill())
        self.contract.bill_call(self.jan_call[0])
        self.assertEqual(0, self.contract.bill.free_min)
        self.assertEqual(2, self.contract.bill.billed_min)

    def test_bill_call_2(self):
        self.contract.new_month(1, 2018, Bill())
        for call in self.jan_call:
            self.contract.bill_call(call)
        self.assertEqual(0, self.contract.bill.free_min)
        self.assertEqual(8, self.contract.bill.billed_min)

    def test_bill_call_3(self):
        self.contract.new_month(2, 2018, Bill())
        for i in range(15):
            for call in self.jan_call:
                self.contract.bill_call(call)
        self.assertEqual(0, self.contract.bill.free_min)
        self.assertEqual(120, self.contract.bill.billed_min)

    def test_cancel_contract(self):
        self.contract.new_month(1, 2018, Bill())
        exp_res = 50
        act_res = self.contract.cancel_contract()
        self.assertEqual(exp_res, act_res, "There is no call in the first month and you should be charged with full amout of MTM fee")

    def test_cancel_contract_2(self):
        self.contract.new_month(2, 2018, Bill())
        exp_res = 50
        act_res = self.contract.cancel_contract()
        self.assertEqual(exp_res, act_res, "There is no call in the first month and you should be charged with full amout of MTM fee")

    def test_cancel_contract_3(self):
        self.contract.new_month(3, 2018, Bill())
        for i in range(15):
            for call in self.jan_call:
                self.contract.bill_call(call)
        exp_res = 56
        act_res = self.contract.cancel_contract()
        self.assertEqual(exp_res, act_res, "There is no call in the first month and you should be charged with full amout of MTM fee")


class Test33(unittest.TestCase):
    def setUp(self):
        self.exp_start = date(2017, 1, 12)
        self.contract = PrepaidContract(date(2017, 1, 12), balance=50)
        self.jan_call = create_call(jan_data)
        self.temp_bill = Bill()
        self.contract.new_month(1,2017, self.temp_bill)
        self.assertEqual(self.exp_start, self.contract.start)
        self.assertEqual(self.temp_bill, self.contract.bill)

    def test_new_month(self):
        self.assertEqual(-50, self.contract.bill.fixed_cost)
        self.assertEqual(0.025, self.contract.bill.min_rate)
        self.assertEqual(0, self.contract.bill.billed_min)
        self.assertEqual(0, self.contract.bill.free_min)

    def test_new_month_2(self):
        temp_bill = Bill()
        temp_bill.add_fixed_cost(25)
        self.contract.new_month(2, 2017, temp_bill)
        self.assertEqual(-25, self.contract.bill.fixed_cost)

    def test_new_month_3(self):
        temp_bill = Bill()
        temp_bill.add_fixed_cost(25)
        self.contract.new_month(2, 2017, temp_bill)
        temp_bill_2 = Bill()
        temp_bill_2.add_fixed_cost(-25)
        self.contract.new_month(3,2017, temp_bill_2)
        self.assertEqual(-50, self.contract.bill.fixed_cost)

    def test_new_month_4(self):
        temp_bill = Bill()
        temp_bill.add_fixed_cost(41)
        self.contract.new_month(2, 2017, temp_bill)
        self.assertEqual(-9, self.contract.bill.fixed_cost)
        temp_bill_2 = Bill()
        temp_bill_2.add_fixed_cost(-9)
        self.contract.new_month(3, 2017, temp_bill_2)
        self.assertEqual(-43, self.contract.bill.fixed_cost)

    def test_new_month_5(self):
        temp_bill = Bill()
        temp_bill.add_fixed_cost(41)
        self.contract.new_month(2, 2017, temp_bill)
        self.assertEqual(-9, self.contract.bill.fixed_cost)
        temp_bill_2 = Bill()
        temp_bill_2.add_fixed_cost(41)
        self.contract.new_month(3, 2017, temp_bill_2)
        self.assertEqual(7, self.contract.bill.fixed_cost)

    def test_new_month_6(self):
        temp_bill = Bill()
        temp_bill.add_fixed_cost(25)
        self.contract.new_month(2, 2017, temp_bill)
        temp_bill_2 = Bill()
        temp_bill_2.add_fixed_cost(25)
        self.contract.new_month(3, 2017, temp_bill_2)
        self.assertEqual(0, self.contract.bill.fixed_cost)

    def test_bill_call(self):
        self.contract.new_month(1, 2018, Bill())
        self.contract.bill_call(self.jan_call[0])
        self.assertEqual(0, self.contract.bill.free_min)
        self.assertEqual(2, self.contract.bill.billed_min)

    def test_bill_call_2(self):
        self.contract.new_month(1, 2018, Bill())
        for call in self.jan_call:
            self.contract.bill_call(call)
        self.assertEqual(0, self.contract.bill.free_min)
        self.assertEqual(8, self.contract.bill.billed_min)

    def test_bill_call_3(self):
        self.contract.new_month(2, 2018, Bill())
        for i in range(15):
            for call in self.jan_call:
                self.contract.bill_call(call)
        self.assertEqual(0, self.contract.bill.free_min)
        self.assertEqual(120, self.contract.bill.billed_min)

    def test_cancel_contract(self):
        exp_res = 0
        act_res = self.contract.cancel_contract()
        self.assertEqual(exp_res,act_res, "The prepaid value will not be returned")

    def test_cancel_contract_2(self):
        temp_bill = Bill()
        temp_bill.add_fixed_cost(41)
        temp_bill.add_billed_minutes(400)
        self.contract.new_month(2, 2017, temp_bill)
        exp_res = 1
        act_res = self.contract.cancel_contract()
        self.assertEqual(exp_res, act_res, "The billed cost is 51 and credit is 50 you still own the company 1")

    def test_cancel_contract_3(self):
        temp_bill = Bill()
        temp_bill.add_fixed_cost(41)
        self.contract.new_month(2, 2017, temp_bill)
        temp_bill_2 = Bill()
        temp_bill_2.add_fixed_cost(41)
        self.contract.new_month(3, 2017, temp_bill_2)
        temp_bill.add_billed_minutes(100)
        self.assertEqual(7, self.contract.cancel_contract(), "YOu still own the company")

    def test_cancel_contract_4(self):
        temp_bill = Bill()
        temp_bill.add_fixed_cost(41)
        self.contract.new_month(1, 2017, temp_bill)
        temp_bill_2 = Bill()
        temp_bill_2.add_fixed_cost(24)
        self.contract.new_month(2, 2017, temp_bill_2)
        act_res = self.contract.cancel_contract()
        self.assertEqual(0, act_res, "The credit will not be returned")
unittest.main(exit=False)
