# Bs_005 Mpm

**Generated from:** `BS_005-mpm.db`

**Total tables:** 3

## Table of Contents

- [ACTIONS](#actions)
- [COMMUNITIES](#communities)
- [DEPLOYMENT](#deployment)

---

## ACTIONS

### Schema

| Column | Type |
|--------|------|
| `action_type` | TEXT |
| `action_code` | TEXT |
| `abbreviation` | TEXT |
| `consumer_tags_AML` | INTEGER |
| `consumer_tags_Finance` | INTEGER |
| `consumer_tags_Regulatory` | INTEGER |
| `date_range_function` | TEXT |
| `header_information` | REAL |
| `parents` | TEXT |
| `query_reference_database_name` | TEXT |
| `query_reference_query` | TEXT |
| `query_reference_query_version` | TEXT |
| `report_file_name_pattern` | TEXT |
| `report_name` | TEXT |
| `schedule_crontab` | TEXT |
| `schedule_timezone` | TEXT |
| `start_date` | TIMESTAMP |
| `_row_index` | INTEGER |
| `dataset` | TEXT |
| `source_system` | TEXT |
| `communities` | TEXT |

### Data (78 rows)

| action_type | action_code | abbreviation | consumer_tags_AML | consumer_tags_Finance | consumer_tags_Regulatory | date_range_function | header_information | parents | query_reference_database_name | query_reference_query | query_reference_query_version | report_file_name_pattern | report_name | schedule_crontab | schedule_timezone | start_date | _row_index | dataset | source_system | communities |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| REPORT | retail_liability_ticket_report | RSPLTR | 0.0 | 1.0 | 0.0 | get_current_date_5am | None | retail_liability_bets | SDP | ./scripts/WH/US_ALL/05_Queries/Reports_BOP/Reta... | v2.6.1_1.9_1.0 | BS/Retail_Sport_Pool_Liability_Ticket/{ed_year}... | Retail Sports Pool Liability Ticket Report | 15 13 * * * | Etc/UTC | 2024-01-23 13:15:00 | 0 | None | None | None |
| SENSOR | retail_liability_bets | RLBS | nan | nan | nan | get_current_date_5am | None | None | SDP | SELECT exists (SELECT 1 FROM   SDP.RETAIL_MART.... | None | None | None | 15 13 * * * | Etc/UTC | None | 1 | retail_liability_bets | BE | None |
| REPORT | retail_liability_ticket_report_per_community | RSPLTRC | 0.0 | 1.0 | 0.0 | get_current_date_5am | None | retail_liability_ticket_report | SDP | ./scripts/WH/US_ALL/05_Queries/Reports_BOP/Reta... | v2.6.1_1.9_1.0 | BS/Retail_Sport_Pool_Liability_Ticket/{ed_year}... | Retail Sports Pool Liability Ticket Report Per ... | 15 13 * * * | Etc/UTC | 2024-01-23 13:15:00 | 2 | None | None | Baha_Mar_Casino, Atlantis_Paradise_Island_Atlan... |
| REPORT | retail_recap_all_report | RSPRRE | 0.0 | 1.0 | 0.0 | get_current_date_5am | None | retail_recap_sports_aggregate | SDP | ./scripts/WH/US_ALL/05_Queries/Reports_BOP/Reta... | v2.6.1_1.9_1.0 | BS/Retail_Recap_Daily_All/{ed_year}/{ed_month}/... | Retail Sports Pool Recap Report | 15 13 * * * | Etc/UTC | 2024-01-23 13:15:00 | 3 | None | None | None |
| SENSOR | retail_recap_sports_aggregate | RRSAS | nan | nan | nan | get_current_date_5am | None | None | SDP | SELECT exists (SELECT 1 FROM   SDP.RETAIL_MART.... | None | None | None | 15 13 * * * | Etc/UTC | None | 4 | retail_recap_sports_aggregate | BE | None |
| REPORT | retail_recap_all_report_month_to_date | RSPRRMTD | 0.0 | 1.0 | 0.0 | get_current_month_to_date_5am | None | retail_recap_all_report | SDP | ./scripts/WH/US_ALL/05_Queries/Reports_BOP/Reta... | v2.6.1_1.9_1.0 | BS/Retail_Recap_All_Month_To_Date/{ed_year}/{ed... | Retail Sports Pool Recap Month To Date Report | 15 13 * * * | Etc/UTC | 2024-01-23 13:15:00 | 5 | None | None | None |
| REPORT | retail_recap_report_month_to_date_per_community | RSPRRMTDC | 0.0 | 1.0 | 0.0 | get_current_month_to_date_5am | None | retail_recap_all_report | SDP | ./scripts/WH/US_ALL/05_Queries/Reports_BOP/Reta... | v2.6.1_1.9_1.0 | BS/Retail_Recap_Month_To_Date_Per_Community/{ed... | Retail Sports Pool Recap Month To Date Report P... | 15 13 * * * | Etc/UTC | 2024-01-23 13:15:00 | 6 | None | None | Baha_Mar_Casino, Atlantis_Paradise_Island_Atlan... |
| REPORT | retail_recap_report_per_community | RRR | 0.0 | 1.0 | 0.0 | get_current_date_5am | None | retail_recap_all_report | SDP | ./scripts/WH/US_ALL/05_Queries/Reports_BOP/Reta... | v2.6.1_1.9_1.0 | BS/Retail_Recap_Daily_Per_Community/{ed_year}/{... | Retail Sports Pool Recap Report Per Community | 15 13 * * * | Etc/UTC | 2024-01-23 13:15:00 | 7 | None | None | Baha_Mar_Casino, Atlantis_Paradise_Island_Atlan... |
| REPORT | retail_sports_pool_cancelled_ticket_report | RSPCR | 0.0 | 1.0 | 0.0 | get_current_date_5am | None | retail_recap_bets | SDP | ./scripts/WH/US_ALL/05_Queries/Reports_BOP/Reta... | v2.6.1_1.9_1.0 | BS/Retail_Sports_Pool_Cancelled_Ticket/{ed_year... | Retail Sports Pool Cancelled Report | 15 13 * * * | Etc/UTC | 2024-01-23 13:15:00 | 8 | None | None | None |
| SENSOR | retail_recap_bets | RRBS | nan | nan | nan | get_current_date_5am | None | None | SDP | SELECT exists (SELECT 1 FROM   SDP.RETAIL_MART.... | None | None | None | 15 13 * * * | Etc/UTC | None | 9 | retail_recap_bets | BE | None |
| REPORT | retail_sports_pool_cancelled_ticket_report_per_... | RSPCRC | 0.0 | 1.0 | 0.0 | get_current_date_5am | None | retail_sports_pool_cancelled_ticket_report | SDP | ./scripts/WH/US_ALL/05_Queries/Reports_BOP/Reta... | v2.6.1_1.9_1.0 | BS/Retail_Sports_Pool_Cancelled_Ticket_Per_Comm... | Retail Sports Pool Cancelled Report Per Community | 15 13 * * * | Etc/UTC | 2024-01-23 13:15:00 | 10 | None | None | Baha_Mar_Casino, Atlantis_Paradise_Island_Atlan... |
| REPORT | retail_sports_pool_expired_ticket_report | RSPER | 0.0 | 1.0 | 0.0 | get_current_date_5am | None | retail_recap_bets | SDP | ./scripts/WH/US_ALL/05_Queries/Reports_BOP/Reta... | v2.6.1_1.9_1.0 | BS/Retail_Sports_Pool_Expired_Ticket/{ed_year}/... | Retail Sports Pool Expired Report | 15 13 * * * | Etc/UTC | 2024-01-23 13:15:00 | 11 | None | None | None |
| REPORT | retail_sports_pool_expired_ticket_report_per_co... | RSPERPC | 0.0 | 1.0 | 0.0 | get_current_date_5am | None | retail_sports_pool_expired_ticket_report | SDP | ./scripts/WH/US_ALL/05_Queries/Reports_BOP/Reta... | v2.6.1_1.9_1.0 | BS/Retail_Sports_Pool_Expired_Ticket_Per_Commun... | Retail Sports Pool Expired Report Per Community | 15 13 * * * | Etc/UTC | 2024-01-23 13:15:00 | 12 | None | None | Baha_Mar_Casino, Atlantis_Paradise_Island_Atlan... |
| REPORT | retail_sports_pool_pending_voidscancels_lifetim... | RSPPVLTDR | 0.0 | 1.0 | 0.0 | get_current_date_5am | None | retail_recap_bets | SDP | ./scripts/WH/US_ALL/05_Queries/Reports_BOP/Reta... | v2.6.1_1.9_1.0 | BS/Retail_Sports_Pool_Pending_VoidsCancels_Life... | Retail Sports Pool Pending Voids/cancels Lifeti... | 15 13 * * * | Etc/UTC | 2024-03-01 13:15:00 | 13 | None | None | None |
| REPORT | retail_sports_pool_pending_voidscancels_lifetim... | RSPPVLTDRPC | 0.0 | 1.0 | 0.0 | get_current_date_5am | None | retail_sports_pool_pending_voidscancels_lifetim... | SDP | ./scripts/WH/US_ALL/05_Queries/Reports_BOP/Reta... | v2.6.1_1.9_1.0 | BS/Retail_Sports_Pool_Pending_VoidsCancels_Life... | Retail Sports Pool Pending Voids/cancels Lifeti... | 45 13 * * * | Etc/UTC | 2024-03-01 13:45:00 | 14 | None | None | Baha_Mar_Casino, Atlantis_Paradise_Island_Atlan... |
| REPORT | retail_sports_pool_pending_voidscancels_report | RSPPVR | 0.0 | 1.0 | 0.0 | get_current_date_5am | None | retail_recap_bets | SDP | ./scripts/WH/US_ALL/05_Queries/Reports_BOP/Reta... | v2.6.1_1.9_1.0 | BS/Retail_Sports_Pool_Pending_VoidsCancels/{ed_... | Retail Sports Pool Pending Voids/cancels Report | 15 13 * * * | Etc/UTC | 2024-01-23 13:15:00 | 15 | None | None | None |
| REPORT | retail_sports_pool_pending_voidscancels_report_... | RSPPVRPC | 0.0 | 1.0 | 0.0 | get_current_date_5am | None | retail_sports_pool_pending_voidscancels_report | SDP | ./scripts/WH/US_ALL/05_Queries/Reports_BOP/Reta... | v2.6.1_1.9_1.0 | BS/Retail_Sports_Pool_Pending_VoidsCancels_Per_... | Retail Sports Pool Pending Voids/cancels Report... | 15 13 * * * | Etc/UTC | 2024-01-23 13:15:00 | 16 | None | None | Baha_Mar_Casino, Atlantis_Paradise_Island_Atlan... |
| REPORT | retail_sports_pool_resettlement_report | RSPRRESE | 0.0 | 1.0 | 0.0 | get_current_date_5am | None | retail_sport_pool_resettlement | SDP | ./scripts/WH/US_ALL/05_Queries/Reports_BOP/Reta... | v2.6.1_1.9_1.0 | BS/Retail_Sports_Pool_Resettlement_Ticket/{ed_y... | Retail Sports Pool Resettlement Report | 15 13 * * * | Etc/UTC | 2024-01-23 13:15:00 | 17 | None | None | None |
| SENSOR | retail_sport_pool_resettlement | RSPRS | nan | nan | nan | get_current_date_5am | None | None | SDP | SELECT (SELECT case when max(ifnull(ifnull(SETT... | None | None | None | 15 13 * * * | Etc/UTC | None | 18 | retail_sport_pool_resettlement | BE | None |
| REPORT | retail_sports_pool_resettlement_report_per_comm... | RSPRRESEC | 0.0 | 1.0 | 0.0 | get_current_date_5am | None | retail_sports_pool_resettlement_report | SDP | ./scripts/WH/US_ALL/05_Queries/Reports_BOP/Reta... | v2.6.1_1.9_1.0 | BS/Retail_Sports_Pool_Resettlement_Ticket_Per_C... | Retail Sports Pool Resettlement Report Per Comm... | 15 13 * * * | Etc/UTC | 2024-01-23 13:15:00 | 19 | None | None | Baha_Mar_Casino, Atlantis_Paradise_Island_Atlan... |
| REPORT | retail_sports_pool_results_report | RSPRRESU | 0.0 | 1.0 | 0.0 | get_current_date_5am | None | retail_sport_pool_transaction | SDP | ./scripts/WH/US_ALL/05_Queries/Reports_BOP/Reta... | v2.6.1_1.9_1.0 | BS/Retail_Sports_Pool_Results/{ed_year}/{ed_mon... | Retail Sports Pool Results Report | 15 13 * * * | Etc/UTC | 2024-01-23 13:15:00 | 20 | None | None | None |
| SENSOR | retail_sport_pool_transaction | RSPTS | nan | nan | nan | get_current_date_5am | None | None | SDP | SELECT exists (SELECT 1 FROM   SDP.RETAIL_MART.... | None | None | None | 15 13 * * * | Etc/UTC | None | 21 | retail_sport_pool_transaction | BE | None |
| REPORT | retail_sports_pool_results_report_per_community | RSPRRPC | 0.0 | 1.0 | 0.0 | get_current_date_5am | None | retail_sports_pool_results_report | SDP | ./scripts/WH/US_ALL/05_Queries/Reports_BOP/Reta... | v2.6.1_1.9_1.0 | BS/Retail_Sports_Pool_Results_Per_Community/{ed... | Retail Sports Pool Results Report Per Community | 15 13 * * * | Etc/UTC | 2024-01-23 13:15:00 | 22 | None | None | Baha_Mar_Casino, Atlantis_Paradise_Island_Atlan... |
| REPORT | retail_sports_pool_transaction_report | RSPTR | 0.0 | 1.0 | 0.0 | get_current_date_5am | None | retail_sport_pool_transaction | SDP | ./scripts/WH/US_ALL/05_Queries/Reports_BOP/Reta... | v2.6.1_1.9_1.0 | BS/Retail_Sport_Pool_Transaction/{ed_year}/{ed_... | Retail Sports Pool Transaction Report | 15 13 * * * | Etc/UTC | 2024-01-23 13:15:00 | 23 | None | None | None |
| REPORT | retail_sports_pool_transaction_report_per_commu... | RSPTRPC | 0.0 | 1.0 | 0.0 | get_current_date_5am | None | retail_sports_pool_transaction_report | SDP | ./scripts/WH/US_ALL/05_Queries/Reports_BOP/Reta... | v2.6.1_1.9_1.0 | BS/Retail_Sport_Pool_Transaction_Per_Community/... | Retail Sports Pool Transaction Report Per Commu... | 15 13 * * * | Etc/UTC | 2024-01-23 13:15:00 | 24 | None | None | Baha_Mar_Casino, Atlantis_Paradise_Island_Atlan... |
| REPORT | retail_sports_pool_voided_ticket_report | RSPVR | 0.0 | 1.0 | 0.0 | get_current_date_5am | None | retail_recap_bets | SDP | ./scripts/WH/US_ALL/05_Queries/Reports_BOP/Reta... | v2.6.1_1.9_1.0 | BS/Retail_Sports_Pool_Voided_Ticket/{ed_year}/{... | Retail Sports Pool Voided Report | 15 13 * * * | Etc/UTC | 2024-01-23 13:15:00 | 25 | None | None | None |
| REPORT | retail_sports_pool_voided_ticket_report_per_com... | RSPVRC | 0.0 | 1.0 | 0.0 | get_current_date_5am | None | retail_sports_pool_voided_ticket_report | SDP | ./scripts/WH/US_ALL/05_Queries/Reports_BOP/Reta... | v2.6.1_1.9_1.0 | BS/Retail_Sports_Pool_Voided_Ticket_Per_Communi... | Retail Sports Pool Voided Report Per Community | 15 13 * * * | Etc/UTC | 2024-01-23 13:15:00 | 26 | None | None | Baha_Mar_Casino, Atlantis_Paradise_Island_Atlan... |
| REPORT | retail_unpaid_ticket_report | RUTR | 0.0 | 1.0 | 0.0 | get_current_date_5am | None | retail_recap_bets | SDP | ./scripts/WH/US_ALL/05_Queries/Reports_BOP/Reta... | v2.6.1_1.9_1.0 | BS/Retail_Unpaid_Ticket/{ed_year}/{ed_month}/{e... | Retail Unpaid Ticket Report | 15 13 * * * | Etc/UTC | 2024-01-23 13:15:00 | 27 | None | None | None |
| REPORT | retail_unpaid_ticket_report_per_community | RUTRPC | 0.0 | 1.0 | 0.0 | get_current_date_5am | None | retail_unpaid_ticket_report | SDP | ./scripts/WH/US_ALL/05_Queries/Reports_BOP/Reta... | v2.6.1_1.9_1.0 | BS/Retail_Unpaid_Ticket_Per_Community/{ed_year}... | Retail Unpaid Ticket Report Per Community | 15 13 * * * | Etc/UTC | 2024-01-23 13:15:00 | 28 | None | None | Baha_Mar_Casino, Atlantis_Paradise_Island_Atlan... |
| REPORT | retail_sports_pool_voided_ticket_report_month_t... | RSPVRMTD | 0.0 | 1.0 | 0.0 | get_current_month_to_date_5am | None | retail_sports_pool_voided_ticket_report | SDP | ./scripts/WH/US_ALL/05_Queries/Reports_BOP/Reta... | v2.6.1_1.9_1.0 | BS/Retail_Sports_Pool_Voided_Ticket_Month_To_Da... | Retail Sports Pool Voided Report MTD | 15 13 * * * | Etc/UTC | 2024-01-23 13:15:00 | 29 | None | None | None |
| REPORT | retail_sports_pool_voided_ticket_report_month_t... | RSPVRPCMTD | 0.0 | 1.0 | 0.0 | get_current_month_to_date_5am | None | retail_sports_pool_voided_ticket_report | SDP | ./scripts/WH/US_ALL/05_Queries/Reports_BOP/Reta... | v2.6.1_1.9_1.0 | BS/Retail_Sports_Pool_Voided_Ticket_Month_To_Da... | Retail Sports Pool Voided Report Per Community MTD | 15 13 * * * | Etc/UTC | 2024-11-29 15:05:00 | 30 | None | None | Baha_Mar_Casino, Atlantis_Paradise_Island_Atlan... |
| REPORT | retail_sports_pool_cancelled_ticket_report_mont... | RSPCRMTD | 0.0 | 1.0 | 0.0 | get_current_month_to_date_5am | None | retail_sports_pool_cancelled_ticket_report | SDP | ./scripts/WH/US_ALL/05_Queries/Reports_BOP/Reta... | v2.6.1_1.9_1.0 | BS/Retail_Sports_Pool_Cancelled_Ticket_MTD/{ed_... | Retail Sports Pool Cancelled Report MTD | 15 13 * * * | Etc/UTC | 2024-01-23 13:15:00 | 31 | None | None | None |
| REPORT | retail_sports_pool_cancelled_ticket_report_mont... | RSPCRPCMTD | 0.0 | 1.0 | 0.0 | get_current_month_to_date_6am | None | retail_sports_pool_cancelled_ticket_report | SDP | ./scripts/WH/US_ALL/05_Queries/Reports_BOP/Reta... | v2.6.1_1.9_1.0 | BS/Retail_Sports_Pool_Cancelled_Ticket_Month_To... | Retail Sports Pool Cancelled Report Per Communi... | 15 13 * * * | Etc/UTC | 2024-11-29 15:05:00 | 32 | None | None | Baha_Mar_Casino, Atlantis_Paradise_Island_Atlan... |
| REPORT | rosi_big_transactions_report_all | RBTRA | 0.0 | 1.0 | 0.0 | get_current_date_5am | None | business_activity | NJ_Prod | ./scripts/WH/US_ALL/05_Queries/Report/Rosi/Rosi... | v2.6.1_1.9_1.0 | BS/Rosi_Big_Transactions_All/{ed_year}/{ed_mont... | Rosi Big Transactions Report | 15 14 * * * | Etc/UTC | 2024-08-26 14:15:00 | 33 | None | None | None |
| SENSOR | business_activity | BAS | nan | nan | nan | get_current_date_5am | None | None | NJ_Prod | call "Audit".IS_ROSI_INGESTION_COMPLETE('{{Doma... | None | None | None | 15 14 * * * | Etc/UTC | None | 34 | business_activity | money_management | None |
| REPORT | rosi_big_transactions_report_per_community | RBTR | 0.0 | 1.0 | 0.0 | get_current_date_5am | None | rosi_big_transactions_report_all | NJ_Prod | ./scripts/WH/US_ALL/05_Queries/Report/Rosi/RPT_... | v2.6.1_1.9_1.0 | BS/Rosi_Big_Transactions_Per_Community/{ed_year... | Rosi Big Transactions Report Per Community | 30 14 * * * | Etc/UTC | 2024-08-26 14:30:00 | 35 | None | None | Baha_Mar_Casino, Atlantis_Paradise_Island_Atlan... |
| REPORT | rosi_bill_denominations_all | RBDRA | 0.0 | 1.0 | 0.0 | get_current_date_5am | None | business_activity | NJ_Prod | ./scripts/WH/US_ALL/05_Queries/Report/Rosi/Rosi... | v2.6.1_1.9_1.0 | BS/Rosi_Bill_Denominations_All/{ed_year}/{ed_mo... | Rosi Bill Denominations Report | 15 14 * * * | Etc/UTC | 2024-08-26 14:15:00 | 36 | None | None | None |
| REPORT | rosi_bill_denominations_per_community | RBDR | 0.0 | 1.0 | 0.0 | get_current_date_5am | None | rosi_bill_denominations_all | NJ_Prod | ./scripts/WH/US_ALL/05_Queries/Report/Rosi/RPT_... | v2.6.1_1.9_1.0 | BS/Rosi_Bill_Denominations_Per_Community/{ed_ye... | Rosi Bill Denominations Report Per Community | 30 14 * * * | Etc/UTC | 2024-08-26 14:30:00 | 37 | None | None | Baha_Mar_Casino, Atlantis_Paradise_Island_Atlan... |
| REPORT | rosi_cash_balances_all | RCBRA | 0.0 | 1.0 | 0.0 | get_current_date_5am | None | account, accountbalance | NJ_Prod | ./scripts/WH/US_ALL/05_Queries/Report/Rosi/RPT_... | v2.6.1_1.9_1.0 | BS/Rosi_Cash_Balances_All/{ed_year}/{ed_month}/... | Rosi Cash Balances Report | 15 14 * * * | Etc/UTC | 2024-08-26 14:15:00 | 38 | None | None | None |
| SENSOR | account | AS | nan | nan | nan | get_current_date_5am | None | None | NJ_Prod | SELECT "Audit".is_etl_completed('{{ DataSetNm }... | None | None | None | 15 14 * * * | Etc/UTC | None | 39 | account | ROSI | None |
| SENSOR | accountbalance | AS | nan | nan | nan | get_current_date_5am | None | None | NJ_Prod | SELECT "Audit".is_etl_completed('{{ DataSetNm }... | None | None | None | 15 14 * * * | Etc/UTC | None | 40 | accountbalance | ROSI | None |
| REPORT | rosi_cash_balances_per_community | RCBR | 0.0 | 1.0 | 0.0 | get_current_date_5am | None | rosi_cash_balances_all | NJ_Prod | ./scripts/WH/US_ALL/05_Queries/Report/Rosi/RPT_... | v2.6.1_1.9_1.0 | BS/Rosi_Cash_Balances_Per_Community/{ed_year}/{... | Rosi Cash Balances Report Per Community | 30 14 * * * | Etc/UTC | 2024-08-26 14:30:00 | 41 | None | None | Baha_Mar_Casino, Atlantis_Paradise_Island_Atlan... |
| REPORT | rosi_daily_transactions_report_all | RDTRA | 0.0 | 1.0 | 0.0 | get_current_date_5am | None | account, businessactivity | NJ_Prod | ./scripts/WH/US_ALL/05_Queries/Report/Rosi/RPT_... | v2.6.1_1.9_1.0 | BS/Rosi_Daily_Transactions_All/{ed_year}/{ed_mo... | Rosi Daily Transactions Report | 15 14 * * * | Etc/UTC | 2024-08-26 14:15:00 | 42 | None | None | None |
| SENSOR | businessactivity | BS | nan | nan | nan | get_current_date_5am | None | None | NJ_Prod | SELECT "Audit".is_etl_completed('{{ DataSetNm }... | None | None | None | 15 14 * * * | Etc/UTC | None | 43 | businessactivity | ROSI | None |
| REPORT | rosi_daily_transactions_report_per_community | RDTR | 0.0 | 1.0 | 0.0 | get_current_date_5am | None | rosi_daily_transactions_report_all | NJ_Prod | ./scripts/WH/US_ALL/05_Queries/Report/Rosi/RPT_... | v2.6.1_1.9_1.0 | BS/Rosi_Daily_Transactions_Per_Community/{ed_ye... | Rosi Daily Transactions Report Per Community | 30 14 * * * | Etc/UTC | 2024-08-26 14:30:00 | 44 | None | None | Baha_Mar_Casino, Atlantis_Paradise_Island_Atlan... |
| REPORT | rosi_electronic_accounting_report_all | REARA | 0.0 | 1.0 | 0.0 | get_current_date_5am | None | business_activity | NJ_Prod | ./scripts/WH/US_ALL/05_Queries/Report/Rosi/Rosi... | v2.6.1_1.9_1.0 | BS/Rosi_Electronic_Accounting_All/{ed_year}/{ed... | Rosi Electronic Accounting Report | 15 14 * * * | Etc/UTC | 2024-08-26 14:15:00 | 45 | None | None | None |
| REPORT | rosi_electronic_accounting_report_per_community | REAR | 0.0 | 1.0 | 0.0 | get_current_date_5am | None | rosi_electronic_accounting_report_all | NJ_Prod | ./scripts/WH/US_ALL/05_Queries/Report/Rosi/RPT_... | v2.6.1_1.9_1.0 | BS/Rosi_Electronic_Accounting_Per_Community/{ed... | Rosi Electronic Accounting Report Per Community | 30 14 * * * | Etc/UTC | 2024-08-26 14:30:00 | 46 | None | None | Baha_Mar_Casino, Atlantis_Paradise_Island_Atlan... |
| REPORT | rosi_irs_paids_all | RIPR | 0.0 | 1.0 | 0.0 | get_current_date_5am | None | activity_tax, activity_tax_line, business_activity | NJ_Prod | ./scripts/WH/US_ALL/05_Queries/Report/Rosi/Rosi... | v2.6.1_1.9_1.0 | BS/Rosi_IRS_Paids_All/{ed_year}/{ed_month}/{ed_... | Rosi Irs Paids Report | 15 14 * * * | Etc/UTC | 2024-08-26 14:15:00 | 47 | None | None | None |
| SENSOR | activity_tax | ATS | nan | nan | nan | get_current_date_5am | None | None | NJ_Prod | call "Audit".IS_ROSI_INGESTION_COMPLETE('{{Doma... | None | None | None | 15 14 * * * | Etc/UTC | None | 48 | activity_tax | money_management | None |
| SENSOR | activity_tax_line | ATLS | nan | nan | nan | get_current_date_5am | None | None | NJ_Prod | call "Audit".IS_ROSI_INGESTION_COMPLETE('{{Doma... | None | None | None | 15 14 * * * | Etc/UTC | None | 49 | activity_tax_line | money_management | None |
| REPORT | rosi_irs_paids_per_community | RIPRC | 0.0 | 1.0 | 0.0 | get_current_date_5am | None | rosi_irs_paids_all | NJ_Prod | ./scripts/WH/US_ALL/05_Queries/Report/Rosi/RPT_... | v2.6.1_1.9_1.0 | BS/Rosi_IRS_Paids_Per_Community/{ed_year}/{ed_m... | Rosi IRS Paids Report Per Community | 30 14 * * * | Etc/UTC | 2024-08-26 14:30:00 | 50 | None | None | Baha_Mar_Casino, Atlantis_Paradise_Island_Atlan... |
| REPORT | rosi_irs_paids_report_month_to_date | RIPMTDR | 0.0 | 1.0 | 0.0 | get_current_month_to_date_5am | None | rosi_irs_paids_all | NJ_Prod | ./scripts/WH/US_ALL/05_Queries/Report/Rosi/RPT_... | v2020.03.206459.0 | BS/Rosi_IRS_Paids_All_Month_To_Date/{ed_year}/{... | Rosi Irs Paids Month To Date Report | 45 14 * * * | Etc/UTC | 2024-12-01 14:45:00 | 51 | None | None | None |
| REPORT | rosi_irs_paids_report_year_to_date | RIPYTDR | 0.0 | 1.0 | 0.0 | get_current_year_to_date_5am | None | rosi_irs_paids_all | NJ_Prod | ./scripts/WH/US_ALL/05_Queries/Report/Rosi/RPT_... | v2020.03.206459.0 | BS/Rosi_IRS_Paids_All_Year_To_Date/{ed_year}/{e... | Rosi Irs Paids Year To Date Report | 45 14 * * * | Etc/UTC | 2024-12-01 14:45:00 | 52 | None | None | None |
| REPORT | rosi_patron_kiosk_activity_report_per_community | RPKAR | 0.0 | 1.0 | 0.0 | get_current_date_5am | None | player, businessactivity | NJ_Prod | ./scripts/WH/US_ALL/05_Queries/Report/Rosi/RPT_... | v2.6.1_1.9_1.0 | BS/Rosi_Patron_Kiosk_Activity_Per_Community/{ed... | Rosi Patron Kiosk Activity Report Per Community | 0 14 * * * | Etc/UTC | 2024-04-10 14:00:00 | 53 | None | None | Baha_Mar_Casino, Atlantis_Paradise_Island_Atlan... |
| SENSOR | player | PS | nan | nan | nan | get_current_date_5am | None | None | NJ_Prod | SELECT "Audit".is_etl_completed('{{ DataSetNm }... | None | None | None | 0 14 * * * | Etc/UTC | None | 54 | player | ROSI | None |
| REPORT | rosi_teller_balance_by_cage_report_all | RTBBCRA | 0.0 | 1.0 | 0.0 | get_current_date_5am | None | business_activity, account, account_balance, ru... | NJ_Prod | ./scripts/WH/US_ALL/05_Queries/Report/Rosi/Rosi... | v2.6.1_1.9_1.0 | BS/Rosi_Teller_Balance_By_Cage_All/{ed_year}/{e... | Rosi Teller Balance By Cage Report | 15 14 * * * | Etc/UTC | 2024-08-26 14:15:00 | 55 | None | None | None |
| SENSOR | account_balance | ABS | nan | nan | nan | get_current_date_5am | None | None | NJ_Prod | call "Audit".IS_ROSI_INGESTION_COMPLETE('{{Doma... | None | None | None | 15 14 * * * | Etc/UTC | None | 56 | account_balance | money_management | None |
| SENSOR | running_account_balance | RABS | nan | nan | nan | get_current_date_5am | None | None | NJ_Prod | call "Audit".IS_ROSI_INGESTION_COMPLETE('{{Doma... | None | None | None | 15 14 * * * | Etc/UTC | None | 57 | running_account_balance | money_management | None |
| REPORT | rosi_teller_balance_by_cage_report_per_community | RTBBCR | 0.0 | 1.0 | 0.0 | get_current_date_5am | None | rosi_teller_balance_by_cage_report_all | NJ_Prod | ./scripts/WH/US_ALL/05_Queries/Report/Rosi/RPT_... | v2.6.1_1.9_1.0 | BS/Rosi_Teller_Balance_By_Cage_Per_Community/{e... | Rosi Teller Balance by Cage Report Per Community | 30 14 * * * | Etc/UTC | 2024-08-26 14:30:00 | 58 | None | None | Baha_Mar_Casino, Atlantis_Paradise_Island_Atlan... |
| REPORT | rosi_teller_balance_by_kiosk_report_all | RTBBKRA | 0.0 | 1.0 | 0.0 | get_current_date_5am | None | business_activity | NJ_Prod | ./scripts/WH/US_ALL/05_Queries/Report/Rosi/Rosi... | v2.6.1_1.9_1.0 | BS/Rosi_Teller_Balance_By_Kiosk_All/{ed_year}/{... | Rosi Teller Balance By Kiosk Report | 15 14 * * * | Etc/UTC | 2024-08-26 14:15:00 | 59 | None | None | None |
| REPORT | rosi_teller_balance_by_kiosk_report_per_community | RTBBKR | 0.0 | 1.0 | 0.0 | get_current_date_5am | None | rosi_teller_balance_by_kiosk_report_all | NJ_Prod | ./scripts/WH/US_ALL/05_Queries/Report/Rosi/RPT_... | v2.6.1_1.9_1.0 | BS/Rosi_Teller_Balance_By_Kiosk_Per_Community/{... | Rosi Teller Balance By Kiosk Report Per Community | 30 14 * * * | Etc/UTC | 2024-08-26 14:30:00 | 60 | None | None | Baha_Mar_Casino, Atlantis_Paradise_Island_Atlan... |
| REPORT | rosi_teller_balance_report_all | RTBRA | 0.0 | 1.0 | 0.0 | get_current_date_5am | None | business_activity, account, account_balance, ru... | NJ_Prod | ./scripts/WH/US_ALL/05_Queries/Report/Rosi/Rosi... | v2.6.1_1.9_1.0 | BS/Report-Rosi-Teller-Balance-Report-All/{ed_ye... | Rosi Teller Balance Report | 15 14 * * * | Etc/UTC | 2024-08-26 14:15:00 | 61 | None | None | None |
| REPORT | rosi_teller_balance_report_per_community | RTBR | 0.0 | 1.0 | 0.0 | get_current_date_5am | None | rosi_teller_balance_report_all | NJ_Prod | ./scripts/WH/US_ALL/05_Queries/Report/Rosi/RPT_... | v2.6.1_1.9_1.0 | BS/Rosi_Teller_Balance_Per_Community/{ed_year}/... | Rosi Teller Balance Report Per Community | 30 14 * * * | Etc/UTC | 2024-08-26 14:30:00 | 62 | None | None | Baha_Mar_Casino, Atlantis_Paradise_Island_Atlan... |
| REPORT | rosi_voucher_weekly_all | RVWRA | 0.0 | 1.0 | 0.0 | get_current_week_5am | None | voucher, businessactivity | NJ_Prod | ./scripts/WH/US_ALL/05_Queries/Report/Rosi/RPT_... | v2.6.1_1.9_1.0 | BS/Rosi_Voucher_Weekly_All/{ed_year}/{ed_month}... | Rosi Voucher Weekly Report | 15 14 * * 1 | Etc/UTC | 2024-08-26 14:15:00 | 63 | None | None | None |
| SENSOR | voucher | VS | nan | nan | nan | get_current_week_5am | None | None | NJ_Prod | SELECT "Audit".is_etl_completed('{{ DataSetNm }... | None | None | None | 15 14 * * 1 | Etc/UTC | None | 64 | voucher | ROSI | None |
| REPORT | rosi_voucher_weekly_per_community | RVWR | 0.0 | 1.0 | 0.0 | get_current_week_5am | None | rosi_voucher_weekly_all | NJ_Prod | ./scripts/WH/US_ALL/05_Queries/Report/Rosi/RPT_... | v2.6.1_1.9_1.0 | BS/Rosi_Voucher_Weekly_Per_Community/{ed_year}/... | Rosi Voucher Weekly Report Per Community | 30 14 * * 1 | Etc/UTC | 2024-08-26 14:30:00 | 65 | None | None | Baha_Mar_Casino, Atlantis_Paradise_Island_Atlan... |
| REPORT | rosi_vouchers_created_all | VCRA | 0.0 | 1.0 | 0.0 | get_current_date_5am | None | business_activity, voucher | NJ_Prod | ./scripts/WH/US_ALL/05_Queries/Report/Rosi/Rosi... | v2.6.1_1.9_1.0 | BS/Rosi_Vouchers_Created_All/{ed_year}/{ed_mont... | Rosi Vouchers Created Report | 15 14 * * * | Etc/UTC | 2024-08-26 14:15:00 | 66 | None | None | None |
| REPORT | rosi_vouchers_created_per_community | VCR | 0.0 | 1.0 | 0.0 | get_current_date_5am | None | rosi_vouchers_created_all | NJ_Prod | ./scripts/WH/US_ALL/05_Queries/Report/Rosi/RPT_... | v2.6.1_1.9_1.0 | BS/Rosi_Vouchers_Created_Per_Community/{ed_year... | Rosi Vouchers Created Report Per Community | 30 14 * * * | Etc/UTC | 2024-08-26 14:30:00 | 67 | None | None | Baha_Mar_Casino, Atlantis_Paradise_Island_Atlan... |
| REPORT | rosi_vouchers_expired_all | VERA | 0.0 | 1.0 | 0.0 | get_current_date_5am | None | business_activity, voucher | NJ_Prod | ./scripts/WH/US_ALL/05_Queries/Report/Rosi/Rosi... | v2.6.1_1.9_1.0 | BS/Rosi_Vouchers_Expired_All/{ed_year}/{ed_mont... | Rosi Vouchers Expired Report | 15 14 * * * | Etc/UTC | 2024-08-26 14:15:00 | 68 | None | None | None |
| REPORT | rosi_vouchers_expired_per_community | VER | 0.0 | 1.0 | 0.0 | get_current_date_5am | None | rosi_vouchers_expired_all | NJ_Prod | ./scripts/WH/US_ALL/05_Queries/Report/Rosi/RPT_... | v2.6.1_1.9_1.0 | BS/Rosi_Vouchers_Expired_Per_Community/{ed_year... | Rosi Vouchers Expired Report Per Community | 30 14 * * * | Etc/UTC | 2024-08-26 14:30:00 | 69 | None | None | Baha_Mar_Casino, Atlantis_Paradise_Island_Atlan... |
| REPORT | rosi_vouchers_paidout_all | VPRA | 0.0 | 1.0 | 0.0 | get_current_date_5am | None | business_activity, voucher | NJ_Prod | ./scripts/WH/US_ALL/05_Queries/Report/Rosi/Rosi... | v2.6.1_1.9_1.0 | BS/Rosi_Vouchers_PaidOut_All/{ed_year}/{ed_mont... | Rosi Vouchers PaidOut Report | 15 14 * * * | Etc/UTC | 2024-08-26 14:15:00 | 70 | None | None | None |
| REPORT | rosi_vouchers_paidout_per_community | VPR | 0.0 | 1.0 | 0.0 | get_current_date_5am | None | rosi_vouchers_paidout_all | NJ_Prod | ./scripts/WH/US_ALL/05_Queries/Report/Rosi/RPT_... | v2.6.1_1.9_1.0 | BS/Rosi_Vouchers_PaidOut_Per_Community/{ed_year... | Rosi Vouchers PaidOut Report Per Community | 30 14 * * * | Etc/UTC | 2024-08-26 14:30:00 | 71 | None | None | Baha_Mar_Casino, Atlantis_Paradise_Island_Atlan... |
| REPORT | rosi_vouchers_unpaid_all | VURA | 0.0 | 1.0 | 0.0 | get_current_date_5am | None | business_activity, voucher, voucher_audit | NJ_Prod | ./scripts/WH/US_ALL/05_Queries/Report/Rosi/Rosi... | v2.6.1_1.9_1.0 | BS/Rosi_Vouchers_Unpaid_All/{ed_year}/{ed_month... | Rosi Vouchers Unpaid Report | 15 14 * * * | Etc/UTC | 2024-08-26 14:15:00 | 72 | None | None | None |
| SENSOR | voucher_audit | VAS | nan | nan | nan | get_current_date_5am | None | None | NJ_Prod | call "Audit".IS_ROSI_INGESTION_COMPLETE('{{Doma... | None | None | None | 15 14 * * * | Etc/UTC | None | 73 | voucher_audit | money_management | None |
| REPORT | rosi_vouchers_unpaid_per_community | VUR | 0.0 | 1.0 | 0.0 | get_current_date_5am | None | rosi_vouchers_unpaid_all | NJ_Prod | ./scripts/WH/US_ALL/05_Queries/Report/Rosi/RPT_... | v2.6.1_1.9_1.0 | BS/Rosi_Vouchers_Unpaid_Per_Community/{ed_year}... | Rosi Vouchers Unpaid Report Per Community | 30 14 * * * | Etc/UTC | 2024-08-26 14:30:00 | 74 | None | None | Baha_Mar_Casino, Atlantis_Paradise_Island_Atlan... |
| REPORT | taxable_handle_recap_vs_trans_month_to_date_report | THRMTD | 0.0 | 1.0 | 0.0 | get_current_month_to_date_5am | None | taxable_handle_recap_vs_trans_report | NJ_Prod | ./scripts/WH/US_ALL/05_Queries/Report_Variances... | v2023.12.1_1.9_1.0 | BS/TaxableHandleRecapVsTrans_Month_To_Date/{ed_... | Taxable Handle Recap vs. Transactions Month To ... | 30 14 * * * | Etc/UTC | 2024-07-01 14:30:00 | 75 | None | None | None |
| REPORT | taxable_handle_recap_vs_trans_report | THR | 0.0 | 1.0 | 0.0 | get_current_date_5am | None | betting | NJ_Prod | ./scripts/WH/US_ALL/05_Queries/Report_Variances... | v2023.12.1_1.9_1.0 | BS/Taxable_Handle_Recap_Vs_Trans/{ed_year}/{ed_... | Taxable Handle Recap vs. Transactions Report | 0 14 * * * | Etc/UTC | 2024-01-29 14:00:00 | 76 | None | None | None |
| SENSOR | betting | BS | nan | nan | nan | get_current_date_5am | None | None | NJ_Prod | SELECT "Audit".is_etl_completed('{{ DataSetNm }... | None | None | None | 0 14 * * * | Etc/UTC | None | 77 | betting | BE | None |

---

## COMMUNITIES

### Schema

| Column | Type |
|--------|------|
| `id` | INTEGER |
| `name` | TEXT |
| `_row_index` | INTEGER |

### Data (2 rows)

| id | name | _row_index |
| --- | --- | --- |
| 8571101 | Baha_Mar_Casino | 0 |
| 8421102 | Atlantis_Paradise_Island_Atlantis_Casino | 1 |

---

## DEPLOYMENT

### Schema

| Column | Type |
|--------|------|
| `deployment_code` | TEXT |
| `deployment_version` | TEXT |
| `domain_code` | TEXT |
| `warehouse_auto_suspend` | INTEGER |
| `warehouse_max_cluster_count` | INTEGER |
| `warehouse_scaling_policy` | TEXT |
| `warehouse_warehouse_size` | TEXT |
| `warehouse_warehouse_type` | TEXT |
| `internal_stage` | TEXT |
| `external_stage` | TEXT |
| `domain_timezone` | TEXT |

### Data (1 rows)

| deployment_code | deployment_version | domain_code | warehouse_auto_suspend | warehouse_max_cluster_count | warehouse_scaling_policy | warehouse_warehouse_size | warehouse_warehouse_type | internal_stage | external_stage | domain_timezone |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| BS_005 | BS_005 | BS | 120 | 4 | STANDARD | MEDIUM | SNOWPARK-OPRIMIZED | GENERIC_REPORTING.BS_005.REPORTING | GENERIC_REPORTING.REPORTING.PRODUCTION | US / Eastern |
