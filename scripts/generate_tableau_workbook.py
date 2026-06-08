import os

def create_connection_xml(ds_name, filename, cols_def):
    """
    Generates XML for a single textscan datasource.
    Uses hash notation for relation name/table as required by Tableau.
    """
    col_str = ""
    for i, (name, dtype) in enumerate(cols_def.items()):
        col_str += f'        <column datatype="{dtype}" name="{name}" ordinal="{i}" />\n'
        
    records_str = ""
    for name, dtype in cols_def.items():
        agg = "Sum" if dtype in ("real", "integer") else "Count"
        records_str += f"""      <metadata-record class='column'>
        <remote-name>{name}</remote-name>
        <local-name>[{name}]</local-name>
        <local-type>{dtype}</local-type>
        <aggregation>{agg}</aggregation>
        <contains-null>true</contains-null>
      </metadata-record>
"""

    rel_name = filename.replace('.', '#')
    
    # Build column elements for the datasource level (role assignment)
    ds_columns = ""
    for name, dtype in cols_def.items():
        if dtype in ("real", "integer"):
            ds_columns += f'    <column datatype="{dtype}" name="[{name}]" role="measure" type="quantitative" />\n'
        else:
            ds_columns += f'    <column datatype="{dtype}" name="[{name}]" role="dimension" type="{"ordinal" if dtype == "date" else "nominal"}" />\n'
    
    xml = f"""  <datasource caption='{ds_name}' inline='true' name='{ds_name}' version='18.1'>
    <connection class='textscan' directory='../data/processed/dashboard_data' filename='{filename}' password='' server=''>
      <relation name='{rel_name}' table='[{rel_name}]' type='table'>
        <columns character-set='UTF-8' header='yes' locale='en_US' separator=','>
{col_str}        </columns>
      </relation>
      <metadata-records>
{records_str}      </metadata-records>
    </connection>
{ds_columns}    <semantic-values>
      <semantic-value key='[Country].[Name]' value='&quot;India&quot;' />
    </semantic-values>
  </datasource>
"""
    return xml

def make_worksheet(name, ds_name):
    """Create a minimal valid worksheet connected to a datasource with empty shelves."""
    return f"""    <worksheet name='{name}'>
      <table>
        <view>
          <datasources>
            <datasource name='{ds_name}' />
          </datasources>
          <aggregation value='true' />
        </view>
        <style />
        <panes>
          <pane>
            <view>
              <breakdown value='auto' />
            </view>
            <mark class='Automatic' />
          </pane>
        </panes>
        <rows />
        <cols />
      </table>
    </worksheet>
"""

def main():
    out_dir = "dashboard"
    os.makedirs(out_dir, exist_ok=True)
    twb_path = os.path.join(out_dir, "bluestock_mutual_funds_dashboard.twb")
    
    print(f"Creating Tableau Workbook XML at: {twb_path}")
    
    # ── Column definitions for all 9 data files ──
    columns_page1_aum = {"date": "date", "fund_house": "string", "aum_crore": "real", "aum_lakh_crore": "real", "num_schemes": "integer"}
    columns_page1_folios = {"month": "date", "total_folios_crore": "real", "equity_folios_crore": "real", "debt_folios_crore": "real", "hybrid_folios_crore": "real", "others_folios_crore": "real"}
    columns_page1_kpi = {"total_aum_lakh_cr": "real", "sip_inflow_cr": "real", "total_folios_cr": "real", "num_schemes": "integer"}
    columns_page1_sip = {"month": "date", "sip_inflow_crore": "real", "active_sip_accounts_crore": "real", "new_sip_accounts_lakh": "real", "sip_aum_lakh_crore": "real", "yoy_growth_pct": "real"}
    columns_page2_scorecard = {"amfi_code": "integer", "fund_house": "string", "scheme_name": "string", "category": "string", "sub_category": "string", "plan": "string", "expense_ratio_pct": "real", "cagr_1yr_pct": "real", "cagr_3yr_pct": "real", "cagr_5yr_pct": "real", "cagr_5yr_available": "string", "annualized_return_pct": "real", "annualized_volatility_pct": "real", "sharpe_ratio": "real", "sortino_ratio": "real", "alpha_pct": "real", "beta": "real", "r_squared": "real", "max_drawdown_pct": "real", "drawdown_start_date": "date", "drawdown_trough_date": "date", "drawdown_recovery_date": "date", "return_3yr_rank_score": "real", "sharpe_rank_score": "real", "alpha_rank_score": "real", "expense_rank_score": "real", "max_drawdown_rank_score": "real", "score_0_100": "real", "tracking_error_nifty100_pct": "real", "tracking_error_nifty50_pct": "real", "aum_crore": "real"}
    columns_page2_nav = {"amfi_code": "integer", "date": "date", "nav": "real", "close_value": "real", "indexed_nav": "real", "indexed_benchmark": "real", "scheme_name": "string", "fund_house": "string", "category": "string", "plan": "string", "benchmark_name": "string", "benchmark_index_code": "string"}
    columns_page3_tx = {"transaction_id": "integer", "investor_id": "string", "transaction_date": "date", "transaction_type": "string", "amount_inr": "real", "state": "string", "city": "string", "city_tier": "string", "age_group": "string", "gender": "string", "kyc_status": "string", "scheme_name": "string", "fund_house": "string", "category": "string"}
    columns_page4_category = {"month": "date", "category": "string", "net_inflow_crore": "real", "is_fy25": "string"}
    columns_page4_sip = {"month": "date", "sip_inflow_crore": "real", "active_sip_accounts_crore": "real", "new_sip_accounts_lakh": "real", "sip_aum_lakh_crore": "real", "yoy_growth_pct": "real", "nifty50_close": "real"}

    # ── Build datasource XML ──
    ds_xml = ""
    ds_xml += create_connection_xml("ds_page1_aum_by_fund_house", "page1_aum_by_fund_house.csv", columns_page1_aum)
    ds_xml += create_connection_xml("ds_page1_folios_timeline", "page1_folios_timeline.csv", columns_page1_folios)
    ds_xml += create_connection_xml("ds_page1_industry_kpis", "page1_industry_kpis.csv", columns_page1_kpi)
    ds_xml += create_connection_xml("ds_page1_sip_inflows_timeline", "page1_sip_inflows_timeline.csv", columns_page1_sip)
    ds_xml += create_connection_xml("ds_page2_fund_scorecard", "page2_fund_scorecard.csv", columns_page2_scorecard)
    ds_xml += create_connection_xml("ds_page2_fund_nav_history", "page2_fund_nav_history.csv", columns_page2_nav)
    ds_xml += create_connection_xml("ds_page3_investor_transactions", "page3_investor_transactions.csv", columns_page3_tx)
    ds_xml += create_connection_xml("ds_page4_category_inflows", "page4_category_inflows.csv", columns_page4_category)
    ds_xml += create_connection_xml("ds_page4_sip_market_trends", "page4_sip_market_trends.csv", columns_page4_sip)

    # ── Build worksheet XML (empty shelves, connected to datasources) ──
    ws_xml = "  <worksheets>\n"
    # Page 1
    ws_xml += make_worksheet("P1_KPI_Total_AUM", "ds_page1_industry_kpis")
    ws_xml += make_worksheet("P1_KPI_SIP_Inflows", "ds_page1_industry_kpis")
    ws_xml += make_worksheet("P1_KPI_Folios", "ds_page1_industry_kpis")
    ws_xml += make_worksheet("P1_KPI_Schemes", "ds_page1_industry_kpis")
    ws_xml += make_worksheet("P1_Industry_AUM_Timeline", "ds_page1_aum_by_fund_house")
    ws_xml += make_worksheet("P1_AUM_by_Fund_House", "ds_page1_aum_by_fund_house")
    # Page 2
    ws_xml += make_worksheet("P2_Risk_Return_Scatter", "ds_page2_fund_scorecard")
    ws_xml += make_worksheet("P2_Fund_Scorecard_Table", "ds_page2_fund_scorecard")
    ws_xml += make_worksheet("P2_Fund_NAV_vs_Benchmark", "ds_page2_fund_nav_history")
    # Page 3
    ws_xml += make_worksheet("P3_Transactions_by_State", "ds_page3_investor_transactions")
    ws_xml += make_worksheet("P3_Transaction_Type_Donut", "ds_page3_investor_transactions")
    ws_xml += make_worksheet("P3_SIP_by_Age_Group", "ds_page3_investor_transactions")
    ws_xml += make_worksheet("P3_Monthly_Transaction_Volume", "ds_page3_investor_transactions")
    # Page 4
    ws_xml += make_worksheet("P4_SIP_Inflow_vs_Nifty", "ds_page4_sip_market_trends")
    ws_xml += make_worksheet("P4_Category_Inflow_Heatmap", "ds_page4_category_inflows")
    ws_xml += make_worksheet("P4_Top_Categories_FY25", "ds_page4_category_inflows")
    ws_xml += make_worksheet("P4_KPI_SIP_YoY_Growth", "ds_page4_sip_market_trends")
    ws_xml += "  </worksheets>\n"

    # ── Build dashboard XML ──
    dash_xml = """  <dashboards>
    <dashboard name='1. Industry Overview'>
      <style />
      <datasources />
      <zones>
        <zone h='100000' id='1' type='layout-basic' w='100000' x='0' y='0'>
          <zone h='20000' id='11' type='layout-flow' w='100000' x='0' y='0'>
            <zone h='100000' id='12' name='P1_KPI_Total_AUM' w='25000' x='0' y='0' />
            <zone h='100000' id='13' name='P1_KPI_SIP_Inflows' w='25000' x='25000' y='0' />
            <zone h='100000' id='14' name='P1_KPI_Folios' w='25000' x='50000' y='0' />
            <zone h='100000' id='15' name='P1_KPI_Schemes' w='25000' x='75000' y='0' />
          </zone>
          <zone h='40000' id='17' name='P1_Industry_AUM_Timeline' w='100000' x='0' y='20000' />
          <zone h='40000' id='18' name='P1_AUM_by_Fund_House' w='100000' x='0' y='60000' />
        </zone>
      </zones>
    </dashboard>
    <dashboard name='2. Fund Performance'>
      <style />
      <datasources />
      <zones>
        <zone h='100000' id='2' type='layout-basic' w='100000' x='0' y='0'>
          <zone h='50000' id='21' type='layout-flow' w='100000' x='0' y='0'>
            <zone h='100000' id='22' name='P2_Risk_Return_Scatter' w='50000' x='0' y='0' />
            <zone h='100000' id='23' name='P2_Fund_Scorecard_Table' w='50000' x='50000' y='0' />
          </zone>
          <zone h='50000' id='24' name='P2_Fund_NAV_vs_Benchmark' w='100000' x='0' y='50000' />
        </zone>
      </zones>
    </dashboard>
    <dashboard name='3. Investor Analytics'>
      <style />
      <datasources />
      <zones>
        <zone h='100000' id='3' type='layout-basic' w='100000' x='0' y='0'>
          <zone h='50000' id='31' type='layout-flow' w='100000' x='0' y='0'>
            <zone h='100000' id='32' name='P3_Transactions_by_State' w='50000' x='0' y='0' />
            <zone h='100000' id='33' name='P3_Transaction_Type_Donut' w='50000' x='50000' y='0' />
          </zone>
          <zone h='50000' id='34' type='layout-flow' w='100000' x='0' y='50000'>
            <zone h='100000' id='35' name='P3_SIP_by_Age_Group' w='50000' x='0' y='0' />
            <zone h='100000' id='36' name='P3_Monthly_Transaction_Volume' w='50000' x='50000' y='0' />
          </zone>
        </zone>
      </zones>
    </dashboard>
    <dashboard name='4. SIP &amp; Market Trends'>
      <style />
      <datasources />
      <zones>
        <zone h='100000' id='4' type='layout-basic' w='100000' x='0' y='0'>
          <zone h='15000' id='41' name='P4_KPI_SIP_YoY_Growth' w='100000' x='0' y='0' />
          <zone h='42500' id='43' name='P4_SIP_Inflow_vs_Nifty' w='100000' x='0' y='15000' />
          <zone h='42500' id='44' type='layout-flow' w='100000' x='0' y='57500'>
            <zone h='100000' id='45' name='P4_Category_Inflow_Heatmap' w='50000' x='0' y='0' />
            <zone h='100000' id='46' name='P4_Top_Categories_FY25' w='50000' x='50000' y='0' />
          </zone>
        </zone>
      </zones>
    </dashboard>
  </dashboards>
"""

    # ── Assemble final TWB ──
    twb_xml = f"""<?xml version='1.0' encoding='utf-8' ?>
<workbook source-build='2018.1.0 (20181.18.0416.1506)' source-platform='mac' version='18.1' xmlns:user='http://www.tableausoftware.com/xml/user'>
  <preferences>
    <color-palette name='Bluestock Theme' type='regular'>
      <color>#012970</color>
      <color>#F05537</color>
      <color>#1E3A8A</color>
      <color>#F97316</color>
      <color>#3B82F6</color>
      <color>#EF4444</color>
      <color>#10B981</color>
      <color>#8B5CF6</color>
      <color>#6B7280</color>
      <color>#F3F4F6</color>
    </color-palette>
  </preferences>
  <datasources>
{ds_xml}  </datasources>
{ws_xml}
{dash_xml}
  <windows>
    <window class='worksheet' name='P1_KPI_Total_AUM'>
      <cards>
        <edge name='left'>
          <strip size='160'>
            <card type='pages' />
            <card type='filters' />
            <card type='marks' />
          </strip>
        </edge>
      </cards>
    </window>
  </windows>
</workbook>
"""

    with open(twb_path, "w", encoding="utf-8") as f:
        f.write(twb_xml)
        
    print(f"Tableau Workbook (.twb) generated at {twb_path}")
    print("All 9 data sources are pre-connected. Worksheets have empty shelves ready for field drag-and-drop.")

if __name__ == '__main__':
    main()
