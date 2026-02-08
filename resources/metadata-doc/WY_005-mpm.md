# Wy_005 Mpm

**Generated from:** `WY_005-mpm.db`

**Total tables:** 2

## Table of Contents

- [ACTIONS](#actions)
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
| `pii_information_csv_column_encryption` | TEXT |
| `pii_information_decrypt_method` | TEXT |
| `pii_information_encryption_support` | TEXT |
| `header_information_header_support` | TEXT |
| `header_information_no_header_column` | INTEGER |

### Data (49 rows)

| action_type | action_code | abbreviation | consumer_tags_AML | consumer_tags_Finance | consumer_tags_Regulatory | date_range_function | parents | query_reference_database_name | query_reference_query | query_reference_query_version | report_file_name_pattern | report_name | schedule_crontab | schedule_timezone | start_date | _row_index | dataset | source_system | pii_information_csv_column_encryption | pii_information_decrypt_method | pii_information_encryption_support | header_information_header_support | header_information_no_header_column |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| REPORT | daily_transaction_deposit_withdrawal_report_bop | DTDWRB | 0.0 | 1.0 | 0.0 | get_current_date_6am | generic_reporting.wy_004.recon_check | SDP | ./scripts/WH/US_ALL/05_Queries/Reports_BOP/BOP/... | 1.0.0 | WY/Daily_Deposit_Withdrawal/{ed_year}/{ed_month... | Daily Deposit Withdrawal Report | 0 16 * * * | Etc/UTC | 2024-06-05 15:00:00 | 0 | None | None | None | None | None | None | nan |
| SENSOR | generic_reporting.wy_004.recon_check | GR0CS | nan | nan | nan | get_current_date_6am | None | SDP | SELECT GENERIC_REPORTING.WY_004.is_recon_comple... | None | None | None | 0 16 * * * | Etc/UTC | None | 1 | generic_reporting.wy_004.recon_check | WY | None | None | None | None | nan |
| REPORT | daily_transaction_report_bop | DTRB | 0.0 | 1.0 | 0.0 | get_current_date_6am | generic_reporting.wy_004.recon_check | SDP | ./scripts/WH/US_ALL/05_Queries/Reports_BOP/BOP/... | 1.0.0 | WY/Neo_Daily_Transaction/{ed_year}/{ed_month}/{... | Daily Transaction Report | 0 16 * * * | Etc/UTC | 2024-03-28 15:00:00 | 2 | None | None | None | None | None | None | nan |
| REPORT | dormant_acct_report_bop | DARB | 0.0 | 1.0 | 0.0 | get_date_range_for_static_from_date_6am | dormant_player_mart_data_feed | SDP | ./scripts/WH/US_ALL/05_Queries/Reports_BOP/BOP/... | 1.0.0 | WY/Dormant_Report/{ed_year}/{ed_month}/{ed_day}... | Dormant Account Report | 0 15 * * * | Etc/UTC | 2022-06-06 15:00:00 | 3 | None | None | None | None | None | None | nan |
| SENSOR | dormant_player_mart_data_feed | DPMDFS | nan | nan | nan | get_date_range_for_static_from_date_6am | None | SDP | SELECT (SELECT case when max("LAST_UPDATE_PLAYE... | None | None | None | 0 15 * * * | Etc/UTC | None | 4 | dormant_player_mart_data_feed | WY | None | None | None | None | nan |
| REPORT | dtr_deposit_failed_backin_report | DDFBR | 0.0 | 1.0 | 0.0 | get_current_date_6am | generic_reporting.wy_004.recon_check | SDP | ./scripts/WH/US_ALL/05_Queries/Reports_BOP/BOP/... | 1.0.0 | WY/DTR_Deposit_Failed_Backin/{ed_year}/{ed_mont... | DTR Deposit Failed Back-In Report | 45 16 * * * | Etc/UTC | 2024-12-11 15:15:00 | 5 | None | None | None | None | None | None | nan |
| REPORT | forfeited_bonus_winnings_report_bop | FBWRB | 0.0 | 1.0 | 0.0 | get_current_date_6am | generic_reporting.wy_004.recon_check | SDP | ./scripts/WH/US_ALL/05_Queries/Reports_BOP/BOP/... | 1.0.0 | WY/Forfeited_Bonus_Winnings/{ed_year}/{ed_month... | Forfeited Bonus Winnings Report | 15 16 * * * | Etc/UTC | 2023-06-06 15:00:00 | 6 | None | None | None | None | None | None | nan |
| REPORT | global_wallet_transactions_report | GWTR | 0.0 | 1.0 | 0.0 | get_current_date_6am | generic_reporting.wy_004.recon_check | SDP | ./scripts/WH/US_ALL/05_Queries/Reports_BOP/BOP/... | 1.0.0 | WY/Global_Wallet_Transactions_Report/{ed_year}/... | Global Wallet Transactions Report | 0 16 * * * | Etc/UTC | 2023-12-21 15:00:00 | 7 | None | None | None | None | None | None | nan |
| REPORT | liability_ticket_report_bop | LTRB | 0.0 | 1.0 | 0.0 | get_current_date_6am | task_mart_sports_pool_digital_recap_bets | SDP | ./scripts/WH/US_ALL/05_Queries/Reports_BOP/BE/D... | 1.0.0 | WY/Sport_Pool_Liability_Ticket/{ed_year}/{ed_mo... | Sports Pool Liability Ticket Report | 0 15 * * * | Etc/UTC | 2024-01-29 15:00:00 | 8 | None | None | None | None | None | None | nan |
| SENSOR | task_mart_sports_pool_digital_recap_bets | TMSPDRBS | nan | nan | nan | get_current_date_6am | None | SDP | select (SELECT exists (SELECT 1                ... | None | None | None | 0 15 * * * | Etc/UTC | None | 9 | task_mart_sports_pool_digital_recap_bets | WY | None | None | None | None | nan |
| REPORT | month_to_date_transaction_deposit_withdrawal_re... | MTDTDWRB | 0.0 | 1.0 | 0.0 | get_current_month_to_date_6am | daily_transaction_deposit_withdrawal_report_bop | SDP | ./scripts/WH/US_ALL/05_Queries/Reports_BOP/BOP/... | 1.0.0 | WY/Month_To_Date_Deposit_Withdrawal/{ed_year}/{... | Daily Deposit Withdrawal Month To Date Report | 0 15 * * * | Etc/UTC | 2024-06-05 15:00:00 | 10 | None | None | None | None | None | None | nan |
| REPORT | noncashable_bonus_balance_report_bop | NBBRB | 0.0 | 1.0 | 0.0 | get_current_date_6am | generic_reporting.wy_004.recon_check | SDP | ./scripts/WH/US_ALL/05_Queries/Reports_BOP/BOP/... | 1.0.0 | WY/Non-Cashable_Bonus_Balance/{ed_year}/{ed_mon... | Non-Cashable Bonus Balance Report | 0 16 * * * | Etc/UTC | 2024-03-28 15:00:00 | 11 | None | None | None | None | None | None | nan |
| REPORT | patron_account_summary_report_bop | PASRB | 0.0 | 1.0 | 0.0 | get_current_date_6am | generic_reporting.wy_004.recon_check | SDP | ./scripts/WH/US_ALL/05_Queries/Reports_BOP/BOP/... | 1.0.0 | WY/Patron_Account_Summary/{ed_year}/{ed_month}/... | Patron Account Summary Report | 0 16 * * * | Etc/UTC | 2024-03-28 15:00:00 | 12 | None | None | None | None | None | None | nan |
| REPORT | patron_account_summary_report_bop_month_to_date | PASRBMTD | 0.0 | 1.0 | 0.0 | get_current_month_to_date_6am | patron_account_summary_report_bop | SDP | ./scripts/WH/US_ALL/05_Queries/Reports_BOP/BOP/... | 1.0.0 | WY/Patron_Account_Summary_Month_To_Date/{ed_yea... | Patron Account Summary Month To Date Report | 0 15 * * * | Etc/UTC | 2024-07-09 15:30:00 | 13 | None | None | None | None | None | None | nan |
| REPORT | patron_account_summary_report_bop_finance | PASRBF | 0.0 | 1.0 | 0.0 | get_current_date_6am | generic_reporting.wy_004.recon_check | SDP | ./scripts/WH/US_ALL/05_Queries/Reports_BOP/BOP/... | 1.0.0 | WY/Patron_Account_Summary_Finance/{ed_year}/{ed... | Patron Account Summary Report Finance | 0 16 * * * | Etc/UTC | 2024-03-28 15:00:00 | 14 | None | None | None | None | None | None | nan |
| REPORT | patron_account_summary_report_bop_month_to_date... | PASRBMTDF | 0.0 | 1.0 | 0.0 | get_current_month_to_date_6am | patron_account_summary_report_bop_finance | SDP | ./scripts/WH/US_ALL/05_Queries/Reports_BOP/BOP/... | 1.0.0 | WY/Patron_Account_Summary_Finance_Month_To_Date... | Patron Account Summary Month To Date Report Fin... | 0 15 * * * | Etc/UTC | 2024-07-09 15:30:00 | 15 | None | None | None | None | None | None | nan |
| REPORT | patron_acct_adjust_report_month_to_date_bop | PAARMTDB | 0.0 | 1.0 | 0.0 | get_current_month_to_date_6am | patron_acct_adjust_report_bop | SDP | ./scripts/WH/US_ALL/05_Queries/Reports_BOP/BOP/... | 1.0.0 | WY/Patron_Account_Adjustment_Month_To_Date/{ed_... | Patron Account Adjustment Month To Date Report | 0 15 * * * | Etc/UTC | 2024-07-09 15:30:00 | 16 | None | None | None | None | None | None | nan |
| REPORT | pending_wthdrwl_depst_report_bop | PWDRB | 0.0 | 1.0 | 0.0 | get_current_date_6am | generic_reporting.wy_004.recon_check | SDP | ./scripts/WH/US_ALL/05_Queries/Reports_BOP/BOP/... | 1.0.0 | WY/PendingTransaction/WithdrawalsAndDeposits/{e... | Pending Withdrawal And Deposit Report | 0 16 * * * | Etc/UTC | 2024-11-14 15:15:00 | 17 | None | None | None | None | None | None | nan |
| REPORT | problem_gamblers_report_bop | PGRB | 0.0 | 1.0 | 0.0 | get_current_week_6am | problem_gambler_mart_data_feed | SDP | ./scripts/WH/US_ALL/05_Queries/Reports_BOP/BOP/... | 1.0.0 | WY/Problem_Gamblers/{ed_year}/{ed_month}/{ed_da... | Problem Gamblers Report | 0 15 * * 3 | Etc/UTC | 2024-03-28 15:00:00 | 18 | None | None | None | None | None | None | nan |
| SENSOR | problem_gambler_mart_data_feed | PGMDFS | nan | nan | nan | get_current_week_6am | None | SDP | SELECT (SELECT case when max("LAST_UPDATE_PLAYE... | None | None | None | 0 15 * * 3 | Etc/UTC | None | 19 | problem_gambler_mart_data_feed | WY | None | None | None | None | nan |
| REPORT | sports_pool_cancelled_ticket_report_bop | SPCTRB | 0.0 | 1.0 | 0.0 | get_current_date_6am | generic_reporting.wy_004.recon_check | SDP | ./scripts/WH/US_ALL/05_Queries/Reports_BOP/BE/D... | 1.0.0 | WY/Sports_Pool_Cancelled_Ticket/{ed_year}/{ed_m... | Sports Pool Cancelled Report | 0 16 * * * | Etc/UTC | 2024-01-29 15:00:00 | 20 | None | None | None | None | None | None | nan |
| REPORT | sports_pool_digital_recap_report_bop | SPDRRB | 0.0 | 1.0 | 0.0 | get_current_date_6am | generic_reporting.wy_004.recon_check | SDP | ./scripts/WH/US_ALL/05_Queries/Reports_BOP/BE/D... | 1.0.0 | WY/Sports_Pool_Digital_Recap/{ed_year}/{ed_mont... | Sports Pool Digital Recap Report | 0 16 * * * | Etc/UTC | 2024-01-29 15:00:00 | 21 | None | None | None | None | None | None | nan |
| REPORT | sports_pool_digital_recap_report_month_to_date_bop | SPDRRMTDB | 0.0 | 1.0 | 0.0 | get_current_month_to_date_6am | sports_pool_digital_recap_report_bop | SDP | ./scripts/WH/US_ALL/05_Queries/Reports_BOP/BE/M... | 1.0.0 | WY/Sports_Pool_Digital_Recap_Month_To_Date/{ed_... | Sports Pool Digital Recap Month To Date Report | 0 15 * * * | Etc/UTC | 2024-07-09 15:30:00 | 22 | None | None | None | None | None | None | nan |
| REPORT | sports_pool_resettlement_report_bop | SPRRB | 0.0 | 1.0 | 0.0 | get_current_date_6am | generic_reporting.wy_004.recon_check | SDP | ./scripts/WH/US_ALL/05_Queries/Reports_BOP/BE/D... | 1.0.0 | WY/Sports_Pool_Resettlement_Ticket/{ed_year}/{e... | Sports Pool Resettlement Report | 0 16 * * * | Etc/UTC | 2024-07-09 15:30:00 | 23 | None | None | None | None | None | None | nan |
| REPORT | sports_pool_resettlement_report_bop_month_to_date | SPRRBMTD | 0.0 | 1.0 | 0.0 | get_current_month_to_date_6am | sports_pool_resettlement_report_bop | SDP | ./scripts/WH/US_ALL/05_Queries/Reports_BOP/BE/D... | 1.0.0 | WY/Sports_Pool_Resettlement_Ticket_Month_To_Dat... | Sports Pool Resettlement Month To Date Report | 0 15 * * * | Etc/UTC | 2024-07-09 15:30:00 | 24 | None | None | None | None | None | None | nan |
| REPORT | sports_pool_resettlement_report_bop_year_to_date | SPRRBYTD | 0.0 | 1.0 | 0.0 | get_current_year_to_date_6am | sports_pool_resettlement_report_bop | SDP | ./scripts/WH/US_ALL/05_Queries/Reports_BOP/BE/D... | 1.0.0 | WY/Sports_Pool_Resettlement_Ticket_Year_To_Date... | Sports Pool Resettlement Year To Date Report | 0 15 * * * | Etc/UTC | 2024-07-09 15:30:00 | 25 | None | None | None | None | None | None | nan |
| REPORT | sports_pool_results_report_bop | SPRRBP | 0.0 | 1.0 | 0.0 | get_current_date_6am | generic_reporting.wy_004.recon_check | SDP | ./scripts/WH/US_ALL/05_Queries/Reports_BOP/BE/D... | 1.0.0 | WY/Sports_Pool_Results/{ed_year}/{ed_month}/{ed... | Sports Pool Results Report | 0 16 * * * | Etc/UTC | 2024-07-09 15:30:00 | 26 | None | None | None | None | None | None | nan |
| REPORT | sports_pool_results_report_categorized_bop | SPRRCB | 0.0 | 1.0 | 0.0 | get_current_date_6am | digital_sport_pool_transaction_feed | SDP | ./scripts/WH/US_ALL/05_Queries/Reports_BOP/BE/D... | 1.0.0 | WY/Sports_Pool_Results_Categorized/{ed_year}/{e... | Sports Pool Results Categorized Report | 0 15 * * * | Etc/UTC | 2024-07-09 15:30:00 | 27 | None | None | None | None | None | None | nan |
| SENSOR | digital_sport_pool_transaction_feed | DSPTFS | nan | nan | nan | get_current_date_6am | None | SDP | SELECT (SELECT case when max(ifnull(ifnull("SET... | None | None | None | 0 15 * * * | Etc/UTC | None | 28 | digital_sport_pool_transaction_feed | WY | None | None | None | None | nan |
| REPORT | sports_pool_results_report_categorized_month_to... | SPRRCMTDB | 0.0 | 1.0 | 0.0 | get_current_month_to_date_6am | sports_pool_results_report_categorized_bop | NJ_Prod | ./scripts/WH/US_ALL/05_Queries/Reports_BOP/BE/M... | 1.0.0 | WY/Sports_Pool_Results_Categorized_Month_To_Dat... | Sports Pool Results Categorized Month To Date R... | 0 15 * * * | Etc/UTC | 2024-07-09 15:30:00 | 29 | None | None | None | None | None | None | nan |
| REPORT | sports_pool_results_report_month_to_date_bop | SPRRMTDB | 0.0 | 1.0 | 0.0 | get_current_month_to_date_6am | sports_pool_results_report_bop | NJ_Prod | ./scripts/WH/US_ALL/05_Queries/Reports_BOP/BE/M... | 1.0.0 | WY/Sports_Pool_Results_Month_To_Date/{ed_year}/... | Sports Pool Results Month To Date Report | 0 15 * * * | Etc/UTC | 2024-07-09 15:30:00 | 30 | None | None | None | None | None | None | nan |
| REPORT | sports_pool_transaction_report_bop | SPTRB | 0.0 | 1.0 | 0.0 | get_current_date_6am | generic_reporting.wy_004.recon_check | SDP | ./scripts/WH/US_ALL/05_Queries/Reports_BOP/BE/D... | 1.0.0 | WY/Sport_Pool_Transaction/{ed_year}/{ed_month}/... | Sports Pool Transaction Report | 0 16 * * * | Etc/UTC | 2024-01-29 15:00:00 | 31 | None | None | None | None | None | None | nan |
| REPORT | sports_pool_voided_ticket_report_bop | SPVTRB | 0.0 | 1.0 | 0.0 | get_current_date_6am | generic_reporting.wy_004.recon_check | SDP | ./scripts/WH/US_ALL/05_Queries/Reports_BOP/BE/D... | 1.0.0 | WY/Sports_Pool_Voided_Ticket/{ed_year}/{ed_mont... | Sports Pool Voided Report | 0 16 * * * | Etc/UTC | 2024-01-29 15:00:00 | 32 | None | None | None | None | None | None | nan |
| REPORT | tax_reportable_win | TRW | 0.0 | 1.0 | 0.0 | get_current_date_6am | tax_reportable_win_feed | SDP | ./scripts/WH/US_ALL/05_Queries/Reports_BOP/BOP/... | 1.0.0 | WY/Tax_Reportable_Win_Report/{ed_year}/{ed_mont... | Tax Reportable Win | 20 16 * * * | Etc/UTC | 2024-12-18 15:15:00 | 33 | None | None | { 'ssn': None } | bop_kms |  | None | nan |
| SENSOR | tax_reportable_win_feed | TRWFS | nan | nan | nan | get_current_date_6am | None | SDP | SELECT (SELECT case when max("LAST_UPDATE_PLAYE... | None | None | None | 20 16 * * * | Etc/UTC | None | 34 | tax_reportable_win_feed | WY | None | None | None | None | nan |
| REPORT | tax_reportable_win_month_to_date | TRWMTD | 0.0 | 1.0 | 0.0 | get_current_month_to_date_6am | tax_reportable_win | SDP | ./scripts/WH/US_ALL/05_Queries/Reports_BOP/BOP/... | 1.0.0 | WY/Tax_Reportable_Win_Monthly_Report/{ed_year}/... | Tax Reportable Win Month To Date Report | 20 16 * * * | Etc/UTC | 2024-12-18 15:15:00 | 35 | None | None | { 'ssn': None } | bop_kms |  | None | nan |
| REPORT | tax_reportable_win_year_to_date | TRWYTD | 0.0 | 1.0 | 0.0 | get_current_year_to_date_6am | tax_reportable_win | SDP | ./scripts/WH/US_ALL/05_Queries/Reports_BOP/BOP/... | 1.0.0 | WY/Tax_Reportable_Win_Yearly_Report/{ed_year}/{... | Tax Reportable Win Year To Date Report | 20 16 * * * | Etc/UTC | 2024-12-18 15:15:00 | 36 | None | None | { 'ssn': None } | bop_kms |  | None | nan |
| REPORT | wagering_summary_report_bop | WSRB | 0.0 | 1.0 | 0.0 | get_current_date_6am | generic_reporting.wy_004.recon_check | SDP | ./scripts/WH/US_ALL/05_Queries/Reports_BOP/BOP/... | 1.0.0 | WY/WageringSummary/{ed_year}/{ed_month}/{ed_day... | Wagering Summary Report | 0 16 * * * | Etc/UTC | 2024-03-28 15:00:00 | 37 | None | None | None | None | None | None | nan |
| REPORT | wallet_transactions_report | WTR | 0.0 | 1.0 | 0.0 | get_current_date_6am | daily_transaction_mart_data_feed | SDP | ./scripts/WH/US_ALL/05_Queries/Reports_BOP/BOP/... | 1.0.0 | WY/Wallet_Transactions_Report/{ed_year}/{ed_mon... | Wallet Transactions Report | 0 15 * * * | Etc/UTC | 2024-03-28 15:00:00 | 38 | None | None | None | None | None | None | nan |
| SENSOR | daily_transaction_mart_data_feed | DTMDFS | nan | nan | nan | get_current_date_6am | None | SDP | SELECT (SELECT case when max("LAST_UPDATE_PLAYE... | None | None | None | 0 15 * * * | Etc/UTC | None | 39 | daily_transaction_mart_data_feed | WY | None | None | None | None | nan |
| REPORT | patron_acct_adjust_report_bop | PAARB | 0.0 | 1.0 | 0.0 | get_current_date_6am | generic_reporting.wy_004.recon_check | SDP | ./scripts/WH/US_ALL/05_Queries/Reports_BOP/BOP/... | 1.0.0 | WY/PatronAccountAdjustment/{ed_year}/{ed_month}... | Patron Account Adjustment Report | 0 16 * * * | Etc/UTC | 2024-03-28 15:00:00 | 40 | None | None | None | None | None | None | nan |
| REPORT | noncashable_bonus_balance_report_bop_month_to_d... | NBBRBMTDB | 0.0 | 1.0 | 0.0 | get_current_month_to_date_6am | noncashable_bonus_balance_report_bop | SDP | ./scripts/WH/US_ALL/05_Queries/Reports_BOP/BOP/... | 1.0.0 | WY/Non-Cashable_Bonus_Balance_Month_To_Date/{ed... | Non-Cashable Bonus Balance Month To Date Report | 30 15 * * * | Etc/UTC | 2024-07-09 15:30:00 | 41 | None | None | None | None | None | None | nan |
| REPORT | wagering_summary_report_bop_month_to_date | WSRBMTD | 0.0 | 0.0 | 1.0 | get_current_month_to_date_6am | wagering_summary_report_bop | SDP | ./scripts/WH/US_ALL/05_Queries/Reports_BOP/BOP/... | 1.0.0 | WY/WH_WageringSummary_Month_To_Date/{ed_year}/{... | Wagering Summary Month To Date Report | 0 15 * * * | Etc/UTC | 2024-07-09 15:30:00 | 42 | None | None | None | None | None | None | nan |
| REPORT | sports_pool_voided_ticket_report_year_to_date_bop | SPVTRYTDB | 0.0 | 1.0 | 0.0 | get_current_year_to_date_6am | sports_pool_voided_ticket_report_bop | SDP | ./scripts/WH/US_ALL/05_Queries/Reports_BOP/BE/M... | v2.6.1_1.9_1.0 | WY/Sports_Pool_Voided_Ticket_Year_To_Date/{ed_y... | Sports Pool Voided Year To Date Report | 0 15 * * * | Etc/UTC | 2024-05-01 15:00:00 | 43 | None | None | None | None | None | PdfHeader() | 0.0 |
| REPORT | sports_pool_voided_ticket_report_month_to_date_bop | SPVTRMTDB | 0.0 | 1.0 | 0.0 | get_current_month_to_date_6am | sports_pool_voided_ticket_report_bop | SDP | ./scripts/WH/US_ALL/05_Queries/Reports_BOP/BE/M... | v2.6.1_1.9_1.0 | WY/Sports_Pool_Voided_Ticket_Month_To_Date/{ed_... | Sports Pool Voided Month To Date Report | 0 15 * * * | Etc/UTC | 2024-05-01 15:00:00 | 44 | None | None | None | None | None | PdfHeader() | 0.0 |
| REPORT | sports_pool_cancelled_ticket_report_year_to_dat... | SPCTRYTDB | 0.0 | 1.0 | 0.0 | get_current_year_to_date_6am | sports_pool_cancelled_ticket_report_bop | SDP | ./scripts/WH/US_ALL/05_Queries/Reports_BOP/BE/M... | v2.6.1_1.9_1.0 | WY/Sports_Pool_Cancelled_Ticket_Year_To_Date/{e... | Sports Pool Cancelled Year To Date Report | 0 15 * * * | Etc/UTC | 2024-05-01 15:00:00 | 45 | None | None | None | None | None | PdfHeader() | 0.0 |
| REPORT | sports_pool_cancelled_ticket_report_month_to_da... | SPCTRMTDB | 0.0 | 1.0 | 0.0 | get_current_month_to_date_6am | sports_pool_cancelled_ticket_report_bop | SDP | ./scripts/WH/US_ALL/05_Queries/Reports_BOP/BE/M... | v2.6.1_1.9_1.0 | WY/Sports_Pool_Cancelled_Ticket_Month_To_Date/{... | Sports Pool Cancelled Month To Date Report | 0 15 * * * | Etc/UTC | 2024-05-01 15:00:00 | 46 | None | None | None | None | None | PdfHeader() | 0.0 |
| REPORT | taxable_handle_recap_vs_trans_month_to_date_rep... | THRVTMTDRB | 0.0 | 1.0 | 0.0 | get_current_month_to_date | taxable_handle_recap_vs_trans_report_bop | SDP | ./scripts/WH/US_ALL/05_Queries/Report_Variances... | 1.0.0 | WY/TaxableHandleRecapVsTrans_Month_To_Date/{ed_... | Taxable Handle Recapvstrans | 35 16 * * * | Etc/UTC | 2024-06-04 08:35:00 | 47 | None | None | None | None | None | None | nan |
| REPORT | taxable_handle_recap_vs_trans_report_bop | THRVTRB | 0.0 | 1.0 | 0.0 | get_current_date | generic_reporting.wy_004.recon_check | SDP | ./scripts/WH/US_ALL/05_Queries/Report_Variances... | 1.0.0 | WY/Taxable_Handle_Recap_Vs_Trans/{ed_year}/{ed_... | Taxable Handle Recapvstrans | 0 16 * * * | Etc/UTC | 2024-06-04 08:00:00 | 48 | None | None | None | None | None | None | nan |

---

## DEPLOYMENT

### Schema

| Column | Type |
|--------|------|
| `deploymentz_code` | TEXT |
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

| deploymentz_code | deployment_version | domain_code | warehouse_auto_suspend | warehouse_max_cluster_count | warehouse_scaling_policy | warehouse_warehouse_size | warehouse_warehouse_type | internal_stage | external_stage | domain_timezone |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| WY_005 | 0.0.5 | WY | 120 | 4 | STANDARD | MEDIUM | SNOWPARK-OPTIMIZED | GENERIC_REPORTING."WY_005".REPORTING | GENERIC_REPORTING.REPORTING.PRODUCTION | US/Eastern |
