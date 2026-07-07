# Month-End Finance Close Process

**Purpose:** To ensure the general ledger is complete, accurate and closed on a timely basis each month, with all balance sheet accounts reconciled and reviewed.

**Scope:** Applies to each monthly reporting period. All references to "WD" mean working days after month end (e.g. WD2 = second working day of the new month).

**Roles:**
- **Preparer** – Financial/Management Accountant responsible for the task
- **Reviewer** – Finance Manager / Financial Controller
- **Approver** – CFO or delegate (for judgemental provisions and tax)

---

## Close Timetable (Summary)

| WD | Task | Preparer | Reviewer |
|----|------|----------|----------|
| WD1 | Sub-ledger cut-off (AP, AR, payroll, bank) confirmed | Accountant | FC |
| WD2 | Update revenue share | Accountant | FC |
| WD2 | Other revenue recognised | Accountant | FC |
| WD3 | Prepayments reconciliation | Accountant | FC |
| WD3 | Accrued expenses reconciliation | Accountant | FC |
| WD4 | Employee provisions | Accountant | FC |
| WD5 | Income tax provision | Accountant | CFO |
| WD5 | Final review, GL lock, flash reporting | FC | CFO |

---

## 1. Update Revenue Share

**Objective:** Ensure revenue share owed to / due from partners is calculated, recorded and agreed for the month.

**Steps:**
1. Extract the month's gross revenue by partner/product from the billing system or revenue report.
2. Apply the contractual revenue share percentages per each partner agreement (maintain a master rate table; check for any rate changes, tiers or minimum guarantees effective this month).
3. Calculate the revenue share payable (or receivable) for the month and prepare the supporting schedule showing gross revenue × rate = share amount, by partner.
4. Post the journal:
   - Dr Revenue share expense (or contra-revenue, per accounting policy)
   - Cr Revenue share payable (accrual)
5. Reconcile the revenue share payable account: opening balance + current month accrual − payments made = closing balance. Agree payments to bank/AP.
6. Where partner statements or self-billing reports are received, agree the calculated share to the partner's statement and investigate variances above the agreed threshold (e.g. >1% or $1,000).
7. Reviewer checks rates to contracts, recalculates a sample, and signs off the schedule.

**Controls / evidence:** Signed revenue share schedule, rate table with contract references, partner statement reconciliations, posted journal reference.

---

## 2. Prepayments Reconciliation

**Objective:** Ensure prepaid expenses are correctly amortised and the prepayments balance is fully supported.

**Working paper:** [Prepayments Schedule (Google Sheet)](https://docs.google.com/spreadsheets/d/1uUPOHs479r5mX8DaaPJTRkyECb0IkFUcrYKwd8mqw7I/edit?gid=1072322654#gid=1072322654) — all new items, monthly amortisation and the GL reconciliation are maintained in this sheet.

**Steps:**
1. Review AP invoices posted in the month for new items that should be capitalised as prepayments (e.g. annual insurance, software subscriptions, rent paid in advance, licences) above the capitalisation threshold (e.g. $500 and covering more than one month).
2. Add new prepayments to the linked Prepayments Schedule, recording: supplier, description, invoice reference, total amount, coverage period (start/end dates), monthly amortisation amount, and expense GL code.
3. Run the monthly amortisation: release one month's charge for each active item.
   - Dr Expense (relevant P&L line)
   - Cr Prepayments
4. Remove fully amortised items and confirm their balance is nil.
5. Reconcile the schedule total to the prepayments GL balance. Investigate and clear any difference before close.
6. Review for stale or doubtful items (e.g. prepayments to suppliers no longer used) and write off if no future benefit exists.
7. Reviewer agrees a sample of items to source invoices and checks the amortisation math, then signs off.

**Controls / evidence:** Prepayments schedule reconciled to GL (nil variance), source invoices attached for new items, review sign-off.

---

## 3. Accrued Expenses Reconciliation

**Objective:** Ensure all expenses incurred but not yet invoiced are accrued, and prior accruals are released or trued up.

**Steps:**
1. Reverse (or confirm auto-reversal of) prior month's accruals where invoices have now been received.
2. Identify current month accruals from:
   - Open purchase orders with goods/services received but not invoiced (GRNI report)
   - Recurring known costs not yet billed (utilities, rent, professional fees, contractors, commissions, interest)
   - Department head confirmations for significant unbilled work (request by WD2)
   - Invoices received after cut-off relating to the current month
3. Prepare the accruals schedule with: supplier/description, basis of estimate, amount, expense GL code, and expected invoice date.
4. Post the journal:
   - Dr Expense
   - Cr Accrued expenses
5. Reconcile the accruals schedule to the accrued expenses GL balance.
6. Perform an accrual accuracy review: compare last month's accruals to actual invoices received and adjust the estimation approach for recurring items with material variances.
7. Review aged accruals (e.g. >3 months old with no invoice) and release if no longer required, with reviewer approval.
8. Reviewer checks basis of significant estimates (e.g. items > $5,000) and signs off.

**Controls / evidence:** Accruals schedule reconciled to GL, basis of estimate documented per item, aged accruals review, sign-off.

---

## 4. Employee Provisions

**Objective:** Ensure provisions for employee entitlements are complete and measured correctly at month end.

**Steps:**
1. Obtain the month-end leave balances report from the payroll/HRIS system (annual leave, and long service leave where applicable).
2. **Annual leave provision:** calculate as leave hours × current pay rate × (1 + on-costs %) per employee. On-costs include superannuation/pension, payroll tax and workers' compensation as applicable.
3. **Long service leave provision (if applicable):** update for current service, salaries and probability/discount assumptions per policy; split current vs non-current.
4. **Bonus/incentive provision:** accrue the year-to-date entitlement based on the current scheme and expected performance outcome; document assumptions and obtain HR/management confirmation for material changes.
5. **Payroll accruals:** accrue unpaid salaries/wages for days worked after the last pay run, plus associated superannuation and payroll tax not yet remitted.
6. Post movement journals:
   - Dr Employee benefits expense
   - Cr Provision for annual leave / LSL / bonus / accrued payroll
7. Reconcile each provision account to its supporting calculation and to the payroll system report.
8. Analytical review: compare provision movements month-on-month and explain significant changes (headcount, pay rises, leave taken).
9. Reviewer agrees inputs to payroll reports, checks on-cost rates against current statutory rates, and signs off. Bonus provisions above threshold approved by CFO.

**Controls / evidence:** Payroll system leave report, provision calculation workbook, journal references, month-on-month movement analysis, sign-offs.

---

## 5. Other Revenue

**Objective:** Ensure non-core revenue streams are completely captured and recognised in the correct period.

**Steps:**
1. Identify all other revenue sources for the month, e.g.:
   - Interest income on bank deposits and term deposits
   - Sublease / rental income
   - Government grants or rebates
   - Gains on disposal of assets
   - Sundry recoveries and one-off items
2. **Interest income:** obtain bank statements/term deposit schedules; accrue interest earned but not yet credited.
3. **Grants/rebates:** confirm eligibility conditions are met before recognising; defer amounts relating to future periods or unmet conditions.
4. **Other items:** agree to supporting documentation (agreements, remittances, disposal calculations).
5. Post journals:
   - Dr Cash / receivable / accrued income
   - Cr Other revenue (by category)
6. Reconcile deferred/accrued income accounts related to other revenue.
7. Analytical review: compare other revenue to budget and prior months; explain variances above threshold.
8. Reviewer checks recognition treatment (point-in-time vs over-time, gross vs net) and signs off.

**Controls / evidence:** Supporting schedules per revenue type, bank statements, grant agreements, variance commentary, sign-off.

---

## 6. Income Tax Provision

**Objective:** Record an appropriate income tax expense and current/deferred tax balances for the month.

**Steps:**
1. Determine year-to-date accounting profit before tax from the closed (pre-tax) trial balance.
2. Calculate taxable income by adjusting for permanent differences (e.g. non-deductible entertainment, fines) and temporary differences (e.g. provisions not yet deductible, depreciation differences), using the effective tax rate methodology or full computation per policy.
3. Calculate the current month tax expense: YTD tax expense at the applicable rate less tax expense recognised in prior months.
4. Post the journal:
   - Dr Income tax expense
   - Cr Current tax liability (provision for income tax)
   - Dr/Cr Deferred tax asset/liability for movements in temporary differences (at least quarterly, or monthly if material)
5. Update the tax provision reconciliation: opening balance + current period provision − instalments/payments made (e.g. PAYG instalments) = closing balance. Agree payments to bank and tax authority accounts.
6. Reconcile the effective tax rate: tax expense ÷ profit before tax, and explain any deviation from the statutory rate.
7. Review recoverability of deferred tax assets (e.g. carried-forward losses) where relevant.
8. CFO (or tax advisor for complex matters) reviews the computation and approves the provision. Flag any uncertain tax positions for separate assessment.

**Controls / evidence:** Tax computation workbook, effective tax rate reconciliation, provision account reconciliation agreed to tax authority statements, CFO approval.

---

## Final Close Steps

1. Confirm all reconciliations above are complete, reviewed and signed off in the close checklist.
2. Run the final trial balance; perform a P&L and balance sheet analytical review against budget and prior month, documenting explanations for material variances.
3. Post any final adjustments approved by the reviewer.
4. Lock the GL period to prevent further posting.
5. Distribute flash results / management reports per the reporting calendar.
6. Log any issues, late adjustments or process improvements in the close issues register for follow-up before next month-end.

---

## Appendix – Standing Requirements

- **Thresholds:** Document accrual/prepayment capitalisation thresholds and variance investigation thresholds; review annually.
- **Reconciliation standard:** Every reconciliation must show GL balance, supporting balance, itemised differences (target nil), preparer, reviewer and dates.
- **Retention:** Store all close workpapers in the shared close folder for the period, retained per document retention policy.
- **Segregation of duties:** Preparer and reviewer must be different people; journals above approval thresholds require secondary approval.
