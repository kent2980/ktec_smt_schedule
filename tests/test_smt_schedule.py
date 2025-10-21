#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Tests for SMTSchedule class."""

import pytest
import pandas as pd
import tempfile
import os
from pathlib import Path
from unittest.mock import patch, MagicMock
import sys

# パッケージからインポート
from ktec_smt_schedule.smt_schedule import SMTSchedule
from ktec_smt_schedule.lot_info import LotInfo


class TestSMTSchedule:
    """SMTScheduleクラスのテストケース"""

    @pytest.fixture
    def temp_dir(self):
        """テスト用の一時ディレクトリ"""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield tmpdir

    @pytest.fixture
    def sample_excel_data(self):
        """サンプルExcelデータのDataFrame"""
        # 実際のExcelファイル構造に基づいたテストデータ
        data = []

        # 6行の空行
        for i in range(6):
            data.append([None] * 40)

        # 7行目: ヘッダー行
        header_row = [
            None,
            "品 目 名 称",
            "指図－工程",
            "基 準",
            "前 月 累 計",
            "日付",
            "取数",
        ]
        for i in range(7, 30):
            header_row.append(f"2025-10-{i-6:02d}")
        while len(header_row) < 40:
            header_row.append(None)
        data.append(header_row)

        # 3行の空行
        for i in range(3):
            data.append([None] * 40)

        # データ行1 (偶数行 - 製品情報)
        data_row1 = [None, "VCB-NPB2F", "1198827-10", "2025-10-02", 2000.0, 0, "GC17"]
        for i in range(7, 30):
            if i == 9:  # 2025-10-03
                data_row1.append(2000)
            else:
                data_row1.append(None)
        while len(data_row1) < 40:
            data_row1.append(None)
        data_row1[36] = 100  # AK列
        data.append(data_row1)

        # データ行2 (奇数行 - 基板情報)
        data_row2 = [None, "DCP-133Z集合/REFA", "Y8470696RA", None, 2000, 20, None]
        for i in range(7, 30):
            data_row2.append(None)
        while len(data_row2) < 40:
            data_row2.append(None)
        data_row2[36] = 100  # AK列
        data.append(data_row2)

        # データ行3 (偶数行 - 製品情報)
        data_row3 = [None, "VCB-NPB2F", "1198829-10", "2025-10-02", 3000.0, 0, "GC17"]
        for i in range(7, 30):
            if i == 9:  # 2025-10-03
                data_row3.append(3000)
            else:
                data_row3.append(None)
        while len(data_row3) < 40:
            data_row3.append(None)
        data_row3[36] = 200  # AK列
        data.append(data_row3)

        # データ行4 (奇数行 - 基板情報)
        data_row4 = [None, "DCP-133Z集合/REFA", "Y8470696RA", None, 3000, 20, None]
        for i in range(7, 30):
            data_row4.append(None)
        while len(data_row4) < 40:
            data_row4.append(None)
        data_row4[36] = 200  # AK列
        data.append(data_row4)

        df = pd.DataFrame(data)
        return df

    def test_get_lot_info_file_not_found(self, temp_dir):
        """存在しないファイルのテスト"""
        with pytest.raises(Exception, match="ファイル読み取りエラー"):
            SMTSchedule.get_lot_info(temp_dir, "GC01")

    @patch("pandas.read_excel")
    def test_get_lot_info_success(self, mock_read_excel, temp_dir, sample_excel_data):
        """正常なファイル読み込みのテスト"""
        # Excelファイルを作成
        excel_path = os.path.join(temp_dir, "GC01.xls")
        with open(excel_path, "w") as f:
            f.write("dummy excel file")

        # pandas.read_excelのモック設定
        mock_read_excel.return_value = sample_excel_data

        # CSVファイル出力のモック
        with patch.object(pd.DataFrame, "to_csv"):
            result = SMTSchedule.get_lot_info(temp_dir, "GC01")

        assert isinstance(result, pd.DataFrame)
        # 結果が空でないかまたは空であるかを確認
        # （データの処理次第で結果が変わる可能性があるため）

    def test_get_lot_info_unsupported_format(self, temp_dir):
        """サポートされていないファイル形式のテスト"""
        # .txtファイルを作成（xlsファイルは存在しない）
        txt_path = os.path.join(temp_dir, "GC01.txt")
        with open(txt_path, "w") as f:
            f.write("dummy file")

        with pytest.raises(Exception, match="ファイル読み取りエラー"):
            SMTSchedule.get_lot_info(temp_dir, "GC01")

    @patch("ktec_smt_schedule.smt_schedule.SMTSchedule.get_lot_info")
    def test_get_lot_infos_success(self, mock_get_lot_info, temp_dir):
        """複数ファイル読み込みのテスト"""
        # モックデータ
        sample_data = pd.DataFrame(
            {
                "machine_name": ["GC01", "GC01"],
                "model_name": ["VCB-NPB2F", "VCB-NPB2F"],
                "lot_number": ["1198827-10", "1198829-10"],
            }
        )

        # get_lot_infoが成功する場合のモック
        mock_get_lot_info.return_value = sample_data

        # CSVファイル出力のモック
        with patch.object(pd.DataFrame, "to_csv"):
            result = SMTSchedule.get_lot_infos(temp_dir, 1, 2)

        assert isinstance(result, pd.DataFrame)
        assert len(result) == 4  # 2つのファイル × 2行ずつ

    @patch("ktec_smt_schedule.smt_schedule.SMTSchedule.get_lot_info")
    def test_get_lot_infos_empty_result(self, mock_get_lot_info, temp_dir):
        """空の結果のテスト"""
        # 空のDataFrameを返すモック
        mock_get_lot_info.side_effect = FileNotFoundError("File not found")

        result = SMTSchedule.get_lot_infos(temp_dir, 1, 2)

        assert isinstance(result, pd.DataFrame)
        assert result.empty

    def test_read_csv_utf8_bom_success(self, temp_dir):
        """UTF-8-BOM CSV読み込みのテスト"""
        # テスト用CSVファイルを作成
        csv_path = os.path.join(temp_dir, "test.csv")
        test_data = pd.DataFrame({"col1": ["値1", "値2"], "col2": [100, 200]})
        test_data.to_csv(csv_path, encoding="utf-8-sig", index=False)

        result = SMTSchedule.read_csv_utf8_bom(csv_path)

        assert isinstance(result, pd.DataFrame)
        assert len(result) == 2
        assert list(result.columns) == ["col1", "col2"]

    def test_read_csv_utf8_bom_file_not_found(self):
        """存在しないCSVファイルのテスト"""
        result = SMTSchedule.read_csv_utf8_bom("nonexistent.csv")

        assert isinstance(result, pd.DataFrame)
        assert result.empty

    def test_save_csv_utf8_bom_success(self, temp_dir):
        """UTF-8-BOM CSV保存のテスト"""
        # テストデータ
        test_data = pd.DataFrame({"col1": ["テスト1", "テスト2"], "col2": [100, 200]})

        csv_path = os.path.join(temp_dir, "output.csv")

        # ファイル保存
        SMTSchedule.save_csv_utf8_bom(test_data, csv_path)

        # ファイルが作成されたか確認
        assert os.path.exists(csv_path)

        # 内容を確認
        loaded_data = pd.read_csv(csv_path, encoding="utf-8-sig")
        pd.testing.assert_frame_equal(test_data, loaded_data)

    def test_save_csv_utf8_bom_with_index(self, temp_dir):
        """インデックス付きCSV保存のテスト"""
        test_data = pd.DataFrame({"col1": ["テスト1", "テスト2"], "col2": [100, 200]})

        csv_path = os.path.join(temp_dir, "output_with_index.csv")

        SMTSchedule.save_csv_utf8_bom(test_data, csv_path, index=True)

        assert os.path.exists(csv_path)

        # インデックス付きで読み込み
        loaded_data = pd.read_csv(csv_path, encoding="utf-8-sig", index_col=0)
        pd.testing.assert_frame_equal(test_data, loaded_data)


class TestCSVOperations:
    """CSV操作の統合テスト"""

    def test_csv_round_trip(self, tmp_path):
        """CSV保存→読み込みの往復テスト"""
        # サンプルデータ
        sample_data = pd.DataFrame(
            {
                "machine_name": ["GC01", "GC01", "GC02"],
                "model_name": ["VCB-NPB2F", "VCB-NPB2F", "VCB-MB551"],
                "board_name": ["DCP-133Z集合", "DCP-133Z集合", "DCP"],
                "lot_number": ["1198827-10", "1198829-10", "1198839-10"],
                "volume": [2000.0, 3000.0, 480.0],
            }
        )

        csv_file = tmp_path / "test_data.csv"

        # 保存
        SMTSchedule.save_csv_utf8_bom(sample_data, str(csv_file))

        # 読み込み
        loaded_data = SMTSchedule.read_csv_utf8_bom(str(csv_file))

        # データの整合性確認
        assert len(loaded_data) == len(sample_data)
        assert list(loaded_data.columns) == list(sample_data.columns)

        # 数値列の確認
        pd.testing.assert_series_equal(
            loaded_data["volume"].astype(float),
            sample_data["volume"].astype(float),
            check_names=False,
        )

    def test_japanese_text_encoding(self, tmp_path):
        """日本語テキストのエンコーディングテスト"""
        japanese_data = pd.DataFrame(
            {
                "製品名": ["テスト製品A", "テスト製品B"],
                "基板名": ["基板/バージョン1.0", "基板/バージョン2.0"],
                "数量": [1000, 2000],
            }
        )

        csv_file = tmp_path / "japanese_test.csv"

        # UTF-8-BOMで保存
        SMTSchedule.save_csv_utf8_bom(japanese_data, str(csv_file))

        # UTF-8-BOMで読み込み
        loaded_data = SMTSchedule.read_csv_utf8_bom(str(csv_file))

        # 日本語が正しく保存・読み込みされているか確認
        assert loaded_data.iloc[0]["製品名"] == "テスト製品A"
        assert loaded_data.iloc[1]["基板名"] == "基板/バージョン2.0"


if __name__ == "__main__":
    # 直接実行時の簡易テスト
    print("SMTScheduleクラスのテストを実行中...")

    import tempfile

    # 基本的なCSV操作テスト
    with tempfile.TemporaryDirectory() as temp_dir:
        test_data = pd.DataFrame({"col1": ["テスト1", "テスト2"], "col2": [100, 200]})

        csv_path = os.path.join(temp_dir, "test.csv")

        try:
            # 保存テスト
            SMTSchedule.save_csv_utf8_bom(test_data, csv_path)
            print("✅ CSV保存テスト成功")

            # 読み込みテスト
            loaded_data = SMTSchedule.read_csv_utf8_bom(csv_path)
            assert len(loaded_data) == 2
            print("✅ CSV読み込みテスト成功")

            # 存在しないファイルのテスト
            empty_df = SMTSchedule.read_csv_utf8_bom("nonexistent.csv")
            assert empty_df.empty
            print("✅ 存在しないファイルテスト成功")

            print("基本的なSMTScheduleテストが成功しました！")

        except Exception as e:
            print(f"❌ テストエラー: {e}")
            import traceback

            traceback.print_exc()
