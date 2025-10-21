#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Tests for LotInfo class."""

import pytest
from datetime import date
import sys
from pathlib import Path

# プロジェクトのsrcディレクトリをパスに追加
project_root = Path(__file__).parent.parent
src_path = project_root / "src"
sys.path.insert(0, str(src_path))

from lot_info import LotInfo


class TestLotInfo:
    """LotInfoクラスのテストケース"""

    def test_lot_info_initialization(self):
        """LotInfoの初期化テスト"""
        lot_info = LotInfo()

        assert lot_info.machine_name == ""
        assert lot_info.model_name == ""
        assert lot_info.board_name == ""
        assert lot_info.lot_number == ""
        assert lot_info.model_code == ""
        assert lot_info.default_date is None
        assert lot_info.volume == 0
        assert lot_info.rest_volume == 0
        assert lot_info.line_code == ""
        assert lot_info.productions == {}
        assert lot_info.divisions_volume == 0

    def test_lot_info_attribute_assignment(self):
        """LotInfoの属性設定テスト"""
        lot_info = LotInfo()

        # 属性設定
        lot_info.machine_name = "GC01"
        lot_info.model_name = "VCB-NPB2F"
        lot_info.board_name = "DCP-133Z集合"
        lot_info.lot_number = "1198827-10"
        lot_info.model_code = "Y8470696RA"
        lot_info.default_date = date(2025, 10, 2)
        lot_info.volume = 2000
        lot_info.rest_volume = 0
        lot_info.line_code = "GC17"
        lot_info.productions = {"2025-10-02": 2000}
        lot_info.divisions_volume = 20

        # 設定値の確認
        assert lot_info.machine_name == "GC01"
        assert lot_info.model_name == "VCB-NPB2F"
        assert lot_info.board_name == "DCP-133Z集合"
        assert lot_info.lot_number == "1198827-10"
        assert lot_info.model_code == "Y8470696RA"
        assert lot_info.default_date == date(2025, 10, 2)
        assert lot_info.volume == 2000
        assert lot_info.rest_volume == 0
        assert lot_info.line_code == "GC17"
        assert lot_info.productions == {"2025-10-02": 2000}
        assert lot_info.divisions_volume == 20

    def test_lot_info_productions_dict(self):
        """productions辞書の操作テスト"""
        lot_info = LotInfo()

        # 生産予定を追加
        lot_info.productions["2025-10-01"] = 1000
        lot_info.productions["2025-10-02"] = 2000
        lot_info.productions["2025-10-03"] = 1500

        assert len(lot_info.productions) == 3
        assert lot_info.productions["2025-10-01"] == 1000
        assert lot_info.productions["2025-10-02"] == 2000
        assert lot_info.productions["2025-10-03"] == 1500

    def test_lot_info_vars_conversion(self):
        """LotInfoのvars()変換テスト"""
        lot_info = LotInfo()
        lot_info.machine_name = "GC01"
        lot_info.model_name = "VCB-NPB2F"
        lot_info.volume = 2000
        lot_info.productions = {"2025-10-02": 2000}

        vars_dict = vars(lot_info)

        assert isinstance(vars_dict, dict)
        assert vars_dict["machine_name"] == "GC01"
        assert vars_dict["model_name"] == "VCB-NPB2F"
        assert vars_dict["volume"] == 2000
        assert vars_dict["productions"] == {"2025-10-02": 2000}

    def test_lot_info_with_none_date(self):
        """default_dateがNoneの場合のテスト"""
        lot_info = LotInfo()

        # 初期状態ではNone
        assert lot_info.default_date is None

        # 明示的にNoneを設定
        lot_info.default_date = None
        assert lot_info.default_date is None

    def test_lot_info_with_japanese_text(self):
        """日本語テキストの設定テスト"""
        lot_info = LotInfo()

        lot_info.model_name = "テスト製品名"
        lot_info.board_name = "テスト基板/バージョン1.0"
        lot_info.line_code = "棚番テスト"

        assert lot_info.model_name == "テスト製品名"
        assert lot_info.board_name == "テスト基板/バージョン1.0"
        assert lot_info.line_code == "棚番テスト"


if __name__ == "__main__":
    # 直接実行時の簡易テスト
    print("LotInfoクラスのテストを実行中...")

    test_instance = TestLotInfo()

    try:
        test_instance.test_lot_info_initialization()
        print("✅ 初期化テスト成功")

        test_instance.test_lot_info_attribute_assignment()
        print("✅ 属性設定テスト成功")

        test_instance.test_lot_info_productions_dict()
        print("✅ productions辞書テスト成功")

        test_instance.test_lot_info_vars_conversion()
        print("✅ vars()変換テスト成功")

        test_instance.test_lot_info_with_none_date()
        print("✅ None日付テスト成功")

        test_instance.test_lot_info_with_japanese_text()
        print("✅ 日本語テキストテスト成功")

        print("すべてのLotInfoテストが成功しました！")

    except Exception as e:
        print(f"❌ テストエラー: {e}")
        import traceback

        traceback.print_exc()
