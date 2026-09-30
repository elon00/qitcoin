import unittest

COIN = 1_000_000
MAX_SUPPLY_QTC = 1_000_000_000_000
MAX_MONEY = MAX_SUPPLY_QTC * COIN
INITIAL = 250_000 * COIN
INTERVAL = 2_000_000

def subsidy(height):
    h = height // INTERVAL
    return 0 if h >= 38 else INITIAL >> h

class MonetaryPolicyTest(unittest.TestCase):
    def test_int64_safety(self):
        self.assertLessEqual(MAX_MONEY, 2**63 - 1)

    def test_boundaries(self):
        self.assertEqual(subsidy(0), 250_000 * COIN)
        self.assertEqual(subsidy(INTERVAL - 1), 250_000 * COIN)
        self.assertEqual(subsidy(INTERVAL), 125_000 * COIN)
        self.assertEqual(subsidy(38 * INTERVAL), 0)

    def test_total_issuance_cap(self):
        total = sum(subsidy(i * INTERVAL) * INTERVAL for i in range(38))
        self.assertEqual(total // COIN, 999_999_999_974)
        self.assertLessEqual(total, MAX_MONEY)

if __name__ == "__main__":
    unittest.main()
