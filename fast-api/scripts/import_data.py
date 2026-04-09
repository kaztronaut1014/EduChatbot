import pandas as pd
from neo4j import GraphDatabase
from dotenv import load_dotenv
import os
import re

load_dotenv()

# ================= CẤU HÌNH NEO4J =================
URI = os.getenv("NEO4J_URI")
USER = os.getenv("NEO4J_USERNAME")
PASSWORD = os.getenv("NEO4J_PASSWORD")

def xu_ly_chuoi_phuc_tap(chuoi_goc):
    if pd.isna(chuoi_goc):
        return []
        
    chuoi = str(chuoi_goc)
    
    # BƯỚC 1: Cạo rác (Xóa ngoặc vuông, nháy đơn, nháy kép, xuống dòng)
    chuoi = re.sub(r"[\[\]'\"\n]", " ", chuoi).strip()
    
    if not chuoi or chuoi.lower() in ["none", "nan", "không", "0", ""]:
        return []
        
    # BƯỚC 2: Băm chuỗi (Bằng phẩy, chấm phẩy, dấu và...)
    mang_da_cat = re.split(r'[,;；，&]|\s+và\s+', chuoi)
    
    # BƯỚC 3: Rửa sạch từng phần tử
    ket_qua = [item.strip() for item in mang_da_cat if item.strip()]
    return ket_qua

def import_excel_to_neo4j(file_path, ma_nganh, ten_nganh):
    print(f"\nĐang đọc file Excel: {file_path}...")
    try:
        df = pd.read_excel(file_path)
    except Exception as e:
        print(f"Lỗi không đọc được file: {e}")
        return

    # Gọt sạch sẽ khoảng trắng thừa ở đầu/cuối tên cột
    df.columns = df.columns.str.strip()

    # Bộ từ điển
    dict_doi_ten = {
        "Số TC": "TinChi", "Số tín chỉ": "TinChi", "Tín chỉ": "TinChi", "số tc": "TinChi", "TC": "TinChi",
        "Mã HP": "MaHP", "mã hp": "MaHP", "Mã học phần": "MaHP",
        "Tên môn": "TenMon", "Tên MH": "TenMon", "Tên học phần": "TenMon",
        "Học kỳ": "HocKy", "Hoc ky": "HocKy", "HK": "HocKy", "Học kì": "HocKy", "Học kỳ dự kiến": "HocKy", 
        "Học kỳ đề xuất": "HocKy", "Học kỳ thực hiện": "HocKy",
        "Khối kiến thức": "KhoiKienThuc", "Khối KT": "KhoiKienThuc", 
        "Loại học phần": "LoaiHocPhan", "Loại môn": "LoaiHocPhan", "Bắt buộc/Tự chọn": "LoaiHocPhan", "Loại": "LoaiHocPhan",
        "Mã HP học trước": "MaHPTruoc", "Môn học trước": "MaHPTruoc", "Môn tiên quyết": "MaHPTruoc"
    }
    df.rename(columns=dict_doi_ten, inplace=True)

    driver = GraphDatabase.driver(URI, auth=(USER, PASSWORD))
    print("Đang thiết kế đồ thị... Vui lòng đợi!")
    
    with driver.session() as session:
        count = 0
        for index, row in df.iterrows():
            try:
                # Bỏ qua nếu Mã Học Phần trống
                if pd.isna(row.get('MaHP')) or str(row.get('MaHP')).strip() == "": 
                    continue
                
                ma_hp = str(row['MaHP']).strip()
                ten_mon = str(row.get('TenMon', 'Chưa có tên')).strip()
                tin_chi_raw = row.get('TinChi', 0) 
                tin_chi = int(tin_chi_raw) if pd.notna(tin_chi_raw) else 0
                
                khoi_kien_thuc_raw = row.get('KhoiKienThuc', 'Không xác định')
                khoi_kien_thuc = str(khoi_kien_thuc_raw).strip() if pd.notna(khoi_kien_thuc_raw) and str(khoi_kien_thuc_raw).strip() != '' else "Không xác định"
                
                loai_hoc_phan_raw = row.get('LoaiHocPhan', 'Không xác định')
                loai_hoc_phan = str(loai_hoc_phan_raw).strip() if pd.notna(loai_hoc_phan_raw) and str(loai_hoc_phan_raw).strip() != '' else "Không xác định"

                # ==========================================
                # 1. TẠO NODE MÔN HỌC & CÁC THUỘC TÍNH CHUNG
                # ==========================================
                cypher_core = """
                MERGE (n:Nganh {ma_nganh: $ma_nganh})
                SET n.ten_nganh = $ten_nganh
                
                MERGE (tc:TinChi {so_luong: $tin_chi})
                MERGE (kkt:KhoiKienThuc {ten_khoi: $khoi_kien_thuc})
                MERGE (lhp:LoaiHocPhan {ten_loai: $loai_hoc_phan})
                
                // ĐÃ FIX: MERGE bằng mã HP để chống trùng
                MERGE (m:MonHoc {ma_hp: $ma_hp})
                SET m.ten_mon = $ten_mon
                
                MERGE (m)-[:CO_SO_TIN_CHI]->(tc)
                MERGE (m)-[:THUOC_KHOI_KIEN_THUC]->(kkt)
                MERGE (m)-[:THUOC_LOAI_HOC_PHAN]->(lhp)
                MERGE (m)-[:THUOC_CHUONG_TRINH]->(n)
                """
                session.run(cypher_core, 
                            ma_nganh=ma_nganh, ten_nganh=ten_nganh, 
                            ma_hp=ma_hp, ten_mon=ten_mon, tin_chi=tin_chi,
                            khoi_kien_thuc=khoi_kien_thuc, loai_hoc_phan=loai_hoc_phan)
                
                # ==========================================
                # 2. XỬ LÝ HỌC KỲ (Tách chuỗi)
                # ==========================================
                danh_sach_hoc_ky = xu_ly_chuoi_phuc_tap(row.get('HocKy'))
                if not danh_sach_hoc_ky: 
                    danh_sach_hoc_ky = ['0']

                # print(f"👉 Môn {ma_hp} - Học kỳ: {danh_sach_hoc_ky}")
                for hk in danh_sach_hoc_ky:
                    cypher_hk = """
                    MATCH (n:Nganh {ma_nganh: $ma_nganh})
                    MATCH (m:MonHoc {ma_hp: $ma_hp})
                    
                    MERGE (h:HocKy {id: $ma_nganh + '_' + $hk})
                    SET h.ten_hoc_ky = $hk
                    
                    // ĐÃ FIX: Nối Học kỳ vào Ngành, Nối Môn học vào Học kỳ
                    MERGE (h)-[:THUOC_CHUONG_TRINH]->(n) 
                    MERGE (m)-[:THUOC_HOC_KY]->(h) 
                    """
                    session.run(cypher_hk, ma_nganh=ma_nganh, ma_hp=ma_hp, hk=hk)

                # ==========================================
                # 3. XỬ LÝ MÔN TIÊN QUYẾT (Tách chuỗi)
                # ==========================================
                danh_sach_hp_truoc = xu_ly_chuoi_phuc_tap(row.get('MaHPTruoc'))
                for hp_truoc in danh_sach_hp_truoc:
                    cypher_pre = """
                    MATCH (m:MonHoc {ma_hp: $ma_hp})
                    MERGE (pre:MonHoc {ma_hp: $hp_truoc}) 
                    MERGE (m)-[:YEU_CAU_MON_TRUOC]->(pre)
                    """
                    session.run(cypher_pre, ma_hp=ma_hp, hp_truoc=hp_truoc)

                count += 1

            except Exception as e:
                print(f"❌ Lỗi ở dòng {index} (Môn: {row.get('MaHP', 'Unknown')}): {e}")
    driver.close()
    print(f"🎉 Đã nhập thành công {count} môn học!")

if __name__ == "__main__":
    danh_sach_nganh = [
        {"file": "data/CongNgheThongTin_ekg.xlsx", "ma_nganh": "CNTT", "ten_nganh": "Công nghệ thông tin"},
        {"file": "data/QuanlyGiaoDuc_ekg.xlsx", "ma_nganh": "QLGD", "ten_nganh": "Quản lý giáo dục"},
        {"file": "data/CongNgheKyThuatDienTu_ekg.xlsx", "ma_nganh": "CNKTDT", "ten_nganh": "Công nghệ Kỹ thuật Điện tử"}
    ]
    
    driver = GraphDatabase.driver(URI, auth=(USER, PASSWORD))
    with driver.session() as session:
        session.run("MATCH (n) DETACH DELETE n")
        print("Đã dọn dẹp sạch sẽ Neo4j!")
    driver.close()

    for nganh in danh_sach_nganh:
        print(f"--- Đang nạp dữ liệu ngành: {nganh['ten_nganh']} ---")
        import_excel_to_neo4j(nganh['file'], nganh['ma_nganh'], nganh['ten_nganh'])
        
    print("\nĐã nạp xong toàn bộ EKG!")