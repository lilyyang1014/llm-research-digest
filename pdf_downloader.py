# pdf_downloader.py (最终官方API+智能延迟版)

import os
import time
import random  # 导入 random 库
from typing import Tuple, Optional
import arxiv  # 严格使用官方库

class PdfDownloader:
    """
    使用官方 arxiv.download_pdf() 方法，但加入了智能的随机延迟，
    以尊重服务器的速率限制，从而最大化下载成功率。
    """
    def __init__(self, config):
        self.config = config
        self.min_pdf_size_kb = self.config.MIN_PDF_SIZE_KB

    def download_single_paper(self, paper: 'arxiv.Result', download_dir: str) -> Tuple[Optional[str], Optional[str]]:
        try:
            full_id_with_version = paper.get_short_id()
            clean_id_no_version = full_id_with_version.split('v')[0]
            filename = f"{clean_id_no_version.replace('/', '_')}.pdf"
            filepath = os.path.join(download_dir, filename)
        except Exception as e:
            print(f"  -> [Error] Could not process paper metadata for download: {e}")
            return None, None

        if os.path.exists(filepath):
            try:
                if os.path.getsize(filepath) >= self.min_pdf_size_kb * 1024:
                    print(f"  -> File '{filename}' already exists and is valid. Skipping download.")
                    return filepath, filename
            except OSError:
                pass

        # --- 核心解决方案：引入更长且随机的延迟 ---
        # 生成一个 5 到 12 秒之间的随机延迟，模拟人类的思考和点击间隔
        delay = random.uniform(5, 12)
        print(f"  -> Pausing for {delay:.1f} seconds to respect API rate limits...")
        time.sleep(delay)
        # --- 结束修改 ---

        print(f"  -> Downloading '{filename}' using official API...")
        try:
            # 依然严格使用你指定的官方方法
            paper.download_pdf(dirpath=download_dir, filename=filename)

            # 下载后验证逻辑... (保持不变)
            if not os.path.exists(filepath):
                print(f"  -> [Error] Download call completed, but file '{filename}' was not created.")
                return None, None
            
            file_size_kb = os.path.getsize(filepath) / 1024
            if file_size_kb >= self.min_pdf_size_kb:
                print(f"  -> Success. Downloaded '{filename}' ({file_size_kb:.1f} KB).")
                return filepath, filename
            else:
                print(f"  -> [Error] Downloaded file '{filename}' is too small ({file_size_kb:.1f} KB). Deleting invalid file.")
                os.remove(filepath)
                return None, None

        except Exception as e:
            print(f"  -> [Error] An error occurred during official API download for '{filename}': {e}")
            if os.path.exists(filepath):
                try:
                    os.remove(filepath)
                except OSError:
                    pass
            return None, None