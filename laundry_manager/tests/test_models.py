"""Core data-integrity tests for the laundry manager."""
import os
import shutil
import tempfile
import unittest

_APPDATA = tempfile.mkdtemp(prefix="laundry_manager_tests_")
os.environ["APPDATA"] = _APPDATA

from database.connection import Database
from database.schema import initialize_database
from models.all_models import (
    CustomerModel,
    InvoiceModel,
    ItemTypeModel,
    OrderModel,
    UserModel,
)


class ModelTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        initialize_database()

    @classmethod
    def tearDownClass(cls):
        if Database._conn is not None:
            Database._conn.close()
            Database._conn = None
        shutil.rmtree(_APPDATA, ignore_errors=True)

    def _create_order(self):
        customer_id = CustomerModel.create("Test Customer", "", "", "", "individual", None, "")
        item = ItemTypeModel.get_all()[0]
        total = float(item["wash_price"]) * 2
        order_id, _ = OrderModel.create(
            customer_id,
            None,
            [{
                "item_type_id": item["id"],
                "item_name": item["name"],
                "service_type": "wash",
                "quantity": 2,
                "unit_price": item["wash_price"],
                "total_price": total,
            }],
            "at_order",
            0,
            "",
            1,
        )
        return order_id, customer_id, total

    def test_first_login_requires_a_password_change(self):
        admin = UserModel.get_by_username("admin")
        self.assertEqual(admin["must_change_password"], 1)
        UserModel.change_password(admin["id"], "a-secure-password")
        self.assertEqual(UserModel.get_by_id(admin["id"])["must_change_password"], 0)

    def test_order_invoice_and_payment_stay_in_sync(self):
        order_id, _, total = self._create_order()
        OrderModel.record_payment(order_id, total)
        order = OrderModel.get_by_id(order_id)
        invoice = InvoiceModel.get_all("paid")[0]
        self.assertEqual(order["payment_status"], "paid")
        self.assertEqual(invoice["order_id"], order_id)
        self.assertEqual(invoice["paid_amount"], total)

    def test_payment_rejects_invalid_amounts(self):
        order_id, _, total = self._create_order()
        with self.assertRaises(ValueError):
            OrderModel.record_payment(order_id, -1)
        with self.assertRaises(ValueError):
            OrderModel.record_payment(order_id, total + 1)

    def test_referenced_customer_cannot_be_deleted(self):
        _, customer_id, _ = self._create_order()
        with self.assertRaises(ValueError):
            CustomerModel.delete(customer_id)

    def test_invoice_filter_is_parameterized(self):
        self.assertEqual(InvoiceModel.get_all("unpaid' OR 1=1 --"), [])

    def test_order_rejects_customer_and_company_together(self):
        customer_id = CustomerModel.create("Separate Customer", "", "", "", "individual", None, "")
        from models.all_models import CompanyModel
        company_id = CompanyModel.create("Separate Company", "", "", "", "")
        item = ItemTypeModel.get_all()[0]
        with self.assertRaises(ValueError):
            OrderModel.create(
                customer_id, company_id,
                [{"item_type_id": item["id"], "item_name": item["name"],
                  "service_type": "wash", "quantity": 1,
                  "unit_price": item["wash_price"], "total_price": item["wash_price"]}],
                "at_order", 0, "", 1,
            )


if __name__ == "__main__":
    unittest.main()
