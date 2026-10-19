import requests
import time
from datetime import datetime
import os
import getpass
import json
import subprocess
import pandas as pd
import threading
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# ================== Git 推送配置 ==================
GITHUB_REPO = "Juineii/yuhz_br1020"
GITHUB_BRANCH = "main"
PUSH_INTERVAL = 60
# GitHub Personal Access Token 优先从环境变量 GITHUB_TOKEN 读取

# ================== 选项 → CSV 文件映射（★ 这里就是你自定义文件名的地方）==================
# key   : API 返回的 opt_id（"000A" ~ "000G"），可以从抓包里的 "opt_id" 字段确认
# value : 该选项对应的 CSV 文件完整路径（Windows 示例；Linux/macOS 请改成 /home/xxx/...）
OPTION_FILE_MAP = {
    "000A": r"D:\fansign\ing\yuhz_br1020\YUHZ线上团签.csv"
}

# 没匹配到 opt_id 时，统一写到这个文件（可自定义）
DEFAULT_LOG_FILE = r"D:\fansign\ing\yuhz_br1020\其他.csv"

# 确保所有目录都存在
for _f in list(OPTION_FILE_MAP.values()) + [DEFAULT_LOG_FILE]:
    os.makedirs(os.path.dirname(_f), exist_ok=True)


# ========== 原有配置信息 ==========
api_url = "https://en.beatroad.co.kr/exec/front/order/Formproductmileage/"

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36 Edg/136.0.0.0",
    "Accept": "application/json, text/javascript, */*; q=0.01",
    "Accept-Encoding": "gzip, deflate, br, zstd",
    "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6,ko;q=0.5     ",
    "Cache-Control": "no-cache",
    "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
    "Origin": "https://en.beatroad.co.kr",
    "Pragma": "no-cache",
    "Referer": "https://en.beatroad.co.kr/order/orderform.html?basket_type=A0000&delvtype=B",
    "X-Requested-With": "XMLHttpRequest"
}

# ========== Cookies（保持原样，请定期更新） ==========
cookies = {
    "_fwb": "33C7kmCKPmroNREFFdzESJ.1760455807491",
    "CUK45": "cuk45_beatroad_focoqlk97r4j5lkjtca7ao2c089vlc9t",
    "CUK2Y": "cuk2y_beatroad_focoqlk97r4j5lkjtca7ao2c089vlc9t",
    "siteLT": "dd4aeff5-5c7e-67f0-4cf9-f3c9e1d79337",
    "analytics_longterm": "analytics_longterm.beatroad_2.E6A62AE.1760455810919",
    "CVID_Y": "CVID_Y.535755404a5a515d6c02.1792422730147",
    "CFAE_CUK1Y": "CFAE_CUK1Y.beatroad_1.QK5QE2N.1761025757505",
    "wcs_bt": "undefined:1785295412|undefined:1785295392|unknown:1778812704",
    "wish_id": "97c72dd4768f018a845576ce1220050c",
    "recent_plist2": "10896%7C10928%7C10930%7C10955%7C10957%7C10939%7C10956%7C10973%7C10972%7C10996%7C10997%7C11072%7C11068%7C11071%7C11070%7C11104%7C11118%7C11119%7C11128%7C11139%7C11140%7C11154%7C11165%7C11248%7C11284%7C11283%7C11282%7C11324%7C11371%7C11392%7C11473%7C11482%7C11605%7C11617%7C11631%7C11628%7C11678%7C11667%7C11673%7C11708%7C11770%7C11771%7C11769%7C11784%7C11792%7C11834%7C11845%7C11892%7C11907%7C11958",
    "return_url": "%2Forder%2Forderform.html%3Fbasket_type%3DA0000%26delvtype%3DB",
    "ECSESSID": "4tsbrct33r3cqln4oj5s7p9ee4vss23e",
    "isviewtype": "pc",
    "ec_ipad_device": "F",
    "siteSID": "aa5bbbb3-43b5-73b7-7330-16bbef4be8e3",
    "analytics_session_id": "analytics_session_id.beatroad_2.D010DAE.1792422690035",
    "CVID": "CVID.535755404a5a515d6c02.1792422690035",
    "org_phpsess_id_2": "4tsbrct33r3cqln4oj5s7p9ee4vss23e",
    "fb_event_id": "event_id.beatroad.2.5XTAXTJ9ZTDMJP4VUHPNHGB6WVEK4WVU",
    "login_provider_2": "%7B%22member_id%22%3A%22qq35142634515152%22%2C%22provider%22%3Anull%2C%22client_id%22%3Anull%7D",
    "iscache": "F",
    "ec_mem_level": "2",
    "PHPSESSVERIFY": "b39f06dbd1a06422f914183c2bf01a6b",
    "fb_external_id": "ccd90dbcd056173b970c5d4c3a2c04579110630c0a0f3462b984a6cab980bdb3",
    "couponcount_2": "0",
    "atl_epcheck": "1",
    "atl_option": "1%2C1%2CH",
    "basketprice_2": "%26%2336%3B37.02",
    "ec_async_cache_avail_mileage_2": "0.00",
    "ec_async_cache_used_mileage_2": "0.00",
    "ec_async_cache_returned_mileage_2": "0",
    "ec_async_cache_unavail_mileage_2": "0",
    "ec_async_cache_used_deposit_2": "0",
    "ec_async_cache_all_deposit_2": "0",
    "ec_async_cache_deposit_refund_wait_2": "0",
    "ec_async_cache_member_total_deposit_2": "0",
    "wishcount_2": "0"
}

# ========== requests 会话配置 ==========
session = requests.Session()
retries = Retry(
    total=5,
    backoff_factor=2,
    status_forcelist=[500, 502, 503, 504],
    allowed_methods=["POST"]
)
adapter = HTTPAdapter(max_retries=retries)
session.mount("https://", adapter)
session.mount("http://", adapter)

# ========== 全局线程安全变量 ==========
lines_since_last_push = 0
lines_lock = threading.Lock()
file_lock = threading.Lock()


# ================== Git 推送函数 ==================
def git_push_update():
    """将所有 CSV 文件提交并推送到 GitHub"""
    try:
        token = os.environ.get('GITHUB_TOKEN')
        if not token:
            print("⚠️ 环境变量 GITHUB_TOKEN 未设置，跳过 Git 推送")
            return False

        remote_url = f"https://{token}@github.com/{GITHUB_REPO}.git"

        # ★ 关键修改：一次性 add 所有文件（覆盖 OPTION_FILE_MAP 里的所有 CSV）
        subprocess.run(['git', 'add', '-A'], check=True, capture_output=True, timeout=30)

        result = subprocess.run(['git', 'diff', '--cached', '--quiet'], capture_output=True, timeout=30)
        if result.returncode != 0:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            commit_msg = f"自动更新数据 {timestamp}"
            subprocess.run(['git', 'commit', '-m', commit_msg], check=True, capture_output=True, timeout=30)
            subprocess.run(
                ['git', 'push', remote_url, f'HEAD:{GITHUB_BRANCH}'],
                check=True,
                capture_output=True,
                text=True,
                timeout=30
            )
            print(f"✅ 已推送到 GitHub: {commit_msg}")
            return True
        else:
            print("⏭️ CSV 文件无变化，跳过推送")
            return True

    except subprocess.TimeoutExpired:
        print("❌ Git 操作超时 (30秒)，推送失败")
        return False
    except subprocess.CalledProcessError as e:
        print(f"❌ Git 操作失败: {e.stderr if e.stderr else e}")
        return False
    except Exception as e:
        print(f"❌ 推送过程中发生错误: {e}")
        return False


# ========== 写入指定 CSV 文件（线程安全） ==========
def write_to_csv_file(target_file, time_str, product_name, stock_change, single_sale):
    """
    将监控结果写入指定 CSV 文件
    :param target_file: 目标 CSV 路径
    """
    global lines_since_last_push
    try:
        columns = ["时间", "商品名称", "库存变化", "单笔销量"]

        with file_lock:
            os.makedirs(os.path.dirname(target_file), exist_ok=True)
            if os.path.exists(target_file):
                df_existing = pd.read_csv(target_file, encoding='utf-8-sig')
            else:
                df_existing = pd.DataFrame(columns=columns)

            new_row = pd.DataFrame([[time_str, product_name, stock_change, single_sale]], columns=columns)
            df_updated = pd.concat([df_existing, new_row], ignore_index=True)
            df_updated.to_csv(target_file, index=False, encoding='utf-8-sig')

        # 打印时带上文件名，方便区分
        fname = os.path.basename(target_file)
        print(f"{time_str} [{fname}] 商品[{product_name}] 库存变化: {stock_change}, 单笔销量: {single_sale}")

        with lines_lock:
            lines_since_last_push += 1

    except Exception as e:
        print(f"❌ 写入CSV文件失败 ({target_file}): {e}")


# ========== 推送工作线程 ==========
def push_worker():
    global lines_since_last_push
    while True:
        time.sleep(PUSH_INTERVAL)
        with lines_lock:
            pending = lines_since_last_push
        if pending > 0:
            print(f"⏰ 定时推送：有 {pending} 条新数据待推送")
            with file_lock:
                success = git_push_update()
            if success:
                with lines_lock:
                    lines_since_last_push = 0
                print("✅ 推送成功，计数器已归零")
            else:
                print("⚠️ 推送失败，下次再试")


# ========== 获取库存（★ 关键修改：按 opt_id 拆开） ==========
def get_stock_from_api():
    """
    调用 API 获取库存，返回以 "product_no_opt_id" 为 key 的字典
    每个选项（成员）独立记录，避免相互覆盖
    """
    try:
        response = session.post(api_url, headers=headers, cookies=cookies, timeout=30)
        response.raise_for_status()
        data = response.json()

        product_list = data.get("product", [])
        stocks = {}
        for product in product_list:
            product_no = product.get("product_no")
            opt_id = product.get("opt_id") or ""            # 例如 "000F"
            product_name = product.get("product_name", "未知商品")
            option_value = product.get("option_value", "") or ""  # 例如 "판#$%..."
            stock = product.get("stock_number", None)

            if product_no is None or stock is None:
                continue

            # ★ 用 (product_no, opt_id) 组成唯一 key
            key = f"{product_no}_{opt_id}" if opt_id else str(product_no)

            # 从 option_value 提取可读的成员名（第 1 段，用 #$% 分隔）
            member_name = option_value.split("#$%")[0].strip() if option_value else ""

            stocks[key] = {
                "product_no": product_no,
                "opt_id": opt_id,
                "name": product_name,
                "member_name": member_name,   # 例如 "판", "현준"
                "stock": int(stock),
            }

        return stocks

    except Exception as e:
        print(f"{datetime.now()} ❌ API请求失败: {e}")
        return {}


# ========== 主监控函数 ==========
def monitor_stock():
    print("📁 选项 → CSV 文件映射：")
    for k, v in OPTION_FILE_MAP.items():
        print(f"   opt_id={k}  →  {v}")
    print(f"   其它未匹配 →  {DEFAULT_LOG_FILE}")
    print("-" * 60)

    previous_stocks = {}
    initial_stocks = {}

    while True:
        current_stocks = get_stock_from_api()
        if not current_stocks:
            print("⚠️ 无法获取库存数量")
        else:
            current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            for key, info in current_stocks.items():
                product_name = info["name"]
                opt_id = info["opt_id"]
                member_name = info["member_name"]
                current_stock = info["stock"]

                # ★ 根据 opt_id 决定写入哪个 CSV
                target_file = OPTION_FILE_MAP.get(opt_id, DEFAULT_LOG_FILE)

                # 用于打印 / 写入 CSV 的展示名称
                display_name = f"{product_name} [{member_name}]" if member_name else product_name

                # 第一次记录初始库存
                if key not in initial_stocks:
                    initial_stocks[key] = current_stock
                    previous_stocks[key] = current_stock

                    write_to_csv_file(
                        target_file, current_time,
                        display_name,
                        str(current_stock),
                        str(abs(current_stock))
                    )
                    print(f"{current_time} [opt={opt_id}][{member_name}] 初始库存: {current_stock}")

                # 库存变化
                elif current_stock != previous_stocks[key]:
                    stock_diff = previous_stocks[key] - current_stock
                    stock_change_str = f"{previous_stocks[key]} -> {current_stock}"

                    write_to_csv_file(
                        target_file, current_time,
                        display_name,
                        stock_change_str,
                        str(stock_diff)
                    )
                    print(
                        f"{current_time} [opt={opt_id}][{member_name}] "
                        f"库存变化: {previous_stocks[key]} -> {current_stock}, 销量: {stock_diff}"
                    )
                    previous_stocks[key] = current_stock

        time.sleep(10)


# ========== 程序入口 ==========
if __name__ == "__main__":
    print("启动监控")
    push_thread = threading.Thread(target=push_worker, daemon=True)
    push_thread.start()

    try:
        monitor_stock()
    except KeyboardInterrupt:
        print("\n监控程序被用户终止")
        with lines_lock:
            pending = lines_since_last_push
        if pending > 0:
            print(f"正在推送剩余的 {pending} 条数据...")
            with file_lock:
                success = git_push_update()
            if success:
                print("✅ 剩余数据已推送")
            else:
                print("⚠️ 剩余数据推送失败，请手动检查")
        else:
            print("无待推送数据")