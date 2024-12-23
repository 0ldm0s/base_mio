# -*- coding: UTF-8 -*-
import os
import re
import sys
import copy
import math
import time
import zlib
import base64
import random
import string
import hashlib
import binascii
import platform
import ipaddress
import subprocess
from datetime import datetime, timedelta, timezone
from dateutil.relativedelta import relativedelta, MO, SU
from decimal import Decimal
from flask import request, current_app
from typing import Any, Tuple, Union, Optional, List, Dict

try:
    from cryptography.hazmat.primitives.asymmetric.ec import EllipticCurve
    from cryptography.hazmat.primitives.asymmetric.utils import (
        decode_dss_signature,
        encode_dss_signature,
    )
except ModuleNotFoundError:
    EllipticCurve = None


def get_canonical_os_name() -> str:
    if sys.platform in ("win32", "cygwin"):
        return "windows"
    if sys.platform == "darwin":
        result = subprocess.run(["sysctl", "-a", "machdep.cpu.brand_string"], stdout=subprocess.PIPE)
        brand_string: str = result.stdout.decode("UTF-8").strip().lower()
        if "apple" in brand_string:
            return "mac_m1"
        return "mac"
    if sys.platform.startswith("linux"):
        info: str = platform.processor()
        if info == "aarch64":
            return "linux_aarch64"
        return "linux"
    if "bsd" in sys.platform:
        if "freebsd" in sys.platform:
            return "freebsd"
        return "bsd"
    return "unknown"


def check_ua(keys: List[str]) -> bool:
    user_agent: str = str(request.headers.get("User-Agent")).lower()
    for k in keys:
        if user_agent.find(k.lower()) >= 0:
            return True
    return False


def check_bot() -> bool:
    return check_ua(["bot", "spider", "google"])


def check_ie() -> bool:
    return check_ua(["MSIE", "like gecko"])


def in_dict(dic: dict, key: str) -> bool:
    for kt in dic.keys():
        if kt == key:
            return True
    return False


def is_enable(dic: dict, key: str) -> bool:
    """
    主要用于判断权限字典内对应的键是否为布尔值。
    要求字典内对应的元素的字典必须为布尔值，否则返回false
    """
    if not in_dict(dic, key):
        return False
    _ = dic[key]
    if not isinstance(_, bool):
        return False
    return _


def do_sum(*args) -> Decimal:
    """
    对传入的数字进行求和计算

    :param args: 传入计算用的变量，支持str,float,int。非数字则跳过
    """
    calc_num: Decimal = Decimal("0")
    for num in args:
        if not is_number(num):
            continue
        calc_num += Decimal(str(num))
    return calc_num


def get_keyword(
        keyword: str, default: Any, **kwargs: Dict[str, Any]
) -> Tuple[Any, Dict[str, Any]]:
    """
    对传入的kwargs弹出指定keyword的数据。
    请注意：pop之后的数据会从kwargs里移除

    :param keyword: 从 kwargs 获取数据用的键
    :param default: 当获取不到数据时返回的默认值
    :param kwargs: 变量集
    :return: 弹出的数据和 kwargs
    """
    try:
        value = kwargs.pop(keyword)
    except KeyError:
        value = default
    return value, kwargs


def get_real_ip(
        idx: int = 0, show_all: bool = False, ipv6only: bool = True, console_log=None
) -> str:
    real_ip: str = ""
    if "HTTP_CF_CONNECTING_IP" in request.environ:
        real_ip = request.environ["HTTP_CF_CONNECTING_IP"]
    elif "HTTP_X_CLIENT" in request.environ:
        real_ip = request.environ["HTTP_X_CLIENT"]
    elif "HTTP_FORWARDED" in request.environ:
        http_forwarded: str = str(request.environ["HTTP_FORWARDED"])
        xp = http_forwarded.split(";")
        for s in xp:
            if s.startswith("for="):
                _, real_ip, *_ = s.split("=")
                if check_is_ip(real_ip):
                    break
    if len(real_ip) > 0:
        return real_ip
    if "HTTP_X_REAL_IP" in request.environ:
        real_ip = request.environ["HTTP_X_REAL_IP"]
    elif "HTTP_X_FORWARDED_FOR" in request.environ:
        real_ip = request.environ["HTTP_X_FORWARDED_FOR"]
    else:
        real_ip = request.environ["REMOTE_ADDR"]
    if "," in real_ip and not show_all:
        try:
            _tmp_: List[str] = real_ip.split(",")
            real_ip = _tmp_[idx].strip()
        except Exception as e:
            if console_log:
                console_log.error(e)
    if not ipv6only:
        # for haproxy v4v6 mode
        real_ip = real_ip.replace("::ffff:", "") if real_ip.startswith("::ffff:") else real_ip
    return real_ip


def check_is_ip(ip_addr: str) -> bool:
    try:
        ipaddress.ip_address(ip_addr)
        return True
    except ValueError:
        return False


def timestamp2str(
        timestamp: int, iso_format: str = "%Y-%m-%d %H:%M:%S", hours: int = 0, minutes: int = 0,
        console_log=None
) -> Optional[str]:
    dt = None
    try:
        utc_time = datetime.fromtimestamp(timestamp)
        local_dt = utc_time + timedelta(hours=hours, minutes=minutes)
        dt = local_dt.strftime(iso_format)
    except Exception as e:
        if console_log:
            console_log.error(e)
    return dt


def str2timestamp(
        date: str, iso_format: str = "%Y-%m-%d %H:%M:%S", hours: int = 0, minutes: int = 0,
        console_log=None
) -> Optional[int]:
    ts = None
    try:
        time_array = time.strptime(date, iso_format)
        timestamp = time.mktime(time_array)
        local_time = datetime.fromtimestamp(timestamp)
        local_dt = local_time + timedelta(hours=hours, minutes=minutes)
        timestamp = time.mktime(local_dt.timetuple())
        ts = int(timestamp)
    except Exception as e:
        if console_log:
            console_log.error(e)
    return ts


def get_bool(obj: Any) -> bool:
    """
    主要用于excel中，将代表true的字符转换为实际的布尔值
    """
    obj = False if obj is None else obj
    if isinstance(obj, bool) is False:
        if is_number(obj):
            obj = True if str2int(obj) == 1 else False
        elif isinstance(obj, str):
            tmp: str = str(obj).strip().lower()
            if tmp == "y" or tmp == "t" or tmp == "yes" or tmp == "true":
                obj = True
            else:
                obj = False
        else:
            obj = False
    return obj


def get_root_path() -> str:
    """
    获取当前项目的根路径
    """
    root_path = os.path.abspath(os.path.dirname(__file__) + "/../../")
    return root_path


def file_lock(filename: str, txt: str = " ", exp: int = None, reader: bool = False) -> Tuple[int, str]:
    lock = os.path.join(get_root_path(), "lock")
    if not os.path.exists(lock):
        os.makedirs(lock)
    lock = os.path.join(lock, filename)
    if not os.path.isfile(lock):
        is_ok, txt = write_txt_file(lock, txt)
        return -1 if not is_ok else 1, txt
    # 如果文件存在，则判断是否需要检测过期
    if exp is None or not is_number(exp):
        return 0, u"Locked." if not reader else read_txt_file(lock)
    exp = int(exp)
    if exp <= 0:
        return 0, u"Locked." if not reader else read_txt_file(lock)
    exp = int(exp * 60)  # 是否有超过界限的问题？
    file_time = int(os.stat(lock).st_mtime)
    if exp >= (int(time.time()) - file_time):
        os.unlink(lock)
        return file_lock(filename, txt, exp)
    # 判断是否要读取内容
    return 0, u"Locked." if not reader else read_txt_file(lock)


def write_txt_file(filename: str, txt: str = " ", encoding: str = "UTF-8") -> Tuple[bool, str]:
    if os.path.isfile(filename):
        os.unlink(filename)
    try:
        with open(filename, "w", encoding=encoding) as locker:
            locker.write(txt)
        return True, "OK"
    except Exception as e:
        return False, str(e)


def read_txt_file(filename: str, encoding: str = "UTF-8") -> str:
    if not os.path.isfile(filename):
        return ""
    txt = ""
    with open(filename, "r", encoding=encoding, errors="ignore") as reader:
        for line in reader:
            if line is None or len(line) <= 0:
                continue
            txt += line
    return txt


def write_file(
        filename: str, txt: Union[str, bytes] = " ", method: str = "w+", encoding: str = "UTF-8"
) -> Tuple[bool, str]:
    try:
        with open(filename, method, encoding=encoding) as locker:
            locker.write(txt)
        return True, "OK"
    except Exception as e:
        return False, str(e)


def read_file(filename: str, method: str = "r", encoding: str = "UTF-8") -> Optional[Union[str, bytes]]:
    if not os.path.isfile(filename):
        return None
    with open(filename, method, encoding=encoding) as reader:
        txt = reader.read()
    return txt


def file_unlock(filename: str) -> Tuple[int, str]:
    lock: str = os.path.join(get_root_path(), "lock")
    if not os.path.exists(lock):
        return 1, u"Unlocked."
    try:
        lock = os.path.join(lock, filename)
        if os.path.isfile(lock):
            os.unlink(lock)
        return 1, u"Unlocked."
    except Exception as e:
        return -1, str(e)


def random_str(random_length: int = 8) -> str:
    a: List[str] = list(string.ascii_letters)
    random.shuffle(a)
    return "".join(a[:random_length])


def random_number_str(random_length: int = 8) -> str:
    a: List[str] = [str(0), str(1), str(2), str(3), str(4), str(5), str(6), str(7), str(8), str(9)]
    random.shuffle(a)
    return "".join(a[:random_length])


def random_char(size: int = 6, special: bool = False) -> str:
    import random
    import string
    chars = string.ascii_letters + string.digits
    if special:
        chars += "!@#$%^&*"
    return "".join(random.choice(chars) for _ in range(size))


def get_file_list(
        root_path: str, files: Optional[List[str]] = None, is_sub: bool = False, is_full_path: bool = True,
        include_hide_file: bool = False
) -> List[str]:
    if files is None or not isinstance(files, list):
        return files if isinstance(files, list) else []
    for lists in os.listdir(root_path):
        if lists.startswith(".") or lists.endswith(".pyc"):
            if not include_hide_file:
                continue
        if is_full_path:
            path = os.path.join(root_path, lists)
        else:
            path = lists
        if is_sub and os.path.isdir(os.path.join(root_path, lists)):
            files = get_file_list(
                root_path=os.path.join(root_path, lists), files=files, is_sub=is_sub, is_full_path=is_full_path)
        else:
            files.append(path)
    return files


def check_file_in_list(file: str, file_list: List[str] = None) -> bool:
    if file is None or not isinstance(file, str) or \
            file_list is None or not isinstance(file_list, list):
        return False
    file = file.lower()
    if file in file_list:
        return True
    for f in file_list:
        if file.startswith(f.lower()):
            return True
    return False


def crc_file(filename: str) -> str:
    prev = 0
    for eachLine in open(filename, "rb"):
        prev = zlib.crc32(eachLine, prev)
    return "%X" % (prev & 0xFFFFFFFF)


def is_number(s: Any) -> bool:
    if s is not None:
        try:
            s = str(s)
        except ValueError:
            return False
        try:
            float(s)
            return True
        except ValueError:
            pass

        try:
            import unicodedata
            unicodedata.numeric(s)
            return True
        except (TypeError, ValueError):
            pass

    return False


def safe_html_code(string_html: str = "", is_all: bool = True) -> str:
    if string_html is None:
        return ""
    string_html = string_html if isinstance(string_html, str) else str(string_html)
    if is_all:
        return string_html.replace("<", "&lt;").replace(">", "&gt;").replace("%3C", "&lt;").replace("%3E", "&gt;")
    string_html = string_html.replace("%3C", "&lt;").replace("%3E", "&gt;")
    re_script_start = re.compile(r"<\s*script[^>]*>", re.IGNORECASE)
    re_script_end = re.compile(r"<\s*/\s*script\s*>", re.IGNORECASE)
    re_object_start = re.compile(r"<\s*object[^>]*>", re.IGNORECASE)
    re_object_end = re.compile(r"<\s*/\s*object\s*>", re.IGNORECASE)
    re_iframe_start = re.compile(r"<\s*iframe[^>]*>", re.IGNORECASE)
    re_iframe_end = re.compile(r"<\s*/\s*iframe\s*>", re.IGNORECASE)
    string_html = re_script_start.sub("", string_html)  # 直接去掉
    string_html = re_script_end.sub("", string_html)
    string_html = re_object_start.sub("", string_html)
    string_html = re_object_end.sub("", string_html)
    string_html = re_iframe_start.sub("", string_html)
    string_html = re_iframe_end.sub("", string_html)
    return string_html


def ant_path_matcher(ant_path: str, expected_path: str) -> bool:
    star = r"[^\/]+"
    double_star = r".*"
    slash = r"\/"
    question_mark = r"\w"
    dot = r"\."

    output = ant_path.replace(r"/", slash).replace(r".", dot)
    output = re.sub(r"(?<!\*)\*(?!\*)", star, output)
    output = output.replace(r"**", double_star)
    output = output.replace(r"?", question_mark)
    rc = re.compile(output, re.IGNORECASE)
    if rc.match(expected_path) is None:
        return False
    return True


def check_email(email: str) -> bool:
    re_str = r"^[a-zA-Z0-9_-]+(\.[a-zA-Z0-9_-]+){0,4}@[a-zA-Z0-9_-]+(\.[a-zA-Z0-9_-]+){0,4}$"
    if re.match(re_str, email) is None:
        return False
    return True


def get_args_from_dict(
        dt: Dict, ky: str, default: Optional[Any] = "", force_str: bool = False, check_type: bool = True,
) -> Optional[Any]:
    if default is None and force_str:
        default = ""
    word = default if ky not in dt else dt[ky]
    if is_number(word):
        if force_str:
            return str(word).strip()
        return word
    if isinstance(word, str):
        return str(word).strip()
    if force_str:
        return ""
    if word is None:
        return default
    # ! 判断是否跟默认值一致
    if default and check_type and not type(word) is type(default):
        return default  # 避免出现需要list但实际给了str的情况
    return word


def get_variable_from_request(
        key_name: str, default: Optional[Any] = "", method: str = "check", force_str: bool = False
) -> Optional[Any]:
    method = "check" if method is None or not isinstance(method, str) else str(method).strip().lower()
    if default is None and force_str:
        default = ""
    if method == "check":
        word = request.form.get(key_name, None)
        if word is None:
            word = request.args.get(key_name, None)
            if key_name in request.headers:
                word = request.headers[key_name]
        word = default if word is None else word
    elif method == "post":
        word = request.form.get(key_name, default)
    elif method == "get":
        word = request.args.get(key_name, default)
    elif method == "header":
        word = request.headers[key_name] if key_name in request.headers else default
    else:
        return default
    if word is None:
        return default
    if is_number(word):
        if force_str:
            return str(word).strip()
        return word
    return str(word).strip()


def get_local_now(hours: int = 0, minutes: int = 0) -> int:
    utc_dt = datetime.now(timezone.utc).replace(tzinfo=timezone.utc)
    d = utc_dt.astimezone(timezone(timedelta(hours=hours, minutes=minutes)))
    dt = int(time.mktime(d.timetuple()))
    return dt


def get_utc_now() -> int:
    dt = int(time.mktime(datetime.now(timezone.utc).timetuple()))
    return dt


def get_this_week_range(timestamp: int, hours: int = 0, minutes: int = 0) -> Tuple[int, int]:
    try:
        utc_time = datetime.fromtimestamp(timestamp)
        local_dt = utc_time + timedelta(hours=hours, minutes=minutes)
        monday = local_dt + relativedelta(weekday=MO(-1), hour=0, minute=0, second=0)
        sunday = local_dt + relativedelta(weekday=SU, hour=0, minute=0, second=0)
        return int(time.mktime(monday.timetuple())), int(time.mktime(sunday.timetuple()))
    except Exception as e:
        str(e)
        return 0, 0


def get_this_month_range(timestamp: int, hours: int = 0, minutes: int = 0) -> Tuple[int, int]:
    try:
        local_date: Optional[str] = timestamp2str(timestamp, "%Y-%m", hours=hours, minutes=minutes)
        if local_date is None:
            return 0, 0
        start_year, start_month, *_ = local_date.split("-")
        return get_month_range(start_year=int(start_year), start_month=int(start_month), long=0)
    except Exception as e:
        str(e)
        return 0, 0


def get_month_range(start_year: int, start_month: int, long: int) -> Tuple[int, int]:
    try:
        long = 1 if not is_number(long) else int(long)
        timestamp: int = str2timestamp(f"{start_year}-{start_month}-1", "%Y-%m-%d")
        utc_time = datetime.fromtimestamp(timestamp)
        if long >= 0:
            first_day = utc_time + relativedelta(day=1, hour=0, minute=0, second=0)
            last_day = utc_time + relativedelta(months=long, day=31, hour=0, minute=0, second=0)
        else:
            first_day = utc_time + relativedelta(months=long, day=1, hour=0, minute=0, second=0)
            last_day = utc_time + relativedelta(day=31, hour=0, minute=0, second=0)
        return int(time.mktime(first_day.timetuple())), int(time.mktime(last_day.timetuple()))
    except Exception as e:
        str(e)
        return 0, 0


def get_today(is_timestamp: bool = False, hours: int = 0, minutes: int = 0) -> Union[str, int]:
    dn: str = timestamp2str(get_utc_now(), "%Y-%m-%d", hours, minutes)
    if not is_timestamp:
        return dn
    timestamp: int = str2timestamp(dn, "%Y-%m-%d")
    return timestamp


def get_yesterday(is_timestamp: bool = False, hours: int = 0, minutes: int = 0) -> Union[str, int]:
    dt, _ = get_this_days_range(-1, hours, minutes)
    if not is_timestamp:
        return timestamp2str(dt, "%Y-%m-%d")
    return dt


def get_this_days_range(long: int, hours: int = 0, minutes: int = 0) -> Tuple[int, int]:
    long = 1 if not is_number(long) else int(long)
    long = 1 if long == 0 else long
    # 获取当前日期
    dn: str = timestamp2str(get_utc_now(), "%Y-%m-%d", hours, minutes)
    start_time: int = str2timestamp(dn, "%Y-%m-%d", hours, minutes)
    end_time: int
    if long < 0:
        # 如果是往前推的天数
        end_time = copy.deepcopy(start_time)
        end_time = end_time
        start_time = start_time + (3600 * 24 * long)
    else:
        end_time = start_time + (3600 * 24 * long)
    return start_time, end_time


def get_now_microtime(max_ms_lan: int = 6, hours: int = 0, minutes: int = 0) -> int:
    mt: Decimal = Decimal(microtime(get_as_float=True, max_ms_lan=max_ms_lan, hours=hours, minutes=minutes))
    ms: Decimal = Decimal(str(int(math.pow(10, max_ms_lan))))
    return int(mt * ms)


def microtime(get_as_float=False, max_ms_lan: int = 6, hours: int = 0, minutes: int = 0) -> str:
    utc_dt = datetime.now(timezone.utc).replace(tzinfo=timezone.utc)
    d = utc_dt.astimezone(timezone(timedelta(hours=hours, minutes=minutes)))
    t = time.mktime(d.timetuple())
    ms: float = d.microsecond / 1000000.
    if get_as_float:
        ms_txt = str(ms)
        if len(ms_txt) >= max_ms_lan + 2:
            ms_txt = ms_txt[:max_ms_lan + 2]
        else:
            max_loop: int = (max_ms_lan - len(ms_txt)) + 2
            for i in range(max_loop):
                ms_txt = f"{ms_txt}0"
        a = rounded(Decimal(ms_txt), max_ms_lan)
        b = Decimal(t)
        dt = a + b
        return str(dt)
    else:
        return "%.8f %d" % (ms, t)


def md5(txt: str) -> str:
    md = hashlib.md5()
    md.update(txt.encode("UTF-8"))
    return md.hexdigest()


def base64_encode(message: bytes, is_bytes: bool = True) -> Union[bytes, str]:
    crypto: bytes = base64.b64encode(message)
    if is_bytes:
        return crypto
    return crypto.decode("UTF-8")


def base64_decode(crypto: str, is_bytes: bool = True) -> Union[bytes, str]:
    missing_padding = 4 - len(crypto) % 4
    if missing_padding:
        crypto += "=" * missing_padding
    message: bytes = base64.b64decode(crypto)
    if is_bytes:
        return message
    return message.decode("UTF-8")


def base64_txt_encode(message: str) -> str:
    return str(base64_encode(message.encode("UTF-8"), is_bytes=False))


def base64_txt_decode(crypto: str) -> str:
    return str(base64_decode(crypto, is_bytes=False))


def rounded(numerical: Any, decimal: int = 2) -> Decimal:
    decimal = 0 if not is_number(decimal) or decimal <= 0 else decimal
    decimal_place: Decimal
    if not is_number(numerical):
        return Decimal("0")
    numerical_str: str = str(numerical)
    if decimal <= 0:
        decimal_place = Decimal(numerical_str).quantize(Decimal("1"), rounding="ROUND_HALF_UP")
    else:
        zero: str = "0" * (decimal - 1)
        decimal_place = Decimal(numerical_str).quantize(Decimal(f"0.{zero}1"), rounding="ROUND_HALF_UP")
    return decimal_place


def easy_encrypted(
        text: str, is_decode=True, key: Optional[str] = None, expiry: int = 0, console_log=None
) -> Optional[str]:
    try:
        if key is None or len(key) <= 0:
            plan_key: str = current_app.config["SECRET_KEY"]
        else:
            plan_key = key
        key_c_length: int = 4
        key = md5(plan_key)
        key_a: str = md5(key[0:16])
        key_b: str = md5(key[16:32])
        key_c: str
        if key_c_length <= 0:
            key_c = ""
        else:
            if is_decode:
                key_c = text[0:key_c_length]
            else:
                key_c = md5(microtime())[-key_c_length:]
        crypt_key: str = key_a + "" + md5(key_a + "" + key_c)
        key_length: int = len(crypt_key)
        new_data: bytes
        if is_decode:
            new_data = base64_decode(text[key_c_length:])
        else:
            expiry = expiry + get_utc_now() if expiry > 0 else 0
            expiry_str: str = "%010d" % expiry
            plan_text: str = expiry_str + "" + md5(text + "" + key_b)[0:16] + "" + text
            new_data = plan_text.encode("latin-1")
        string_length: int = len(new_data)
        decode_result: str = ""
        encode_result: bytes = b""
        box: List[int] = list(range(0, 256))
        rnd_key: List[int] = []
        for i in range(256):
            start: int = i % key_length
            end: int = start + 1
            rnd_key.append(ord(crypt_key[start:end]))
        j: int = 0
        for i in range(256):
            j = (j + box[i] + rnd_key[i]) % 256
            _tmp_box_: int = copy.deepcopy(box[i])
            box[i] = copy.deepcopy(box[j])
            box[j] = copy.deepcopy(_tmp_box_)
        a: int = 0
        j = 0
        for i in range(string_length):
            a = (a + 1) % 256
            j = (j + box[a]) % 256
            _tmp_box_: int = copy.deepcopy(box[a])
            box[a] = copy.deepcopy(box[j])
            box[j] = copy.deepcopy(_tmp_box_)
            od1: int = new_data[i]
            od2: int = box[(box[a] + box[j]) % 256]
            co: int = (od1 ^ od2)
            if is_decode:
                decode_result = decode_result + chr(co)
            else:
                encode_result = encode_result + bytes(chr(co), encoding="latin-1")
        if is_decode:
            t1: int = int(decode_result[0:10])
            t2: str = decode_result[10:26]
            t3: str = md5(decode_result[26:] + key_b)[0:16]
            if (t1 == 0 or t1 - get_utc_now() > 0) and t2 == t3:
                return decode_result[26:]
        else:
            b64code: bytes = base64_encode(encode_result)
            result: str = b64code.decode("latin-1")
            result = result.replace("=", "")
            result = key_c + "" + result
            test_password: Optional[str] = easy_encrypted(
                result, key=plan_key, expiry=expiry, console_log=console_log)
            if test_password == text:
                return result
    except Exception as e:
        if console_log:
            console_log.error(e)
    return None


def check_chinese_mobile(mobile: str) -> bool:
    try:
        return re.match(r"^1\d{10}$", mobile) is not None
    except Exception as e:
        str(e)
    return False


def str2int(text: str, default: Optional[int] = 0) -> Optional[int]:
    if not is_number(text):
        return default
    return int(Decimal(text))


def eat_html(html: str) -> str:
    dr = re.compile(r"<[^>]+>", re.S)
    dd = dr.sub("", html)
    return dd


def force_bytes(value: Union[str, bytes]) -> bytes:
    if isinstance(value, str):
        return value.encode("UTF-8")
    elif isinstance(value, bytes):
        return value
    else:
        raise TypeError("Expected a string value")


def is_pem_format(key: bytes) -> bool:
    _PEMS = {
        b"CERTIFICATE",
        b"TRUSTED CERTIFICATE",
        b"PRIVATE KEY",
        b"PUBLIC KEY",
        b"ENCRYPTED PRIVATE KEY",
        b"OPENSSH PRIVATE KEY",
        b"DSA PRIVATE KEY",
        b"RSA PRIVATE KEY",
        b"RSA PUBLIC KEY",
        b"EC PRIVATE KEY",
        b"DH PARAMETERS",
        b"NEW CERTIFICATE REQUEST",
        b"CERTIFICATE REQUEST",
        b"SSH2 PUBLIC KEY",
        b"SSH2 ENCRYPTED PRIVATE KEY",
        b"X509 CRL",
    }
    _PEM_RE = re.compile(
        b"----[- ]BEGIN ("
        + b"|".join(_PEMS)
        + b""")[- ]----\r?
.+?\r?
----[- ]END \\1[- ]----\r?\n?""",
        re.DOTALL,
    )
    return bool(_PEM_RE.search(key))


def is_ssh_key(key: bytes) -> bool:
    _SSH_KEY_FORMATS = [
        b"ssh-ed25519",
        b"ssh-rsa",
        b"ssh-dss",
        b"ecdsa-sha2-nistp256",
        b"ecdsa-sha2-nistp384",
        b"ecdsa-sha2-nistp521",
    ]
    _SSH_PUBKEY_RC = re.compile(rb"\A(\S+)[ \t]+(\S+)")
    _CERT_SUFFIX = b"-cert-v01@openssh.com"

    if any(string_value in key for string_value in _SSH_KEY_FORMATS):
        return True

    ssh_pubkey_match = _SSH_PUBKEY_RC.match(key)
    if ssh_pubkey_match:
        key_type = ssh_pubkey_match.group(1)
        if _CERT_SUFFIX == key_type[-len(_CERT_SUFFIX):]:
            return True

    return False


def base64url_encode(_input: bytes) -> bytes:
    return base64.urlsafe_b64encode(_input).replace(b"=", b"")


def base64url_decode(_input: Union[str, bytes]) -> bytes:
    if isinstance(_input, str):
        _input = _input.encode("ascii")

    rem = len(_input) % 4

    if rem > 0:
        _input += b"=" * (4 - rem)

    return base64.urlsafe_b64decode(_input)


def bytes_from_int(val: int) -> bytes:
    remaining = val
    byte_length = 0

    while remaining != 0:
        remaining >>= 8
        byte_length += 1

    return val.to_bytes(byte_length, "big", signed=False)


def to_base64url_uint(val: int) -> bytes:
    if val < 0:
        raise ValueError("Must be a positive integer")

    int_bytes = bytes_from_int(val)

    if len(int_bytes) == 0:
        int_bytes = b"\x00"

    return base64url_encode(int_bytes)


def from_base64url_uint(val: Union[str, bytes]) -> int:
    if isinstance(val, str):
        val = val.encode("ascii")

    data = base64url_decode(val)
    return int.from_bytes(data, byteorder="big")


def number_to_bytes(num: int, num_bytes: int) -> bytes:
    padded_hex = "%0*x" % (2 * num_bytes, num)
    return binascii.a2b_hex(padded_hex.encode("ascii"))


def bytes_to_number(_string: bytes) -> int:
    return int(binascii.b2a_hex(_string), 16)


def der_to_raw_signature(der_sig: bytes, curve: EllipticCurve) -> bytes:
    num_bits = curve.key_size
    num_bytes = (num_bits + 7) // 8

    r, s = decode_dss_signature(der_sig)

    return number_to_bytes(r, num_bytes) + number_to_bytes(s, num_bytes)


def raw_to_der_signature(raw_sig: bytes, curve: EllipticCurve) -> bytes:
    num_bits = curve.key_size
    num_bytes = (num_bits + 7) // 8

    if len(raw_sig) != 2 * num_bytes:
        raise ValueError("Invalid signature")

    r = bytes_to_number(raw_sig[:num_bytes])
    s = bytes_to_number(raw_sig[num_bytes:])

    return encode_dss_signature(r, s)


def chear_list(waiting: List, check_type: type = str) -> List:
    checked: List = []
    if waiting is None or not isinstance(waiting, list):
        return checked
    for _item_ in waiting:
        if _item_ is None or not isinstance(_item_, check_type):
            continue
        if check_type == str:
            _item_ = str(_item_).strip()
            if len(_item_) == 0:
                continue
        checked.append(_item_)
    return checked


def process_bar(num, total):
    rate = float(num) / total
    ratenum = int(100 * rate)
    r = "\r[{}{}]{}%".format("*" * ratenum, " " * (100 - ratenum), ratenum)
    sys.stdout.write(r)
    if num >= total:
        sys.stdout.write("\r\n")
    sys.stdout.flush()
