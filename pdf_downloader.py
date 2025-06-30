# pdf_downloader.py (新修复版 - 坚持使用API)

import os
import time
from typing import Tuple, Optional
import arxiv # 确保导入了 arxiv 库

class PdfDownloader:
    """
    Handles the downloading of a single PDF file for an arXiv paper
    using the official arxiv library API to avoid anti-bot measures.
    """
    def __init__(self, config):
        """
        Initializes the PdfDownloader with a configuration object.
        """
        self.config = config
        self.min_pdf_size_kb = self.config.MIN_PDF_SIZE_KB

    def download_single_paper(self, paper: 'arxiv.Result', download_dir: str) -> Tuple[Optional[str], Optional[str]]:
        """
        Downloads a single PDF using the paper's dedicated download_pdf() method,
        ensuring the ID is clean (version-free) before generating the filename.

        Args:
            paper (arxiv.Result): The paper object from the arxiv library.
            download_dir (str): The directory where the PDF should be saved.

        Returns:
            A tuple containing (filepath, filename). Both are None if download fails.
        """
        try:
            # --- 核心修复点 ---
            # 1. 获取带有版本号的完整ID，用于错误日志
            full_id_with_version = paper.get_short_id()
            
            # 2. 清理ID，移除版本号。这是最关键的一步。
            # '2506.10323v2' -> '2506.10323'
            clean_id_no_version = full_id_with_version.split('v')[0]
            
            # 3. 根据清理后的ID构建我们期望的文件名。
            # 这既是我们要传递给API的文件名，也是我们之后要用来查找文件的依据。
            filename = f"{clean_id_no_version.replace('/', '_')}.pdf"
            filepath = os.path.join(download_dir, filename)

            # 礼貌性地暂停一下
            time.sleep(1.5)

            # --- 4. 调用官方API进行下载 ---
            # 我们明确地把清理过的、我们期望的 `filename` 传递给它。
            # 这能避免API内部可能存在的对带版本号ID的错误处理。
            paper.download_pdf(dirpath=download_dir, filename=filename)

            # 5. 验证下载的文件
            if os.path.exists(filepath) and os.path.getsize(filepath) >= self.min_pdf_size_kb * 1024:
                print(f"  -> Successfully downloaded: {filename}")
                return filepath, filename
            else:
                print(f"  -> [Warning] Download failed or file size is too small for {filename}.")
                if os.path.exists(filepath):
                    os.remove(filepath) # 清理无效文件
                return None, None
                
        except Exception as e:
            # 专门处理下载错误，提供更详细的上下文
            print(f"  -> [Error] An error occurred during download for paper ID '{full_id_with_version}': {e}")
            return None, None