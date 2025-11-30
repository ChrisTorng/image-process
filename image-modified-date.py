import os
import shutil
import argparse
from pathlib import Path
from datetime import datetime

def set_file_times(filepath, timestamp):
    """設定檔案的建立時間、存取時間和修改時間為指定的時間戳"""
    # 將 datetime 轉換為時間戳（秒）
    time_sec = timestamp.timestamp()
    
    # 設定存取時間和修改時間
    os.utime(filepath, (time_sec, time_sec))
    
    # 在 Windows 上設定建立時間
    if os.name == 'nt':
        import pywintypes
        import win32file
        import win32con
        
        # 轉換為 Windows 時間格式
        win_time = pywintypes.Time(timestamp)
        
        # 開啟檔案並設定建立時間
        handle = win32file.CreateFile(
            filepath,
            win32con.GENERIC_WRITE,
            win32con.FILE_SHARE_READ | win32con.FILE_SHARE_WRITE,
            None,
            win32con.OPEN_EXISTING,
            win32con.FILE_ATTRIBUTE_NORMAL,
            None
        )
        win32file.SetFileTime(handle, win_time, win_time, win_time)
        handle.close()

def copy_and_update_timestamps(src_folder, dest_folder):
    """複製檔案並更新時間戳"""
    src_path = Path(src_folder)
    dest_path = Path(dest_folder)
    
    if not src_path.exists():
        print(f"錯誤：來源資料夾不存在: {src_folder}")
        return
    
    # 建立目標資料夾（如果不存在）
    dest_path.mkdir(parents=True, exist_ok=True)
    
    # 遍歷來源資料夾中的所有檔案
    file_count = 0
    for src_file in src_path.rglob('*'):
        if src_file.is_file():
            # 計算相對路徑
            rel_path = src_file.relative_to(src_path)
            dest_file = dest_path / rel_path
            
            # 建立目標子資料夾（如果需要）
            dest_file.parent.mkdir(parents=True, exist_ok=True)
            
            # 複製檔案
            shutil.copy2(src_file, dest_file)
            
            # 取得原始檔案的修改時間
            modified_time = datetime.fromtimestamp(os.path.getmtime(src_file))
            
            # 設定目標檔案的所有時間戳為修改時間
            set_file_times(str(dest_file), modified_time)
            
            file_count += 1
            print(f"已處理: {rel_path}")
    
    print(f"\n完成！總共處理了 {file_count} 個檔案。")

def main():
    parser = argparse.ArgumentParser(
        description='複製檔案並將建立/存取時間設定為修改時間'
    )
    parser.add_argument('source', help='來源資料夾路徑')
    parser.add_argument('destination', help='目標資料夾路徑')
    
    args = parser.parse_args()
    
    copy_and_update_timestamps(args.source, args.destination)

if __name__ == '__main__':
    main()
