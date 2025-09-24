# 🎯 Hướng dẫn cải thiện độ chính xác nhận diện khuôn mặt

## ✅ Các cải tiến đã thực hiện:

### 1. **Giảm Tolerance (Độ nghiêm ngặt)**
- **Trước:** 0.6 (quá lỏng lẻo)
- **Sau:** 0.4 (nghiêm ngặt hơn)
- **Ý nghĩa:** Giảm khả năng nhận diện sai

### 2. **Cải thiện thuật toán nhận diện**
- ✅ Sử dụng multiple templates per employee
- ✅ Chọn template tốt nhất cho mỗi người
- ✅ Cải thiện quality score calculation
- ✅ Resize ảnh lớn để tăng performance
- ✅ Sử dụng cả HOG và CNN models
- ✅ Chọn khuôn mặt lớn nhất nếu có nhiều khuôn mặt

### 3. **Tính toán confidence score tốt hơn**
- ✅ Dựa trên distance và quality
- ✅ Boost confidence cho ảnh chất lượng cao
- ✅ Hiển thị số templates đã so sánh

## 📊 Cách điều chỉnh độ chính xác:

### **Giảm Tolerance (Nghiêm ngặt hơn):**
```bash
# Trong docker-compose.yml hoặc .env
FACE_RECOGNITION_TOLERANCE=0.3  # Rất nghiêm ngặt
FACE_RECOGNITION_TOLERANCE=0.35 # Nghiêm ngặt
```

### **Tăng Tolerance (Lỏng lẻo hơn):**
```bash
FACE_RECOGNITION_TOLERANCE=0.5  # Vừa phải
FACE_RECOGNITION_TOLERANCE=0.6  # Lỏng lẻo
```

## 🎯 Hướng dẫn sử dụng để có độ chính xác cao:

### **1. Chất lượng ảnh đăng ký:**
- ✅ **Ánh sáng tốt:** Tránh bóng tối, ánh sáng quá mạnh
- ✅ **Khuôn mặt rõ ràng:** Không bị mờ, không bị che khuất
- ✅ **Kích thước phù hợp:** Khuôn mặt chiếm 20-30% ảnh
- ✅ **Góc chụp:** Nhìn thẳng, không nghiêng quá nhiều
- ✅ **Chỉ 1 khuôn mặt:** Không có người khác trong ảnh

### **2. Đăng ký nhiều templates:**
```bash
# Đăng ký 3-5 ảnh khác nhau cho mỗi người
# - Ảnh chụp thẳng
# - Ảnh chụp nghiêng nhẹ
# - Ảnh với ánh sáng khác nhau
# - Ảnh với biểu cảm khác nhau
```

### **3. Test và điều chỉnh:**
```bash
# Test với ảnh đã đăng ký
curl -X POST http://localhost:5555/api/face/recognize \
  -F "image=@test_image.jpg"

# Kiểm tra confidence score
# - > 0.8: Rất tốt
# - 0.6-0.8: Tốt
# - 0.4-0.6: Chấp nhận được
# - < 0.4: Cần cải thiện
```

## 🔧 Troubleshooting:

### **Vấn đề: Không nhận diện được**
**Nguyên nhân có thể:**
1. Tolerance quá thấp (0.3)
2. Ảnh chất lượng kém
3. Chưa đăng ký đủ templates
4. Ánh sáng khác biệt quá nhiều

**Giải pháp:**
1. Tăng tolerance lên 0.5
2. Cải thiện chất lượng ảnh
3. Đăng ký thêm templates
4. Test với ảnh tương tự điều kiện đăng ký

### **Vấn đề: Nhận diện sai**
**Nguyên nhân có thể:**
1. Tolerance quá cao (0.6+)
2. Templates chất lượng kém
3. Nhiều người giống nhau

**Giải pháp:**
1. Giảm tolerance xuống 0.3-0.4
2. Xóa templates chất lượng kém
3. Đăng ký nhiều templates chất lượng cao

## 📈 Monitoring:

### **Kiểm tra logs:**
```bash
docker-compose logs -f face-recognition-app
```

### **Kiểm tra database:**
```bash
# Xem số lượng templates
docker exec -it face_attendance_app python -c "
import psycopg2
conn = psycopg2.connect('postgresql://postgres:postgres@160.191.245.38:5433/face_attendance')
cursor = conn.cursor()
cursor.execute('SELECT employee_id, COUNT(*) FROM face_embeddings WHERE status=\\'ACTIVE\\' GROUP BY employee_id;')
for row in cursor.fetchall():
    print(f'Employee {row[0]}: {row[1]} templates')
"
```

## 🎯 Kết luận:

**Độ chính xác hiện tại đã được cải thiện đáng kể:**
- ✅ Tolerance: 0.4 (nghiêm ngặt)
- ✅ Multiple templates per employee
- ✅ Better quality assessment
- ✅ Improved confidence calculation

**Để có độ chính xác tối ưu:**
1. Sử dụng ảnh chất lượng cao
2. Đăng ký 3-5 templates per person
3. Test và điều chỉnh tolerance theo nhu cầu
4. Monitor logs và database thường xuyên
