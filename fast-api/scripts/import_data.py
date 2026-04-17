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
                
                // ĐÃ FIX: Cách ly Khối kiến thức và Loại học phần theo từng Ngành
                MERGE (kkt:KhoiKienThuc {id: $ma_nganh + '_' + $khoi_kien_thuc})
                SET kkt.ten_khoi = $khoi_kien_thuc
                
                MERGE (lhp:LoaiHocPhan {id: $ma_nganh + '_' + $loai_hoc_phan})
                SET lhp.ten_loai = $loai_hoc_phan
                
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
        {"file": "data/cntt_ekg.xlsx", "ma_nganh": "CNTT", "ten_nganh": "Công nghệ thông tin"},
        {"file": "data/QuanlyGiaoDuc_ekg.xlsx", "ma_nganh": "QLGD", "ten_nganh": "Quản lý giáo dục"},
        {"file": "data/congnghekythuatdientu_ekg.xlsx", "ma_nganh": "CNKTDT", "ten_nganh": "Công nghệ Kỹ thuật Điện tử"},
        {"file": "data/congnghekythuatdientuvienthong_ekg.xlsx", "ma_nganh": "CNKTDTVT", "ten_nganh": "Công nghệ Kỹ thuật Điện tử Viễn thông"},
        {"file": "data/congnghekythuatmoitruong_ekg.xlsx", "ma_nganh": "CNKTMT", "ten_nganh": "Công nghệ Kỹ thuật Môi trường"},
        {"file": "data/dialyhoc_ekg.xlsx", "ma_nganh": "DLH", "ten_nganh": "Địa lý học"},
        {"file": "data/dulich_ekg.xlsx", "ma_nganh": "DL", "ten_nganh": "Du lịch"},
        {"file": "data/giaoducchinhtri_ekg.xlsx", "ma_nganh": "GDCT", "ten_nganh": "Giáo dục chính trị"},
        {"file": "data/giaoducmamnon_ekg.xlsx", "ma_nganh": "GDMN", "ten_nganh": "Giao dục mầm non"},
        {"file": "data/giaoductieuhoc_ekg.xlsx", "ma_nganh": "GDTH", "ten_nganh": "Giáo dục tiểu học"},
        {"file": "data/ketoan_ekg.xlsx", "ma_nganh": "KET", "ten_nganh": "Kế toán"},
        {"file": "data/luat_ekg.xlsx", "ma_nganh": "LUAT", "ten_nganh": "Luật"},
        {"file": "data/quantrinhahangvadichvuanuong_ekg.xlsx", "ma_nganh": "QTNHDVAU", "ten_nganh": "Quản trị nhà hàng và dịch vụ ăn uống"},
        {"file": "data/khoahocdulieu_ekg.xlsx", "ma_nganh": "KHDL", "ten_nganh": "Khoa học dữ liệu"},
        {"file": "data/khoahocmoitruong_ekg.xlsx", "ma_nganh": "KHMT", "ten_nganh": "Khoa học môi trường"},
        {"file": "data/kiemtoan_ekg.xlsx", "ma_nganh": "KIT", "ten_nganh": "Kiểm toán"},
        {"file": "data/kinhdoanhquocte_ekg.xlsx", "ma_nganh": "KDQT", "ten_nganh": "Kinh doanh quốc tế"},
        {"file": "data/kythuatdien.xlsx", "ma_nganh": "KTD", "ten_nganh": "Kỹ thuật điện"},
        {"file": "data/kythuatdientuvienthong(thietkevimach).xlsx", "ma_nganh": "TKVM", "ten_nganh": "Kỹ thuật điện tử viễn thông (thiết kế vi mạch)"},
        {"file": "data/kythuatphanmem_ekg.xlsx", "ma_nganh": "KTPM", "ten_nganh": "Kỹ thuật phần mềm"},
        {"file": "data/lichsuhoc_ekg.xlsx", "ma_nganh": "LSH", "ten_nganh": "Lịch sử học"},
        {"file": "data/ngonnguanh_ekg.xlsx", "ma_nganh": "NNA", "ten_nganh": "Ngôn ngữ Anh"},
        {"file": "data/quantrivanphong_ekg.xlsx", "ma_nganh": "QTVP", "ten_nganh": "Quản trị văn phòng"},
        {"file": "data/quantrikinhdoanh_ekg.xlsx", "ma_nganh": "QTKD", "ten_nganh": "Quản trị kinh doanh"},
        {"file": "data/quoctehoc_ekg.xlsx", "ma_nganh": "QTH", "ten_nganh": "Quốc tế học"},
        {"file": "data/suphamamnhac_ekg.xlsx", "ma_nganh": "SPAN", "ten_nganh": "Sư phạm âm nhạc"},
        {"file": "data/suphamkhoahoctunhien(giaovienTHCS)_ekg.xlsx", "ma_nganh": "KHTNTHCS", "ten_nganh": "Sư phạm khoa học tự nhiên (giáo viên THCS)"},
        {"file": "data/suphamlichsu_ekg.xlsx", "ma_nganh": "SPLS", "ten_nganh": "Sư phạm lịch sử"},
        {"file": "data/suphamlichsudialy(giaovienTHCS)_ekg.xlsx", "ma_nganh": "DLTHCS", "ten_nganh": "Sư phạm lịch sử địa lý (giáo viên THCS)"},
        {"file": "data/suphammythuat_ekg.xlsx", "ma_nganh": "SPMT", "ten_nganh": "Sư phạm mỹ thuật"},
        {"file": "data/suphamnguvan_ekg.xlsx", "ma_nganh": "SPNV", "ten_nganh": "Sư phạm ngữ văn"},
        {"file": "data/suphamsinhhoc_ekg.xlsx", "ma_nganh": "SPSH", "ten_nganh": "Sư phạm sinh học"},
        {"file": "data/suphamtienganh_ekg.xlsx", "ma_nganh": "SPTA", "ten_nganh": "Sư phạm tiếng Anh"},
        {"file": "data/suphamtoanhoc_ekg.xlsx", "ma_nganh": "SPTH", "ten_nganh": "Sư phạm toán học"},
        {"file": "data/suphamvatly_ekg.xlsx", "ma_nganh": "SPVL", "ten_nganh": "Sư phạm vật lý"},
        {"file": "data/taichinhnganhang_ekg.xlsx", "ma_nganh": "TCNH", "ten_nganh": "Tài chính ngân hàng"},
        {"file": "data/tamlyhoc_ekg.xlsx", "ma_nganh": "TLH", "ten_nganh": "Tâm lý học"},
        {"file": "data/thongtinthuvien_ekg.xlsx", "ma_nganh": "TTTV", "ten_nganh": "Thông tin thư viện"},
        {"file": "data/toanungdung_ekg.xlsx", "ma_nganh": "TUD", "ten_nganh": "Toán ứng dụng"},
        {"file": "data/trituenhantao_ekg.xlsx", "ma_nganh": "TTNT", "ten_nganh": "Trí tuệ nhân tạo"},
        {"file": "data/vietnamhoc_ekg.xlsx", "ma_nganh": "VNH", "ten_nganh": "Việt Nam học"}
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