import requests
import json
import os
from datetime import datetime
import calendar

# 由于Python中没有直接的Lunar库，我们需要使用第三方库或者模拟实现
# 这里假设你已经安装了lunar-python库: pip install lunar-python
# 或者你可以使用其他农历计算库
try:
    from lunar_python import Lunar
except ImportError:
    print("请安装lunar-python库: pip install lunar-python")

def get_solar_date():
    """获取今天的公历日期"""
    today = datetime.now()
    return f"{today.year}-{today.month}-{today.day}"

def get_lunar_date():
    """获取今天的农历日期"""
    today = datetime.now()
    lunar = Lunar.fromDate(today)
    return f"{lunar.getYearInChinese()}年，{lunar.getMonthInChinese()}月，{lunar.getDayInChinese()}日"

def calculate_birth_day(birth_list):
    """计算生日距离天数"""
    print("开始计算生日距离...")
    data_list = []
    today = datetime.now()
    lunar_today = Lunar.fromDate(today)

    for birth in birth_list:
        # 解析生日
        birth_parts = birth['birth'].split('-')
        birth_year = int(birth_parts[0])
        birth_month = int(birth_parts[1])
        birth_day = int(birth_parts[2])

        # 创建农历生日对象
        birth_date = Lunar.fromYmd(birth_year, birth_month, birth_day)
        lunar_birth = f"{birth_date.getYearInChinese()}年，{birth_date.getMonthInChinese()}月，{birth_date.getDayInChinese()}日"
        age = lunar_today.getYear() - birth_date.getYear()

        # 计算下次生日
        birth_lunar_month = birth_date.getMonth()
        birth_lunar_day = birth_date.getDay()

        # 今年的生日
        try:
            current_year_birth = Lunar.fromYmd(lunar_today.getYear(), birth_lunar_month, birth_lunar_day)
            current_year_solar = current_year_birth.getSolar()
            current_birth_date = datetime(current_year_solar.getYear(), current_year_solar.getMonth(), current_year_solar.getDay())

            if current_birth_date.date() <= today.date():
                # 今年生日已过，计算明年的生日
                next_year_birth = Lunar.fromYmd(lunar_today.getYear() + 1, birth_lunar_month, birth_lunar_day)
                next_year_solar = next_year_birth.getSolar()
                next_birth_date = datetime(next_year_solar.getYear(), next_year_solar.getMonth(), next_year_solar.getDay())
            else:
                # 今年生日还未到
                next_birth_date = current_birth_date

            # 计算天数差
            next_birth_day = (next_birth_date.date() - today.date()).days
        except:
            # 如果遇到闰月等特殊情况，默认设置为365天
            next_birth_day = 365

        data_list.append({
            'name': birth['name'],
            'birth': lunar_birth,
            'age': age,
            'nextBirthDay': next_birth_day
        })

    return data_list

def notify(contents, token):
    """发送通知"""
    if not token or not contents:
        print("通知跳过：token 或 contents 为空")
        return

    print("开始发送 HTTP 请求...")

    # 使用Server酱通知
    url = f"https://sctapi.ftqq.com/{token}.send"
    payload = {
        'title': contents.get('title', ''),
        'desp': contents.get('desp', '')
    }

    try:
        response = requests.post(url, data=payload)
        print(f"HTTP 响应状态: {response.status_code} {response.reason}")
    except Exception as e:
        print(f"发送通知失败: {e}")

def progress(birth_list, token):
    """处理生日提醒主流程"""
    print("开始处理数据...")

    solar_date = get_solar_date()
    lunar_date = get_lunar_date()

    print("计算生日信息...")
    data_list = calculate_birth_day(birth_list)

    content = f"# 今天是 {solar_date}，阴历 {lunar_date}\n"

    for item in data_list:
        content += f"\n## {item['name']}\n"
        content += f"- {item['birth']}，{item['age']}岁\n"
        content += f"- 距离下次生日还有 {item['nextBirthDay']} 天\n"

    print("生成内容完成")
    print("开始发送通知...")

    notify({
        'title': "开心每一天",
        'desp': content
    }, token)

def get_str_obj(env_var):
    """解析环境变量中的字符串对象"""
    try:
        return json.loads(os.environ.get(env_var, '[]'))
    except:
        return []

def main():
    """主函数"""
    birth_list = get_str_obj('BIRTHS')
    notify_token = os.environ.get('NOTIFY', '')

    progress(birth_list, notify_token)
    print("执行完成")

if __name__ == '__main__':
    main()
