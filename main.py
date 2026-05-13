from datetime import datetime
import logging
from func_etl import read_File, transform_Data, make_report, save_csv, save_json, print_data,clean_Data

# config logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler("pipeline.log", encoding='utf-8'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

def main():
    start_time = datetime.now()
    logger.info("=== PIPELINE BẮT ĐẦU ===")

    try:
        # Đường dẫn
        input_path  = "data/input/raw_sale.csv"
        output_csv  = "data/output/sales_clean.csv"
        output_json = "data/output/report.json"

        # 1. Đọc
        raw_data = read_File(input_path)

        # 2. Validate + Transform
        clean_data, errors = transform_Data(raw_data)

        # 3. Aggregate
        report_data = make_report(clean_data)

        # 4. Ghi kết quả
        save_csv(clean_data, output_csv)
        save_json(report_data, output_json)

        # 5. In báo cáo
        print_data(report_data)

        elapsed = (datetime.now() - start_time).total_seconds()
        logger.info(f"=== PIPELINE HOÀN THÀNH ({elapsed:.2f}s) ===")

    except FileNotFoundError as e:
        logger.error(f"File not found: {e}")
        raise
    except Exception as e:
        logger.critical(f"Unexpected error: {e}", exc_info=True)
        raise

if __name__ == "__main__":
    main()
