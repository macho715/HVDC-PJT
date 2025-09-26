"""
HVDC Excel Reporter - Calculation Module
"""

import pandas as pd
import numpy as np
from datetime import datetime
from typing import Dict, List
import logging
from src import config, utils

logger = logging.getLogger(__name__)


class WarehouseCalculator:
    """
    Handles all business logic and calculations for the HVDC report.
    """

    def __init__(self):
        self.warehouse_columns = config.WAREHOUSE_COLUMNS
        self.site_columns = config.SITE_COLUMNS
        self.flow_codes = config.FLOW_CODES
        self.LOC_PRIORITY = config.LOC_PRIORITY
        self.warehouse_base_sqm = config.WAREHOUSE_BASE_SQM
        self.warehouse_sqm_rates = config.WAREHOUSE_SQM_RATES

    def process_real_data(self, df: pd.DataFrame):
        """
        Processes the raw data, including date conversion and Flow Code calculation.
        """
        logger.info("🔧 Processing raw data...")

        date_columns = (
            ["ETD/ATD", "ETA/ATA", "Status_Location_Date"]
            + self.warehouse_columns
            + self.site_columns
        )
        for col in date_columns:
            if col in df.columns:
                df[col] = pd.to_datetime(df[col], errors="coerce")

        df = self._override_flow_code(df)

        if "Pkg" in df.columns:
            df["total handling"] = df["Pkg"].fillna(1).astype(int)
        else:
            df["total handling"] = 1

        logger.info("✅ Raw data processing complete.")
        return df

    def _override_flow_code(self, df: pd.DataFrame):
        """
        Recalculates the Flow Code based on the latest logic.
        """
        logger.info("🔄 Recalculating Flow Code...")

        WH_COLS = [col for col in self.warehouse_columns if col != "MOSB"]
        MOSB_COLS = ["MOSB"]

        if "wh handling" in df.columns:
            df.rename(columns={"wh handling": "wh_handling_legacy"}, inplace=True)

        for col in WH_COLS + MOSB_COLS:
            if col in df.columns:
                df[col] = df[col].replace({0: np.nan, "": np.nan})

        status_col = "Status_Location"
        if status_col in df.columns:
            is_pre_arrival = df[status_col].str.contains(
                "Pre Arrival", case=False, na=False
            )
        else:
            is_pre_arrival = pd.Series(False, index=df.index)

        wh_cnt = df[WH_COLS].notna().sum(axis=1)
        offshore = df[MOSB_COLS].notna().any(axis=1).astype(int)

        base_step = 1
        flow_raw = wh_cnt + offshore + base_step

        df["FLOW_CODE"] = np.where(is_pre_arrival, 0, np.clip(flow_raw, 1, 4))
        df["FLOW_DESCRIPTION"] = df["FLOW_CODE"].map(self.flow_codes)

        logger.info("✅ Flow Code recalculation complete.")
        return df

    def calculate_final_location(self, df: pd.DataFrame):
        """
        Calculates the final location of items based on priority.
        """
        logger.info("🔄 Calculating final location...")

        def calc_final_location(row):
            all_locations = self.warehouse_columns + self.site_columns
            dated = {c: row[c] for c in all_locations if c in row and pd.notna(row[c])}

            if not dated:
                return "Unknown"

            max_date = max(dated.values())
            latest = [l for l, d in dated.items() if d == max_date]

            if len(latest) > 1:
                latest.sort(key=lambda x: self.LOC_PRIORITY.get(x, 99))

            return latest[0]

        df["Final_Location"] = df.apply(calc_final_location, axis=1)
        logger.info("✅ Final location calculation complete.")
        return df

    def detect_same_date_warehouse_transfer(self, row) -> List[Dict]:
        """
        Detects same-day transfers between warehouses.
        """
        transfers = []
        warehouse_pairs = [
            ("DSV Indoor", "DSV Al Markaz"),
            ("DSV Indoor", "DSV Outdoor"),
            ("DSV Al Markaz", "DSV Outdoor"),
            ("DSV Indoor", "MOSB"),
            ("DSV Al Markaz", "MOSB"),
        ]

        for from_wh, to_wh in warehouse_pairs:
            from_date = pd.to_datetime(row.get(from_wh), errors="coerce")
            to_date = pd.to_datetime(row.get(to_wh), errors="coerce")

            if (
                pd.notna(from_date)
                and pd.notna(to_date)
                and from_date.date() == to_date.date()
            ):
                transfers.append(
                    {
                        "from_warehouse": from_wh,
                        "to_warehouse": to_wh,
                        "transfer_date": from_date,
                        "pkg_quantity": utils.get_pkg(row),
                        "transfer_type": "warehouse_to_warehouse",
                    }
                )
        return transfers

    def calculate_warehouse_inbound(self, df: pd.DataFrame) -> Dict:
        """
        Calculates warehouse inbound movements.
        """
        logger.info("🔄 Calculating warehouse inbound...")
        inbound_items = []
        warehouse_transfers = []
        total_inbound = 0
        by_warehouse = {}
        by_month = {}

        all_locations = self.warehouse_columns + self.site_columns

        for idx, row in df.iterrows():
            transfers = self.detect_same_date_warehouse_transfer(row)

            for transfer in transfers:
                warehouse_transfers.append(
                    {
                        "Item_ID": idx,
                        "Transfer_Type": "warehouse_to_warehouse",
                        "From_Warehouse": transfer["from_warehouse"],
                        "To_Warehouse": transfer["to_warehouse"],
                        "Transfer_Date": transfer["transfer_date"],
                        "Year_Month": transfer["transfer_date"].strftime("%Y-%m"),
                        "Pkg_Quantity": transfer["pkg_quantity"],
                    }
                )

            for location in all_locations:
                if location in row.index and pd.notna(row[location]):
                    try:
                        arrival_date = pd.to_datetime(row[location])
                        pkg_quantity = utils.get_pkg(row)

                        is_transfer_destination = any(
                            t["to_warehouse"] == location for t in transfers
                        )

                        if not is_transfer_destination:
                            inbound_items.append(
                                {
                                    "Item_ID": idx,
                                    "Location": location,
                                    "Warehouse": location,
                                    "Inbound_Date": arrival_date,
                                    "Year_Month": arrival_date.strftime("%Y-%m"),
                                    "Vendor": row.get("Vendor", "Unknown"),
                                    "Pkg_Quantity": pkg_quantity,
                                    "Status_Location": row.get(
                                        "Status_Location", "Unknown"
                                    ),
                                    "Inbound_Type": "external_arrival",
                                }
                            )
                            total_inbound += pkg_quantity
                            by_warehouse[location] = (
                                by_warehouse.get(location, 0) + pkg_quantity
                            )
                            month_key = arrival_date.strftime("%Y-%m")
                            by_month[month_key] = (
                                by_month.get(month_key, 0) + pkg_quantity
                            )
                    except Exception as e:
                        logger.warning(
                            f"Error parsing date (Row {idx}, Location {location}): {e}"
                        )
                        continue

        logger.info("✅ Inbound calculation complete.")
        return {
            "total_inbound": total_inbound,
            "by_warehouse": by_warehouse,
            "by_month": by_month,
            "inbound_items": inbound_items,
            "warehouse_transfers": warehouse_transfers,
        }

    def calculate_warehouse_outbound(self, df: pd.DataFrame) -> Dict:
        """
        Calculates warehouse outbound movements.
        """
        logger.info("🔄 Calculating warehouse outbound...")
        outbound_items = []
        total_outbound = 0
        by_warehouse = {}
        by_month = {}

        all_locations = self.warehouse_columns + self.site_columns

        for idx, row in df.iterrows():
            transfers = self.detect_same_date_warehouse_transfer(row)

            for transfer in transfers:
                pkg_quantity = transfer["pkg_quantity"]
                transfer_date = transfer["transfer_date"]
                from_wh = transfer["from_warehouse"]

                outbound_items.append(
                    {
                        "Item_ID": idx,
                        "From_Location": from_wh,
                        "To_Location": transfer["to_warehouse"],
                        "Warehouse": from_wh,
                        "Outbound_Date": transfer_date,
                        "Year_Month": transfer_date.strftime("%Y-%m"),
                        "Pkg_Quantity": pkg_quantity,
                        "Status_Location": row.get("Status_Location", "Unknown"),
                        "Outbound_Type": "warehouse_transfer",
                    }
                )
                total_outbound += pkg_quantity
                by_warehouse[from_wh] = by_warehouse.get(from_wh, 0) + pkg_quantity
                month_key = transfer_date.strftime("%Y-%m")
                by_month[month_key] = by_month.get(month_key, 0) + pkg_quantity

            for location in all_locations:
                if location in row.index and pd.notna(row[location]):
                    try:
                        current_date = pd.to_datetime(row[location])
                        next_movements = []
                        for next_loc in self.site_columns:
                            if next_loc in row.index and pd.notna(row[next_loc]):
                                next_date = pd.to_datetime(row[next_loc])
                                if next_date >= current_date:
                                    next_movements.append((next_loc, next_date))

                        if next_movements:
                            next_location, next_date = min(
                                next_movements, key=lambda x: x[1]
                            )
                            pkg_quantity = utils.get_pkg(row)

                            outbound_items.append(
                                {
                                    "Item_ID": idx,
                                    "From_Location": location,
                                    "To_Location": next_location,
                                    "Warehouse": location,
                                    "Site": next_location,
                                    "Outbound_Date": next_date,
                                    "Year_Month": next_date.strftime("%Y-%m"),
                                    "Pkg_Quantity": pkg_quantity,
                                    "Status_Location": row.get(
                                        "Status_Location", "Unknown"
                                    ),
                                    "Outbound_Type": "warehouse_to_site",
                                }
                            )
                            total_outbound += pkg_quantity
                            by_warehouse[location] = (
                                by_warehouse.get(location, 0) + pkg_quantity
                            )
                            month_key = next_date.strftime("%Y-%m")
                            by_month[month_key] = (
                                by_month.get(month_key, 0) + pkg_quantity
                            )
                    except Exception as e:
                        logger.warning(
                            f"Error in outbound calculation (Row {idx}, Location {location}): {e}"
                        )
                        continue

        logger.info("✅ Outbound calculation complete.")
        return {
            "total_outbound": total_outbound,
            "by_warehouse": by_warehouse,
            "by_month": by_month,
            "outbound_items": outbound_items,
        }

    def calculate_warehouse_inventory(self, df: pd.DataFrame) -> Dict:
        """
        Calculates warehouse inventory based on Status_Location.
        """
        logger.info("🔄 Calculating warehouse inventory...")
        all_locations = self.warehouse_columns + self.site_columns
        month_range = pd.date_range("2023-02", "2025-06", freq="MS")
        month_strings = [month.strftime("%Y-%m") for month in month_range]

        inventory_by_month = {}
        inventory_by_location = {}

        if "Status_Location" in df.columns:
            for month_str in month_strings:
                month_end = pd.Timestamp(month_str) + pd.offsets.MonthEnd(0)
                inventory_by_month[month_str] = {}

                for location in all_locations:
                    at_location = df[df["Status_Location"] == location]
                    inventory_count = 0
                    for idx, row in at_location.iterrows():
                        if location in row.index and pd.notna(row[location]):
                            try:
                                arrival_date = pd.to_datetime(row[location])
                                if arrival_date <= month_end:
                                    inventory_count += utils.get_pkg(row)
                            except Exception as e:
                                logger.warning(
                                    f"Error in inventory calculation (Row {idx}, Location {location}): {e}"
                                )
                                continue
                    inventory_by_month[month_str][location] = inventory_count
                    inventory_by_location[location] = (
                        inventory_by_location.get(location, 0) + inventory_count
                    )

        total_inventory = sum(inventory_by_location.values())
        logger.info("✅ Inventory calculation complete.")
        return {
            "inventory_by_month": inventory_by_month,
            "inventory_by_location": inventory_by_location,
            "total_inventory": total_inventory,
            "status_location_distribution": (
                df["Status_Location"].value_counts().to_dict()
                if "Status_Location" in df.columns
                else {}
            ),
        }

    def calculate_direct_delivery(self, df: pd.DataFrame) -> Dict:
        """
        Identifies direct deliveries from port to site.
        """
        logger.info("🔄 Calculating direct deliveries...")
        direct_delivery_df = df[df["FLOW_CODE"].isin([0, 1])]
        direct_items = []

        for idx, row in direct_delivery_df.iterrows():
            for site in self.site_columns:
                if site in row.index and pd.notna(row[site]):
                    try:
                        site_date = pd.to_datetime(row[site])
                        direct_items.append(
                            {
                                "Item_ID": idx,
                                "Site": site,
                                "Direct_Date": site_date,
                                "Year_Month": site_date.strftime("%Y-%m"),
                                "Flow_Code": row["FLOW_CODE"],
                                "Pkg_Quantity": utils.get_pkg(row),
                            }
                        )
                    except:
                        continue

        logger.info("✅ Direct delivery calculation complete.")
        return {"total_direct": len(direct_delivery_df), "direct_items": direct_items}

    def calculate_monthly_sqm_inbound(self, df: pd.DataFrame) -> Dict:
        """
        Calculates monthly SQM inbound.
        """
        logger.info("📦 Calculating monthly SQM inbound...")
        monthly_inbound_sqm = {}
        months = pd.date_range("2023-02", "2025-06", freq="MS")
        month_strings = [month.strftime("%Y-%m") for month in months]

        for month_str in month_strings:
            monthly_inbound_sqm[month_str] = {}
            for warehouse in self.warehouse_columns:
                total_sqm = 0
                for idx, row in df.iterrows():
                    if warehouse in row.index and pd.notna(row[warehouse]):
                        try:
                            arrival_date = pd.to_datetime(row[warehouse])
                            if arrival_date.strftime("%Y-%m") == month_str:
                                total_sqm += utils.get_sqm(row)
                        except:
                            continue
                monthly_inbound_sqm[month_str][warehouse] = total_sqm

        logger.info("✅ Monthly SQM inbound calculation complete.")
        return monthly_inbound_sqm

    def calculate_monthly_sqm_outbound(self, df: pd.DataFrame) -> Dict:
        """
        Calculates monthly SQM outbound.
        """
        logger.info("📤 Calculating monthly SQM outbound...")
        monthly_outbound_sqm = {}
        all_locations = self.warehouse_columns + self.site_columns
        months = pd.date_range("2023-02", "2025-06", freq="MS")
        month_strings = [month.strftime("%Y-%m") for month in months]

        for month_str in month_strings:
            monthly_outbound_sqm[month_str] = {}
            for warehouse in self.warehouse_columns:
                total_sqm = 0
                for idx, row in df.iterrows():
                    if warehouse in row.index and pd.notna(row[warehouse]):
                        try:
                            current_date = pd.to_datetime(row[warehouse])
                            next_movements = []
                            for next_loc in all_locations:
                                if (
                                    next_loc != warehouse
                                    and next_loc in row.index
                                    and pd.notna(row[next_loc])
                                ):
                                    next_date = pd.to_datetime(row[next_loc])
                                    if next_date >= current_date:
                                        next_movements.append((next_loc, next_date))

                            if next_movements:
                                _, next_date = min(next_movements, key=lambda x: x[1])
                                if next_date.strftime("%Y-%m") == month_str:
                                    total_sqm += utils.get_sqm(row)
                        except:
                            continue
                monthly_outbound_sqm[month_str][warehouse] = total_sqm

        logger.info("✅ Monthly SQM outbound calculation complete.")
        return monthly_outbound_sqm

    def calculate_cumulative_sqm_inventory(
        self, inbound_sqm: Dict, outbound_sqm: Dict
    ) -> Dict:
        """
        Calculates cumulative SQM inventory.
        """
        logger.info("📊 Calculating cumulative SQM inventory...")
        cumulative_inventory = {}
        months = pd.date_range("2023-02", "2025-06", freq="MS")
        month_strings = [month.strftime("%Y-%m") for month in months]

        current_inventory = {warehouse: 0.0 for warehouse in self.warehouse_columns}

        for month_str in month_strings:
            cumulative_inventory[month_str] = {}
            for warehouse in self.warehouse_columns:
                monthly_inbound = inbound_sqm.get(month_str, {}).get(warehouse, 0)
                monthly_outbound = outbound_sqm.get(month_str, {}).get(warehouse, 0)
                net_change = monthly_inbound - monthly_outbound

                current_inventory[warehouse] = max(
                    0, current_inventory[warehouse] + net_change
                )
                base_capacity = self.warehouse_base_sqm.get(warehouse, 1)

                cumulative_inventory[month_str][warehouse] = {
                    "inbound_sqm": monthly_inbound,
                    "outbound_sqm": monthly_outbound,
                    "net_change_sqm": net_change,
                    "cumulative_inventory_sqm": current_inventory[warehouse],
                    "utilization_rate_%": (current_inventory[warehouse] / base_capacity)
                    * 100,
                    "base_capacity_sqm": base_capacity,
                }

        logger.info("✅ Cumulative SQM inventory calculation complete.")
        return cumulative_inventory

    def calculate_monthly_invoice_charges(self, cumulative_inventory: Dict) -> Dict:
        """
        Calculates monthly invoice charges based on SQM.
        """
        logger.info("💰 Calculating monthly invoice charges...")
        monthly_charges = {}

        for month_str, month_data in cumulative_inventory.items():
            monthly_charges[month_str] = {}
            total_monthly_charge = 0

            for warehouse in self.warehouse_columns:
                if warehouse in month_data:
                    sqm_used = month_data[warehouse]["cumulative_inventory_sqm"]
                    sqm_rate = self.warehouse_sqm_rates.get(warehouse, 20.0)
                    warehouse_charge = sqm_used * sqm_rate
                    total_monthly_charge += warehouse_charge

                    monthly_charges[month_str][warehouse] = {
                        "sqm_used": sqm_used,
                        "sqm_rate_aed": sqm_rate,
                        "monthly_charge_aed": warehouse_charge,
                        "utilization_rate_%": month_data[warehouse][
                            "utilization_rate_%"
                        ],
                    }

            monthly_charges[month_str][
                "total_monthly_charge_aed"
            ] = total_monthly_charge

        logger.info("✅ Monthly invoice charge calculation complete.")
        return monthly_charges

    def analyze_sqm_data_quality(self, df: pd.DataFrame) -> Dict:
        """
        Analyzes the quality of the SQM data.
        """
        logger.info("🔍 Analyzing SQM data quality...")
        total_rows = len(df)
        actual_sqm_count = 0
        estimated_sqm_count = 0
        actual_sqm_sources = {}
        total_actual_sqm = 0
        total_estimated_sqm = 0

        for _, row in df.iterrows():
            sqm_value, source_type, source_column = utils.get_sqm_with_source(row)

            if source_type == "ACTUAL":
                actual_sqm_count += 1
                total_actual_sqm += sqm_value
                actual_sqm_sources[source_column] = (
                    actual_sqm_sources.get(source_column, 0) + 1
                )
            else:
                estimated_sqm_count += 1
                total_estimated_sqm += sqm_value

        analysis_result = {
            "total_records": total_rows,
            "actual_sqm_records": actual_sqm_count,
            "estimated_sqm_records": estimated_sqm_count,
            "actual_sqm_percentage": (
                (actual_sqm_count / total_rows) * 100 if total_rows > 0 else 0
            ),
            "estimated_sqm_percentage": (
                (estimated_sqm_count / total_rows) * 100 if total_rows > 0 else 0
            ),
            "actual_sqm_sources": actual_sqm_sources,
            "avg_actual_sqm": (
                total_actual_sqm / actual_sqm_count if actual_sqm_count > 0 else 0
            ),
            "avg_estimated_sqm": (
                total_estimated_sqm / estimated_sqm_count
                if estimated_sqm_count > 0
                else 0
            ),
            "total_actual_sqm": total_actual_sqm,
            "total_estimated_sqm": total_estimated_sqm,
        }

        logger.info("✅ SQM data quality analysis complete.")
        return analysis_result
