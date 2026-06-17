from api_client import send_request
from config import CANO, ACNT_PRDT_CD, TARGET_SYMBOL
from logger import get_logger

logger = get_logger("account")

def get_account_balance():
    """
    Retrieves account balance and holdings for the target symbol.
    Returns a dict with 'available_cash' and 'target_qty'.
    """
    path = "/uapi/domestic-stock/v1/trading/inquire-balance"
    # VTTC8434R is the Mock Trading TR_ID for inquiring balance
    tr_id = "VTTC8434R"
    
    params = {
        "CANO": CANO,
        "ACNT_PRDT_CD": ACNT_PRDT_CD,
        "AFHR_FLPR_YN": "N",    # Offline order evaluation N
        "OFL_YN": "",           # Blank
        "INQR_DVSN": "02",      # Inquiry division: 02 (by items)
        "UNPR_DVSN": "01",      # Unit price division
        "FUND_STTL_ICLD_YN": "N",
        "FNCG_AMT_AUTO_RDPT_YN": "N",
        "PRCS_DVSN": "01",
        "CTX_AREA_FK100": "",
        "CTX_AREA_NK100": ""
    }
    
    response_data = send_request("GET", path, tr_id, params=params)
    
    result = {
        "available_cash": 0,
        "target_qty": 0
    }
    
    if response_data and response_data.get("rt_cd") == "0":
        try:
            # output2 contains the overall account summary
            output2 = response_data.get("output2", [])
            if output2:
                # dnca_tot_amt is total deposit amount, or prvs_rcdl_excc_amt
                # using prvs_rcdl_excc_amt (previous day's cash balance) or dnca_tot_amt
                result["available_cash"] = int(output2[0].get("dnca_tot_amt", 0))
                
            # output1 contains a list of holdings
            holdings = response_data.get("output1", [])
            for item in holdings:
                if item.get("pdno") == TARGET_SYMBOL:
                    result["target_qty"] = int(item.get("hldg_qty", 0))
                    break
                    
            logger.info(f"Account Balance: {result['available_cash']} KRW | Holdings for {TARGET_SYMBOL}: {result['target_qty']} shares")
            return result
            
        except (KeyError, ValueError, TypeError) as e:
            logger.error(f"Failed to parse account balance. Error: {e}")
            logger.error(f"Response: {response_data}")
    else:
        logger.error("Failed to fetch account balance.")
        if response_data:
            logger.error(f"Message: {response_data.get('msg1')}")
            
    return None

if __name__ == "__main__":
    # 터미널에서 직접 실행했을 때 잔고를 출력해주는 테스트 코드입니다.
    print("잔고 조회를 시작합니다...")
    balance = get_account_balance()
    if balance:
        print(f"\n[잔고 확인 결과]")
        print(f"주문 가능 현금: {balance['available_cash']:,} 원")
        print(f"삼성전자 보유 수량: {balance['target_qty']} 주")
    else:
        print("잔고 조회에 실패했습니다. 로그를 확인해주세요.")
