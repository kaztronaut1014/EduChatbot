import chromadb
import os

# Tạo thư mục chứa database vector nếu chưa có
os.makedirs("data/chromadb_data", exist_ok=True)

# Khởi tạo ChromaDB
client = chromadb.PersistentClient(path="data/chromadb_data")
collection = client.get_or_create_collection(name="cypher_examples")

# Danh sách các ví dụ mẫu (bạn có thể thêm 50-100 câu vào đây sau)
examples = [
        {
            "id": "ex1",
            "question": "Trường mình đào tạo những ngành nào? / Có bao nhiêu ngành học?",
            "cypher": "MATCH (n:Nganh) RETURN n.ten_nganh"
        },
        {
            "id": "ex2",
            "question": "Ngành Công nghệ thông tin học những môn gì? / Cho tôi danh sách môn học của ngành CNTT.",
            "cypher": "MATCH (m:MonHoc)-[:THUOC_CHUONG_TRINH]->(n:Nganh) WHERE toLower(n.ten_nganh) CONTAINS 'công nghệ thông tin' RETURN m.ten_mon"
        },
        {
            "id": "ex3",
            "question": "Ngành Quản lý giáo dục (hoặc ngành bất kỳ) có tổng cộng bao nhiêu tín chỉ? Gồm những môn nào?",
            "cypher": "MATCH (m:MonHoc)-[:THUOC_CHUONG_TRINH]->(n:Nganh) WHERE toLower(n.ten_nganh) CONTAINS 'quản lý giáo dục' OPTIONAL MATCH (m)-[:CO_SO_TIN_CHI]->(tc:TinChi) OPTIONAL MATCH (m)-[:THUOC_KHOI_KIEN_THUC]->(k:KhoiKienThuc) WHERE k.id STARTS WITH n.ma_nganh + '_' RETURN n.ten_nganh, m.ten_mon, tc.so_luong, k.ten_khoi"
        },
        {
            "id": "ex4",
            "question": "Môn Cơ sở dữ liệu cần học môn nào trước? / Môn tiên quyết của CSDL là gì?",
            "cypher": "MATCH (m:MonHoc {{ten_mon: 'Cơ sở dữ liệu'}})-[:YEU_CAU_MON_TRUOC]->(pre:MonHoc) RETURN pre.ten_mon"
        },
        {
            "id": "ex5",
            "question": "Môn Mạng máy tính bao nhiêu tín chỉ?",
            "cypher": "MATCH (m:MonHoc {{ten_mon: 'Mạng máy tính'}})-[:CO_SO_TIN_CHI]->(tc:TinChi) RETURN tc.so_luong"
        },
        {
            "id": "ex6",
            "question": "Học kỳ 1 ngành Quản lý giáo dục có tổng cộng bao nhiêu tín chỉ? Học kỳ này học những môn gì?",
            "cypher": "MATCH (m:MonHoc)-[:THUOC_HOC_KY]->(h:HocKy {{ten_hoc_ky: '1'}})-[:THUOC_CHUONG_TRINH]->(n:Nganh) WHERE toLower(n.ten_nganh) CONTAINS toLower('quản lý giáo dục') OPTIONAL MATCH (m)-[:CO_SO_TIN_CHI]->(tc:TinChi) OPTIONAL MATCH (m)-[:THUOC_KHOI_KIEN_THUC]->(k:KhoiKienThuc) WHERE k.id STARTS WITH n.ma_nganh + '_' RETURN n.ten_nganh, h.ten_hoc_ky, m.ten_mon, tc.so_luong, k.ten_khoi"
        },
        {
            "id": "ex7",
            "question": "Học kỳ 3 ngành Công nghệ thông tin có những môn tự chọn nào?",
            "cypher": "MATCH (m:MonHoc)-[:THUOC_HOC_KY]->(h:HocKy {{ten_hoc_ky: '3'}})-[:THUOC_CHUONG_TRINH]->(n:Nganh) WHERE toLower(n.ten_nganh) CONTAINS 'công nghệ thông tin' MATCH (m)-[:THUOC_LOAI_HOC_PHAN]->(l:LoaiHocPhan {{ten_loai: 'Tự chọn'}}) WHERE l.id STARTS WITH n.ma_nganh + '_' RETURN m.ten_mon"
        },
        {
            "id": "ex8",
            "question": "Khối kiến thức chuyên ngành của ngành Quản trị kinh doanh gồm những môn nào?",
            "cypher": "MATCH (m:MonHoc)-[:THUOC_CHUONG_TRINH]->(n:Nganh) WHERE toLower(n.ten_nganh) CONTAINS 'quản trị kinh doanh' MATCH (m)-[:THUOC_KHOI_KIEN_THUC]->(k:KhoiKienThuc {{ten_khoi: 'Kiến thức chuyên ngành'}}) WHERE k.id STARTS WITH n.ma_nganh + '_' RETURN m.ten_mon"
        },
        {
            "id": "ex9",
            "question": "Danh sách môn học theo khối kiến thức của ngành Kỹ thuật phần mềm?",
            "cypher": "MATCH (m:MonHoc)-[:THUOC_CHUONG_TRINH]->(n:Nganh) WHERE toLower(n.ten_nganh) CONTAINS 'kỹ thuật phần mềm' MATCH (m)-[:THUOC_KHOI_KIEN_THUC]->(k:KhoiKienThuc) WHERE k.id STARTS WITH n.ma_nganh + '_' RETURN k.ten_khoi, collect(m.ten_mon) AS Danh_Sach_Mon"
        },
        {
            "id": "ex10",
            "question": "Có bao nhiêu ngành tất cả?",
            "cypher": "MATCH (n:Nganh) RETURN count(n) AS Tong_So_Nganh"
        },
        {
            "id": "ex11",
            "question": "Học kỳ 2 ngành Công nghệ thông tin học những môn gì? Cần học những môn nào trước?",
            "cypher": "MATCH (m:MonHoc)-[:THUOC_HOC_KY]->(h:HocKy {{ten_hoc_ky: '2'}})-[:THUOC_CHUONG_TRINH]->(n:Nganh) WHERE toLower(n.ten_nganh) CONTAINS 'công nghệ thông tin' OPTIONAL MATCH (m)-[:THUOC_KHOI_KIEN_THUC]->(k:KhoiKienThuc) WHERE k.id STARTS WITH n.ma_nganh + '_' OPTIONAL MATCH (m)-[:YEU_CAU_MON_TRUOC]->(pre:MonHoc) OPTIONAL MATCH (m)-[:CO_SO_TIN_CHI]->(tc:TinChi) RETURN m.ten_mon, k.ten_khoi, tc.so_luong, collect(DISTINCT pre.ten_mon) AS Mon_Tien_Quyet"
        },
        {
            "id": "ex12",
            "question": "Ngành Ngôn ngữ Anh có những môn tự chọn và bắt buộc nào?",
            "cypher": "MATCH (m:MonHoc)-[:THUOC_CHUONG_TRINH]->(n:Nganh) WHERE toLower(n.ten_nganh) CONTAINS 'ngôn ngữ anh' OPTIONAL MATCH (m)-[:THUOC_LOAI_HOC_PHAN]->(l:LoaiHocPhan) WHERE l.id STARTS WITH n.ma_nganh + '_' RETURN m.ten_mon, l.ten_loai"
        },
        {
            "id": "ex13",
            "question": "Tư vấn lộ trình học ngành Công nghệ thông tin? / 4 năm học ngành CNTT như thế nào? / Review chương trình đào tạo ngành CNTT?",
            "cypher": "MATCH (m:MonHoc)-[:THUOC_HOC_KY]->(h:HocKy)-[:THUOC_CHUONG_TRINH]->(n:Nganh) WHERE toLower(n.ten_nganh) CONTAINS 'công nghệ thông tin' OPTIONAL MATCH (m)-[:THUOC_KHOI_KIEN_THUC]->(k:KhoiKienThuc) WHERE k.id STARTS WITH n.ma_nganh + '_' RETURN toInteger(h.ten_hoc_ky) AS Hoc_Ky, k.ten_khoi, collect(m.ten_mon) AS Cac_Mon_Hoc ORDER BY Hoc_Ky"
        },
        {
            "id": "ex14",
            "question": "Năm nhất ngành Công nghệ thông tin học những môn gì? / Liệt kê chi tiết năm 1 ngành CNTT?",
            "cypher": "MATCH (m:MonHoc)-[:THUOC_HOC_KY]->(h:HocKy)-[:THUOC_CHUONG_TRINH]->(n:Nganh) WHERE toLower(n.ten_nganh) CONTAINS 'công nghệ thông tin' AND h.ten_hoc_ky IN ['1', '2', '3'] OPTIONAL MATCH (m)-[:THUOC_KHOI_KIEN_THUC]->(k:KhoiKienThuc) WHERE k.id STARTS WITH n.ma_nganh + '_' OPTIONAL MATCH (m)-[:THUOC_HOC_KY]->(all_h:HocKy)-[:THUOC_CHUONG_TRINH]->(n) RETURN h.ten_hoc_ky AS HK_Hien_Tai, k.ten_khoi, m.ten_mon, collect(DISTINCT all_h.ten_hoc_ky) AS Cac_HK ORDER BY toInteger(HK_Hien_Tai)"
        },
        {
            "id": "ex15",
            "question": "Môn Cơ sở lập trình có quan trọng không? / Rớt môn Cấu trúc dữ liệu bị chặn bao nhiêu môn? / Môn X có phải môn cổ chai không?",
            "cypher": "MATCH (m:MonHoc)<-[:YEU_CAU_MON_TRUOC]-(next:MonHoc) WHERE toLower(m.ten_mon) CONTAINS 'cơ sở lập trình' RETURN m.ten_mon, count(next) AS So_Mon_Bi_Chan, collect(next.ten_mon) AS Danh_Sach_Mon_Bi_Chan"
        },
        {
            "id": "ex16",
            "question": "Ngành Công nghệ thông tin môn nào quan trọng nhất? / Các môn học cổ chai của ngành CNTT?",
            "cypher": "MATCH (m:MonHoc)-[:THUOC_CHUONG_TRINH]->(n:Nganh) WHERE toLower(n.ten_nganh) CONTAINS 'công nghệ thông tin' MATCH (m)<-[:YEU_CAU_MON_TRUOC]-(next:MonHoc) RETURN m.ten_mon, count(next) AS So_Mon_Bi_Chan, collect(next.ten_mon) AS Danh_Sach_Mon_Bi_Chan ORDER BY So_Mon_Bi_Chan DESC LIMIT 5"
        },
        {
            "id": "ex17",
            "question": "Chuyên ngành Kỹ thuật phần mềm môn nào quan trọng nhất? / Các môn cổ chai của chuyên ngành HTTT?",
            "cypher": "MATCH (m:MonHoc)-[:THUOC_CHUONG_TRINH]->(n:Nganh) WHERE toLower(n.ten_nganh) CONTAINS 'công nghệ thông tin' MATCH (m)-[:THUOC_KHOI_KIEN_THUC]->(k:KhoiKienThuc) WHERE k.id STARTS WITH n.ma_nganh + '_' AND (NOT toLower(k.ten_khoi) CONTAINS 'chuyên ngành' OR toLower(k.ten_khoi) CONTAINS 'kỹ thuật phần mềm') MATCH (m)<-[:YEU_CAU_MON_TRUOC]-(next:MonHoc) RETURN m.ten_mon, count(next) AS So_Mon_Bi_Chan, collect(next.ten_mon) AS Danh_Sach_Mon_Bi_Chan ORDER BY So_Mon_Bi_Chan DESC LIMIT 5"
        },
        {
            "id": "ex18",
            "question": "Chương trình đào tạo ngành CNTT chuyên ngành Kỹ thuật máy tính? / Lộ trình chuyên ngành Hệ thống thông tin?",
            "cypher": "MATCH (m:MonHoc)-[:THUOC_HOC_KY]->(h:HocKy)-[:THUOC_CHUONG_TRINH]->(n:Nganh) WHERE toLower(n.ten_nganh) CONTAINS 'công nghệ thông tin' MATCH (m)-[:THUOC_KHOI_KIEN_THUC]->(k:KhoiKienThuc) WHERE k.id STARTS WITH n.ma_nganh + '_' AND (NOT toLower(k.ten_khoi) CONTAINS 'chuyên ngành' OR toLower(k.ten_khoi) CONTAINS 'kỹ thuật máy tính') OPTIONAL MATCH (m)-[:THUOC_LOAI_HOC_PHAN]->(l:LoaiHocPhan) WHERE l.id STARTS WITH n.ma_nganh + '_' OPTIONAL MATCH (m)-[:CO_SO_TIN_CHI]->(tc:TinChi) OPTIONAL MATCH (m)-[:THUOC_HOC_KY]->(all_h:HocKy)-[:THUOC_CHUONG_TRINH]->(n) OPTIONAL MATCH (m)-[:YEU_CAU_MON_TRUOC]->(pre:MonHoc) RETURN toInteger(h.ten_hoc_ky) AS Hoc_Ky, k.ten_khoi, m.ten_mon, tc.so_luong, l.ten_loai, collect(DISTINCT all_h.ten_hoc_ky) AS Cac_HK, collect(DISTINCT pre.ten_mon) AS Mon_Tien_Quyet ORDER BY Hoc_Ky"
        },
        {
            "id": "ex19",
            "question": "Tính tổng số tín chỉ của chuyên ngành Khoa học máy tính? / Chuyên ngành Hệ thống thông tin bao nhiêu tín?",
            "cypher": "MATCH (m:MonHoc)-[:THUOC_CHUONG_TRINH]->(n:Nganh) WHERE toLower(n.ten_nganh) CONTAINS 'công nghệ thông tin' MATCH (m)-[:THUOC_KHOI_KIEN_THUC]->(k:KhoiKienThuc) WHERE k.id STARTS WITH n.ma_nganh + '_' AND (NOT toLower(k.ten_khoi) CONTAINS 'chuyên ngành' OR toLower(k.ten_khoi) CONTAINS 'khoa học máy tính') OPTIONAL MATCH (m)-[:CO_SO_TIN_CHI]->(tc:TinChi) OPTIONAL MATCH (m)-[:THUOC_LOAI_HOC_PHAN]->(l:LoaiHocPhan) WHERE l.id STARTS WITH n.ma_nganh + '_' OPTIONAL MATCH (m)-[:THUOC_HOC_KY]->(all_h:HocKy)-[:THUOC_CHUONG_TRINH]->(n) OPTIONAL MATCH (m)-[:YEU_CAU_MON_TRUOC]->(pre:MonHoc) RETURN m.ten_mon, tc.so_luong, k.ten_khoi, l.ten_loai, collect(DISTINCT all_h.ten_hoc_ky) AS Cac_HK, collect(DISTINCT pre.ten_mon) AS Mon_Tien_Quyet"
        },
        {
            "id": "ex20",
            "question": "Học kỳ 7 chuyên ngành Hệ thống thông tin có những môn gì? / Kỳ 6 chuyên ngành KTPM bao nhiêu tín?",
            "cypher": "MATCH (m:MonHoc)-[:THUOC_HOC_KY]->(h:HocKy {{ten_hoc_ky: '7'}})-[:THUOC_CHUONG_TRINH]->(n:Nganh) WHERE toLower(n.ten_nganh) CONTAINS 'công nghệ thông tin' MATCH (m)-[:THUOC_KHOI_KIEN_THUC]->(k:KhoiKienThuc) WHERE k.id STARTS WITH n.ma_nganh + '_' AND (NOT toLower(k.ten_khoi) CONTAINS 'chuyên ngành' OR toLower(k.ten_khoi) CONTAINS 'hệ thống thông tin') OPTIONAL MATCH (m)-[:CO_SO_TIN_CHI]->(tc:TinChi) OPTIONAL MATCH (m)-[:THUOC_LOAI_HOC_PHAN]->(l:LoaiHocPhan) WHERE l.id STARTS WITH n.ma_nganh + '_' OPTIONAL MATCH (m)-[:YEU_CAU_MON_TRUOC]->(pre:MonHoc) RETURN m.ten_mon, tc.so_luong, k.ten_khoi, l.ten_loai, h.ten_hoc_ky, collect(DISTINCT pre.ten_mon) AS Mon_Tien_Quyet"
        }
    ]

# Chuẩn bị dữ liệu
documents = [ex["question"] for ex in examples]
metadatas = [{"cypher": ex["cypher"]} for ex in examples]
ids = [ex["id"] for ex in examples]

# Đẩy vào database
collection.upsert(documents=documents, metadatas=metadatas, ids=ids)
print(f"✅ Đã nạp thành công {len(examples)} ví dụ vào ChromaDB!")