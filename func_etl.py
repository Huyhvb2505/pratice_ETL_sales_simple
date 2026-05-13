import csv
import logging
import re
import json
from datetime import datetime
from pathlib import Path


logger = logging.getLogger(__name__)

"""func read file"""
def read_File(path_file):
    path_file = Path(path_file)

# Check path file nếu ko tồn tại raise ra lỗi
    if not path_file.is_file():
        raise FileNotFoundError(f"File not found: {path_file}")
    
# open file để xử lý
    logger.info(f"PIPELINE: Start reading {path_file}")

    with open(path_file, 'r', encoding='utf-8') as f:
        data = csv.DictReader(f)
        read = list(data)

    logger.info(f"Read {len(read)} records from {path_file}")
    return read
"""func check validate data"""
def validate_data(data,row_number):
    """Validate một dòng dữ liệu. Trả về (bool, list_errors)."""
    errors = []
    email_pattern = r'^[\w.-]+@[\w.-]+\.[a-zA-Z]{2,}$'

    # check quantity
    try:
       qty = int(data.get('quantity',""))
       if qty <= 0:
            errors.append(f"Invalid quantity, must > 0: {qty}")
    except ValueError:
         errors.append(f"quantity is not an integer: {data.get('quantity')}")

    # check unit_price
    try:
        price = float(data.get('unit_price',""))
        if price <= 0:
            errors.append(f"Invalid unit_price, must > 0: {price}")
    except ValueError:
        errors.append(f"unit_price is not a number: {data.get('unit_price')}")

    # check email

    email = data.get('customer_email','').strip()
    if not re.match(email_pattern, email):
        errors.append(f"Invalid email format: {email}")

    if errors:
        logger.warning(f"Row number {row_number}: {'; '.join(errors)}")

    return len(errors) == 0, errors

"""clean data"""
def clean_Data(data):
    """Transform dữ liệu theo yêu cầu."""
    """
    Làm sạch và chuẩn hóa một dòng dữ liệu.
    Giả sử dòng đã qua validation.
    """
    

    return {
        "date": datetime.strptime(data.get('date'),"%Y-%m-%d").date(),
        "product": data.get("product", "Unknown").strip().title() or "Unknown",
        "category": data.get("category", "Unknown").strip() or "Unknown",    
        "quantity": int(data.get("unit_quantity", 0)),
        "unit_price": float(data.get("unit_price", 0.0)),
        "total_amount": int(data["quantity"]) * float(data["unit_price"]),
        "customer_email": data.get("customer_email", "").strip().lower(),
    }

"""transform data"""
def transform_Data(raw_Data):
    """
    Chạy toàn bộ validate + transform.
    Trả về (clean_data, error_records).
    """
    clean_data = []
    error_records = []

    for i,data in enumerate(raw_Data, start = 2):
        is_valid, errors = validate_data(data,i)
        if is_valid:
            clean_data.append(clean_Data(data))
        else:
            error_records.append({"row_number": i,"data": data, "errors": errors})

    logger.info(f"Valid counts: {len(clean_data)}, Error counts: {len(error_records)}")
    return clean_data, error_records

def make_report(clean_Data):
    """Tổng hợp dữ liệu thành báo cáo."""

    if not clean_Data:
        return {}
    
    # tổng doanh thu
    total_Revenue = sum(d["total_amount"] for d in clean_Data)

    # revenue by cate
    rev_by_cate = {}
    for d in clean_Data:
        cate = d["category"]
        rev_by_cate[cate] = rev_by_cate.get(cate, 0) + d["total_amount"]

    # doanh thu theo ngay
    rev_by_day = {}
    for d in clean_Data:
        value_date = str(d["date"])
        rev_by_day[value_date] = rev_by_day.get(value_date, 0) + d["total_amount"]

    # Sản phẩm bán nhiều nhất

    rev_by_pro = {}
    for d in clean_Data:
        pro = d["product"]
        rev_by_pro[pro] = rev_by_pro.get(pro, 0) + d["total_amount"]

    top_products = sorted(rev_by_pro.items(), key = lambda x: x[1],reverse=True)

    reports = {
        "total_orders": len(clean_Data),
        "total_revenue": total_Revenue,
        "avg_amount_per_order": total_Revenue / len(clean_Data),
        "revenue_by_category": rev_by_cate,
        "revenue_by_day": rev_by_day,
        "top_products": top_products[:2]
    }

    return reports
    
def save_csv(data,path_file):
    """Write data in csv file"""
    if not data:
        logger.warning(f"No data to save to CSV")
        return 
    
    # csv chi save text or number ma date la datetime type neen cen convert ve string
    date_str = [{**i,"date": str(i["date"])} for i in data]

    Path(path_file).parent.mkdir(parents=True, exist_ok=True)

    with open(path_file, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=date_str[0].keys())
        writer.writeheader()
        writer.writerows(date_str)

    logger.info(f"Wrote {len(date_str)} records to {path_file}")

def save_json(data,path_file):
    """write report to json file"""
    Path(path_file).parent.mkdir(parents=True, exist_ok=True)

    with open(path_file, "w", newline="", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

    logger.info(f"Save data to {path_file}")    


def print_data(data):
    """In báo cáo ra console theo format đẹp."""
    print("\n" + "="*50)
    print("   BÁO CÁO DOANH THU")
    print("="*50)
    print(f"Tổng đơn hàng:   {data['total_orders']:>10,}")
    print(f"Tổng doanh thu:  {data['total_revenue']:>10,.0f} VNĐ")
    print(f"Trung bình/đơn:  {data['avg_amount_per_order']:>10,.0f} VNĐ")
    
    
    print("\nDoanh thu theo danh mục:")
    for cat, dt in sorted(data["revenue_by_category"].items()):
        print(f"  {cat:<20} {dt:>12,.0f} VNĐ")

    print("\nTop sản phẩm bán chạy:")
    for rank, (sp, sl) in enumerate(data["top_products"], 1):
        print(f"  {rank}. {sp:<20} {sl:>5} units")

    print("="*50)
