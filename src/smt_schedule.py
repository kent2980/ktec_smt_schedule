import pandas as pd
import os
from .lot_info import LotInfo
from typing import Dict
from pathlib import Path


class SMTSchedule:

    @staticmethod
    def get_lot_info(dir_path: str, line_code: str) -> pd.DataFrame:
        """
        ExcelファイルのアクティブシートからLotInfoのDataFrameを生成する
        .xlsx と .xls 形式に対応

        Args:
            dir_path (str): Excelファイルが格納されているディレクトリパス
            line_code (str): ライン識別コード

        Returns:
            pd.DataFrame: LotInfo情報を含むDataFrame
        """
        project_dir = Path(__file__).resolve().parent.parent

        try:
            path = os.path.join(dir_path, f"{line_code}.xls")
            if not os.path.exists(path):
                raise FileNotFoundError(f"指定されたファイルが存在しません: {path}")
            # ファイル拡張子を取得
            _, ext = os.path.splitext(path)
            ext = ext.lower()

            support_ext = [".xlsx", ".xls"]

            if ext in support_ext:
                df = pd.read_excel(path, sheet_name=0)  # 最初のシートを読み取り
                # dfの8行目をヘッダーに設定
                df.columns = df.iloc[6, :]
                # dfから最初の10行を削除
                df = df.iloc[10:, :].reset_index(drop=True)
                # dfからA列を削除
                df = df.iloc[:, 1:]
                # dfのすべての行を検査してA列が空白の行を削除
                df = df[df.iloc[:, 0].notna()].reset_index(drop=True)
                # dfからすべての行を検査してAK列が数値以外の行を削除
                df = df[
                    pd.to_numeric(df.iloc[:, 36], errors="coerce").notna()
                ].reset_index(drop=True)
                df.to_csv(Path.joinpath(project_dir, "out.csv").as_posix())
                # dfから
                i = 0
                lot_info_dict: Dict[str, LotInfo] = {}
                for index, row in df.iterrows():
                    if i == 0:
                        info = LotInfo()
                        info.machine_name = line_code.split(".")[0]
                    # rowが偶数行なら
                    try:
                        if index % 2 == 0:
                            # すでに追加済みの指図の場合スキップ
                            if row["指図－工程"] in lot_info_dict:
                                i = 0
                                continue
                            info.model_name = row["品 目 名 称"]
                            info.lot_number = row["指図－工程"]
                            info.default_date = row["基 準"]
                            info.rest_volume = (
                                row["前 月 累 計"]
                                if pd.isna(row["前 月 累 計"] == False)
                                else 0
                            )
                            info.line_code = row["日付"]
                            info.divisions_volume = (
                                row["取数"] if row["取数"] != "nan" else 0
                            )
                            i += 1
                            # 生産計画を読み込む
                            for r in range(7, 30):
                                column_name = df.columns[r]
                                if pd.isna(row[column_name]) == False:
                                    info.productions[column_name] = row[column_name]
                        # rowが偶数行なら
                        else:
                            info.board_name = row["品 目 名 称"].split("/")[0]
                            info.model_code = row["指図－工程"]
                            info.volume = (
                                row["前 月 累 計"] if row["前 月 累 計"] != "nan" else 0
                            )
                            i += 1
                        if i == 2:
                            if len(info.productions) > 0:
                                lot_info_dict[info.lot_number] = info
                            i = 0
                    except Exception as e:
                        print(
                            f"行の処理中にエラーが発生しました (行番号: {index + 1}): {e}"
                        )
                        continue
                # 辞書をDataFrameに変換して返す
                if lot_info_dict:
                    return pd.DataFrame([vars(info) for info in lot_info_dict.values()])
                else:
                    return pd.DataFrame()
            else:
                raise ValueError(
                    f"サポートされていないファイル形式です: {ext}。.xlsx または .xlsb ファイルを使用してください。"
                )

        except Exception as e:
            raise Exception(f"ファイル読み取りエラー: {str(e)}")

    @staticmethod
    def get_lot_infos(dir_path: str, start_line: int, end_line: int) -> pd.DataFrame:
        """
        指定された範囲内で最初に見つかった有効なExcelファイルを読み込み、LotInfoのDataFrameを連結して返す
        """
        df_list = []
        for code in range(start_line, end_line):
            line_code = f"GC{code:02d}"
            print(f"Processing {line_code}.xls")
            try:
                df = SMTSchedule.get_lot_info(dir_path, line_code)
                if not df.empty:
                    df_list.append(df)
            except FileNotFoundError:
                print(f"ファイルが見つかりません: {line_code}.xls")
                continue
            except Exception as e:
                print(f"エラーが発生しました ({line_code}.xls): {e}")
                continue

        if df_list:
            return pd.concat(df_list, ignore_index=True)
        return pd.DataFrame()
