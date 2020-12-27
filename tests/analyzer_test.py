import unittest
from smtm import Analyzer
from unittest.mock import *

class AnalyzerTests(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_put_request_append_request(self):
        analyzer = Analyzer()
        analyzer.put_request("mango")
        self.assertEqual(analyzer.request[-1], "mango")

    def test_put_result_append_result(self):
        analyzer = Analyzer()
        analyzer.initialize("mango")
        analyzer.update_info_func = MagicMock()
        analyzer.put_result("banana")
        self.assertEqual(analyzer.result[-1], "banana")

    def test_put_result_call_update_info_func_with_asset_type_and_callback(self):
        analyzer = Analyzer()
        analyzer.initialize("mango")
        analyzer.update_info_func = MagicMock()
        analyzer.put_result("banana")
        analyzer.update_info_func.assert_called_once_with("asset", analyzer.put_asset_info)

    def test_initialize_keep_update_info_func(self):
        analyzer = Analyzer()
        analyzer.initialize("mango")
        self.assertEqual(analyzer.update_info_func, "mango")

    def test_put_asset_info_append_asset_info(self):
        analyzer = Analyzer()
        analyzer.make_score_record = MagicMock()
        analyzer.put_asset_info("apple")
        self.assertEqual(analyzer.asset_record_list[-1], "apple")

    def test_put_asset_info_should_call_make_score_record(self):
        analyzer = Analyzer()
        analyzer.make_score_record = MagicMock()
        analyzer.put_asset_info("apple")
        self.assertEqual(analyzer.asset_record_list[-1], "apple")
        analyzer.make_score_record.assert_called_once_with("apple")

    def test_make_start_point_call_update_info_func_with_asset_type_and_callback(self):
        analyzer = Analyzer()
        analyzer.update_info_func = MagicMock()
        analyzer.make_start_point()
        analyzer.update_info_func.assert_called_once_with("asset", analyzer.put_asset_info)

    def test_make_start_point_clear_asset_info_and_request_result(self):
        analyzer = Analyzer()
        analyzer.update_info_func = MagicMock()
        analyzer.request.append("mango")
        analyzer.result.append("banana")
        analyzer.asset_record_list.append("apple")
        analyzer.make_start_point()
        self.assertEqual(len(analyzer.request), 0)
        self.assertEqual(len(analyzer.result), 0)
        self.assertEqual(len(analyzer.asset_record_list), 0)

    def test_make_score_record_create_correct_score_record_when_asset_is_not_changed(self):
        analyzer = Analyzer()
        class DummyAssetInfo():
            pass
        dummy_asset = DummyAssetInfo()
        dummy_asset.balance = 50000
        dummy_asset.asset = [
            ("banana", 1500, 10),
            ("mango", 1000, 4.5),
            ("apple", 250, 2)]
        dummy_asset.quote = {
            "banana": 1700,
            "mango": 700,
            "apple": 500}

        # 시작점을 생성하기 위해 초기 자산 정보 추가
        analyzer.asset_record_list.append(dummy_asset)

        target_dummy_asset = DummyAssetInfo()
        target_dummy_asset.balance = 50000
        target_dummy_asset.asset = [
            ("banana", 1500, 10),
            ("mango", 1000, 4.5),
            ("apple", 250, 2)]
        target_dummy_asset.quote = {
            "banana": 2000,
            "mango": 1050,
            "apple": 400}
        target_dummy_asset.timestamp = 500

        analyzer.make_score_record(target_dummy_asset)
        self.assertEqual(len(analyzer.score_record_list), 1)

        score_record = analyzer.score_record_list[0]
        self.assertEqual(score_record.balance, 50000)
        self.assertEqual(score_record.cumulative_return, 6.149)

        self.assertEqual(score_record.asset[0][0], "banana")
        self.assertEqual(score_record.asset[0][1], 1500)
        self.assertEqual(score_record.asset[0][2], 2000)
        self.assertEqual(score_record.asset[0][3], 10)
        self.assertEqual(score_record.asset[0][4], 33.333)

        self.assertEqual(score_record.asset[1][0], "mango")
        self.assertEqual(score_record.asset[1][1], 1000)
        self.assertEqual(score_record.asset[1][2], 1050)
        self.assertEqual(score_record.asset[1][3], 4.5)
        self.assertEqual(score_record.asset[1][4], 5)

        self.assertEqual(score_record.asset[2][0], "apple")
        self.assertEqual(score_record.asset[2][1], 250)
        self.assertEqual(score_record.asset[2][2], 400)
        self.assertEqual(score_record.asset[2][3], 2)
        self.assertEqual(score_record.asset[2][4], 60)

        self.assertEqual(score_record.price_change_ratio[target_dummy_asset.asset[0][0]], 17.647)
        self.assertEqual(score_record.price_change_ratio[target_dummy_asset.asset[1][0]], 50)
        self.assertEqual(score_record.price_change_ratio[target_dummy_asset.asset[2][0]], -20)

    def test_make_score_record_create_correct_score_record_when_asset_is_changed(self):
        analyzer = Analyzer()
        class DummyAssetInfo():
            pass
        dummy_asset = DummyAssetInfo()
        dummy_asset.balance = 50000
        dummy_asset.asset = [
            ("banana", 1500, 10),
            ("apple", 250, 2)]
        dummy_asset.quote = {
            "banana": 1700,
            "mango": 500,
            "apple": 500}

        # 시작점을 생성하기 위해 초기 자산 정보 추가
        analyzer.asset_record_list.append(dummy_asset)

        target_dummy_asset = DummyAssetInfo()
        target_dummy_asset.balance = 10000
        target_dummy_asset.asset = [
            ("mango", 1000, 7.5),
            ("apple", 250, 10.7)]
        target_dummy_asset.quote = {
            "banana": 2000,
            "mango": 500,
            "apple": 800}

        target_dummy_asset.timestamp = 500

        analyzer.make_score_record(target_dummy_asset)
        self.assertEqual(len(analyzer.score_record_list), 1)

        score_record = analyzer.score_record_list[0]
        self.assertEqual(score_record.balance, 10000)
        self.assertEqual(score_record.cumulative_return, -67.191)

        self.assertEqual(score_record.asset[0][0], "mango")
        self.assertEqual(score_record.asset[0][1], 1000)
        self.assertEqual(score_record.asset[0][2], 500)
        self.assertEqual(score_record.asset[0][3], 7.5)
        self.assertEqual(score_record.asset[0][4], -50)

        self.assertEqual(score_record.asset[1][0], "apple")
        self.assertEqual(score_record.asset[1][1], 250)
        self.assertEqual(score_record.asset[1][2], 800)
        self.assertEqual(score_record.asset[1][3], 10.7)
        self.assertEqual(score_record.asset[1][4], 220)

        self.assertEqual(score_record.price_change_ratio[target_dummy_asset.asset[0][0]], 0)
        self.assertEqual(score_record.price_change_ratio[target_dummy_asset.asset[1][0]], 60)

    def test_make_score_record_create_correct_score_record_when_start_asset_is_empty(self):
        analyzer = Analyzer()
        class DummyAssetInfo():
            pass
        dummy_asset = DummyAssetInfo()
        dummy_asset.balance = 23456
        dummy_asset.asset = []
        dummy_asset.quote = {
            "banana": 1700,
            "mango": 300,
            "apple": 500}

        # 시작점을 생성하기 위해 초기 자산 정보 추가
        analyzer.asset_record_list.append(dummy_asset)

        target_dummy_asset = DummyAssetInfo()
        target_dummy_asset.balance = 5000
        target_dummy_asset.asset = [
            ("mango", 500, 5.23),
            ("apple", 250, 2.11)]
        target_dummy_asset.quote = {
            "banana": 2000,
            "mango": 300,
            "apple": 750}

        target_dummy_asset.timestamp = 500

        analyzer.make_score_record(target_dummy_asset)
        self.assertEqual(len(analyzer.score_record_list), 1)

        score_record = analyzer.score_record_list[0]
        self.assertEqual(score_record.balance, 5000)
        self.assertEqual(score_record.cumulative_return, -65.248)

        self.assertEqual(score_record.asset[0][0], "mango")
        self.assertEqual(score_record.asset[0][1], 500)
        self.assertEqual(score_record.asset[0][2], 300)
        self.assertEqual(score_record.asset[0][3], 5.23)
        self.assertEqual(score_record.asset[0][4], -40)

        self.assertEqual(score_record.asset[1][0], "apple")
        self.assertEqual(score_record.asset[1][1], 250)
        self.assertEqual(score_record.asset[1][2], 750)
        self.assertEqual(score_record.asset[1][3], 2.11)
        self.assertEqual(score_record.asset[1][4], 200)

        self.assertEqual(score_record.price_change_ratio[target_dummy_asset.asset[0][0]], 0)
        self.assertEqual(score_record.price_change_ratio[target_dummy_asset.asset[1][0]], 50)

    def test_make_score_record_create_correct_score_record_when_asset_and_balance_is_NOT_changed(self):
        analyzer = Analyzer()
        class DummyAssetInfo():
            pass
        dummy_asset = DummyAssetInfo()
        dummy_asset.balance = 1000
        dummy_asset.asset = []
        dummy_asset.quote = {"apple": 500}

        # 시작점을 생성하기 위해 초기 자산 정보 추가
        analyzer.asset_record_list.append(dummy_asset)

        target_dummy_asset = DummyAssetInfo()
        target_dummy_asset.balance = 1000
        target_dummy_asset.asset = []
        target_dummy_asset.quote = {"apple": 750}

        target_dummy_asset.timestamp = 500

        analyzer.make_score_record(target_dummy_asset)
        self.assertEqual(len(analyzer.score_record_list), 1)

        score_record = analyzer.score_record_list[0]
        self.assertEqual(score_record.balance, 1000)
        self.assertEqual(score_record.cumulative_return, 0)

        self.assertEqual(len(score_record.asset), 0)
        self.assertEqual(len(score_record.price_change_ratio.keys()), 0)
