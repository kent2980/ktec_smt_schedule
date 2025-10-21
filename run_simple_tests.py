#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""テスト実行スクリプト - UV環境対応"""

import sys
import os
from pathlib import Path

# プロジェクトルートとsrcディレクトリをパスに追加
project_root = Path(__file__).parent
src_path = project_root / "src"
sys.path.insert(0, str(src_path))


def test_basic_imports():
    """基本的なインポートテスト"""
    print("=== 基本インポートテスト ===")
    try:
        from smt_schedule import SMTSchedule
        from lot_info import LotInfo

        print("✅ パッケージインポート成功")
        return True
    except ImportError as e:
        print(f"❌ インポートエラー: {e}")
        return False


def test_lot_info():
    """LotInfoクラスのテスト"""
    print("\n=== LotInfoテスト ===")
    try:
        from lot_info import LotInfo
        from datetime import date

        # 初期化テスト
        lot_info = LotInfo()
        assert lot_info.machine_name == ""
        assert lot_info.volume == 0
        assert lot_info.productions == {}
        print("✅ LotInfo初期化成功")

        # 属性設定テスト
        lot_info.machine_name = "GC01"
        lot_info.model_name = "テスト製品"
        lot_info.volume = 1000
        lot_info.productions["2025-10-01"] = 500

        assert lot_info.machine_name == "GC01"
        assert lot_info.model_name == "テスト製品"
        assert lot_info.volume == 1000
        assert lot_info.productions["2025-10-01"] == 500
        print("✅ LotInfo属性設定成功")

        return True
    except Exception as e:
        print(f"❌ LotInfoテストエラー: {e}")
        return False


def test_smt_schedule_csv():
    """SMTScheduleのCSV機能テスト"""
    print("\n=== SMTSchedule CSV機能テスト ===")
    try:
        from smt_schedule import SMTSchedule
        import pandas as pd
        import tempfile

        # テストデータ
        test_data = pd.DataFrame(
            {
                "col1": ["テスト1", "テスト2"],
                "col2": [100, 200],
                "日本語列": ["値A", "値B"],
            }
        )

        with tempfile.TemporaryDirectory() as temp_dir:
            csv_path = os.path.join(temp_dir, "test.csv")

            # 保存テスト
            SMTSchedule.save_csv_utf8_bom(test_data, csv_path)
            assert os.path.exists(csv_path)
            print("✅ CSV保存成功")

            # 読み込みテスト
            loaded_data = SMTSchedule.read_csv_utf8_bom(csv_path)
            assert len(loaded_data) == 2
            assert len(loaded_data.columns) == 3
            assert loaded_data.iloc[0]["col1"] == "テスト1"
            assert loaded_data.iloc[1]["日本語列"] == "値B"
            print("✅ CSV読み込み成功")

            # 存在しないファイルテスト
            empty_df = SMTSchedule.read_csv_utf8_bom("nonexistent.csv")
            assert empty_df.empty
            print("✅ 存在しないファイル処理成功")

        return True
    except Exception as e:
        print(f"❌ SMTSchedule CSVテストエラー: {e}")
        import traceback

        traceback.print_exc()
        return False


def test_environment():
    """環境情報の表示"""
    print("\n=== 環境情報 ===")
    import platform

    print(f"Python: {sys.version}")
    print(f"Platform: {platform.platform()}")
    print(f"Architecture: {platform.architecture()}")

    # 依存関係チェック
    try:
        import pandas as pd

        print(f"✅ pandas: {pd.__version__}")
    except ImportError:
        print("❌ pandas not found")

    try:
        import numpy as np

        print(f"✅ numpy: {np.__version__}")
    except ImportError:
        print("❌ numpy not found")

    try:
        import openpyxl

        print(f"✅ openpyxl: {openpyxl.__version__}")
    except ImportError:
        print("❌ openpyxl not found")


def main():
    """メイン関数"""
    print("ktec_smt_schedule - 簡易テスト実行")
    print("=" * 50)

    # 環境情報表示
    test_environment()

    # テスト実行
    tests_passed = 0
    total_tests = 3

    if test_basic_imports():
        tests_passed += 1

    if test_lot_info():
        tests_passed += 1

    if test_smt_schedule_csv():
        tests_passed += 1

    # 結果表示
    print("\n" + "=" * 50)
    print(f"テスト結果: {tests_passed}/{total_tests} 成功")

    if tests_passed == total_tests:
        print("✅ すべてのテストが成功しました！")
        return 0
    else:
        print(f"❌ {total_tests - tests_passed} 個のテストが失敗しました")
        return 1


if __name__ == "__main__":
    sys.exit(main())
